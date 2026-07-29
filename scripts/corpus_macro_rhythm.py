#!/usr/bin/env python3
# 宏观节奏实测：L1 编剧自标注卡点提取 + L2 全语料逐集曲线
# 用途：story-architect 宏观节奏校准的实证数据（配套 docs/真实爆款台词与节奏数据 §13）
import zipfile, re, json, statistics as st
from pathlib import Path

SRC = Path('/Users/lei/Downloads/完本剧情')
VERIFIED = ['无双', '太奶奶', '盛夏芬德拉', '腹黑女佣', '北王刀', '一品布衣', '噬骨危情', '闪婚老公', '家里家外']

# ---------- 中文数字 ----------
CN = {'零':0,'一':1,'二':2,'两':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,'百':100}
def cn2int(s):
    if s.isdigit(): return int(s)
    total, cur = 0, 0
    for ch in s:
        v = CN.get(ch)
        if v is None: return None
        if v >= 10:
            cur = max(cur, 1) * v
            total += cur
            cur = 0
        else:
            cur = cur * 10 + v if cur >= 10 else v
    return total + cur

def docx_lines(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8', 'ignore')
    return [t for t in (''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p)).strip()
            for p in re.split(r'</w:p>', xml)) if t]

# ---------- L1：编剧自标注 ----------
EP_INLINE = re.compile(r'第\s*([一二三四五六七八九十百零0-9]{1,5})\s*集')
def l1_extract(path):
    """返回 [(ep, 标注类型)]；覆盖两种形态：拆解笔记行内『第X集：…卡点：…』与剧本内【卡点/钩子】标注"""
    lines = docx_lines(path)
    marks, cur_ep = [], None
    for ln in lines:
        m = EP_INLINE.search(ln[:12])
        if m:
            ep = cn2int(m.group(1))
            if ep: cur_ep = ep
        for kind in ('卡点', '钩子'):
            if kind in ln and cur_ep:
                # 行内多次只计一次
                marks.append((cur_ep, kind))
                break
    return marks

# ---------- L2：逐集曲线 ----------
EP_RES = [re.compile(r'^第\s*[一二三四五六七八九十百零0-9]+\s*集'), re.compile(r'^EP\s*\d+', re.I),
          re.compile(r'^【?第?\s*\d{1,3}\s*[集话]】?\s*$'), re.compile(r'^\d{1,3}\s*$')]
SCENE_RE = re.compile(r'^\d{1,3}[-–—.、]\d{1,3}[\s、,，]|^场景|^【?\d{1,3}[-–—]\d{1,3}】?\s')
ACTION_RE = re.compile(r'^[▲△]')
META_RE = re.compile(r'^(人物|人|出场人物)\s*[:：]|^(日|夜|晨|黄昏)[\s，,]+(内|外)|^字幕[:：]|^闪回|^插叙|^(时间|地点|气氛)[:：]')
DLG_RE = re.compile(r'^([^：:▲△]{1,14})[:：](.+)$')
MONO_KEYS = ('画外音', 'OS', 'os', 'VO', '内心', '旁白', '心声', '独白', '自语')
NOT_SPEAKER = re.compile(r'人物|地点|时间|场景|备注|标题|大纲|梗概|说明|注意|作者|联系|导演|道具|服装|音乐|音效|镜头|特效|字幕|卡点|钩子')

def parse_eps(path):
    lines = docx_lines(path)
    eps, cur = [], None
    for ln in lines:
        if len(ln) < 16 and any(r.match(ln) for r in EP_RES):
            cur = []; eps.append(cur); continue
        if cur is None or ACTION_RE.match(ln) or SCENE_RE.match(ln) or META_RE.match(ln):
            continue
        m = DLG_RE.match(ln)
        if m:
            spk, txt = m.group(1).strip(), m.group(2).strip()
            if NOT_SPEAKER.search(spk) or not txt: continue
            spk = re.sub(r'（.*?）|\(.*?\)', '', spk).strip()
            cur.append((spk, txt, any(k in spk for k in MONO_KEYS)))
    return [e for e in eps if len(e) >= 3]

def l2_curves(eps):
    seen = set(); new_chars, intensity, turns = [], [], []
    for e in eps:
        spks = {t[0] for t in e if not t[2]}
        new_chars.append(len(spks - seen)); seen |= spks
        n = len(e)
        exq = sum(t[1].count('！') + t[1].count('!') + t[1].count('？') + t[1].count('?') for t in e)
        intensity.append(exq / n if n else 0)
        turns.append(n)
    return new_chars, intensity, turns

def peaks_spacing(vals, k=0.5):
    """局部峰（高于全剧均值+k*std 且为3邻域极大）→ 峰间隔列表"""
    if len(vals) < 8: return []
    mu, sd = st.mean(vals), (st.pstdev(vals) or 1e-9)
    idx = [i for i in range(1, len(vals)-1)
           if vals[i] >= mu + k*sd and vals[i] >= vals[i-1] and vals[i] >= vals[i+1]]
    return [b - a for a, b in zip(idx, idx[1:])]

if __name__ == '__main__':
    # ===== L1 =====
    print('========== L1 编剧自标注卡点/钩子位置 ==========')
    all_marks = {}
    for f in sorted(SRC.glob('*.docx')):
        try: marks = l1_extract(f)
        except Exception: continue
        if len(marks) >= 3:
            all_marks[f.name[:20]] = marks
    pos_norm = []   # 归一化位置（ep/总集数）
    for name, marks in all_marks.items():
        eps_nums = [m[0] for m in marks]
        total = max(eps_nums)
        if total < 10: continue
        uniq = sorted(set(eps_nums))
        print(f'{name} | 总集~{total} | 标注{len(uniq)}处 | 集位置: {uniq[:20]}{"..." if len(uniq)>20 else ""}')
        # 标注间隔（连续标注集间距）
        gaps = [b-a for a, b in zip(uniq, uniq[1:])]
        if gaps: print(f'   间隔: 中位 {st.median(gaps)}, 分布 {sorted(gaps)[:15]}')
        pos_norm += [e/total for e in uniq]
    if pos_norm:
        deciles = [0]*10
        for p in pos_norm: deciles[min(int(p*10), 9)] += 1
        print('L1 卡点归一化位置十分位分布(前→后):', deciles)

    # ===== L2 =====
    print('\n========== L2 全语料逐集曲线 ==========')
    dec_new = [[] for _ in range(10)]; dec_int = [[] for _ in range(10)]
    spacings_all, spacings_hits = [], []
    n_ok = 0
    for f in sorted(SRC.glob('*.docx')):
        try: eps = parse_eps(f)
        except Exception: continue
        if len(eps) < 20: continue
        n_ok += 1
        new_chars, intensity, turns = l2_curves(eps)
        L = len(eps)
        for i in range(L):
            d = min(int(i/L*10), 9)
            dec_new[d].append(new_chars[i]); dec_int[d].append(intensity[i])
        sp = peaks_spacing(intensity)
        spacings_all += sp
        if any(v in f.name for v in VERIFIED): spacings_hits += sp
    print(f'纳入 {n_ok} 部（≥20集）')
    print('新角色引入/集（十分位均值，验证三阶段）:', [round(st.mean(x), 2) for x in dec_new])
    print('强度代理 感叹+问/块（十分位均值）    :', [round(st.mean(x), 3) for x in dec_int])
    if spacings_all:
        print(f'强度峰间隔（全语料 n={len(spacings_all)}）: 中位 {st.median(spacings_all)}, p25/p75 = '
              f'{sorted(spacings_all)[len(spacings_all)//4]}/{sorted(spacings_all)[len(spacings_all)*3//4]}')
    if spacings_hits:
        print(f'强度峰间隔（已验证爆款 n={len(spacings_hits)}）: 中位 {st.median(spacings_hits)}')
