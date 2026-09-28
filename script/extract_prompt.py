#!/usr/bin/env python3
"""
extract_prompt.py — 从卡片文件按 ID 段边界提取英文 Prompt 代码块（通用工具）

背景（2026-08-08 事故固化）：PROP-013 生成时曾用 re.search 全局匹配
「道具 Prompt（EN）」代码块，匹配到文件第一个（PROP-001 手修笔记），
导致生成错误道具图、重复扣费。本工具强制按段边界提取 + 关键词门控。

用法：
  python3 script/extract_prompt.py --card 资产/道具卡片.md --id PROP-013
  python3 script/extract_prompt.py --card 资产/角色卡片.md --id CHAR-001 --field "L01" (可选)
  python3 script/extract_prompt.py --card ... --id ... --keyword watch  # 关键词门控

规则：
  1. 段边界：从 '## <id>' 或 '## <id> · ' 定位段起点，到下一个 '## ' 段起点结束
  2. 段内找第一个 ``` 围栏代码块（跨行，re.S）
  3. --keyword 门控：提取结果必须包含关键词，否则 exit 1（防止提取到别的段）
  4. 输出到 stdout（或 --output 文件）
"""
import argparse
import re
import sys


def extract(card_path: str, item_id: str):
    text = open(card_path, encoding="utf-8").read()
    # 段起点：'## <id>' 或 '## <id> · 名称'（跳过 ## 前缀后的任何空白）
    start = re.search(rf"^##\s*{re.escape(item_id)}(?:\s*·|\s|$)", text, re.M)
    if not start:
        sys.exit(f"ERROR: 卡片中未找到段 '## {item_id}'（{card_path}）")
    seg_start = start.start()
    # 段终点：下一个同级 '## ' 段（排除 '####' 等更小标题）
    nxt = re.search(r"^##\s+(?!{re.escape(item_id)})", text[seg_start + 1:], re.M)
    seg_end = seg_start + 1 + nxt.start() if nxt else len(text)
    seg = text[seg_start:seg_end]
    # 段内第一个围栏代码块
    m = re.search(r"```[^\n]*\n(.*?)```", seg, re.S)
    if not m:
        sys.exit(f"ERROR: 段 '## {item_id}' 内未找到 ``` 代码块（{card_path}）")
    return seg[:120].split("\n")[0].strip(), m.group(1).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True, help="卡片文件路径（如 资产/道具卡片.md）")
    ap.add_argument("--id", required=True, help="条目 ID（如 PROP-013 / CHAR-001 / SCENE-003）")
    ap.add_argument("--keyword", help="门控关键词（必须出现在提取的 prompt 中，如 watch）")
    ap.add_argument("--output", help="输出文件（默认 stdout）")
    args = ap.parse_args()

    header, prompt = extract(args.card, args.id)

    if args.keyword:
        if args.keyword not in prompt:
            sys.exit(
                f"FAIL 门控: 段 '{args.id}' 提取的 prompt 不含关键词 '{args.keyword}'，"
                f"疑似提取错段，已阻止。段标题: {header}"
            )
        print(f"[门控通过] 段 '{args.id}' ({header}) prompt 含关键词 '{args.keyword}' ✅")

    if args.output:
        open(args.output, "w", encoding="utf-8").write(prompt)
        print(f"已写入 {args.output}（{len(prompt)} 字符）")
    else:
        print(prompt)


if __name__ == "__main__":
    main()
