#!/usr/bin/env python3
"""格式门控 — 检查分集剧本的格式一致性。drama-director G4 首项检查。"""
import argparse, os, re, sys, yaml

REQUIRED_SECTIONS = [
    "元信息摘要", "时长预算表", "本集观众必须听懂",
    "本集制作备注", "本集资产", "结尾钩子",
]

def check_frontmatter(fm: dict) -> list:
    errors = []
    for f in ["episode_id", "episode_title", "season",
              "scene_ids", "character_ids", "look_ids", "prop_ids"]:
        if f not in fm:
            errors.append(f"缺顶层字段: {f}")
    # 时长字段：新契约用 duration_sec（秒，整数，与制作层 episode_profile 口径一致）；
    # 历史剧本用 duration_min（分钟），兼容两者至少其一（历史文件不迁移）。
    if "duration_sec" not in fm and "duration_min" not in fm:
        errors.append("缺时长字段: duration_sec（或历史格式 duration_min）")
    # 制作参数（model/ratio/resolution/...）不属于剧本层，由 yaml_check 在制作层把关，
    # 分集剧本 frontmatter 不再校验 seedance_defaults。
    return errors


def check_table(content: str) -> list:
    errors = []
    h = re.search(r'^\| 镜号 \| shot_id', content, re.MULTILINE)
    if not h:
        h2 = re.search(r'^\|.*镜.*\|', content, re.MULTILINE)
        if h2:
            cols = h2.group().count('|') - 1
            errors.append(f"镜头表 {cols} 列，应为 11 列")
        else:
            errors.append("未找到镜头表")

    # Continuation rows: line-by-line, only flag when previous line is a
    # table row with a non-empty first cell (prevents false positives).
    lines = content.split('\n')
    prev_is_table_with_content = False
    cr_count = 0
    for line in lines:
        line = line.strip()
        is_table = line.startswith('|') and line.endswith('|')
        if not is_table:
            prev_is_table_with_content = False
            continue
        first_cell = line.split('|')[1].strip()
        has_content = bool(first_cell)
        if not has_content and prev_is_table_with_content:
            cr_count += 1
        prev_is_table_with_content = has_content
    if cr_count > 0:
        errors.append(f"{cr_count} 行空管子续行，多句对白应写在同一格")

    return errors


def check_sections(content: str) -> list:
    return [f"缺段落: {s}" for s in REQUIRED_SECTIONS if s not in content]


def check_transitions(content: str) -> list:
    errors = []
    segs = re.findall(r'^## SEG\d+', content, re.MULTILINE)
    trans = content.count("转场")
    if len(segs) > 1 and trans == 0:
        errors.append(f"{len(segs)} 个 SEG 无转场标记")
    return errors


def check_validation(content: str) -> list:
    return ["缺 VALIDATION 块"] if "VALIDATION" not in content else []


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ep", required=True)
    p.add_argument("--project-root", required=True)
    a = p.parse_args()

    fpath = os.path.join(a.project_root, "剧本", a.ep, f"{a.ep}_剧本.md")
    if not os.path.exists(fpath):
        print(f"文件不存在: {fpath}"); sys.exit(1)

    with open(fpath) as f:
        c = f.read()

    fm = {}
    m = re.match(r'^---\s*\n(.*?)\n---', c, re.DOTALL)
    if m:
        try: fm = yaml.safe_load(m.group(1)) or {}
        except: pass

    print(f"📋 格式门控 — {a.ep}")
    all_errors = []
    for label, fn in [
        ("Frontmatter", lambda: check_frontmatter(fm)),
        ("表格/续行", lambda: check_table(c)),
        ("段落完整", lambda: check_sections(c)),
        ("转场标记", lambda: check_transitions(c)),
        ("VALIDATION", lambda: check_validation(c)),
    ]:
        errs = fn()
        print(f"{'✅' if not errs else '❌'} {label}")
        for e in errs: print(f"   {e}")
        all_errors.extend(errs)

    if all_errors:
        print(f"\n❌ {len(all_errors)} 个问题"); sys.exit(1)
    print("\n✅ 全部通过"); sys.exit(0)


if __name__ == "__main__":
    main()
