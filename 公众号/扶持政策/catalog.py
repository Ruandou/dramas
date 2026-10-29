#!/usr/bin/env python3
"""资料底库的校验、导出与人工核验入口。"""
import argparse
import json
import re
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'catalog.json'
CATEGORIES = {'policies', 'platforms', 'models', 'tools'}
KINDS = {'policy', 'place', 'platform', 'model', 'tool-use'}
ACCESS = {'public', 'invitation', 'business', 'unknown', 'not_applicable'}
WINDOWS = {'application', 'incentive', 'contract', 'validity'}
WINDOW_LABELS = {'application': '申报', 'incentive': '激励', 'contract': '签约', 'validity': '政策有效期'}


def timestamp():
    return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')


def safe_url(url):
    try:
        p = urlsplit(url)
        return (p.scheme in {'http', 'https'} and bool(p.hostname)
                and not p.username and not p.password and not re.search(r'[\s<>"\x00-\x1f]', url))
    except ValueError:
        return False


def validate(doc):
    if doc.get('schema_version') != 1:
        raise ValueError('不支持的 schema_version')
    date.fromisoformat(doc['reported_as_of'])
    ids = [r['id'] for r in doc['records']]
    if len(ids) != len(set(ids)):
        raise ValueError('重复记录 ID')
    for r in doc['records']:
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]+', r['id']):
            raise ValueError(f"无效 ID: {r['id']}")
        if r['category'] not in CATEGORIES or r['kind'] not in KINDS or r['access'] not in ACCESS:
            raise ValueError(f"分类/入口类型无效: {r['id']}")
        if r['lifecycle'] not in {'listed', 'historical', 'unknown'}:
            raise ValueError('生命周期无效')
        if not r['title'] or not r['entity_id']:
            raise ValueError('标题与实体 ID 不得为空')
        source_ids = [s['id'] for s in r['sources']]
        if not source_ids or len(source_ids) != len(set(source_ids)):
            raise ValueError(f"来源缺失/重复: {r['id']}")
        for s in r['sources']:
            if not safe_url(s['url']) or s['grade'] not in {'A', 'B', 'C'}:
                raise ValueError(f"来源无效: {r['id']}")
        keys = [f['key'] for f in r['fields']]
        if len(keys) != len(set(keys)):
            raise ValueError('字段键重复')
        for field in r['fields']:
            if not isinstance(field['value'], str) or not field['source_ids']:
                raise ValueError('字段值须为文本且关联来源')
            if set(field['source_ids']) - set(source_ids):
                raise ValueError('字段引用不存在的来源')
            if field.get('verified_at'):
                datetime.fromisoformat(field['verified_at'])
                proof = field.get('verification', {})
                if not proof.get('quote', '').strip() or proof.get('source_id') not in field['source_ids']:
                    raise ValueError('已核字段须保存摘录与来源')
                if proof.get('value') != field['value']:
                    raise ValueError('字段已变化，必须重新核验或清除旧核验标记')
        metadata_keys = {'title', 'access', 'lifecycle'}
        if r.get('window'):
            metadata_keys |= {'window.kind', 'window.start', 'window.end'}
        proofs = r.get('metadata_verification', {})
        for key, proof in proofs.items():
            if key not in metadata_keys or not proof.get('quote', '').strip() or proof.get('source_id') not in source_ids:
                raise ValueError('元数据核验须保存合法字段、摘录和来源')
            datetime.fromisoformat(proof['verified_at'])
            actual = r['window'][key.split('.')[1]] if key.startswith('window.') else r[key]
            if 'value' not in proof or proof['value'] != actual:
                raise ValueError('元数据已变化，必须重新核验或清除旧核验标记')
        if r.get('last_verified_at') and (not all(f.get('verified_at') for f in r['fields']) or not metadata_keys <= proofs.keys()):
            raise ValueError('禁止把部分核验标成整条已核')
        if set(r['related_ids']) - set(ids) or r['id'] in r['related_ids']:
            raise ValueError('关联记录无效')
        for key in ('reported_as_of',):
            date.fromisoformat(r[key])
        for key in ('imported_at', 'updated_at', 'last_verified_at'):
            if r.get(key):
                datetime.fromisoformat(r[key])
        w = r.get('window')
        if w:
            if w['kind'] not in WINDOWS:
                raise ValueError('时间窗口类型无效')
            for k in ('start', 'end'):
                if w.get(k):
                    date.fromisoformat(w[k])
            if w.get('start') and w.get('end') and w['start'] > w['end']:
                raise ValueError('窗口开始晚于结束')
        if not r['history']:
            raise ValueError('记录缺少来源沿革')
    referenced = []
    for document in doc['documents']:
        if Path(document['filename']).name != document['filename'] or not document['filename'].endswith('.md'):
            raise ValueError('清单文件名必须是本地 Markdown 文件名')
        for b in document['blocks']:
            if b['type'] == 'table':
                if set(b['record_ids']) - set(ids):
                    raise ValueError('文档引用不存在的记录')
                referenced.extend(b['record_ids'])
    if set(referenced) != {r['id'] for r in doc['records'] if r['kind'] != 'policy'}:
        raise ValueError('清单与底库记录覆盖不一致')
    return doc


def load(path=DATA):
    return validate(json.loads(Path(path).read_text(encoding='utf-8')))


def save(doc, path=DATA):
    validate(doc)
    path = Path(path)
    tmp = path.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def value(record, key):
    return next((f['value'] for f in record['fields'] if f['key'] == key), '')


def window_state(record, today):
    w = record.get('window')
    if record['lifecycle'] == 'historical':
        return 'historical'
    if not w or not (w.get('start') or w.get('end')):
        return 'unknown'
    if w.get('end') and today > w['end']:
        return 'ended'
    if w.get('start') and today < w['start']:
        return 'upcoming'
    return 'current'


def cell(text):
    return str(text).replace('|', '\\|').replace('\n', '<br>')


def source_cell(record):
    return '、'.join(f"{s['grade']} [{s['label']}]({s['url']})" for s in record['sources'])


def record_table(records, columns):
    header = [label for _, label in columns] + ['来源（非逐字段核验）', '资料 ID', '核验']
    rows = ['| ' + ' | '.join(header) + ' |', '|' + '|'.join(['---'] * len(header)) + '|']
    for r in records:
        vals = [r['title'] if key == 'title' else value(r, key) for key, _ in columns]
        verified = sum(bool(f['verified_at']) for f in r['fields'])
        vals += [source_cell(r), r['id'], f'{verified}/{len(r["fields"])} 字段已核']
        rows.append('| ' + ' | '.join(cell(v) for v in vals) + ' |')
    return '\n'.join(rows)


def markdown_exports(doc):
    records = {r['id']: r for r in doc['records']}
    outputs = {}
    for d in doc['documents']:
        parts = [f'# {d["title"]}', '> 自动生成：只改「扶持政策/data/catalog.json」，再运行 build.py；不要手改本文件。',
                 f'> 原资料截至 {doc["reported_as_of"]}。来源等级不等于事实已核验；导入不代表重新核实。']
        count = 0
        for b in d['blocks']:
            if b['type'] == 'text':
                parts.append(re.sub(r'(^## .+?)（\d+）$', r'\1', b['text'], flags=re.MULTILINE))
            elif b['type'] == 'table':
                subset = [records[k] for k in b['record_ids']]
                count += len(subset)
                parts.append(record_table(subset, b['columns']))
        parts += [f'## 底库统计\n\n收录 {count} 条资料记录（按条目/用途计，不代表独立产品或可用机会数）。']
        outputs[d['filename']] = '\n\n'.join(p for p in parts if p.strip()) + '\n'
    policies = [r for r in doc['records'] if r['kind'] == 'policy']
    parts = ['# 微短剧扶持与政策台账', '> 自动生成：权威数据为「扶持政策/data/catalog.json」，运行 build.py 同步。',
             f'> 原资料截至 {doc["reported_as_of"]}；窗口、金额与条件均待逐字段留证复核。无截止日不等于滚动申报；激励期、签约期不等于公开申报期。',
             '## 扶持项目与历史批次',
             record_table(policies, [('issuer', '发布方'), ('title', '项目'), ('benefit', '给什么'), ('eligibility', '谁能申'), ('entry', '入口'), ('deadline_note', '时间口径')])]
    for r in policies:
        w = r.get('window')
        window = f"{WINDOW_LABELS[w['kind']]}：{w.get('start') or '起始日未记录'} 至 {w.get('end') or '截止日未记录'}" if w else '申报窗口待核'
        parts.append(f'## {r["title"]}\n\n- 资料 ID：{r["id"]}\n- {window}\n- 个人参与：{value(r, "individual_note") or "未核实"}\n- 来源：{source_cell(r)}')
        if r['notes']:
            parts.append('\n'.join('- ' + n for n in r['notes']))
    parts += ['## 使用边界\n\n- 最高金额是评审上限，不是到手价。\n- 名单邀约、主体资质、版权、备案要求各自核对。\n- 平台评级旧价目不当作当前合同报价；未知分账口径不推算收益。']
    outputs['扶持政策台账.md'] = '\n\n'.join(parts) + '\n'
    return outputs


def review(doc, record_id, field_key, source_id, quote, new_value=None, note=''):
    if not quote.strip():
        raise ValueError('核验必须提供原文摘录')
    record = next(r for r in doc['records'] if r['id'] == record_id)
    at = timestamp()
    metadata_keys = {'title', 'access', 'lifecycle'}
    if record.get('window'):
        metadata_keys |= {'window.kind', 'window.start', 'window.end'}
    if field_key in metadata_keys:
        if source_id not in {s['id'] for s in record['sources']}:
            raise ValueError('核验来源必须属于该记录')
        target, key = (record['window'], field_key.split('.')[1]) if field_key.startswith('window.') else (record, field_key)
        before = target[key]
        after = new_value if new_value is not None else before
        if field_key in {'window.start', 'window.end'} and after == 'null':
            after = None
        target[key] = after
        record.setdefault('metadata_verification', {})[field_key] = {
            'verified_at': at, 'source_id': source_id, 'quote': quote, 'note': note, 'value': after}
    else:
        field = next(f for f in record['fields'] if f['key'] == field_key)
        if source_id not in field['source_ids']:
            raise ValueError('核验来源必须属于该字段的来源集合')
        before = field['value']
        after = new_value if new_value is not None else before
        field['value'] = after
        field['verified_at'] = at
        field['verification'] = {'source_id': source_id, 'quote': quote, 'note': note, 'value': after}
    if before != after:
        record['updated_at'] = at
    complete = all(f['verified_at'] for f in record['fields']) and metadata_keys <= record.get('metadata_verification', {}).keys()
    dates = [f['verified_at'] for f in record['fields']] + [p['verified_at'] for p in record.get('metadata_verification', {}).values()]
    record['last_verified_at'] = min(dates) if complete else None
    record['history'].append({'kind': 'review', 'at': at, 'field': field_key,
                              'before': before, 'after': after, 'source_id': source_id,
                              'quote': quote, 'summary': note or '人工逐字段核验'})
    validate(doc)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('check')
    r = sub.add_parser('review')
    for name in ('record', 'field', 'source', 'quote'):
        r.add_argument('--' + name, required=True)
    r.add_argument('--value')
    r.add_argument('--note', default='')
    args = p.parse_args()
    doc = load()
    if args.command == 'review':
        review(doc, args.record, args.field, args.source, args.quote, args.value, args.note)
        save(doc)
        print('核验已记录；运行 build.py 同步清单与页面。')
    else:
        print(f'底库通过校验：{len(doc["records"])} 条；{len(doc["documents"])} 份清单。')


if __name__ == '__main__':
    main()
