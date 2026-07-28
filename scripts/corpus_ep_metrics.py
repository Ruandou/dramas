#!/usr/bin/env python3
# 爆款剧本批量量化分析器（一次性分析工具）
import zipfile, re, sys, json, statistics as st
from pathlib import Path

SRC = Path('/Users/lei/Downloads/完本剧情')

def docx_lines(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8', 'ignore')
    out = []
    for p in re.split(r'</w:p>', xml):
        t = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p)).strip()
        if t:
            out.append(t)
    return out

EP_RE = re.compile(r'^第\s*[一二三四五六七八九十百零0-9]+\s*集|^EP\s*\d+|^\d{1,3}\s*[集话]\s*$')
SCENE_RE = re.compile(r'^\d{1,3}[-–—.、]\d{1,3}[\s、,，]|^场景|^【?\d{1,3}[-–—]\d{1,3}】?\s')
ACTION_RE = re.compile(r'^[▲△]')
META_RE = re.compile(r'^(人物|人)\s*[:：]|^(日|夜|晨|黄昏)\s+(内|外)|^字幕[:：]|^闪回|^插叙|^\d+\s*$')
DLG_RE = re.compile(r'^([^：:▲△]{1,14})[:：](.+)$')
MONO_KEYS = ('画外音', 'OS', 'os', 'VO', '内心', '旁白', '心声', '独白', '自语')

def is_mono(speaker):
    return any(k in speaker for k in MONO_KEYS)

def sentences(text):
    parts = re.split(r'[。！？!?…]+', text)
    return [p for p in (x.strip() for x in parts) if p]

def analyze(path):
    lines = docx_lines(path)
    eps = []  # list of dicts
    cur = None
    for ln in lines:
        if EP_RE.match(ln) and len(ln) < 15:
            cur = {'turns': [], 'action': 0}
            eps.append(cur)
            continue
        if cur is None:
            continue
        if ACTION_RE.match(ln):
            cur['action'] += 1
            continue
        if SCENE_RE.match(ln) or META_RE.match(ln):
            continue
        m = DLG_RE.match(ln)
        if m:
            spk, txt = m.group(1).strip(), m.group(2).strip()
            if len(txt) < 1 or META_RE.match(ln):
                continue
            cur['turns'].append((spk, txt, is_mono(spk)))
    eps = [e for e in eps if len(e['turns']) >= 3]
    if not eps:
        return None
    turns_per_ep = [len(e['turns']) for e in eps]
    all_turns = [t for e in eps for t in e['turns']]
    mono = sum(1 for t in all_turns if t[2])
    turn_chars = [len(t[1]) for t in all_turns]
    turn_sents = [len(sentences(t[1])) or 1 for t in all_turns]
    sent_chars = [len(s) for t in all_turns for s in sentences(t[1])]
    action_per_ep = [e['action'] for e in eps]
    return {
        'episodes': len(eps),
        'turns_total': len(all_turns),
        'turns_per_ep_med': st.median(turns_per_ep),
        'turns_per_ep_p10_p90': (sorted(turns_per_ep)[int(len(turns_per_ep)*.1)], sorted(turns_per_ep)[int(len(turns_per_ep)*.9)-1]),
        'dialogue_pct': round(100*(1 - mono/len(all_turns)), 1),
        'mono_pct': round(100*mono/len(all_turns), 1),
        'chars_per_turn_med': st.median(turn_chars),
        'sents_per_turn_med': st.median(turn_sents),
        'sents_per_turn_p90': sorted(turn_sents)[int(len(turn_sents)*.9)-1],
        'chars_per_sent_med': st.median(sent_chars),
        'chars_per_sent_p90': sorted(sent_chars)[int(len(sent_chars)*.9)-1],
        'action_per_ep_med': st.median(action_per_ep),
    }

if __name__ == '__main__':
    files = sys.argv[1:]
    results = {}
    for f in files:
        p = SRC / f
        try:
            r = analyze(p)
            results[f] = r or 'PARSE_FAIL(集标记未识别或格式不同)'
        except Exception as e:
            results[f] = f'ERROR: {e}'
    print(json.dumps(results, ensure_ascii=False, indent=1))
