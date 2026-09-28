#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 EP##_segments.yaml 提取对白，生成 SRT 并烧录字幕、拼接成片；支持人物出场卡。

本机 ffmpeg 无 libass/subtitles/drawtext 滤镜（Homebrew 精简构建），
故用 PIL 渲染字幕条 PNG + overlay enable=between(t,..) 烧录。

对白时间轴为估算：每段内按台词字数比例分配（无 ASR 对齐），
排版规范对齐 docs/references/爆款短剧制作工艺拉片.md：
字幕块底边距底部 320px（25%）、字幕中心约 72% 高度、白字黑描边；
单行短句优先，超 14 字自动折行仅为兜底（源头台词应控制短句）。

人物出场卡（name card）：segments.yaml 的 segment 上可选 `name_card` 字段
（dict 或 list），首次登场自动叠加「姓名（大）+ 关系/头衔（小）」卡；
地点卡（location card）：可选 `location_card` 字段，场景首次出现时叠加
竖排地点名（如「护国公府」），爆款实测同款：

  - segment_id: EP01-SEG02
    name_card:            # 或 list 支持同段多卡
      name: 宋昭           # 必填：姓名（大字）
      role: 护国公府二小姐  # 可选：以主角为锚点的关系或头衔（小字）
      style: vertical      # 可选：vertical（默认，四部爆款实测均竖排）| horizontal
      at: 0.3              # 可选：段内出现时刻（秒，默认 0.3；应对准角色清晰露脸镜头）
      duration: 2.5        # 可选：停留时长（秒，默认 2.5；爆款实测 ≥2s）
      x: 480               # 可选：像素坐标覆盖；未指定时自动选画面较空一侧（左/右边缘复杂度分析）
      y: 140
    location_card:         # 地点卡：场景首次出现的 SEG 登记
      text: 护国公府        # 必填：地点名（建议 ≤6 字）
      at: 0.3              # 可选，同上
      duration: 2.5

字幕-语音对齐（--tts-dir）：默认时间轴按字数估算；传入 tts_batch_edge 产出的
目录（001.mp3...与 cue 顺序一致）后，按每句音频实际时长重排时间轴，
再经 mix_tts_from_srt.py 按 SRT 起点叠音即可声字同步。同时产出
`EP##_对白_lines.txt`（一行一句，供 tts_batch_edge --lines）闭环。

用法（仓库根）：
  python3 script/burn_subtitles.py EP01 --project-root dramas/<剧名>
产出：
  <project>/剧本/EP01/EP01_对白.srt          （字幕文件）
  <project>/assets/generated/EP01/EP01_成片.mp4      （无字幕拼接）
  <project>/assets/generated/EP01/EP01_成片_字幕.mp4 （烧录字幕+出场卡成片）
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat

FONT_CANDIDATES = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
]
CARD_FONT_CANDIDATES = [                     # 出场卡用宋体类衬线（对齐爆款竖排卡质感）
    "/System/Library/Fonts/Supplemental/Songti.ttc",
]
FONT_SIZE = 46           # 字幕字号（爆款实测 46–50px@720w）
WRAP_CHARS = 14          # 每行最大字符数
BOTTOM_MARGIN = 320      # 字幕块底边距画面底部（字幕中心≈72%高度，避开播放器底部UI；爆款实测）
LEAD_IN = 0.5            # 每段首条台词起始偏移
TAIL_PAD = 0.4           # 每段末尾留白
MIN_CUE = 1.0            # 单条最短显示时长

# 人物出场卡默认参数（见 docs/references/爆款短剧制作工艺拉片.md §四）
CARD_AT = 0.3            # 段内默认出现时刻（应对准角色清晰露脸镜头，可用 at 覆盖）
CARD_DURATION = 2.5      # 默认停留时长（爆款实测卡在屏 ≥2s）
CARD_NAME_SIZE = 58      # 姓名字号（大，实测≈50–60px）
CARD_ROLE_SIZE = 34      # 关系/头衔字号（小）
CARD_NAME_GAP = 12       # 竖排姓名字间距
CARD_ROLE_GAP = 8        # 竖排身份字间距
LOC_SIZE = 40            # 地点卡字号（竖排单列，介于姓名与身份之间）
LOC_GAP = 10             # 地点卡字间距
CUE_GAP = 0.15           # TTS 对齐模式下相邻 cue 间隔

DIALOG_RE = re.compile(
    r"对白（([^，）]+)[^）]*）：「(.+?)」|<d>\[中文\]\s*(.+?)</d>", re.S)


def extract_dialogue_lines(seg: dict) -> list[str]:
    """提取段内对白（按句拆条）。

    优先读结构化 api 块（subjects/shots[].speakers[].dialogue，P2 主路径，
    与渲染产物解耦）；无结构化块时回退 DIALOG_RE 正则解析 api.text
    （兼容旧格式「对白（角色，voice）：『台词』」与新六段式 <d>[中文] 台词</d>）。"""
    api = seg.get("api") or {}
    shots = api.get("shots") or []
    lines: list[str] = []
    if api.get("subjects") and shots:
        # 结构化块：subjects 提供角色名映射，speakers 按出现顺序收集
        sub_names = {}
        for s in api.get("subjects") or []:
            if s.get("id"):
                sub_names[str(s["id"])] = str(s.get("name") or s["id"])
            if s.get("file"):
                sub_names.setdefault(str(s["file"]), str(s.get("name") or s["file"]))
        for sh in shots:
            for sp in sh.get("speakers") or []:
                sub_ref = str(sp.get("subject") or "").strip()
                dialogue = str(sp.get("dialogue") or "").strip()
                if not dialogue:
                    continue
                # 只拆台词本身（与旧正则路径一致，不拼说话人前缀，避免字幕带「角色：」）
                lines.extend(split_sentences(dialogue))
        return lines
    for m_ in DIALOG_RE.findall(api.get("text", "") or ""):
        # 元组形如 (角色名, 旧格式台词, 新<d>台词)：取非空的台词组（组 1 或组 2）
        line = next((x for x in m_[1:] if x), "")
        if line:
            # 反转义渲染器转义的 < >（<d> 路径可能含 &lt;/&gt;）
            line = line.replace("&lt;", "<").replace("&gt;", ">")
            lines.extend(split_sentences(line.strip()))
    return lines


def ffprobe_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def ffprobe_size(path: Path) -> tuple[int, int]:
    """探测视频宽高（MiniMax-H3 768P 为 768x1344，非 720x1280，字幕/卡需按实际尺寸居中）。"""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True)
    lines = r.stdout.strip().split("\n")
    return int(lines[0].strip()), int(lines[1].strip())


def fmt_srt(sec: float) -> str:
    ms = int(round(sec * 1000))
    h, rem = divmod(ms, 3600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def load_font_path() -> str:
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return p
    print("未找到中文字体", file=sys.stderr)
    sys.exit(1)


def load_font() -> ImageFont.FreeTypeFont:
    """字幕字体：优先取粗体 face（Hiragino W6），对齐爆款字幕字重。"""
    path = load_font_path()
    return _pick_face(path, FONT_SIZE, prefer=("W6", "Bold", "Medium"))


def _pick_face(path: str, size: int, prefer: tuple[str, ...]) -> ImageFont.FreeTypeFont:
    """在 ttc 多 face 中按样式名关键词选择，选不到用 index 0。"""
    for idx in range(8):
        try:
            f = ImageFont.truetype(path, size, index=idx)
        except OSError:
            break
        style = " ".join(f.getname())
        if any(k.lower() in style.lower() for k in prefer):
            return f
    return ImageFont.truetype(path, size)


def load_card_font(size: int) -> ImageFont.FreeTypeFont:
    """出场卡字体：宋体粗体（衬线，古装/年代/都市爆款卡通用质感），缺宋体时回退字幕字体。"""
    for p in CARD_FONT_CANDIDATES:
        if Path(p).exists():
            return _pick_face(p, size, prefer=("Bold", "黑", "Heavy"))
    return _pick_face(load_font_path(), size, prefer=("W6", "Bold", "Medium"))


def wrap(text: str, n: int) -> list[str]:
    return [text[i:i + n] for i in range(0, len(text), n)] or [text]


# 烧录层去标点（爆款实测字幕近零标点：句读删除、句中停顿用空格）；
# 仅作用于画面字幕，SRT 保留原标点供 TTS 断句/审阅。
CUE_PUNCT_RE = re.compile(r"[，。、；：！？!?,.;:…]+|—+|~+|～+")


def clean_cue_text(text: str) -> str:
    # 标点直接删除而非替换为空格（中文标点后无需空格，避免字幕出现怪异空格）
    return re.sub(r"\s+", " ", CUE_PUNCT_RE.sub("", text)).strip()


# 长台词按句拆条（一句一条、随语音节奏切，对齐爆款）；拆分后保留原标点供 SRT/TTS
SENT_SPLIT_RE = re.compile(r"(?<=[。！？!?；;])|(?<=……)|(?<=——)")


def split_sentences(line: str) -> list[str]:
    pieces = [p.strip() for p in SENT_SPLIT_RE.split(line) if p.strip()]
    merged: list[str] = []
    for p in pieces:  # 碎片（≤2字，如单独的“——”残片）并入前一条
        if merged and len(clean_cue_text(p)) <= 2:
            merged[-1] += p
        else:
            merged.append(p)
    return merged or [line]


def render_cue_png(text: str, width: int, out: Path, font) -> int:
    """渲染透明底字幕条（去标点后），返回图高。"""
    lines = wrap(clean_cue_text(text), WRAP_CHARS)
    line_h = FONT_SIZE + 14
    h = line_h * len(lines) + 12
    img = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        w = d.textlength(ln, font=font)
        x = (width - w) / 2
        y = 6 + i * line_h
        d.text((x, y), ln, font=font, fill=(255, 255, 255, 255),
               stroke_width=3, stroke_fill=(0, 0, 0, 220))
    img.save(out)
    return h


def _draw_vertical_column(d: ImageDraw.ImageDraw, chars: str, x: int, y: int,
                          font, size: int, gap: int,
                          fill=(255, 255, 255, 255)) -> int:
    """竖排逐字绘制一列（无描边，阴影另层处理），返回列底部 y。"""
    cy = y
    for ch in chars:
        d.text((x, cy), ch, font=font, fill=fill)
        cy += size + gap
    return cy


def _soft_shadow(txt_layer: Image.Image) -> Image.Image:
    """用文字层 alpha 生成柔和投影（爆款卡是软阴影而非硬黑描边）。"""
    a = txt_layer.split()[3]
    shadow = Image.new("RGBA", txt_layer.size, (0, 0, 0, 0))
    shadow.putalpha(a.point(lambda v: int(v * 0.75)))
    return shadow.filter(ImageFilter.GaussianBlur(4))


def pick_empty_side(mp4: Path, t: float, tmp_png: Path) -> str:
    """抽挂卡时刻的帧，比较左右上部边缘复杂度，返回较空一侧 'left'/'right'。

    参考剧做法：卡放人物侧旁负空间，避免压脸/压主体。分析失败时回退 right。
    """
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", f"{max(t, 0.0):.3f}",
             "-i", str(mp4), "-frames:v", "1", str(tmp_png)],
            check=True, capture_output=True)
        frame = Image.open(tmp_png).convert("L")
        w, h = frame.size
        band_w, y0, y1 = int(w * 0.36), int(h * 0.07), int(h * 0.5)  # 卡所在的上部区域
        edges = frame.filter(ImageFilter.FIND_EDGES)
        left = ImageStat.Stat(edges.crop((0, y0, band_w, y1))).mean[0]
        right = ImageStat.Stat(edges.crop((w - band_w, y0, w, y1))).mean[0]
        return "left" if left < right else "right"
    except Exception as exc:  # 单卡选边失败不阻断整集烧录
        print(f"⚠️ 出场卡选边分析失败（{exc}），默认靠右", file=sys.stderr)
        return "right"


def render_name_card_png(card: dict, out: Path,
                         width: int, height: int,
                         side: str = "right") -> tuple[int, int]:
    """渲染人物出场卡 PNG，返回叠加坐标 (x, y)。

    默认竖排（四部爆款实测均为竖排卡）：身份/关系小字列在左上，
    姓名大字列在右侧向下错落；宋体粗体、白字柔和投影。
    style: vertical（默认）| horizontal（保留选项，姓名一行+关系一行）。
    side：'left'/'right'，由调用方选边（负空间分析）；card 显式 x/y 优先。
    """
    name = str(card.get("name", "") or "").strip()
    role = str(card.get("role", "") or "").strip()
    if len(role) > 7:
        print(f"⚠️ 出场卡身份过长（{len(role)}字）：「{role}」——爆款基准 ≤7 字，建议精简",
              file=sys.stderr)
    style = card.get("style", "vertical")
    if style not in ("vertical", "horizontal"):
        print(f"⚠️ 出场卡 style 非法值「{style}」，已按 vertical 渲染", file=sys.stderr)
        style = "vertical"
    name_font = load_card_font(CARD_NAME_SIZE)
    role_font = load_card_font(CARD_ROLE_SIZE)
    pad = 10

    if style == "horizontal":
        tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
        name_w = int(tmp.textlength(name, font=name_font))
        role_w = int(tmp.textlength(role, font=role_font)) if role else 0
        w = max(name_w, role_w) + pad * 2
        h = CARD_NAME_SIZE + (CARD_ROLE_SIZE + 16 if role else 0) + pad * 2 + 8
        txt = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(txt)
        d.text((pad, pad), name, font=name_font, fill=(255, 255, 255, 255))
        if role:
            d.text((pad, pad + CARD_NAME_SIZE + 14), role, font=role_font,
                   fill=(255, 255, 255, 235))
        dy = int(height * 0.30)
    else:
        role_h = len(role) * (CARD_ROLE_SIZE + CARD_ROLE_GAP) if role else 0
        name_h = len(name) * (CARD_NAME_SIZE + CARD_NAME_GAP)
        stagger = int(role_h * 0.55) if role else 0   # 姓名列向下错落
        name_x = (CARD_ROLE_SIZE + 18 if role else 0) + pad
        w = name_x + CARD_NAME_SIZE + pad + 6
        h = max(role_h, stagger + name_h) + pad * 2
        txt = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(txt)
        if role:
            _draw_vertical_column(d, role, pad, pad, role_font,
                                  CARD_ROLE_SIZE, CARD_ROLE_GAP,
                                  fill=(255, 255, 255, 235))
        _draw_vertical_column(d, name, name_x, pad + stagger, name_font,
                              CARD_NAME_SIZE, CARD_NAME_GAP)
        dy = 130

    dx = 56 if side == "left" else width - txt.width - 56
    m = 10  # 阴影外扩边距，避免模糊尾部被画布截断
    img = Image.new("RGBA", (txt.width + m * 2, txt.height + m * 2), (0, 0, 0, 0))
    img.alpha_composite(_soft_shadow(txt), (m + 3, m + 4))
    img.alpha_composite(txt, (m, m))
    img.save(out)
    return int(card.get("x", dx - m)), int(card.get("y", dy - m))


def render_location_card_png(card: dict, out: Path,
                             width: int, height: int,
                             side: str = "right") -> tuple[int, int]:
    """渲染地点卡 PNG（竖排单列，爆款实测同款如「护国公府」），返回叠加坐标。"""
    text = str(card.get("text", "") or "").strip()
    if len(text) > 6:
        print(f"⚠️ 地点卡过长（{len(text)}字）：「{text}」，建议 ≤6 字", file=sys.stderr)
    font = load_card_font(LOC_SIZE)
    pad = 8
    w = LOC_SIZE + pad * 2 + 4
    h = len(text) * (LOC_SIZE + LOC_GAP) + pad * 2
    txt = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    _draw_vertical_column(d, text, pad, pad, font, LOC_SIZE, LOC_GAP)
    dx = 48 if side == "left" else width - w - 48
    dy = 110
    m = 10
    img = Image.new("RGBA", (w + m * 2, h + m * 2), (0, 0, 0, 0))
    img.alpha_composite(_soft_shadow(txt), (m + 3, m + 4))
    img.alpha_composite(txt, (m, m))
    img.save(out)
    return int(card.get("x", dx - m)), int(card.get("y", dy - m))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--project-root", required=True)
    ap.add_argument("--no-burn", action="store_true", help="只出 SRT 和拼接，不烧字幕")
    ap.add_argument("--tts-dir", help="tts_batch_edge 产出目录（001.mp3...），按音频实际时长对齐字幕时间轴")
    ap.add_argument("--no-asr", action="store_true", help="关闭 ASR 对齐，改用字数估算时间轴（默认开启 ASR）")
    args = ap.parse_args()

    ep = args.episode
    proj = Path(args.project_root)
    seg_yaml = proj / "剧本" / ep / f"{ep}_segments.yaml"
    gen_dir = proj / "assets" / "generated" / ep
    data = yaml.safe_load(seg_yaml.read_text(encoding="utf-8"))
    segments = data.get("segments") or data.get("Segments")

    # 1. 收集片段与对白（按句拆条），累加时间轴；同时收集人物出场卡/地点卡
    cues = []   # [start, end, text, seg_start, seg_end]
    cards = []  # (start, end, card_dict, mp4, mid)
    locs = []   # (start, end, card_dict, mp4, mid)
    clips = []
    seg_scene_cards = []  # (sid, scene_id, has_location_card) — 场景首现缺卡检查用
    t0 = 0.0
    for i, seg in enumerate(segments):
        # 兼容两种命名：segment_id: EP01-SEG01（文件同名）/ seg_id: SEG01（文件 EP01_SEG01）
        sid = seg.get("segment_id") or (
            f"{ep}_{seg['seg_id']}" if seg.get("seg_id") else None)
        if not sid:
            print(f"segments[{i}] 缺 segment_id / seg_id 字段", file=sys.stderr)
            sys.exit(1)
        mp4 = gen_dir / f"{sid}.mp4"
        if not mp4.is_file():
            print(f"缺片段视频：{mp4}", file=sys.stderr)
            sys.exit(1)
        dur = ffprobe_duration(mp4)
        clips.append((mp4, dur))
        nc = seg.get("name_card")
        if nc:
            for card in (nc if isinstance(nc, list) else [nc]):
                if not str(card.get("name", "") or "").strip():
                    print(f"{sid}.name_card 缺必填字段 name", file=sys.stderr)
                    sys.exit(1)
                at = max(0.0, min(float(card.get("at", CARD_AT)),
                                  max(dur - 0.5, 0.0)))
                cd = float(card.get("duration", CARD_DURATION))
                # 选边用挂卡显示窗口中点帧（限在本段内）
                mid = min(at + cd / 2, max(dur - 0.1, 0.0))
                cards.append((t0 + at, min(t0 + at + cd, t0 + dur),
                              card, mp4, mid))
        lc = seg.get("location_card")
        if lc:
            for card in (lc if isinstance(lc, list) else [lc]):
                if not str(card.get("text", "") or "").strip():
                    print(f"{sid}.location_card 缺必填字段 text", file=sys.stderr)
                    sys.exit(1)
                at = max(0.0, min(float(card.get("at", CARD_AT)),
                                  max(dur - 0.5, 0.0)))
                cd = float(card.get("duration", CARD_DURATION))
                mid = min(at + cd / 2, max(dur - 0.1, 0.0))
                locs.append((t0 + at, min(t0 + at + cd, t0 + dur),
                             card, mp4, mid))
        seg_scene_cards.append(
            (sid, ((seg.get("refs") or {}).get("scene_id")), bool(lc)))
        lines = extract_dialogue_lines(seg)
        if lines:
            usable = max(dur - LEAD_IN - TAIL_PAD, MIN_CUE * len(lines))
            weights = [max(len(x), 4) for x in lines]
            total_w = sum(weights)
            t = t0 + LEAD_IN
            for ln, w in zip(lines, weights):
                d = max(usable * w / total_w, MIN_CUE)
                end = min(t + d, t0 + dur - 0.1)
                cues.append([t, end, ln, t0, t0 + dur])
                t = end
        t0 += dur

    # 1.4 卡位检查（仅告警不阻断）：
    # (a) 出场卡/地点卡时间窗重叠 —— 同屏叠卡视觉打架（事故：边荒盐妇 EP01 地点卡与崔氏卡重叠 0.8s）
    _wins = ([(s, e, f"出场卡「{c.get('name','')}」") for s, e, c, _, _ in cards]
             + [(s, e, f"地点卡「{c.get('text','')}」") for s, e, c, _, _ in locs])
    _wins.sort()
    for (s1, e1, n1), (s2, e2, n2) in zip(_wins, _wins[1:]):
        if s2 < e1 - 0.05:
            print(f"⚠️ 卡时间重叠：{n1}({s1:.1f}-{e1:.1f}s) 与 {n2}({s2:.1f}-{e2:.1f}s) —— 建议错开时序", file=sys.stderr)
    # (b) 场景首次出现的 SEG 无地点卡 —— 场景切换漏登（事故：边荒盐妇 EP01 三场景只登了首张）
    _seen = set()
    for sid_, scene_, has_lc_ in seg_scene_cards:
        if scene_ and scene_ not in _seen:
            _seen.add(scene_)
            if not has_lc_:
                print(f"⚠️ 场景首现缺地点卡：{sid_} 首次进入 {scene_} 但未登记 location_card", file=sys.stderr)

    # 1.5 TTS 对齐：按每句音频实际时长重排时间轴（段内顺序、溢出告警）
    if args.tts_dir:
        mp3s = sorted(Path(args.tts_dir).glob("*.mp3"),
                      key=lambda p: int(re.sub(r"\D", "", p.stem) or 0))
        if len(mp3s) != len(cues):
            print(f"TTS 音频数 {len(mp3s)} ≠ 字幕条数 {len(cues)}，无法对齐", file=sys.stderr)
            sys.exit(1)
        cursor = None
        prev_seg = None
        for cue, mp3 in zip(cues, mp3s):
            seg_start, seg_end = cue[3], cue[4]
            if seg_start != prev_seg:  # 新段从段首 LEAD_IN 起排
                cursor = seg_start + LEAD_IN
                prev_seg = seg_start
            d = ffprobe_duration(mp3)
            cue[0] = cursor
            cue[1] = cursor + d
            if cue[1] > seg_end:
                print(f"⚠️ TTS 溢出段尾 {cue[1]-seg_end:.2f}s：「{cue[2][:12]}…」"
                      f"（段窗口 {seg_start:.1f}-{seg_end:.1f}s）", file=sys.stderr)
            cursor = cue[1] + CUE_GAP
        print(f"TTS 对齐：{len(mp3s)} 句音频时长已回填时间轴")

    # 1.6 ASR 对齐：用 faster-whisper 识别每段实际语音边界，按真实语音时长重排时间轴
    # （H3 原生音轨时推荐；字数估算与真实语速/停顿偏差大，导致字幕与对白不同步）
    if not args.no_asr:
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            print("ASR 对齐需要 faster-whisper: pip3 install faster-whisper", file=sys.stderr)
            sys.exit(1)
        print("ASR 对齐：加载模型（首次约 1-2 分钟）...", file=sys.stderr)
        _wm = WhisperModel("base", device="cpu", compute_type="int8")
        _idx = 0
        for seg in segments:
            sid = seg.get("segment_id") or (f"{ep}_{seg['seg_id']}" if seg.get("seg_id") else None)
            if not sid:
                continue
            mp4 = gen_dir / f"{sid}.mp4"
            if _idx >= len(cues):
                break
            seg_start = cues[_idx][3]
            seg_cues = []
            while _idx < len(cues) and abs(cues[_idx][3] - seg_start) < 1e-6:
                seg_cues.append(cues[_idx])
                _idx += 1
            if not seg_cues:
                continue
            try:
                _segs, _ = _wm.transcribe(
                    str(mp4), language="zh", vad_filter=True)
                frags = [(s.start, s.end) for s in _segs]
            except Exception as e:
                print(f"⚠️ {sid} ASR 失败（保留字数估算）：{e}", file=sys.stderr)
                continue
            if not frags:
                print(f"⚠️ {sid} ASR 无语音片段（保留字数估算）", file=sys.stderr)
                continue
            total_voice = sum(e - s for s, e in frags)
            if total_voice <= 0:
                continue
            weights = [max(len(c[2]), 4) for c in seg_cues]
            total_w = sum(weights)

            def _at(ratio: float) -> float:
                target = ratio * total_voice
                acc = 0.0
                for s, e in frags:
                    d = e - s
                    if acc + d >= target:
                        return s + (target - acc)
                    acc += d
                return frags[-1][1]

            cum = 0.0
            for c, w in zip(seg_cues, weights):
                s = _at(cum / total_w)
                cum += w
                e = _at(cum / total_w)
                c[0] = seg_start + max(s, 0.0)
                c[1] = seg_start + max(e, s + 0.1)
        print(f"ASR 对齐：{len(cues)} 条字幕时间轴已按实际语音边界回填")

    # 2. 写 SRT（保留原标点供 TTS/审阅）+ lines.txt（供 tts_batch_edge）
    srt_path = seg_yaml.parent / f"{ep}_对白.srt"
    with srt_path.open("w", encoding="utf-8") as f:
        for i, (s, e, txt, *_rest) in enumerate(cues, 1):
            f.write(f"{i}\n{fmt_srt(s)} --> {fmt_srt(e)}\n{txt}\n\n")
    lines_path = seg_yaml.parent / f"{ep}_对白_lines.txt"
    lines_path.write_text("\n".join(c[2] for c in cues) + "\n", encoding="utf-8")
    print(f"SRT: {srt_path}  cues={len(cues)}  总时长={t0:.2f}s")

    # 3. 拼接（统一音频采样率）
    raw = gen_dir / f"{ep}_成片.mp4"
    n = len(clips)
    inputs = []
    for mp4, _ in clips:
        inputs += ["-i", str(mp4)]
    fc = "".join(f"[{i}:v][{i}:a]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", *inputs,
         "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
         "-r", "24", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "44100", "-b:a", "128k",
         str(raw)], check=True)
    print(f"拼接完成: {raw}")
    if args.no_burn:
        return

    # 4. 渲染字幕/出场卡 PNG + overlay 烧录（按实际视频宽高渲染，避免 720 画布居中于 768 画面时偏左）
    vw, vh = ffprobe_size(clips[0][0])
    width, height = vw, vh
    # 底边距按高度比例缩放（规范基准 720x1280 下 320px ≈ 25%）
    BOTTOM_MARGIN_SCALED = int(BOTTOM_MARGIN * vh / 1280)
    subs_dir = gen_dir / "_subs"
    subs_dir.mkdir(exist_ok=True)
    font = load_font()
    over_inputs, chain = [], []
    prev = "0:v"
    idx = 0
    for s, e, txt, *_rest in cues:
        png = subs_dir / f"cue{idx:03d}.png"
        h = render_cue_png(txt, width, png, font)
        over_inputs += ["-i", str(png)]
        y = height - BOTTOM_MARGIN_SCALED - h
        out = f"v{idx}"
        chain.append(
            f"[{prev}][{idx + 1}:v]overlay=0:{y}:enable='between(t,{s:.3f},{e:.3f})'[{out}]")
        prev = out
        idx += 1
    for s, e, card, seg_mp4, mid in cards:
        png = subs_dir / f"card{idx:03d}.png"
        side = "right"
        if "x" not in card:  # 未手动指定时自动选较空一侧
            side = pick_empty_side(seg_mp4, mid, subs_dir / f"_side{idx:03d}.png")
        cx, cy = render_name_card_png(card, png, width, height, side=side)
        over_inputs += ["-i", str(png)]
        out = f"v{idx}"
        chain.append(
            f"[{prev}][{idx + 1}:v]overlay={cx}:{cy}:enable='between(t,{s:.3f},{e:.3f})'[{out}]")
        prev = out
        idx += 1
    for s, e, card, seg_mp4, mid in locs:
        png = subs_dir / f"loc{idx:03d}.png"
        side = "right"
        if "x" not in card:
            side = pick_empty_side(seg_mp4, mid, subs_dir / f"_side{idx:03d}.png")
        cx, cy = render_location_card_png(card, png, width, height, side=side)
        over_inputs += ["-i", str(png)]
        out = f"v{idx}"
        chain.append(
            f"[{prev}][{idx + 1}:v]overlay={cx}:{cy}:enable='between(t,{s:.3f},{e:.3f})'[{out}]")
        prev = out
        idx += 1
    if cards:
        print(f"出场卡：{len(cards)} 张")
    if locs:
        print(f"地点卡：{len(locs)} 张")
    final = gen_dir / f"{ep}_成片_字幕.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), *over_inputs,
         "-filter_complex", ";".join(chain), "-map", f"[{prev}]", "-map", "0:a",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "copy", str(final)], check=True)
    print(f"烧录完成: {final}")


if __name__ == "__main__":
    main()
