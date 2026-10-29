#!/usr/bin/env python3
"""一次性导入原有清单；已有底库时拒绝覆盖。"""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

import yaml

from catalog import DATA, ROOT, save, timestamp

MATERIALS = ROOT.parent / '素材'
CONFIG = {
    '短剧政策地图.md': ('policies', 'place', 7, [('region', '地区'), ('title', '政策/载体名称'), ('benefit', '给什么'), ('eligibility', '谁能申'), ('reported_status', '原资料状态')]),
    '分发平台清单.md': ('platforms', 'platform', 7, [('title', '平台'), ('company', '归属公司'), ('market', '市场'), ('format', '形态'), ('entry', '参与入口')]),
    '模型清单.md': ('models', 'model', 9, [('title', '模型/产品'), ('company', '公司'), ('version', '版本'), ('specs', '规格'), ('capabilities', '能力'), ('api', 'API'), ('price', '价格口径'), ('use', '短剧用途')]),
    '工具清单.md': ('tools', 'tool-use', 7, [('title', '工具'), ('type', '类型'), ('environment', '平台'), ('price', '价格口径'), ('use', '短剧用途')]),
}


def identity(prefix, text):
    return prefix + '-' + hashlib.sha256(text.encode()).hexdigest()[:12]


def sources(text, grade):
    linked = re.findall(r'\[([^\]]+)\]\((https?://[^\s)]+)\)', text)
    urls = re.findall(r'https?://[^\s)、|]+', text)
    labels = dict((url, label) for label, url in linked)
    found = []
    for url in dict.fromkeys(urls):
        found.append({'id': identity('src', url), 'url': url, 'grade': grade,
                      'label': labels.get(url, urlsplit(url).hostname),
                      'scope': '原清单行级来源；尚未逐字段核验，官网链接不证明整行参数'})
    return found


def field(key, label, val, src):
    return {'key': key, 'label': label, 'value': str(val),
            'source_ids': [s['id'] for s in src], 'verified_at': None}


def base_record(rid, category, kind, title, group, src, at, provenance):
    return {'id': rid, 'entity_id': rid, 'category': category, 'kind': kind,
            'title': title, 'group': group, 'fields': [], 'sources': src, 'tags': [],
            'access': 'unknown', 'lifecycle': 'listed', 'window': None,
            'reported_as_of': '2026-10-29', 'imported_at': at, 'updated_at': None,
            'last_verified_at': None, 'notes': [], 'related_ids': [],
            'history': [{'kind': 'import', 'at': at, 'summary': '从既有清单迁移；不是新发布，也不代表本次完成事实核验'}],
            'provenance': provenance}


def group_name(heading):
    heading = re.sub(r'^#+\s*', '', heading)
    heading = re.sub(r'^(?:[一二三四五六七八九十]+、|\d+[.)）]\s*)', '', heading)
    return re.sub(r'（\d+）$', '', heading).strip()


def import_document(filename, at):
    category, kind, width, columns = CONFIG[filename]
    original = (MATERIALS / filename).read_text(encoding='utf-8')
    lines = original.splitlines()
    document = {'filename': filename, 'title': lines[0].lstrip('# '), 'category': category,
                'blocks': [], 'provenance': {'sha256': hashlib.sha256(original.encode()).hexdigest(),
                                           'original_text': original}}
    records, text, table, heading = [], [], None, ''
    def flush():
        if text:
            document['blocks'].append({'type': 'text', 'text': '\n'.join(text).strip()})
            text.clear()
    skipping_stats = False
    for num, line in enumerate(lines[1:], 2):
        if line.startswith('## '):
            heading = line
            skipping_stats = '统计' in heading
        if skipping_stats:
            continue
        if line.startswith('**统计**') or re.match(r'共 \d+ 个地区', line):
            continue
        if '逐条复核' in line or '来源链接 2026-10-29 逐条核过' in line:
            continue
        cells = [x.strip() for x in re.split(r'(?<!\\)\|', line.strip().strip('|'))]
        if line.startswith('|') and len(cells) == width and '待核' not in heading:
            if re.fullmatch(r'[-: ]+', cells[0]):
                continue
            if cells[0] in {'地区', '平台', '模型', '工具'}:
                flush()
                table = {'type': 'table', 'columns': columns, 'record_ids': []}
                document['blocks'].append(table)
                continue
            if table is None:
                raise ValueError(f'{filename}:{num} 缺少表头')
            title_index = 1 if kind == 'place' else 0
            title = cells[title_index]
            group = group_name(heading) if kind != 'place' else ('拍摄载体' if cells[4] == '常年' else '地方政策')
            grade = cells[-1][0] if kind == 'model' else cells[-2]
            src = sources(cells[-1], grade)
            rid = identity(kind, filename + heading + title + (cells[0] if kind == 'place' else ''))
            r = base_record(rid, category, kind, title, group, src, at,
                            {'file': f'公众号/素材/{filename}', 'row_at_import': num, 'raw_row': line})
            for (key, label), val in zip(columns, cells):
                if key != 'title':
                    r['fields'].append(field(key, label, val, src))
            r['tags'] = [group]
            r['notes'] = ['原资料记录，金额、版本、资质与状态尚需逐字段留证核验。']
            if kind == 'place':
                r['tags'].append(cells[0].split('·')[0])
                r['notes'].append('原表“在开”仅说明收录政策，不证明当前有申报窗口；“常年”是载体属性，不是资金承诺。')
                if cells[4] == '已关闭':
                    r['lifecycle'] = 'historical'
                if cells[0] == '河南·郑州':
                    r['window'] = {'kind': 'validity', 'start': None, 'end': '2026-11-01'}
                    r['notes'].append('原资料称每年9月30日前初审；11月1日是政策有效期，不能当申报截止日。')
                if cells[0] == '山西省':
                    r['notes'].append('500万/200万对应对象存在疑点，可能是基地运营主体；未核原文前不按单部项目资金推荐。')
            if kind == 'platform':
                entry = cells[4]
                if entry.startswith('不对外'):
                    r['fields'][-1]['value'] = entry.replace('不对外', '未查到自助投稿入口', 1)
                    r['notes'].append('“未查到”不是平台明确拒绝外部合作；商务与赛事另核。')
                elif '邀请' in entry:
                    r['access'] = 'invitation'
                elif '待核' not in entry and ('商务' in entry or '采买' in entry or '可承制' in entry):
                    r['access'] = 'business'
                elif '待核' not in entry and '自助' in entry:
                    r['access'] = 'public'
                if title in {'番茄短剧', '连尚', 'HolyShort', 'Bilin'}:
                    r['lifecycle'] = 'unknown'
                if title == 'Instagram Reels':
                    r['notes'].append('Content Monetization 是否适用于 Instagram 尚待核实，不与 Facebook 计划混同。')
                if title == 'DramaWave':
                    r['notes'].append('原资料中的2026年2月至5月活动已结束；活动关闭不等于平台停止运营。')
            if kind == 'model':
                r['access'] = 'not_applicable'
                if title in {'Sora 2', 'Sora 1', 'Veo 3', 'Veo 2', 'Imagen 4 Ultra'}:
                    r['lifecycle'] = 'historical'
                    r['notes'].append('原资料标停用/历史版本；停运范围和日期仍需凭官方公告复核。')
                if title == 'Veo 3.1':
                    r['notes'].append('Vertex 与 Gemini preview 是不同服务入口，不能按“停运”字样整体下架。')
                if title == 'Seedance 2.5':
                    r['notes'].append('4K可用性须按方舟当前对应模型列复核，不把旧定价表中的“暂不支持”外推到全部服务。')
            if kind == 'tool-use':
                r['access'] = 'not_applicable'
                product = 'ComfyUI' if title.startswith('ComfyUI') else ('小云雀' if title.startswith('小云雀') else title)
                if title in {'剪映专业版', '剪映朗读', '剪映识别'}:
                    product = '剪映'
                r['entity_id'] = identity('product', product)
                if title in {'Cartoon Animator 5', 'Fish Audio', 'Storyboarder', 'ElevenLabs Studio'}:
                    r['notes'].append('本条系统支持、价格比较、免费额度或维护状态仍需专项核实，不作为采购依据。')
            records.append(r)
            table['record_ids'].append(rid)
        else:
            text.append(line)
    flush()
    for b in document['blocks']:
        if b['type'] == 'text' and b['text']:
            b['text'] = b['text'].replace('## 空档省', '## 检索空档（未查到不等于不存在）')
            if '核验：' in b['text']:
                b['text'] = b['text'].replace('> 核验：', '> 原采集笔记（待复核）：')
    return records, document


def import_policies(at):
    original = (ROOT / 'data' / 'policy.yaml').read_text(encoding='utf-8')
    old = yaml.safe_load(original)
    ledger = (MATERIALS / '扶持政策台账.md').read_text(encoding='utf-8')
    sections = re.split(r'\n### ', ledger)
    notes = {}
    for section in sections[1:]:
        h, _, content = section.partition('\n')
        key = next((rid for token, rid in [('1.', 'sh-2026'), ('2.', 'wx-q4'), ('3.', 'wx-novel'), ('4.', 'sz-2025'), ('5.', 'hq-2026')] if h.startswith(token)), None)
        if key:
            notes[key] = [line[2:] for line in content.splitlines() if line.startswith('- ')]
    records = []
    labels = {'issuer': '发布方', 'region': '地区', 'benefit': '支持内容', 'eligibility': '适用主体',
              'individual': '个人资格（原资料）', 'individual_note': '个人参与条件', 'entry': '入口说明',
              'deadline_note': '时间口径', 'note': '历史批次说明'}
    for item in old['items'] + old['closed']:
        closed = item in old['closed']
        rid = item['id']
        grade = item.get('evidence', 'B' if rid in {'hg-1000', 'zj-contest'} else 'A')
        src = sources(item['url'], grade)
        r = base_record(rid, 'policies', 'policy', item['title'], '平台扶持' if item.get('type') == 'platform' or rid == 'hg-1000' else '政府扶持', src, at,
                        {'file': '公众号/扶持政策/data/policy.yaml', 'original_item': json.loads(json.dumps(item, default=str))})
        for key, label in labels.items():
            if key in item:
                val = item[key]
                if isinstance(val, bool):
                    val = 'yes' if val else 'no'
                r['fields'].append(field(key, label, val, src))
        r['notes'] = notes.get(rid, []) + ['自原台账导入，来源等级保留，不据此宣称整条已核验。']
        if item.get('deadline'):
            r['window'] = {'kind': {'wx-q4': 'incentive', 'wx-novel': 'contract'}.get(rid, 'application'),
                           'start': str(item['start']) if item.get('start') else None, 'end': str(item['deadline'])}
        if closed:
            r['lifecycle'] = 'historical'
        if rid == 'sh-2026':
            r['access'] = 'public'
        if rid == 'wx-novel':
            r['access'] = 'invitation'
            r['notes'].append('只有名单内作者与承制方能签约，个人资格不代表公开报名。')
        if rid == 'wx-q4':
            r['notes'].append('这是已加入计划者的激励周期，不是新主体的报名窗口。')
        corrections = []
        if rid == 'sz-2025':
            r['title'] = '促进微短剧产业高质量发展若干措施（修订版）'
            for f in r['fields']:
                if f['key'] == 'benefit':
                    f['value'] = '剧本最高100万元；取景、精品、研发等最高200万元；园区最高500万元'
            src[0]['grade'] = 'A'
            corrections.append('对齐已修订文字台账：移除未在公报核到的制作成本30%，区分取景/精品/研发与园区上限；本次不冒充重新核验。')
        if rid == 'hq-2026':
            for f in r['fields']:
                if f['key'] == 'benefit':
                    f['value'] = '剧本每部最高1万元；首次拍摄并完整播放最高20万元；住宿按成本40%、每间夜不超过40元，运营主体年度不超过300万元'
            corrections.append('对齐文字台账，补齐最高、成本比例与单主体年度住宿补贴上限。')
        if rid == 'dy-guarantee':
            src[0]['grade'] = 'B'
            corrections.append('财联社报道属于媒体来源，不标为官方原文A。')
        if rid == 'gd-annual':
            r['notes'].append('原表混合省市区不同专项的上限，不能直接相加或承诺同一项目可叠加。')
        if rid == 'hg-script':
            r['notes'].append('2025年评级价目不能当成2026年报价，当前收稿状态待核。')
        for summary in corrections:
            r['history'].append({'kind': 'correction', 'at': at, 'summary': summary})
            r['updated_at'] = at
        records.append(r)
    return records, {'policy_yaml': original, 'ledger_markdown': ledger}


def relate(records):
    by_title = {r['title']: r for r in records}
    policies = {r['id']: r for r in records if r['kind'] == 'policy'}
    for r in records:
        if r['kind'] == 'place':
            region = next(f['value'] for f in r['fields'] if f['key'] == 'region')
            rid = {'广东·深圳': 'sz-2025', '广东·横琴（珠海）': 'hq-2026', '广东·佛山': 'fs-2026', '福建省': 'fj-annual'}.get(region)
            if rid:
                r['related_ids'].append(rid)
                policies[rid]['related_ids'].append(r['id'])
                for f in r['fields']:
                    if f['key'] == 'benefit' and '见《扶持政策台账》' in f['value']:
                        f['value'] = '具体批次、金额和主体要求见关联扶持项目；不重复维护数值。'
        if r['kind'] == 'tool-use':
            r['related_ids'] += [other['id'] for other in records if other['id'] != r['id'] and other['entity_id'] == r['entity_id']]
    pairs = [('Seedance 2.5', '即梦 AI'), ('Kling 4.0', '可灵 AI'), ('Midjourney V8.2', 'Midjourney'),
             ('Vidu Q3', 'Vidu'), ('红果短剧', '抖音短剧')]
    for left, right in pairs:
        if left in by_title and right in by_title:
            a, b = by_title[left], by_title[right]
            a['related_ids'].append(b['id'])
            b['related_ids'].append(a['id'])
    for r in records:
        r['related_ids'] = list(dict.fromkeys(r['related_ids']))


def main():
    if DATA.exists():
        raise SystemExit('底库已存在，拒绝重新导入或覆盖；后续通过 catalog.py review 或编辑底库维护。')
    at = timestamp()
    all_records, docs = [], []
    for filename in CONFIG:
        records, document = import_document(filename, at)
        expected = {'短剧政策地图.md': 71, '分发平台清单.md': 73, '模型清单.md': 91, '工具清单.md': 80}[filename]
        if len(records) != expected:
            raise ValueError(f'{filename} 导入计数异常：{len(records)}，预期{expected}')
        all_records += records
        docs.append(document)
    policies, archive = import_policies(at)
    all_records = policies + all_records
    relate(all_records)
    doc = {'schema_version': 1, 'title': '短剧资料库', 'reported_as_of': '2026-10-29',
           'imported_at': at, 'records': all_records, 'documents': docs, 'migration_archive': archive}
    save(doc)
    print(f'已导入 {len(all_records)} 条记录；所有逐字段核验时间保持为空。')


if __name__ == '__main__':
    main()
