#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 EP##_segments.yaml 提取对白，生成 SRT 并烧录字幕、拼接成片；支持人物出场卡。

本机 ffmpeg 无 libass/subtitles/drawtext 滤镜（Homebrew 精简构建），
故用 PIL 渲染字幕条 PNG + overlay enable=between(t,..) 烧录。

对白时间轴为估算：每段内按台词字数比例分配（无 ASR 对齐），
排版规范对齐 docs/references/爆款短剧制作工艺拉片.md：
底部安全区约 15%、白字黑描边、单行短句优先（超长自动折行）。

人物出场卡（name card）：segments.yaml 的 segment 上可选 `name_card` 字段
（dict 或 list），首次登场自动叠加「姓名（大）+ 关系/头衔（小）」卡：

  - segment_id: EP01-SEG02
    name_card:            # 或 list 支持同段多卡
      name: 宋昭           # 必填：姓名（大字）
      role: 护国公府二小姐  # 可选：以主角为锚点的关系或头衔（小字）
      style: vertical      # 可选：vertical（默认，四部爆款实测均竖排）| horizontal
      at: 0.3              # 可选：段内出现时刻（秒，默认 0.3）
      duration: 1.5        # 可选：停留时长（秒，默认 1.5）
      x: 480               # 可选：像素坐标覆盖默认位置
      y: 140

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
from PIL import Image, ImageDraw, ImageFilter, ImageFont

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
CARD_AT = 0.3            # 段内默认出现时刻
CARD_DURATION = 1.5      # 默认停留时长
CARD_NAME_SIZE = 58      # 姓名字号（大，实测≈50–60px）
CARD_ROLE_SIZE = 34      # 关系/头衔字号（小）
CARD_NAME_GAP = 12       # 竖排姓名字间距
CARD_ROLE_GAP = 8        # 竖排身份字间距

DIALOG_RE = re.compile(r"对白（([^，）]+)[^）]*）：「(.+?)」", re.S)


def ffprobe_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


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


def render_cue_png(text: str, width: int, out: Path, font) -> int:
    """渲染透明底字幕条，返回图高。"""
    lines = wrap(text, WRAP_CHARS)
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


def render_name_card_png(card: dict, out: Path,
                         width: int, height: int) -> tuple[int, int]:
    """渲染人物出场卡 PNG，返回默认叠加坐标 (x, y)。

    默认竖排（四部爆款实测均为竖排卡）：身份/关系小字列在左上，
    姓名大字列在右侧向下错落；宋体粗体、白字柔和投影。
    style: vertical（默认）| horizontal（保留选项，姓名一行+关系一行）。
    """
    name = str(card["name"]).strip()
    role = str(card.get("role", "") or "").strip()
    if len(role) > 7:
        print(f"⚠️ 出场卡身份过长（{len(role)}字）：「{role}」——爆款基准 ≤7 字，建议精简",
              file=sys.stderr)
    style = card.get("style", "vertical")
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
        dx, dy = 56, int(height * 0.30)
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
        dx, dy = width - w - 56, 130

    img = Image.new("RGBA", txt.size, (0, 0, 0, 0))
    img.alpha_composite(_soft_shadow(txt), (3, 4))
    img.alpha_composite(txt)
    img.save(out)
    return int(card.get("x", dx)), int(card.get("y", dy))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--project-root", required=True)
    ap.add_argument("--no-burn", action="store_true", help="只出 SRT 和拼接，不烧字幕")
    args = ap.parse_args()

    ep = args.episode
    proj = Path(args.project_root)
    seg_yaml = proj / "剧本" / ep / f"{ep}_segments.yaml"
    gen_dir = proj / "assets" / "generated" / ep
    data = yaml.safe_load(seg_yaml.read_text(encoding="utf-8"))
    segments = data.get("segments") or data.get("Segments")

    # 1. 收集片段与对白，累加时间轴；同时收集人物出场卡
    cues = []   # (start, end, text)
    cards = []  # (start, end, card_dict)
    clips = []
    t0 = 0.0
    for seg in segments:
        # 兼容两种命名：segment_id: EP01-SEG01（文件同名）/ seg_id: SEG01（文件 EP01_SEG01）
        sid = seg.get("segment_id") or f"{ep}_{seg['seg_id']}"
        mp4 = gen_dir / f"{sid}.mp4"
        if not mp4.is_file():
            print(f"缺片段视频：{mp4}", file=sys.stderr)
            sys.exit(1)
        dur = ffprobe_duration(mp4)
        clips.append((mp4, dur))
        nc = seg.get("name_card")
        if nc:
            for card in (nc if isinstance(nc, list) else [nc]):
                at = min(float(card.get("at", CARD_AT)), max(dur - 0.5, 0.0))
                cd = float(card.get("duration", CARD_DURATION))
                cards.append((t0 + at, min(t0 + at + cd, t0 + dur), card))
        lines = [m[1].strip() for m in DIALOG_RE.findall(seg["api"]["text"])]
        if lines:
            usable = max(dur - LEAD_IN - TAIL_PAD, MIN_CUE * len(lines))
            weights = [max(len(x), 4) for x in lines]
            total_w = sum(weights)
            t = t0 + LEAD_IN
            for ln, w in zip(lines, weights):
                d = max(usable * w / total_w, MIN_CUE)
                end = min(t + d, t0 + dur - 0.1)
                cues.append((t, end, ln))
                t = end
        t0 += dur

    # 2. 写 SRT
    srt_path = seg_yaml.parent / f"{ep}_对白.srt"
    with srt_path.open("w", encoding="utf-8") as f:
        for i, (s, e, txt) in enumerate(cues, 1):
            f.write(f"{i}\n{fmt_srt(s)} --> {fmt_srt(e)}\n{txt}\n\n")
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

    # 4. 渲染字幕/出场卡 PNG + overlay 烧录
    width, height = 720, 1280
    subs_dir = gen_dir / "_subs"
    subs_dir.mkdir(exist_ok=True)
    font = load_font()
    over_inputs, chain = [], []
    prev = "0:v"
    idx = 0
    for s, e, txt in cues:
        png = subs_dir / f"cue{idx:03d}.png"
        h = render_cue_png(txt, width, png, font)
        over_inputs += ["-i", str(png)]
        y = height - BOTTOM_MARGIN - h
        out = f"v{idx}"
        chain.append(
            f"[{prev}][{idx + 1}:v]overlay=0:{y}:enable='between(t,{s:.3f},{e:.3f})'[{out}]")
        prev = out
        idx += 1
    for s, e, card in cards:
        png = subs_dir / f"card{idx:03d}.png"
        cx, cy = render_name_card_png(card, png, width, height)
        over_inputs += ["-i", str(png)]
        out = f"v{idx}"
        chain.append(
            f"[{prev}][{idx + 1}:v]overlay={cx}:{cy}:enable='between(t,{s:.3f},{e:.3f})'[{out}]")
        prev = out
        idx += 1
    if cards:
        print(f"出场卡：{len(cards)} 张")
    final = gen_dir / f"{ep}_成片_字幕.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), *over_inputs,
         "-filter_complex", ";".join(chain), "-map", f"[{prev}]", "-map", "0:a",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "copy", str(final)], check=True)
    print(f"烧录完成: {final}")


if __name__ == "__main__":
    main()
