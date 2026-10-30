#!/usr/bin/env python3
"""从 JSON 底库生成站点与 Markdown 阅读版。"""
import argparse
import json
from pathlib import Path

from catalog import ROOT, load, markdown_exports

HEADERS = '''/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'self'; frame-ancestors 'none'
'''


def public_data(doc):
    result = {k: doc[k] for k in ('schema_version', 'title', 'reported_as_of', 'imported_at')}
    result['records'] = [{k: v for k, v in r.items() if k != 'provenance'} for r in doc['records']]
    for public, original in zip(result['records'], doc['records']):
        public['origin'] = {k: v for k, v in original['provenance'].items() if k in ('file', 'row_at_import')}
    result['documents'] = [{k: v for k, v in d.items() if k != 'provenance'} for d in doc['documents']]
    return result


def build(doc):
    import web
    data = public_data(doc)
    maintenance = ROOT / 'data' / 'maintenance.json'
    if maintenance.exists():
        data['maintenance'] = json.loads(maintenance.read_text(encoding='utf-8'))
    page = web.render(data)
    return {
        'index.html': page,
        'policies.html': page,
        'catalog.js': (ROOT / 'static' / 'catalog.js').read_text(encoding='utf-8'),
        'catalog.css': (ROOT / 'static' / 'catalog.css').read_text(encoding='utf-8'),
        'catalog.json': json.dumps(data, ensure_ascii=False, indent=2) + '\n',
        '404.html': f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">{web.FAVICON}<link rel="stylesheet" href="/catalog.css"><title>页面不存在 · 一人短剧厂牌</title><main class="page-shell"><h1>这条资料不在这里</h1><p>链接可能已变更，可以回资料库重新查找。</p><a href="/">回到短剧资料库</a></main></html>\n',
        '_headers': HEADERS,
    }


def exports(doc):
    return {ROOT.parent / '素材' / name: content for name, content in markdown_exports(doc).items()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, default=ROOT / 'dist')
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    doc = load()
    files = {args.output / name: content for name, content in build(doc).items()}
    files.update(exports(doc))
    stale = [str(path) for path, content in files.items() if not path.exists() or path.read_text(encoding='utf-8') != content]
    if args.check:
        if stale:
            raise SystemExit('产物过期：\n' + '\n'.join(stale))
        print(f'底库、站点与清单一致：{len(files)} 个文件')
        return
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_symlink():
            raise SystemExit(f'拒绝覆盖符号链接：{path}')
        if str(path) in stale:
            path.write_text(content, encoding='utf-8')
    print(f'生成完成：{len(files)} 个文件；修改 {len(stale)} 个，不删除目录或无关文件。')


if __name__ == '__main__':
    main()
