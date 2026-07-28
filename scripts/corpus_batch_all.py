#!/usr/bin/env python3
# 全量语料批处理：76 文件 → 分类统计
import zipfile, re, json, subprocess, tempfile, os, statistics as st
from pathlib import Path

SRC = Path('/Users/lei/Downloads/完本剧情')

EP_RES = [
    re.compile(r'^第\s*[一二三四五六七八九十百零0-9]+\s*集'),
    re.compile(r'^EP\s*\d+', re.I),
    re.compile(r'^【?第?\s*\d{1,3}\s*[集话]】?\s*$'),
    re.compile(r'^\d{1,3}\s*$'),
]
SCENE_RE = re.compile(r'^\d{1,3}[-–—.、]\d{1,3}[\s、,，]|^场景|^【?\d{1,3}[-–—]\d{1,3}】?\s')
ACTION_RE = re.compile(r'^[▲△]')
META_RE = re.compile(r'^(人物|人|出场人物)\s*[:：]|^(日|夜|晨|黄昏)[\s，,]+(内|外)|^字幕[:：]|^闪回|^插叙|^(时间|地点|气氛)[:：]')
DLG_RE = re.compile(r'^([^：:▲△]{1,14})[:：](.+)$')
MONO_KEYS = ('画外音', 'OS', 'os', 'VO', '内心', '旁白', '心声', '独白', '自语')
NOT_SPEAKER = re.compile(r'人物|地点|时间|场景|备注|标题|大纲|梗概|说明|注意|作者|联系|导演|道具|服装|音乐|音效|镜头|特效|字幕')

GENRES = [
    ('男频战神/动作', ['无双','北王刀','战尊','龙帝','武神','镇域','禁主','妖孽高手','少帅','西游','飞狐']),
    ('男频古代/历史', ['一品布衣','太子','绝代','神仙微信','布衣']),
    ('女频总裁/婚恋', ['闪婚','霸总','总裁','傅总','云总','封总','战总','娇妻','甜妻','娇宠','小心肝','钻石男友','邱秘书','余情未了','孕检单','离婚','未婚夫','错爱','恋爱指南','噬骨','引','招惹','坠入','驯野','过分野','假面','撕夜','危情','星辰','声声','念念','许你','幸得','无差别','凤凰男']),
    ('女频古装', ['折腰','请君','长公主','帝后','毒妻','美人谋','凤栖','栀栀','掌生','神算','女配','宫','风雪泣月','绝色']),
    ('年代/家庭', ['家里家外','70年代','太奶奶','大山','灯塔','江南时节','盛夏']),
    ('奇幻/脑洞', ['修仙','神医奶娃','听物','校花迷踪','镜','掌中万物','七宗罪','法官','暗影','救赎']),
]

def classify(name):
    for g, kws in GENRES:
        if any(k in name for k in kws):
            return g
    return '其他/未分类'

def docx_lines(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8', 'ignore')
    return [t for t in (''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p)).strip()
            for p in re.split(r'</w:p>', xml)) if t]

def doc_lines(path):
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tf:
        tmp = tf.name
    try:
        subprocess.run(['textutil', '-convert', 'txt', '-output', tmp, str(path)],
                       check=True, capture_output=True, timeout=60)
        text = open(tmp, encoding='utf-8', errors='ignore').read()
        return [l.strip() for l in text.splitlines() if l.strip()]
    finally:
        os.unlink(tmp) if os.path.exists(tmp) else None

def is_ep(ln):
    return len(ln) < 16 and any(r.match(ln) for r in EP_RES)

def sentences(text):
    return [p for p in (x.strip() for x in re.split(r'[。！？!?…]+', text)) if p]

def analyze_lines(lines):
    eps, cur = [], None
    for ln in lines:
        if is_ep(ln):
            cur = {'turns': []}
            eps.append(cur)
            continue
        if cur is None or ACTION_RE.match(ln) or SCENE_RE.match(ln) or META_RE.match(ln):
            continue
        m = DLG_RE.match(ln)
        if m:
            spk, txt = m.group(1).strip(), m.group(2).strip()
            if NOT_SPEAKER.search(spk) or not txt:
                continue
            cur['turns'].append((spk, txt, any(k in spk for k in MONO_KEYS)))
    eps = [e for e in eps if len(e['turns']) >= 3]
    if len(eps) < 5:
        return None
    tpe = [len(e['turns']) for e in eps]
    allt = [t for e in eps for t in e['turns']]
    mono = sum(1 for t in allt if t[2])
    tsents = [len(sentences(t[1])) or 1 for t in allt]
    schars = [len(s) for t in allt for s in sentences(t[1])]
    return {
        'eps': len(eps), 'turns': len(allt),
        'tpe_med': st.median(tpe),
        'dlg_pct': round(100*(1-mono/len(allt)), 1),
        'spt_med': st.median(tsents), 'spt_p90': sorted(tsents)[int(len(tsents)*.9)-1],
        'cps_med': st.median(schars), 'cps_p90': sorted(schars)[int(len(schars)*.9)-1],
    }

results, skipped = {}, []
for f in sorted(SRC.rglob('*')):
    if not f.is_file() or f.name.startswith('.'):
        continue
    ext = f.suffix.lower()
    if ext == '.docx':
        try:
            r = analyze_lines(docx_lines(f))
        except Exception as e:
            r = None
        results[f.name] = r
    elif ext == '.doc':
        try:
            r = analyze_lines(doc_lines(f))
        except Exception:
            r = None
        results[f.name] = r
    else:
        skipped.append(f.name)

ok = {k: v for k, v in results.items() if v}
fail = [k for k, v in results.items() if not v]

# 分类聚合
by_genre = {}
for name, r in ok.items():
    g = classify(name)
    by_genre.setdefault(g, []).append((name, r))

print('=== 解析成功', len(ok), '部 | 失败', len(fail), '| 跳过(pdf/png)', len(skipped), '===')
agg_rows = []
for g, items in sorted(by_genre.items()):
    dl = [r['dlg_pct'] for _, r in items]
    tp = [r['tpe_med'] for _, r in items]
    cs = [r['cps_med'] for _, r in items]
    sp = [r['spt_p90'] for _, r in items]
    agg_rows.append((g, len(items), round(st.median(tp),1), round(st.median(dl),1), round(st.median(cs),1), round(st.median(sp),1)))
print(json.dumps({'genre_agg[题材,部数,块/集中位,对白%中位,字/句中位,句/块P90中位]': agg_rows}, ensure_ascii=False, indent=1))
# 全语料
alldl = [r['dlg_pct'] for r in ok.values()]
alltp = [r['tpe_med'] for r in ok.values()]
allcs = [r['cps_med'] for r in ok.values()]
allsp = [r['spt_p90'] for r in ok.values()]
alleps = [r['eps'] for r in ok.values()]
print(json.dumps({'全语料': {
    '总部数': len(ok), '总集数': sum(alleps), '总台词块': sum(r['turns'] for r in ok.values()),
    '对白%中位/最小': (st.median(alldl), min(alldl)),
    '块每集中位分布(p10/med/p90)': (sorted(alltp)[int(len(alltp)*.1)], st.median(alltp), sorted(alltp)[int(len(alltp)*.9)-1]),
    '字每句中位分布': (min(allcs), st.median(allcs), max(allcs)),
    '句每块P90中位': st.median(allsp),
}}, ensure_ascii=False, indent=1))
print('--- 逐部（部|集|块/集|对白%|字/句中位）---')
for g, items in sorted(by_genre.items()):
    for name, r in sorted(items):
        print(f"{g} | {name[:28]} | {r['eps']}集 | {r['tpe_med']}块 | {r['dlg_pct']}% | {r['cps_med']}字")
print('--- 解析失败 ---')
for k in fail: print(' ', k)
print('--- 跳过 ---')
for k in skipped: print(' ', k)
