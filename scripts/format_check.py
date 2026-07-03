#!/usr/bin/env python3
"""
格式门控脚本 — 检查分集剧本的格式一致性。
在 scene-writer 输出剧本前、以及 drama-director G4 门控中执行。

用法：
    python3 scripts/format_check.py --ep EP01 --project-root dramas/<剧名>
    python3 scripts/format_check.py --ep EP01 --project-root dramas/<剧名> --verbose

返回码：
    0 = 全部通过
    1 = 有格式问题
"""
import argparse, os, re, sys, yaml

FIELDS_TOP = ["episode_id", "episode_title", "duration_min", "season",
              "scene_ids", "character_ids", "look_ids", "prop_ids"]
FIELDS_NESTED = ["model", "ratio", "resolution", "duration_sec",
                 "generate_audio", "prompt_suffix", "negative_prompt"]
REQUIRED_SECTIONS = [
    "元信息摘要", "时长预算表", "本集观众必须听懂",
    "本集制作备注", "本集资产", "结尾钩子",
]
TABLE_COL_COUNT = 11  # 11列镜头表
CHAR_REF_PATTERN = re.compile(r'\*\*CHAR-\d+[A-Z-]*\d*\*\*')  # **CHAR-001**
ID_REF_PATTERN = re.compile(r'`CHAR-\d+[A-Z-]*\d*`')  # `CHAR-001-L01`
SHOT_REF_PATTERN = re.compile(r'`EP\d{2}-S\d{2}`')  # `EP01-S01`

BARE_CHAR = re.compile(r'(?<!\*)(?<!`)CHAR-\d+[A-Z-]*\d*(?!\*)(?!`)')
# Only flag bare CHAR in dialogue/table context (not in metadata/yaml)
# We'll check differently


def check_frontmatter(fm: dict, verbose: bool) -> list:
    """Check frontmatter field completeness."""
    errors = []
    for field in FIELDS_TOP:
        if field not in fm:
            errors.append(f"  [FRONTMATTER] 缺顶层字段: {field}")
    sd = fm.get("seedance_defaults", {})
    if not isinstance(sd, dict):
        errors.append("  [FRONTMATTER] 缺 seedance_defaults 块")
        sd = {}
    for field in FIELDS_NESTED:
        if field not in sd:
            errors.append(f"  [FRONTMATTER] seedance_defaults 缺字段: {field}")
    if verbose and not errors:
        print("  [FRONTMATTER] 全部字段完整 ✅")
    return errors


def check_table_columns(content: str, verbose: bool) -> list:
    """Check that the shot table has 11 columns."""
    errors = []
    # Find the 11-column table header
    header = re.search(r'^\| 镜号 \| shot_id \| 场景 \| 角色 \| 形象 \| 景别 \| 时长 \| 模式 \| 运镜 \| 画面 \| 对白', content, re.MULTILINE)
    if not header:
        # Try alternate formats
        header2 = re.search(r'^\|.*镜.*\|', content, re.MULTILINE)
        if header2:
            cols = header2.group().count('|') - 1
            if cols == 11:
                # Found 11-col table but different header text
                pass
            elif cols > 0:
                errors.append(f"  [TABLE] 镜头表列数={cols}，应为 11 列（镜号/shot_id/场景/角色/形象/景别/时长/模式/运镜/画面/对白）")
            else:
                errors.append("  [TABLE] 未识别到镜头表")
        else:
            errors.append("  [TABLE] 未找到镜头表")
    if verbose and not errors:
        print("  [TABLE] 11列表格 ✅")
    return errors


def check_continuation_rows(content: str, verbose: bool) -> list:
    """Check for empty pipe continuation rows."""
    errors = []
    cr = re.findall(r'^\|(\s*\|){4,}\s*$', content, re.MULTILINE)
    if cr:
        errors.append(f"  [TABLE] 发现 {len(cr)} 行空管子续行（| | | | ...）。多句对白应写在同一格内换行，不得续行。")
    if verbose and not errors:
        print("  [TABLE] 无空管子续行 ✅")
    return errors


def check_role_format(content: str, verbose: bool) -> list:
    """Check character reference format consistency in dialogue."""
    errors = []
    # In dialogue lines (spoken lines), speakers should be **CHAR-###**
    # Find lines that contain "：「" (dialogue marker)
    dialogue_lines = re.findall(r'[^|]*\u300c[^\u300d]*\u300d', content)
    bare_in_dialogue = []
    for line in dialogue_lines:
        bare = BARE_CHAR.findall(line)
        for b in bare:
            # Check if it's inside a **...** block (already bold-formatted)
            context_before = content[content.find(line)-30:content.find(line)]
            if f'**{b}**' not in line and f'**{b}' not in line:
                bare_in_dialogue.append(b)
    
    if bare_in_dialogue:
        unique = list(set(bare_in_dialogue))
        errors.append(f"  [FORMAT] 对白中发现裸角色引用（应用 **CHAR-###** 粗体）: {', '.join(unique[:5])}")
    
    # Check for backtick in table cells (角色/形象 columns)
    # This is hard to validate precisely, skip for now
    
    if verbose and not errors:
        print("  [FORMAT] 角色引用格式 ✅")
    return errors


def check_sections(content: str, verbose: bool) -> list:
    """Check required sections exist."""
    errors = []
    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"  [SECTION] 缺段落: {section}")
    if verbose and not errors:
        print(f"  [SECTION] 全部 {len(REQUIRED_SECTIONS)} 个段落完整 ✅")
    return errors


def check_transitions(content: str, verbose: bool) -> list:
    """Check for transition markers between segments."""
    errors = []
    # Look for SEG ## markers
    segs = re.findall(r'^### SEG\d+', content, re.MULTILINE)
    trans = re.findall(r'转场', content)
    if len(segs) > 1 and len(trans) == 0:
        errors.append(f"  [TRANSITION] 有 {len(segs)} 个 SEG 但无转场标记（应在段间的 --- 下方加 > 🔀 转场：hard_cut）")
    elif len(segs) > 0 and len(trans) < len(segs) - 1:
        errors.append(f"  [TRANSITION] 有 {len(segs)} 个 SEG 但仅 {len(trans)} 个转场标记（应有 ≥ {len(segs)-1} 个）")
    if verbose and not errors:
        print("  [TRANSITION] 转场标记 ✅")
    return errors


def check_validation(content: str, verbose: bool) -> list:
    """Check for VALIDATION block."""
    errors = []
    if "VALIDATION" not in content:
        errors.append("  [VALIDATION] 缺 VALIDATION 块")
    if verbose and not errors:
        print("  [VALIDATION] ✅")
    return errors


def main():
    parser = argparse.ArgumentParser(description="剧本格式门控检查")
    parser.add_argument("--ep", required=True, help="集号，如 EP01")
    parser.add_argument("--project-root", required=True, help="项目根目录路径")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    args = parser.parse_args()

    fpath = os.path.join(args.project_root, "剧本", args.ep, f"{args.ep}_剧本.md")
    if not os.path.exists(fpath):
        print(f"❌ 文件不存在: {fpath}")
        sys.exit(1)

    with open(fpath) as f:
        content = f.read()

    # Parse frontmatter
    fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    fm = {}
    if fm_match:
        try:
            fm = yaml.safe_load(fm_match.group(1)) or {}
        except:
            pass

    print(f"\n📋 格式门控 — {args.ep}")
    print("=" * 40)

    all_errors = []
    checks = [
        ("Frontmatter字段", lambda: check_frontmatter(fm, args.verbose)),
        ("表格列数", lambda: check_table_columns(content, args.verbose)),
        ("空管子续行", lambda: check_continuation_rows(content, args.verbose)),
        ("角色引用格式", lambda: check_role_format(content, args.verbose)),
        ("段落完整性", lambda: check_sections(content, args.verbose)),
        ("转场标记", lambda: check_transitions(content, args.verbose)),
        ("VALIDATION", lambda: check_validation(content, args.verbose)),
    ]

    for name, check_fn in checks:
        errors = check_fn()
        if errors:
            print(f"❌ {name}")
            for e in errors:
                print(e)
            all_errors.extend(errors)
        else:
            if not args.verbose:
                print(f"✅ {name}")

    print("=" * 40)
    if all_errors:
        print(f"❌ 失败：共 {len(all_errors)} 个格式问题\n")
        sys.exit(1)
    else:
        print("✅ 全部通过！格式一致。\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
