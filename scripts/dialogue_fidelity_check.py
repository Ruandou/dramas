#!/usr/bin/env python3
"""台词逐字保真校验（防 LLM 重打劣化生僻字）。

背景：结构性重构（拆镜/合段/表格改造）中台词被模型重新输出时，低频字会被
形近/音近字替换（实例：边荒盐妇 EP01 vB 重构中 讫/噎/捏/攥 四处劣化，
靠人工逐字对比抓回——本脚本将该校验固化）。

用法（仓库根执行）：
  # 与 git 基线比（最常用：重构后、提交前）
  python3 scripts/dialogue_fidelity_check.py --file "dramas/<剧>/剧本/EP01/EP01_剧本.md" --baseline git:HEAD
  # 与任意文件比（如 vA 快照 / segments.yaml 对剧本）
  python3 scripts/dialogue_fidelity_check.py --file <新文件> --baseline <旧文件路径>

规则：提取两版全部「」内的台词序列，要求**顺序与内容逐字一致**。
退出码：0=一致；1=有差异（打印逐处 diff）；2=参数/读取错误。
"""
from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

QUOTE_RE = re.compile(r"「([^」]*)」")


def extract_lines(text: str) -> list[str]:
    return QUOTE_RE.findall(text)


def read_baseline(spec: str, file_path: str) -> str:
    if spec.startswith("git:"):
        rev = spec[4:] or "HEAD"
        out = subprocess.run(
            ["git", "show", f"{rev}:{file_path}"],
            capture_output=True, text=True,
        )
        if out.returncode != 0:
            print(f"ERROR: git show {rev}:{file_path} 失败：{out.stderr.strip()}", file=sys.stderr)
            sys.exit(2)
        return out.stdout
    p = Path(spec)
    if not p.is_file():
        print(f"ERROR: 基线文件不存在：{spec}", file=sys.stderr)
        sys.exit(2)
    return p.read_text(encoding="utf-8")


def punct_scan(file_path: str) -> int:
    """标点 AI 腔密度扫描（基准 §二口径：省略号按 U+2026 逐字计，一个「……」=2）。

    阈值：省略号 ≤20/千字、破折号 ≤2/千字。防 scene-writer 把「……」当 1 个数导致的漏判。
    退出码：0=入 band；1=超标（逐条列超标项）。
    """
    p = Path(file_path)
    if not p.is_file():
        print(f"ERROR: 文件不存在：{file_path}", file=sys.stderr)
        return 2
    lines = extract_lines(p.read_text(encoding="utf-8"))
    n = sum(len(x) for x in lines)
    if n == 0:
        print("ERROR: 未提取到「」台词", file=sys.stderr)
        return 2
    ell = sum(x.count("\u2026") for x in lines)          # U+2026 逐字（与语料基线同口径）
    dash = sum(x.count("\u2014") for x in lines)         # U+2014 逐字
    ell_k, dash_k = ell / n * 1000, dash / n * 1000
    bad = 0
    ell_ok = ell_k <= 20
    dash_ok = dash_k <= 2
    print(f"台词 {n} 字 | 省略号 {ell_k:.1f}/千（≤20 {'✅' if ell_ok else '❌'}） | 破折号 {dash_k:.1f}/千（≤2 {'✅' if dash_ok else '⚠️'}）")
    if not ell_ok:
        print(f"  ❌ 省略号超标（{ell} 个 U+2026，拖沓腔——无合法理由超 band，必修），含省略号台词：", file=sys.stderr)
        for x in lines:
            if "\u2026" in x:
                print(f"    「{x}」", file=sys.stderr)
        bad = 1
    if not dash_ok:
        # 破折号在单集小样本中会被合法角色口头禅（如「我呸——」）触发（一个“——”=2 字即 ≈ 4.7/千@420字）；
        # 基准的 ≤2 是全剧级口径，故此处只 WARN 不 FAIL，交由人工/reviewer 对声音卡片核实
        print(f"  ⚠️ 破折号 {dash_k:.1f}/千 超全剧级基准 ≤2（{dash} 个 U+2014）——单集小样本常由角色口头禅触发，需对声音卡片核实：若为已定义口头禅则免扣，否则改写。含破折号台词：", file=sys.stderr)
        for x in lines:
            if "\u2014" in x:
                print(f"    「{x}」", file=sys.stderr)
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description="台词「」逐字保真校验 + 标点 AI 腔密度扫描")
    ap.add_argument("--file", required=True, help="待校验文件（新版）")
    ap.add_argument("--baseline", help="基线：git:HEAD / git:<rev> / 文件路径（--punct-scan 模式不需）")
    ap.add_argument("--allow-reorder", action="store_true",
                    help="只比内容集合不比顺序（拆镜重排台词顺序合法时用；默认严格按序）")
    ap.add_argument("--punct-scan", action="store_true",
                    help="标点 AI 腔密度扫描（省略号按 U+2026 逐字计，与语料基线同口径）；不需 --baseline")
    args = ap.parse_args()

    if args.punct_scan:
        return punct_scan(args.file)
    if not args.baseline:
        print("ERROR: 非 --punct-scan 模式必须提供 --baseline", file=sys.stderr)
        return 2

    new_path = Path(args.file)
    if not new_path.is_file():
        print(f"ERROR: 文件不存在：{args.file}", file=sys.stderr)
        return 2
    # git show 用仓库相对路径
    rel = new_path.as_posix()
    new_lines = extract_lines(new_path.read_text(encoding="utf-8"))
    old_lines = extract_lines(read_baseline(args.baseline, rel))

    if args.allow_reorder:
        old_set, new_set = sorted(old_lines), sorted(new_lines)
        if old_set == new_set:
            print(f"✅ 台词保真（集合模式）：{len(new_lines)} 处「」逐字一致")
            return 0
    elif old_lines == new_lines:
        print(f"✅ 台词保真：{len(new_lines)} 处「」顺序与内容逐字一致")
        return 0

    print(f"❌ 台词差异：基线 {len(old_lines)} 处 vs 新版 {len(new_lines)} 处", file=sys.stderr)
    sm = difflib.SequenceMatcher(a=old_lines, b=new_lines)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        for k in range(i1, i2):
            print(f"  - 基线[{k}]: 「{old_lines[k]}」", file=sys.stderr)
        for k in range(j1, j2):
            print(f"  + 新版[{k}]: 「{new_lines[k]}」", file=sys.stderr)
        # 替换对：标出具体劣化字符
        if tag == "replace" and i2 - i1 == j2 - j1:
            for a, b in zip(old_lines[i1:i2], new_lines[j1:j2]):
                bad = [(x, y) for x, y in zip(a, b) if x != y]
                if bad and len(a) == len(b):
                    print(f"    ⚠️ 疑似劣化字: {', '.join(f'{x}→{y}' for x, y in bad)}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
