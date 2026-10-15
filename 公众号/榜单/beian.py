#!/usr/bin/env python3
"""广电总局发行许可通告附件解析（A 级官方源）。

用法:
  python3 beian.py license /art/2026/7/13/art_113_73691.html   # 全国国产网络剧片发行许可情况

产物: raw/beian/<article-id>-license.json（逐条 剧名/许可证号/类型/集数/申报单位）
解析结果按官方口径自校验：各类型条数须与网页正文公布的数量一致，取不到官方数字则拒绝放行。

未支持：月度《拍摄制作…备案公示》附件为 xlsx（2026-09 起）或列结构不同的 PDF（无许可证号字段），
需另写解析（openpyxl），不要套用本脚本的许可证正则。
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from html import unescape
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'raw' / 'beian'
BASE = 'https://www.nrta.gov.cn'
UA = 'personal-short-drama-archive/1.0'

# 官方正文里的“共 N 部”分类型统计，用于校验解析完整性
OFFICIAL = {
    '网络剧': r'网络剧(\d+)部',
    '网络电影': r'网络电影(\d+)部',
    '微短剧': r'微短剧(\d+)部',
    '网络动画片': r'网络动画片(\d+)部',
}


RECORD = re.compile(
    r'^(\d+)\s+(.+?)\s+（([^）]+)）\s*(\S*?审)\s*字\s*（(\d{4})）\s*第(\d+)\s*号\s+(\S+)\s+(\d+)\s+(.+)$',
    re.S,
)


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=40) as resp:
        return resp.read()


def attachment(page: str) -> str:
    """优先取 PDF 附件；若只有 zip/docx，明确报错而不是把压缩包当 PDF 解析。"""
    links = [unescape(u) for u in re.findall(r'href="(/module/download/downfile\.jsp[^"]*)"', page)]
    assert links, '未找到附件'
    def showname(link: str) -> str:
        m = re.search(r'showname=([^&]*)', link)
        return unescape(m.group(1)) if m else ''
    pdfs = [l for l in links if showname(l).lower().endswith('.pdf')]
    if not pdfs:
        raise SystemExit(f'该文附件非 PDF（{ [showname(l) for l in links] }），需另写解压/Word 解析')
    return BASE + pdfs[0]


def pdf_text(data: bytes, tmp: Path) -> str:
    tmp.write_bytes(data)
    return '\n'.join(p.extract_text() or '' for p in PdfReader(str(tmp)).pages)


def split_titles(name: str) -> tuple[str, list[str]]:
    """一行记录正常只有一个剧名。个别序号下并列两个剧名（PDF 中各自占一行），
    官方按行计数，故不拆分，仅把并列剧名单列到 also_listed。同行空格是剧名自身的一部分。"""
    lines = [t.strip() for t in name.split('\n') if t.strip()]
    if len(lines) > 1 and lines[-1].startswith('（'):
        lines[-2] += lines[-1]
        lines.pop()
    return lines[0], lines[1:]


def rows_from(page_text: str) -> list[dict]:
    lines = [re.sub(r'\s+', ' ', l).strip() for l in page_text.splitlines()]
    records, buf = [], ''
    for line in lines:
        # 长许可证号会折行，需把续行并回上一条记录；
        # 序号可能独占一行（如「348」），也须识别为新记录起点
        if re.match(r'^\d+$', line) or re.match(r'^\d+ \S', line):
            if buf:
                records.append(buf)
            buf = line
        elif buf:
            buf += '\n' + line
    if buf:
        records.append(buf)

    rows = []
    for record in records:
        m = RECORD.match(record)
        if not m:
            continue
        title, also_listed = split_titles(m.group(2).strip())
        rows.append({
            'title': title,
            'also_listed': also_listed,
            'region': m.group(3),
            'lic': m.group(4),
            'lic_year': int(m.group(5)),
            'lic_no': int(m.group(6)),
            'type': m.group(7),
            'episodes': int(m.group(8)),
            'applicant': m.group(9).strip(),
        })
    return rows


def official_counts(html_page: str) -> dict:
    """官方数量公布在网页正文（不是 PDF 附件）里，必须取到才允许放行。"""
    body = re.sub(r'<script.*?</script>', ' ', html_page, flags=re.S)
    flat = re.sub(r'\s+', '', unescape(re.sub(r'<[^>]+>', ' ', body)))
    out = {}
    for kind, pattern in OFFICIAL.items():
        m = re.search(pattern, flat)
        if m:
            out[kind] = int(m.group(1))
    return out


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] != 'license':
        raise SystemExit(__doc__)
    _, path = sys.argv[1], sys.argv[2]
    page = get(BASE + path).decode('utf-8', 'ignore')
    tmp = Path('/tmp') / 'nrta-license.pdf'
    text = pdf_text(get(attachment(page)), tmp)
    rows = rows_from(text)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row['type']] = counts.get(row['type'], 0) + 1
    expect = official_counts(page)
    assert expect, '未在网页正文取到官方数量，禁止放行（校验会形同虚设）'
    mismatch = {k: (counts.get(k, 0), v) for k, v in expect.items() if counts.get(k, 0) != v}
    assert not mismatch, f'与官方公布数量不一致 (解析/官方): {mismatch}'

    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f'{Path(path).stem}-license.json'
    dest.write_text(json.dumps({'source': BASE + path, 'rows': rows}, ensure_ascii=False, indent=2) + '\n')
    print(f'PASS: {len(rows)} 条 -> {dest.relative_to(ROOT)}')
    print('  分布:', counts)
    print('  官方:', expect)


if __name__ == '__main__':
    main()
