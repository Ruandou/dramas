#!/usr/bin/env python3
"""把「发布版.md」转成可直接粘进公众号编辑器的 HTML 片段。

为什么不用后台自带的 Markdown 导入：实测它会把相邻列表项合并、部分 ** 不转加粗、
且把 H1 混进正文（019 导入后正文多出标题行、两处列表被并成一段）。

用法：python3 _md2html.py 文章/019_发布版.md 素材/_tmp_body.html
规则：H1 丢弃（走标题字段）；H2→<h2>；连续「- 」→<ul>；|…| →表格；
     **粗**→<strong>；[文字](url)→<a>；【图 N：…】保持独立段落作为插图锚点。
"""
from __future__ import annotations

import html
import pathlib
import re
import sys

INLINE_BOLD = re.compile(r'\*\*(.+?)\*\*')
INLINE_LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = INLINE_LINK.sub(lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', text)
    text = INLINE_BOLD.sub(lambda m: f'<strong>{m.group(1)}</strong>', text)
    return text


def convert(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith('# '):
            i += 1
            continue
        if line.startswith('## '):
            out.append(f'<h2>{inline(line[3:].strip())}</h2>')
            i += 1
            continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                cells = [c.strip() for c in lines[i].strip('|').split('|')]
                if not all(re.fullmatch(r':?-{2,}:?', c) for c in cells):
                    rows.append(cells)
                i += 1
            body = []
            for r, row in enumerate(rows):
                tag = 'th' if r == 0 else 'td'
                body.append('<tr>' + ''.join(f'<{tag}>{inline(c)}</{tag}>' for c in row) + '</tr>')
            out.append('<table><tbody>' + ''.join(body) + '</tbody></table>')
            continue
        if line.startswith('- '):
            items = []
            while i < len(lines) and lines[i].startswith('- '):
                items.append(lines[i][2:].strip())
                i += 1
            out.append('<ul>' + ''.join(f'<li>{inline(t)}</li>' for t in items) + '</ul>')
            continue
        out.append(f'<p>{inline(line.strip())}</p>')
        i += 1
    return '\n'.join(out)


def main() -> None:
    src, dest = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    fragment = convert(src.read_text(encoding='utf-8'))
    dest.write_text(fragment, encoding='utf-8')
    text = re.sub(r'<[^>]+>', '', fragment)
    assert '**' not in text, '仍残留 ** 未转加粗'
    plain_len = len(re.sub(r'\s+', '', text))
    print(f'{dest.name}: {len(fragment)} 字节 / 纯文本 {plain_len} 字符')
    print('元素统计:',
          f'h2={fragment.count("<h2>")}',
          f'p={fragment.count("<p>")}',
          f'li={fragment.count("<li>")}',
          f'strong={fragment.count("<strong>")}',
          f'table={fragment.count("<table>")}',
          f'a={fragment.count("<a ")}')
    anchors = re.findall(r'【图 \d：[^】]+】', text)
    print('图锚点:', anchors)


if __name__ == '__main__':
    main()
