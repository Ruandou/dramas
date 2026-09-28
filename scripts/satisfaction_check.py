#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""爽点密度校验（satisfaction check）— 把爽感密度从事后评审前移为写时自检。

背景：SAT 爽感框架（story-architect 框架五）与题材基线（script-reviewer 高阶 2）
只在大纲层/事后评审层，scene-writer 写单集时无强制约束——易产出"有冲突但不爽"
（机甲 EP01：唯一羞辱冲突用"平静忍耐"回应，爽点全后置到 EP18/EP22，全集 0 个
当场引爆）。本脚本对单集剧本做爽点量化校验，退出码非 0 即不达标，供：
- scene-writer 自检 9（输出前强制运行）
- segment-builder Gate 复核 / script-reviewer R2 机读

爽点识别（两级）：
1. 优先读 scene-writer 在 SEG 标题/备注的 SAT 代号显式标注（如 `SAT-SLAP`）；
2. 未标注的 SEG 用关键词启发式兜底（羞辱/反击/揭穿/反杀/打脸/反转/真相…），
   且"全集无任何 SAT 标注"本身计一条 WARN（推动 writer 养成标注习惯）。

题材分档（阈值从制片规范/大纲读取，缺失回退默认档）：
- 复仇/爽文 ≥3 爽点、打脸占比 ≥40%；都市/轻喜 ≥2；甜宠 ≥1.5；悬疑 ≥1；仙侠 ≥2。

用法：
  python3 scripts/satisfaction_check.py --ep EP01 --project-root dramas/<剧名>
  python3 scripts/satisfaction_check.py --file <剧本.md> [--project-root <项目根>]
  python3 scripts/satisfaction_check.py --ep EP01 --project-root dramas/<剧名> --json
"""
from __future__ import annotations

import argparse, glob, json, os, re, sys

import yaml


def locate_script(project_root: str, ep: str) -> str | None:
    """定位分集剧本 .md：优先 {ep}_剧本.md，否则 {ep}_*.md（带标题主流命名）。"""
    d = os.path.join(project_root, "剧本", ep)
    exact = os.path.join(d, f"{ep}_剧本.md")
    if os.path.isfile(exact):
        return exact
    matches = sorted(glob.glob(os.path.join(d, f"{ep}_*.md")))
    return matches[0] if matches else None

# ---------------------------------------------------------------------------
# 题材分档默认阈值（制片规范/大纲可覆盖）
# ---------------------------------------------------------------------------

# genre_key: (satisfaction_min 每集最低爽点, slap_min_pct 打脸占比下限, opening_payoff_max_sec 开场引爆时限)
GENRE_TIERS = {
    "复仇":   {"satisfaction_min": 3, "slap_min_pct": 40, "opening_payoff_max_sec": 60},
    "爽文":   {"satisfaction_min": 3, "slap_min_pct": 40, "opening_payoff_max_sec": 60},
    "逆袭":   {"satisfaction_min": 3, "slap_min_pct": 30, "opening_payoff_max_sec": 60},
    "都市":   {"satisfaction_min": 2, "slap_min_pct": 0,  "opening_payoff_max_sec": 75},
    "轻喜":   {"satisfaction_min": 2, "slap_min_pct": 0,  "opening_payoff_max_sec": 75},
    "职场":   {"satisfaction_min": 2, "slap_min_pct": 30, "opening_payoff_max_sec": 75},
    "甜宠":   {"satisfaction_min": 1.5, "slap_min_pct": 0, "opening_payoff_max_sec": 90},
    "家庭":   {"satisfaction_min": 1.5, "slap_min_pct": 0, "opening_payoff_max_sec": 90},
    "悬疑":   {"satisfaction_min": 1, "slap_min_pct": 0,  "opening_payoff_max_sec": 90},
    "仙侠":   {"satisfaction_min": 2, "slap_min_pct": 0,  "opening_payoff_max_sec": 75},
    "玄幻":   {"satisfaction_min": 2, "slap_min_pct": 0,  "opening_payoff_max_sec": 75},
}
DEFAULT_TIER = {"satisfaction_min": 2, "slap_min_pct": 0, "opening_payoff_max_sec": 75}

# SAT 代号 → 爽感类型（用于打脸占比统计）
SAT_CODES = {
    "SAT-SLAP": "打脸", "SAT-COME": "逆袭", "SAT-SWEET": "甜蜜",
    "SAT-PAIN": "虐心", "SAT-MYST": "悬疑", "SAT-BURN": "燃",
    "SAT-COMEDY": "搞笑", "SAT-TOUCH": "感动", "SAT-REV": "反转",
}

# 启发式关键词（仅用于 S2 开场引爆 / S3 冲突段的**定位**，不用于 S1 爽点计数——
# S1 爽点只认 SAT 显式标注，避免把"伏笔提及/背景事件"误判为爽点导致假阴性）。
# 爽点回应（正面情绪释放，用于判定冲突是否被当场回应）
SATISFY_KW = ["打脸", "反杀", "反击", "揭穿", "逆袭", "翻盘", "反败为胜",
              "反怼", "回怼", "怼回", "出气", "逆转", "反转"]
# 冲突/欺压（负面情绪施压，需后续爽点回应）
CONFLICT_KW = ["羞辱", "欺压", "欺辱", "侮辱", "嘲讽", "讥笑", "嘲笑", "看不起",
               "轻视", "贬低", "刁难", "为难", "陷害", "栽赃", "背叛",
               "赶出", "逼迫", "威胁"]
# 开场引爆（强情绪事件）
PAYOFF_KW = ["虐杀", "撞破", "背叛", "重生", "反杀", "当众打脸", "揭穿",
             "逼死", "车祸", "复仇"]


# ---------------------------------------------------------------------------
# 解析
# ---------------------------------------------------------------------------

def load_text(path: str) -> str:
    try:
        return open(path, encoding="utf-8").read()
    except OSError:
        return ""


def detect_genre(project_root: str | None, content: str) -> str:
    """题材判定：优先制片规范「题材关键词」字段，其次剧本正文。

    防否定语境误判：如"不得导向复仇工具化"含"复仇"但题材非复仇——
    先取「题材关键词」字段值（权威），字段缺失才回退全文匹配；全文匹配时
    跳过否定语境（不得/禁止/避免/非 + 题材词）。"""
    def _earliest(text: str) -> str:
        """返回文本中**最早出现**的题材词（最靠前者 = 最主要题材）。

        混合题材（如「仙侠玄幻+甜宠逆袭」）按 GENRE_TIERS 遍历序判定会受 dict 序
        影响（逆袭排仙侠前→误判逆袭）；按出现位置判定更稳定——题材关键词字段/
        标题/类型声明里，主题材通常写在最前。跳过否定语境（不得/禁止/避免/非）。"""
        best_key, best_pos = "", len(text) + 1
        for key in GENRE_TIERS:
            for m in re.finditer(re.escape(key), text):
                ctx = text[max(0, m.start() - 4):m.start()]
                if re.search(r"(不得|禁止|避免|而非|非|不是)$", ctx):
                    continue  # 否定语境，跳过
                if m.start() < best_pos:
                    best_pos, best_key = m.start(), key
                break  # 该题材只取最早一处
        return best_key

    # 1. 权威来源：制片规范「题材关键词」字段（如「近未来都市、机甲竞技、轻喜暖甜」）
    if project_root:
        spec = load_text(os.path.join(project_root, "制片规范.md"))
        m = re.search(r"题材关键词\s*[:|]\s*([^\n]+)", spec)
        if m:
            g = _earliest(m.group(1))
            if g:
                return g
    # 2. 回退：全文匹配（取最早出现的题材词）
    text = ""
    if project_root:
        text += load_text(os.path.join(project_root, "制片规范.md"))
    text += content
    return _earliest(text)


def resolve_tier(genre: str, profile: dict) -> dict:
    """题材分档 + episode_profile 覆盖。"""
    tier = dict(GENRE_TIERS.get(genre, DEFAULT_TIER))
    for k in ("satisfaction_min", "slap_min_pct", "opening_payoff_max_sec"):
        if k in profile and isinstance(profile[k], (int, float)):
            tier[k] = profile[k]
    return tier


# episode_profile 块的标志性字段（用于从多个 yaml 块中识别真正的 episode_profile）
_PROFILE_MARKERS = {"shots_per_episode", "segments_per_episode", "segment_duration_sec"}


def _as_profile(data: dict) -> dict:
    """从解析后的 yaml dict 提取 episode_profile（兼容嵌套/平铺，跳过非 profile 块）。"""
    if not isinstance(data, dict):
        return {}
    if _PROFILE_MARKERS & set(data.keys()):  # 平铺
        return data
    for v in data.values():  # 嵌套
        if isinstance(v, dict) and (_PROFILE_MARKERS & set(v.keys())):
            return v
    return {}


def load_episode_profile(project_root: str | None) -> dict:
    """遍历所有 yaml 块，返回第一个含 episode_profile 标志字段的块（多块项目安全）。"""
    if not project_root:
        return {}
    spec = os.path.join(project_root, "制片规范.md")
    if not os.path.isfile(spec):
        return {}
    for m in re.finditer(r"```yaml\s*\n(.*?)```", load_text(spec), re.DOTALL):
        try:
            data = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue
        prof = _as_profile(data)
        if prof:
            return prof
    return {}


def parse_segs(content: str) -> list[dict]:
    """解析 SEG 块：标题行 + 该 SEG 文本 + 估算时长 + 起始镜号。

    返回 [{seg_id, title, body, duration, first_shot_no}]。"""
    segs = []
    # SEG 标题：## SEG01 — 羞辱（对白段·不公感开场·冲突爆发）
    pattern = re.compile(r"^## (SEG\d+)\s*[—\-]?\s*(.*)$", re.MULTILINE)
    matches = list(pattern.finditer(content))
    for i, m in enumerate(matches):
        seg_id = m.group(1)
        title = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        body = content[start:end]
        # 时长标注三种格式兼容：「Segment时长：12s」「Segment 时长：10s」（空格变体，
        # 布衣账房等）「⏱ 12s｜N镜」（她们催我改剧本等）；不匹配会让 duration=0 失真 S2 累计
        dm = re.search(r"Segment\s*时长[：:]\s*(\d+)", body) or \
             re.search(r"⏱\s*(\d+)\s*s", body)
        duration = int(dm.group(1)) if dm else 0
        segs.append({
            "seg_id": seg_id, "title": title, "body": body,
            "duration": duration, "index": i,
        })
    return segs


def seg_sat(seg: dict) -> str | None:
    """SEG 的 SAT 代号（显式标注优先）。"""
    m = re.search(r"SAT-[A-Z]+", seg["title"] + " " + seg["body"])
    return m.group() if m else None


def seg_has_kw(seg: dict, kws: list[str]) -> bool:
    text = seg["title"] + " " + seg["body"]
    return any(k in text for k in kws)


# ---------------------------------------------------------------------------
# 校验
# ---------------------------------------------------------------------------

def check_satisfaction(segs: list[dict], tier: dict, is_first_ep: bool,
                       total_duration: int) -> tuple[list[str], list[str], dict]:
    errors: list[str] = []
    warns: list[str] = []
    if not segs:
        return ["未解析到任何 SEG（## SEG## 标题缺失）"], [], {}

    # 逐 SEG 标注爽点：只认 SAT 显式标注（关键词易把"伏笔提及/背景事件"
    # 误判为爽点导致假阴性——机甲 EP01 实测"夺冠/爆发"等词命中非爽点段）。
    sat_moments = []   # (seg_id, sat_code)
    slap_count = 0
    any_sat_annotation = False
    for seg in segs:
        code = seg_sat(seg)
        if code:
            any_sat_annotation = True
            sat_moments.append((seg["seg_id"], code))
            if code == "SAT-SLAP":
                slap_count += 1

    if not any_sat_annotation:
        warns.append(
            "全集无 SAT 代号显式标注——爽点计数为 0，必然触发 S1 爽感贫血；"
            "scene-writer 必须在 SEG 标题/备注标注主打爽感类型（SAT-SLAP/COME/...），"
            "标注是爽点统计的唯一依据")

    # S1 爽点总数（仅计 SAT 显式标注）
    n_sat = len(sat_moments)
    if n_sat < tier["satisfaction_min"]:
        errors.append(
            f"S1 爽点总数 {n_sat} 低于题材基线 {tier['satisfaction_min']}——"
            f"爽感贫血（已标注爽点：{[s for s, _ in sat_moments] or '无'}）")

    # S2 开场引爆（仅 EP01 强制）
    opening_payoff_sec = None
    if is_first_ep:
        cum = 0
        for seg in segs:
            # 引爆时刻 = 该引爆段的**开始**时刻（观众被击中的时刻），非结束时刻——
            # 段长不应把"55s 开始引爆"误判为"67s 才引爆"（段长 12s 的累计结束时刻）
            if seg_has_kw(seg, PAYOFF_KW) or (seg_sat(seg) in ("SAT-SLAP", "SAT-REV", "SAT-BURN")):
                opening_payoff_sec = cum
                break
            cum += seg["duration"]
        if opening_payoff_sec is None:
            errors.append(
                f"S2 开场引爆缺失：EP01 全集未检出强情绪引爆事件"
                f"（虐杀/背叛/重生/当场打脸/真相），开场钩子不足")
        elif opening_payoff_sec > tier["opening_payoff_max_sec"]:
            errors.append(
                f"S2 开场引爆过晚：首次引爆在 {opening_payoff_sec}s，"
                f"超过 {tier['opening_payoff_max_sec']}s——爽剧 EP01 须在前 "
                f"{tier['opening_payoff_max_sec']}s 内完成一次情绪引爆")

    # S3 冲突当场回应：每个羞辱/欺压段后相邻 2 SEG 内须有反击/打脸
    # （校验所有冲突段，非仅首个——每个欺压都该有当场出气口，漏检会让后续冲突纯忍耐）
    for i, seg in enumerate(segs):
        if seg_has_kw(seg, CONFLICT_KW):
            # 找后续 2 个 SEG 是否有爽点回应
            window = segs[i:i + 3]  # 含本段 + 后 2 段
            responded = any(
                seg_has_kw(s, SATISFY_KW) or seg_sat(s) in ("SAT-SLAP", "SAT-COME", "SAT-REV")
                for s in window[1:]  # 不含本段（本段是施压）
            )
            # 本段若同时含冲突+回应（如当场回怼），视为已回应
            if seg_has_kw(seg, SATISFY_KW) or seg_sat(seg) in ("SAT-SLAP", "SAT-COME", "SAT-REV"):
                responded = True
            if not responded:
                errors.append(
                    f"S3 冲突未当场回应：{seg['seg_id']}（{seg['title'][:20]}）含羞辱/欺压，"
                    f"但相邻 2 SEG 内无反击/打脸——纯忍耐后置，观众被压无出气口")

    # S4 打脸占比（仅当题材要求 slap_min_pct > 0 且非空集）
    slap_pct = (slap_count / n_sat * 100) if n_sat else 0
    if tier["slap_min_pct"] > 0 and n_sat > 0 and slap_pct < tier["slap_min_pct"]:
        warns.append(
            f"S4 打脸(SAT-SLAP)占比 {slap_pct:.0f}% 低于题材配比 {tier['slap_min_pct']}%"
            f"（{slap_count}/{n_sat}）——复仇/逆袭题材打脸应为主打爽点")

    # S5 冲突强度（WARN）：羞辱/欺压段是否具体到利益/关系
    for seg in segs:
        if seg_has_kw(seg, CONFLICT_KW):
            # 具体化信号：金额/账目/利益/关系称谓/具体物件
            concrete = re.search(r"\d+\s*(两|两银|块|万|元|两银子|套|间|亩|股份|铺|店|地)",
                                 seg["body"]) or any(
                k in seg["body"] for k in ["嫁妆", "药钱", "租金", "房", "地契", "股份", "遗产", "欠"])
            if not concrete:
                warns.append(
                    f"S5 冲突强度偏空泛：{seg['seg_id']}（{seg['title'][:20]}）的欺压/羞辱"
                    f"未落到具体利益/关系账目（Rule 43a），易成'嘴炮式阴阳'——"
                    f"建议升级为具体利益侵害或当场打脸")
            break

    metrics = {
        "seg_count": len(segs),
        "satisfaction_count": n_sat,
        "satisfaction_moments": [s for s, _ in sat_moments],
        "slap_count": slap_count,
        "slap_pct": round(slap_pct, 1),
        "opening_payoff_sec": opening_payoff_sec,
        "sat_annotation_present": any_sat_annotation,
    }
    return errors, warns, metrics


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description="爽点密度校验（爽感密度写时自检）")
    p.add_argument("--ep", help="集号，如 EP01（配 --project-root）")
    p.add_argument("--project-root", help="项目根目录（读题材/阈值 + 定位剧本）")
    p.add_argument("--file", help="直接指定剧本 .md 路径")
    p.add_argument("--genre", help="显式指定题材（覆盖自动判定）")
    p.add_argument("--json", action="store_true", help="机读 JSON 输出")
    a = p.parse_args()

    def _fail_json(msg: str, code: int) -> int:
        """--json 模式下错误也输出 JSON 结构（下游机读可区分文件缺失 vs 校验失败）。"""
        if a.json:
            print(json.dumps({"file": a.file or a.ep or "", "error": msg,
                              "errors": [msg], "warns": [], "metrics": {},
                              "pass": False}, ensure_ascii=False))
        else:
            print(msg, file=sys.stderr)
        return code

    if a.file:
        fpath = a.file
    elif a.ep and a.project_root:
        fpath = locate_script(a.project_root, a.ep)
        if not fpath:
            return _fail_json(f"找不到剧本: {a.project_root}/剧本/{a.ep}/{a.ep}_*.md", 1)
    else:
        return _fail_json("需 --file 或 --ep + --project-root", 2)

    if not os.path.isfile(fpath):
        return _fail_json(f"文件不存在: {fpath}", 1)

    content = load_text(fpath)
    fm_dur = 0
    m = re.search(r"duration_sec:\s*(\d+)", content)
    if m:
        fm_dur = int(m.group(1))
    is_first_ep = bool(re.search(r"episode_id:\s*EP0?1\b", content)) or \
                  (a.ep and a.ep.upper() in ("EP01", "EP1"))

    genre = a.genre or detect_genre(a.project_root, content)
    profile = load_episode_profile(a.project_root)
    tier = resolve_tier(genre, profile)
    segs = parse_segs(content)
    errors, warns, metrics = check_satisfaction(segs, tier, is_first_ep, fm_dur)

    if a.json:
        print(json.dumps({
            "file": fpath, "genre": genre, "tier": tier,
            "is_first_ep": is_first_ep, "metrics": metrics,
            "errors": errors, "warns": warns, "pass": not errors,
        }, ensure_ascii=False, indent=2))
    else:
        label = a.ep or os.path.basename(fpath)
        print(f"🎯 爽点密度校验 — {label}（题材档：{genre or '默认'}）")
        print(f"   SEG {metrics.get('seg_count', 0)} ｜ "
              f"爽点 {metrics.get('satisfaction_count', 0)} ｜ "
              f"打脸占比 {metrics.get('slap_pct', 0)}% ｜ "
              f"开场引爆 {metrics.get('opening_payoff_sec') or '—'}s")
        for e in errors:
            print(f"   ❌ {e}")
        for w in warns:
            print(f"   ⚠️ {w}")
        print(f"\n{'✅ 爽点合规' if not errors else f'❌ {len(errors)} 个爽点问题'}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
