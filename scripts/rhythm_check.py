#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""镜头节奏校验（rhythm check）— 把 scene-writer Rule 45 等软规则机器化。

背景：爆款爽剧 ASL 2.5-3s、快慢交替、特写为王、运镜多样；但 AI 写作易退化为
"匀速 4s + 全固定镜头 + 中景"（机甲 EP02 实测 ASL 4.5s、19/20 固定镜头）。
本脚本对单集剧本镜头表做节奏量化校验，退出码非 0 即不达标，供：
- scene-writer 自检 8（输出前强制运行）
- segment-builder Gate 复核（复核 VALIDATION 自报行）

阈值来源：`制片规范.md` → episode_profile（```yaml 代码块内），禁止硬编码；
缺失时回退爽剧快切默认档（DEFAULTS）。

用法：
  python3 scripts/rhythm_check.py --ep EP02 --project-root dramas/<剧名>
  python3 scripts/rhythm_check.py --file <剧本.md> [--project-root <项目根>]
  python3 scripts/rhythm_check.py --ep EP02 --project-root dramas/<剧名> --json
"""
from __future__ import annotations

import argparse, glob, json, os, re, statistics, sys

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
# 默认阈值（爽剧快切档；制片规范 episode_profile 可覆盖）
# ---------------------------------------------------------------------------

DEFAULTS = {
    "asl_max_sec": 3.5,            # C1 平均镜长上限（理想 2.5-3s）
    "monotone_run_max": 4,         # C2 禁止连续 ≥N 镜同时长
    "fixed_camera_max_pct": 60,    # C3 固定镜头占比上限（%）
    "min_nonfixed_types": 2,       # C3 每集至少 N 种非固定运镜
    "closeup_min_pct": 50,         # C4 特写+近景占比下限（%）
    "atmosphere_min_pct": 30,      # C5 氛围/前景镜头占比下限（%，首轮 WARN）
}

# 景别归类
CLOSEUP_SIZES = {"特写", "近景", "大特写", "中特写"}  # CU/MCU/ECU
# 运镜：固定镜头 vs 非固定
FIXED_CAMERA = "固定镜头"
# C5 氛围粒子 / 前景遮挡关键词
ATMOSPHERE_KW = [
    "飘雪", "落雪", "飞雪", "雪", "雨", "雨夜", "雨丝", "烬", "飘烬", "火星",
    "尘", "尘埃", "雾", "薄雾", "光斑", "光晕", "烟", "蒸汽", "花瓣", "落叶",
]
FOREGROUND_KW = [
    "纱帘", "栏杆", "树枝", "门框", "窗框", "前景", "透过", "遮挡", "帘",
    "格栅", "珠帘", "屏风",
]


# ---------------------------------------------------------------------------
# 解析
# ---------------------------------------------------------------------------

# episode_profile 块的标志性字段（用于从多个 yaml 块中识别真正的 episode_profile）
_PROFILE_MARKERS = {"shots_per_episode", "segments_per_episode", "segment_duration_sec"}


def _as_profile(data: dict) -> dict:
    """从一个解析后的 yaml dict 提取 episode_profile 字段。

    兼容两种结构：
    - 嵌套：standard-86: {episode_count: ..., shots_per_episode: ...}（取含标志字段的嵌套 dict）
    - 平铺：episode_profile: standard-86 + episode_count: ... 直接在顶层（取顶层本身）
    非 episode_profile 块（如分集文件头示例 episode_id: EP01）返回 {}。
    """
    if not isinstance(data, dict):
        return {}
    # 平铺：顶层直接含标志字段
    if _PROFILE_MARKERS & set(data.keys()):
        return data
    # 嵌套：某个顶层值是含标志字段的 dict
    for v in data.values():
        if isinstance(v, dict) and (_PROFILE_MARKERS & set(v.keys())):
            return v
    return {}


def load_episode_profile(project_root: str | None) -> dict:
    """从制片规范.md 的 ```yaml 代码块读取 episode_profile。

    遍历所有 yaml 块，返回第一个含 episode_profile 标志字段的块（兼容嵌套/平铺，
    跳过分集文件头示例等非 profile 块）。多 yaml 块项目（机甲/双姝医馆）安全。
    """
    if not project_root:
        return {}
    spec = os.path.join(project_root, "制片规范.md")
    if not os.path.isfile(spec):
        return {}
    try:
        text = open(spec, encoding="utf-8").read()
    except OSError:
        return {}
    for m in re.finditer(r"```yaml\s*\n(.*?)```", text, re.DOTALL):
        try:
            data = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue
        prof = _as_profile(data)
        if prof:
            return prof
    return {}


def resolve_thresholds(profile: dict) -> dict:
    """episode_profile 覆盖默认档；缺失字段回退 DEFAULTS。"""
    th = dict(DEFAULTS)
    for k in th:
        if k in profile and isinstance(profile[k], (int, float)):
            th[k] = profile[k]
    return th


def parse_shots(content: str) -> list[dict]:
    """解析镜头表 11 列：镜号/shot_id/场景/角色/形象/景别/时长/模式/运镜/画面/对白。

    返回 [{shot_no, size, duration, camera, visual, dialogue}, ...]。
    仅取镜号列为纯数字的行（跳过表头/分隔行/续行）。"""
    shots = []
    for line in content.split("\n"):
        line = line.strip()
        # 行首 | 必须有；行尾 | 可选（markdown 表格行尾 | 可省，多句对白续行常致
        # 最后一行无尾 | ——剑宗小祖宗 EP01 实测 22 镜中 17 镜行尾无 |，强制尾 | 会漏解析）
        if not line.startswith("|"):
            continue
        parts = line.split("|")
        # 去掉行首空串（| 前部分）；行尾有 | 时末尾是空串需去掉，无 | 时保留末格
        cells = [c.strip() for c in parts[1:]]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        if len(cells) < 11:
            continue
        if not re.fullmatch(r"\d+", cells[0]):
            continue  # 表头/分隔/续行
        dur_raw = cells[6]
        m = re.search(r"\d+", dur_raw)
        duration = int(m.group()) if m else 0
        shots.append({
            "shot_no": int(cells[0]),
            "size": cells[5],
            "duration": duration,
            "camera": cells[8],
            "visual": cells[9],
            "dialogue": cells[10],
        })
    return shots


# ---------------------------------------------------------------------------
# 校验
# ---------------------------------------------------------------------------

def check_rhythm(shots: list[dict], th: dict) -> tuple[list[str], list[str], dict]:
    """返回 (errors, warns, metrics)。"""
    errors: list[str] = []
    warns: list[str] = []
    n = len(shots)
    if n == 0:
        return ["未解析到任何镜头行（镜头表为空或格式不符）"], [], {}

    durs = [s["duration"] for s in shots]
    sizes = [s["size"] for s in shots]
    cameras = [s["camera"] for s in shots]
    visuals = [s["visual"] for s in shots]

    # 少镜集豁免：standard-86 每集 16-30 镜，<8 镜的集（唯一静音视觉锤段等）
    # 样本太小，均值/比例类指标（C1/C2/C3/C4）统计无意义且易误报，整体豁免。
    SMALL_N = 8
    small_sample = n < SMALL_N

    # C1 平均镜长 ASL
    asl = statistics.mean(durs)
    if not small_sample and asl > th["asl_max_sec"]:
        errors.append(
            f"C1 平均镜长 ASL {asl:.1f}s 超过上限 {th['asl_max_sec']}s——"
            f"节奏偏慢（爽剧快切 2.5-3s），需缩短单镜/增加切镜")

    # C2 镜长单调性：连续 ≥N 镜同时长 + 标准差
    max_run = run = 1
    for i in range(1, n):
        if durs[i] == durs[i - 1]:
            run += 1
            max_run = max(max_run, run)
        else:
            run = 1
    std = statistics.pstdev(durs) if n > 1 else 0.0
    if not small_sample:
        if max_run >= th["monotone_run_max"]:
            errors.append(
                f"C2 镜长单调：连续 {max_run} 镜同时长（≥{th['monotone_run_max']}）——"
                f"匀速无呼吸感，需快慢交替（冲突镜 2-4s / 情绪镜 5-7s）")
        elif std == 0:
            errors.append("C2 镜长标准差为 0（全镜同时长）——匀速无呼吸感")

    # C3 运镜多样性
    fixed = sum(1 for c in cameras if c == FIXED_CAMERA)
    fixed_pct = fixed / n * 100
    nonfixed_types = {c for c in cameras if c and c != FIXED_CAMERA}
    if not small_sample:
        if fixed_pct > th["fixed_camera_max_pct"]:
            errors.append(
                f"C3 固定镜头占比 {fixed_pct:.0f}% 超过上限 {th['fixed_camera_max_pct']}%"
                f"（{fixed}/{n}）——静态 PPT 感，需配置缓推/跟随/俯拍/主观/快切")
        if len(nonfixed_types) < th["min_nonfixed_types"]:
            errors.append(
                f"C3 非固定运镜仅 {len(nonfixed_types)} 种（{sorted(nonfixed_types) or '无'}），"
                f"少于 {th['min_nonfixed_types']} 种——运镜单一")

    # C4 特写占比
    closeup = sum(1 for s in sizes if s in CLOSEUP_SIZES)
    closeup_pct = closeup / n * 100
    if not small_sample and closeup_pct < th["closeup_min_pct"]:
        errors.append(
            f"C4 特写+近景占比 {closeup_pct:.0f}% 低于下限 {th['closeup_min_pct']}%"
            f"（{closeup}/{n}）——竖屏特写为王，中景过多稀释情绪")

    # C5 氛围/前景（首轮 WARN）
    atmo = sum(1 for v in visuals
               if any(k in v for k in ATMOSPHERE_KW) or any(k in v for k in FOREGROUND_KW))
    atmo_pct = atmo / n * 100
    if atmo_pct < th["atmosphere_min_pct"]:
        warns.append(
            f"C5 氛围/前景镜头占比 {atmo_pct:.0f}% 低于参考 {th['atmosphere_min_pct']}%"
            f"（{atmo}/{n}）——画面偏平，建议加氛围粒子（飘雪/雨/烬）或前景遮挡（纱帘/栏杆）")

    metrics = {
        "shot_count": n,
        "asl_sec": round(asl, 2),
        "shot_duration_std": round(std, 2),
        "max_monotone_run": max_run,
        "fixed_camera_pct": round(fixed_pct, 1),
        "nonfixed_camera_types": sorted(nonfixed_types),
        "closeup_pct": round(closeup_pct, 1),
        "atmosphere_pct": round(atmo_pct, 1),
    }
    return errors, warns, metrics


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description="镜头节奏校验（Rule 45 机器化）")
    p.add_argument("--ep", help="集号，如 EP02（配 --project-root）")
    p.add_argument("--project-root", help="项目根目录（读制片规范阈值 + 定位剧本）")
    p.add_argument("--file", help="直接指定剧本 .md 路径（跳过 --ep 定位）")
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

    content = open(fpath, encoding="utf-8").read()
    profile = load_episode_profile(a.project_root)
    th = resolve_thresholds(profile)
    shots = parse_shots(content)
    errors, warns, metrics = check_rhythm(shots, th)

    if a.json:
        print(json.dumps({
            "file": fpath, "thresholds": th, "metrics": metrics,
            "errors": errors, "warns": warns,
            "pass": not errors,
        }, ensure_ascii=False, indent=2))
    else:
        label = a.ep or os.path.basename(fpath)
        print(f"🎬 镜头节奏校验 — {label}")
        print(f"   镜头数 {metrics.get('shot_count', 0)} ｜ "
              f"ASL {metrics.get('asl_sec', 0)}s ｜ "
              f"固定镜头 {metrics.get('fixed_camera_pct', 0)}% ｜ "
              f"特写 {metrics.get('closeup_pct', 0)}% ｜ "
              f"氛围 {metrics.get('atmosphere_pct', 0)}%")
        for e in errors:
            print(f"   ❌ {e}")
        for w in warns:
            print(f"   ⚠️ {w}")
        print(f"\n{'✅ 节奏合规' if not errors else f'❌ {len(errors)} 个节奏问题'}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
