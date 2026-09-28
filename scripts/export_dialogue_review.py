#!/usr/bin/env python3
"""导出对白审查稿：从 EP##_剧本.md 提取全部台词，生成人类易读的纯对白文件。

用途：台词质量人工审查（口语化/电报体/逻辑支撑逐句过），比裸行 lines.txt 多
说话人、情绪标注、SEG/镜号结构；与 srt/lines.txt（TTS/字幕用途）互不替代。

用法：
  python3 scripts/export_dialogue_review.py --ep EP01 --project-root dramas/<剧名>
  python3 scripts/export_dialogue_review.py --file dramas/<剧名>/剧本/EP01/EP01_剧本.md

输出：剧本同目录 EP##_对白_审查.txt（--output 可改）。
本文件为派生产物：剧本改动后必须重新生成，不得手改。
"""

import argparse
import datetime
import re
import sys
from collections import Counter
from pathlib import Path

# **CHAR-001**[点头·极静]：「好。……」 / [待补：年轻守卫][呵斥]：「…」 / **旁白**：「……」（待补 speaker 无粗体，与 dialogue_lint.py/spec 一致）
# （兼容全角括号［］；[待补：…] 为未分配 ID 的群演占位，同样计入审查，见 dialogue_lint.py）
RE_LINE = re.compile(
    r"(?:\*\*(CHAR-[A-Z0-9-]+|旁白)\*\*|\[待补：([^\]]+)\])"
    r"(?:[\[［]([^\]］]*)[\]］])?：「([^」]*)」"
)
RE_SEG = re.compile(r"^##\s+(SEG\d+\s*[—-].*?)\s*$")
RE_SHOT = re.compile(r"`(EP\d+-S\d+)`")
RE_SCENE = re.compile(r"^\*\*【(SCENE-[\w-]+)】([^*]*)\*\*")
RE_CARD_NAME = re.compile(r"^##\s+(CHAR-[A-Z0-9-]+)\s*·\s*(\S+)")
RE_VOICE_NAME = re.compile(r"^\|\s*`(CHAR-[A-Z0-9-]+)`\s*\|\s*([^|\s]+)\s*\|")
RE_EP_TITLE = re.compile(r"^episode_title:\s*(.+?)\s*$", re.M)


def load_name_map(project_root: Path) -> dict:
    mapping = {}
    # 声音卡片先读（含群演），角色卡片后读覆盖（主角名以角色卡为准）
    voice = project_root / "资产" / "声音卡片.md"
    if voice.exists():
        for line in voice.read_text(encoding="utf-8").splitlines():
            m = RE_VOICE_NAME.match(line)
            if m:
                mapping[m.group(1)] = m.group(2)
    card = project_root / "资产" / "角色卡片.md"
    if card.exists():
        for line in card.read_text(encoding="utf-8").splitlines():
            m = RE_CARD_NAME.match(line)
            if m:
                mapping[m.group(1)] = m.group(2)
    return mapping


def export(script_path: Path, name_map: dict, out_path: Path) -> int:
    text = script_path.read_text(encoding="utf-8")
    ep = script_path.stem.split("_")[0]
    m = RE_EP_TITLE.search(text)
    title = m.group(1) if m else ""

    out, count, speakers = [], 0, Counter()
    out.append(f"# {ep} 对白审查稿{'：' + title if title else ''}")
    out.append(
        f"> 生成自 {script_path.name} · {datetime.date.today()} · "
        "派生产物（剧本改后重跑本脚本），仅供人工审查"
    )
    cur_shot = ""
    for raw in text.splitlines():
        if "<!-- VALIDATION" in raw:
            break
        seg = RE_SEG.match(raw)
        if seg:
            out.append("")
            out.append(f"## {seg.group(1)}")
            continue
        sc = RE_SCENE.match(raw)
        if sc:
            out.append(f"  （{sc.group(1)} {sc.group(2).strip()}）")
            continue
        shot = RE_SHOT.search(raw)
        if shot:
            cur_shot = shot.group(1).split("-")[-1]
        for m in RE_LINE.finditer(raw):
            who = m.group(1) or "待补：" + m.group(2)
            mood = m.group(3) or ""
            line = m.group(4)
            name = name_map.get(who, who) if who != "旁白" else "旁白"
            mood_s = f"[{mood}]" if mood else ""
            out.append(f"{cur_shot:>4} {name}{mood_s}：{line}")
            count += 1
            speakers[name] += 1

    out.append("")
    out.append(f"—— 共 {count} 行 · 说话角色 {len(speakers)} 人：")
    for name, n in speakers.most_common():
        out.append(f"    {name}: {n} 行")
    out_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"✅ {out_path}（{count} 行台词）")
    return count


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ep", help="集号，如 EP01")
    ap.add_argument("--project-root", help="项目根，如 dramas/<剧名>")
    ap.add_argument("--file", help="直接指定 EP##_剧本.md 路径")
    ap.add_argument("--output", help="输出路径（默认剧本同目录 EP##_对白_审查.txt）")
    args = ap.parse_args()

    if args.file:
        script_path = Path(args.file)
        project_root = script_path.parent.parent.parent
    elif args.ep and args.project_root:
        project_root = Path(args.project_root)
        script_path = project_root / "剧本" / args.ep / f"{args.ep}_剧本.md"
    else:
        ap.error("需要 --file，或 --ep + --project-root")
        return

    if not script_path.exists():
        sys.exit(f"❌ 剧本不存在：{script_path}")

    name_map = load_name_map(project_root)
    if not name_map:
        print(f"⚠️ 未找到 {project_root}/资产/角色卡片.md，说话人将显示 CHAR-ID")

    ep = script_path.stem.split("_")[0]
    out_path = Path(args.output) if args.output else script_path.parent / f"{ep}_对白_审查.txt"
    n = export(script_path, name_map, out_path)
    if n == 0:
        sys.exit("❌ 未解析到任何台词行，检查剧本格式（**CHAR-###**[标注]：「…」 / **[待补：…]**[标注]：「…」）")


if __name__ == "__main__":
    main()
