#!/usr/bin/env python3
# 爆款成片切镜节奏拉片（机械 ASL 实测）——ffmpeg scene detection
# 用途：为 scene-writer 单镜时长带 / episode_profile 镜头数校准提供成片实测锚
# 语料：/Users/lei/Downloads/【短剧剧本+课程合集】/短剧资源（4 部爆款逐集成片）
# 用法：
#   python3 scripts/corpus_cut_rhythm.py            # 抽样模式（每剧 10 集）
#   python3 scripts/corpus_cut_rhythm.py --full     # 全量模式（断点续跑，结果落盘 JSON）
#   python3 scripts/corpus_cut_rhythm.py --report   # 只从 JSON 汇总报告，不跑检测
import subprocess, re, sys, json, statistics as st
from pathlib import Path

BASE = Path('/Users/lei/Downloads/【短剧剧本+课程合集】/短剧资源')
THRESH = 0.3          # 校准结论：0.3 为硬切保守阈值（家里家外 EP10: ASL 3.0s）
SAMPLE_PER_DRAMA = 10  # 抽样模式每剧集数
CKPT = Path(__file__).parent / 'corpus_cut_rhythm_results.json'
HOOK_SEC = 15.0        # 开场钩子区长度（与三区结构 hook_sec 对齐）

def probe_duration(f):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                          '-of', 'csv=p=0', str(f)], capture_output=True, text=True)
    try: return float(out.stdout.strip())
    except ValueError: return None

def cut_times(f):
    out = subprocess.run(['ffmpeg', '-i', str(f), '-vf',
                          f"select='gt(scene,{THRESH})',metadata=print", '-an', '-f', 'null', '-'],
                         capture_output=True, text=True)
    return [float(m) for m in re.findall(r'pts_time:([\d.]+)', out.stderr)]

def ep_num(p):
    m = re.search(r'(\d+)', p.stem)
    return int(m.group(1)) if m else 0

def main():
    full = '--full' in sys.argv
    report_only = '--report' in sys.argv
    ckpt = json.loads(CKPT.read_text()) if CKPT.exists() else {}

    if not report_only:
        dramas = sorted(d for d in BASE.iterdir() if d.is_dir())
        for d in dramas:
            eps = sorted(d.glob('*.mp4'), key=ep_num)
            if not eps: continue
            if not full and len(eps) >= 5:
                step = max(1, len(eps) // SAMPLE_PER_DRAMA)
                eps = eps[::step][:SAMPLE_PER_DRAMA]
            for f in eps:
                key = f'{d.name}/{f.name}'
                if key in ckpt: continue
                dur = probe_duration(f)
                if not dur: continue
                if dur > 1200:
                    print(f'⏭ 跳过合集长视频 {key}（{dur:.0f}s）', flush=True); continue
                cuts = cut_times(f)
                ckpt[key] = {'dur': dur, 'cuts': cuts}
                CKPT.write_text(json.dumps(ckpt))
                print(f'✓ {key}: {dur:.0f}s {len(cuts)}切', flush=True)

    # ── 汇总报告 ──
    from collections import defaultdict
    by_drama = defaultdict(list)   # drama -> intervals
    hook_iv, body_iv, all_iv = [], [], []
    per_ep_cuts = defaultdict(list)
    for key, v in ckpt.items():
        drama = key.split('/')[0]
        bounds = [0.0] + v['cuts'] + [v['dur']]
        for a, b in zip(bounds, bounds[1:]):
            iv = b - a
            if iv <= 0.2: continue
            all_iv.append(iv); by_drama[drama].append(iv)
            (hook_iv if a < HOOK_SEC else body_iv).append(iv)
        per_ep_cuts[drama].append(len(v['cuts']))
    if not all_iv:
        print('无数据'); return
    print(f'\n===== 汇总（{len(ckpt)} 集 / {len(all_iv)} 镜） =====')
    def line(tag, s):
        s = sorted(s); n = len(s)
        print(f'{tag:<14s} n={n:5d} 中位 {st.median(s):.1f}s p75 {s[n*3//4]:.1f} p90 {s[n*9//10]:.1f} p95 {s[n*19//20]:.1f} | >8s {sum(1 for x in s if x>8)/n:.1%} >10s {sum(1 for x in s if x>10)/n:.1%}')
    line('全部', all_iv)
    line(f'开场前{HOOK_SEC:.0f}s', hook_iv)
    line('正片', body_iv)
    print()
    for k, v in sorted(by_drama.items()):
        line(k[:12], v)
        c = per_ep_cuts[k]
        print(f'{"":14s} 每集切镜: 中位 {st.median(c):.0f} p25/p75 {sorted(c)[len(c)//4]}/{sorted(c)[len(c)*3//4]}')

if __name__ == '__main__':
    main()
