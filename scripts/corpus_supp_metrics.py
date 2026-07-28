#!/usr/bin/env python3
# 补测：感叹号/直述情绪/说话角色数/开场首句/同开头重复/碎片语率/集末悬念
import zipfile, re, json, subprocess, tempfile, os, statistics as st
from pathlib import Path

SRC = Path('/Users/lei/Downloads/完本剧情')
VERIFIED = ['无双', '太奶奶', '盛夏芬德拉', '腹黑女佣', '北王刀', '一品布衣', '噬骨危情', '闪婚老公', '家里家外', '招惹']

EP_RES = [re.compile(r'^第\s*[一二三四五六七八九十百零0-9]+\s*集'), re.compile(r'^EP\s*\d+', re.I),
          re.compile(r'^【?第?\s*\d{1,3}\s*[集话]】?\s*$'), re.compile(r'^\d{1,3}\s*$')]
SCENE_RE = re.compile(r'^\d{1,3}[-–—.、]\d{1,3}[\s、,，]|^场景|^【?\d{1,3}[-–—]\d{1,3}】?\s')
ACTION_RE = re.compile(r'^[▲△]')
META_RE = re.compile(r'^(人物|人|出场人物)\s*[:：]|^(日|夜|晨|黄昏)[\s，,]+(内|外)|^字幕[:：]|^闪回|^插叙|^(时间|地点|气氛)[:：]')
DLG_RE = re.compile(r'^([^：:▲△]{1,14})[:：](.+)$')
MONO_KEYS = ('画外音', 'OS', 'os', 'VO', '内心', '旁白', '心声', '独白', '自语')
NOT_SPEAKER = re.compile(r'人物|地点|时间|场景|备注|标题|大纲|梗概|说明|注意|作者|联系|导演|道具|服装|音乐|音效|镜头|特效|字幕')
EMO_RE = re.compile(r'我(好|很|真|太|特别|非常)(害怕|开心|难过|生气|高兴|伤心|愤怒|痛苦|幸福|绝望|紧张|担心|委屈|后悔|激动|烦|怕|气)')
TONE_END = set('吧呢嘛呀啦哦诶哈咯喽')

def docx_lines(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8', 'ignore')
    return [t for t in (''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p)).strip()
            for p in re.split(r'</w:p>', xml)) if t]

def doc_lines(path):
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tf:
        tmp = tf.name
    try:
        subprocess.run(['textutil', '-convert', 'txt', '-output', tmp, str(path)], check=True, capture_output=True, timeout=60)
        return [l.strip() for l in open(tmp, encoding='utf-8', errors='ignore').read().splitlines() if l.strip()]
    finally:
        os.path.exists(tmp) and os.unlink(tmp)

def is_ep(ln):
    return len(ln) < 16 and any(r.match(ln) for r in EP_RES)

def is_frag(t):
    if t.endswith(('…', '……', '——', '—')): return True
    if not re.search(r'[。！？!?…]$', t):
        return True
    core = re.sub(r'[。！？!?…]+$', '', t)
    return bool(core) and core[-1] in TONE_END

def parse(path):
    lines = docx_lines(path) if path.suffix.lower() == '.docx' else doc_lines(path)
    eps, cur = [], None
    for ln in lines:
        if is_ep(ln):
            cur = []; eps.append(cur); continue
        if cur is None or ACTION_RE.match(ln) or SCENE_RE.match(ln) or META_RE.match(ln):
            continue
        m = DLG_RE.match(ln)
        if m:
            spk, txt = m.group(1).strip(), m.group(2).strip()
            if NOT_SPEAKER.search(spk) or not txt: continue
            mono = any(k in spk for k in MONO_KEYS)
            spk_norm = re.sub(r'（.*?）|\(.*?\)', '', spk).strip()
            cur.append((spk_norm, txt, mono))
    return [e for e in eps if len(e) >= 3]

def metrics(eps):
    ex_per, emo_per, spk_per, samehead_max = [], [], [], []
    open_dlg = 0; end_hook = 0; frag_n = 0; turn_n = 0
    for e in eps:
        ex_per.append(sum(t[1].count('！') + t[1].count('!') for t in e))
        emo_per.append(sum(len(EMO_RE.findall(t[1])) for t in e))
        spk_per.append(len({t[0] for t in e if not t[2]}))
        heads = {}
        for t in e:
            if not t[2]:
                h = t[1][:2]
                heads[h] = heads.get(h, 0) + 1
        samehead_max.append(max(heads.values()) if heads else 0)
        if not e[0][2]: open_dlg += 1
        last = e[-1][1]
        if ('？' in last[-3:]) or last.endswith(('…', '……', '——')): end_hook += 1
        for t in e:
            turn_n += 1
            if is_frag(t[1]): frag_n += 1
    n = len(eps)
    return {
        'eps': n,
        '感叹号/集(中位|p90)': (st.median(ex_per), sorted(ex_per)[int(n*.9)-1]),
        '直述情绪/集(中位|最大)': (st.median(emo_per), max(emo_per)),
        '说话角色数/集(中位|p90)': (st.median(spk_per), sorted(spk_per)[int(n*.9)-1]),
        '同开头2字最大重复/集(中位)': st.median(samehead_max),
        '开场首句=对白%': round(100*open_dlg/n, 1),
        '集末悬念句(？/…结尾)%': round(100*end_hook/n, 1),
        '碎片语率%': round(100*frag_n/turn_n, 1),
    }

allm, hitm = [], []
per_script = {}
for f in sorted(SRC.rglob('*')):
    if not f.is_file() or f.suffix.lower() not in ('.docx', '.doc') or f.name.startswith('.'):
        continue
    try:
        eps = parse(f)
    except Exception:
        continue
    if len(eps) < 5: continue
    m = metrics(eps)
    per_script[f.name[:24]] = m
    allm.append(m)
    if any(v in f.name for v in VERIFIED): hitm.append((f.name[:24], m))

def agg(ms, key, idx=None):
    vals = [(m[key][idx] if idx is not None else m[key]) for m in ms]
    return (min(vals), st.median(vals), max(vals))

print('=== 全语料', len(allm), '部聚合 (min/中位/max) ===')
for key, idx in [('感叹号/集(中位|p90)', 0), ('直述情绪/集(中位|最大)', 0), ('说话角色数/集(中位|p90)', 0),
                 ('同开头2字最大重复/集(中位)', None), ('开场首句=对白%', None), ('集末悬念句(？/…结尾)%', None), ('碎片语率%', None)]:
    print(f'{key}: {agg(allm, key, idx)}')
print()
print('=== 已验证爆款子集 ===')
for name, m in hitm:
    print(name, '|', json.dumps({k: v for k, v in m.items() if k != 'eps'}, ensure_ascii=False))
