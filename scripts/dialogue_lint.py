#!/usr/bin/env python3
"""台词机检门控（dialogue lint）— drama-director G4 第二项检查（format_check 之后）。

硬门控（exit 1）：
  1. 全口径对白占比：对白行 ÷ 全部 spoken lines（分母不剔任何行，Rule 37 v2.3）
     底线 EP01 ≥70%、EP02+ ≥85%；听心声/读心题材 --genre-floor 65
  2. 省略号 >20/千字（台词「」内字符，U+2026 逐字口径，Rule 36f/46c）
  3. 同开头 2 字重复 >2 行（对白行，Rule 13 反 AI 模式）
  4. 相邻 SEG 同为纯独白段（Rule 38d 独白连发禁令）
  5. 同角色跨镜头连续独白 >4 行（Rule 38e：常规 ≤2，豁免连发 ≤4；机检无法
     核验豁免条款，故 3-4 行降为 WARN、>4 行硬失败）

警告（exit 0 但打印，转交 R2 判词腔检测人工复核）：
  - 判词腔 cadence 命中（主角行「短句。短句。」判决模具启发式，Rule 47b）
  - 语义模板黑名单命中（结巴/单字隐忍独白/倒计时句/排比宣言，Rule 36h）
  - 破折号 >2/千字（与 Rule 46c 口径一致：WARN，常由口头禅触发，对声音卡片核实）
  - 感叹号 >10、直述情绪 >1（Rule 36c/d）
  - VALIDATION 自报 dialogue_pct 与复算偏差 >2pp（抓口径游戏）

用法：
  python3 scripts/dialogue_lint.py --ep EP01 --project-root dramas/<剧名>
  python3 scripts/dialogue_lint.py --file dramas/<剧名>/剧本/EP01/EP01_xxx.md
"""
import argparse, glob, os, re, statistics, sys

MONO_KEYS = ("内心", "独白", "自语", "喃喃", "心声", "OS")
# 说话行：**CHAR-xxx**[tag]：「...」 / [待补：desc][tag]：「...」 / 旁白：「...」
LINE_RE = re.compile(
    r'(?:\*\*(?P<char>CHAR[-A-Za-z0-9]+)\*\*|\[待补：(?P<pending>[^\]]+)\]|(?P<narr>旁白))'
    r'\s*(?:\[(?P<tag>[^\]]*)\])?\s*[:：]\s*「(?P<text>[^」]*)」')
EMO_RE = re.compile(r'我(好|很|真|太|特别|非常)(害怕|开心|难过|生气|高兴|伤心|愤怒|痛苦|幸福|绝望|紧张|担心|委屈|后悔|激动|烦|怕|气)')
PUNCT_RE = re.compile(r'[，。！？；：…—、“”"\'「」『』（）()\s]')


def parse_lines(content):
    """返回 [(seg_idx, speaker, kind, text)]，kind ∈ dialogue/mono/narration"""
    segs = re.split(r'^## SEG\d+', content, flags=re.MULTILINE)
    quote_re = re.compile(r'「([^」]*)」')
    rows = []
    for seg_idx, seg_body in enumerate(segs):
        if seg_idx == 0:
            continue  # SEG01 之前的头部（预算表等）不含正式台词行
        # 剔除该段落尾部混入的统计/VALIDATION 区（金句引文不算 spoken line）
        seg_body = re.split(r'^## |<!-- VALIDATION', seg_body, maxsplit=1, flags=re.MULTILINE)[0]
        for phys_line in seg_body.split('\n'):
            matches = list(LINE_RE.finditer(phys_line))
            if not matches:
                continue
            covered = []
            for m in matches:
                speaker = m.group('char') or (m.group('pending') or '').strip() or '旁白'
                tag = m.group('tag') or ''
                text = m.group('text').strip()
                if m.group('narr'):
                    kind = 'narration'
                elif any(k in tag for k in MONO_KEYS):
                    kind = 'mono'
                else:
                    kind = 'dialogue'
                if text:
                    rows.append((seg_idx, speaker, kind, text))
                covered.append((m.start('text'), m.end('text'), speaker, kind))
            # 续引号：同一物理行内未被说话头覆盖的 「...」，归属到其前最近的说话人
            for qm in quote_re.finditer(phys_line):
                if any(s <= qm.start(1) < e for s, e, _, _ in covered):
                    continue
                prev = [c for c in covered if c[1] <= qm.start(1)]
                if prev and qm.group(1).strip():
                    _, _, speaker, kind = prev[-1]
                    rows.append((seg_idx, speaker, kind, qm.group(1).strip()))
    return rows, len(segs) - 1


def verdict_cadence_hit(text):
    """判词腔启发式：≥2 个句读段且每段去标点后 ≤7 字（「不急。坛子不坏。」型）"""
    parts = [p for p in re.split(r'[。！？]', text) if PUNCT_RE.sub('', p)]
    if len(parts) < 2:
        return False
    return all(len(PUNCT_RE.sub('', p)) <= 7 for p in parts)


def semantic_template_hits(rows):
    hits = []
    for seg, spk, kind, text in rows:
        core = PUNCT_RE.sub('', text)
        if re.search(r'(.)、\1', text):
            hits.append((seg, spk, '结巴表怯弱', text))
        if kind == 'mono' and len(core) <= 3:
            hits.append((seg, spk, '单字/双字隐忍独白', text))
        if re.search(r'(等了.{0,4}年|[0-9一二三四五六七八九十百]+年了)', text):
            hits.append((seg, spk, '倒计时深情/仇恨句', text))
        if re.search(r'谁[^，。」]{1,8}[，、]\s*谁', text):
            hits.append((seg, spk, '排比宣言式决心', text))
    return hits


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--ep')
    p.add_argument('--project-root')
    p.add_argument('--file', help='直接指定剧本 md（与 --ep/--project-root 二选一）')
    p.add_argument('--genre-floor', type=float, default=None,
                   help='题材分档占比底线（听心声/读心类传 65）')
    a = p.parse_args()

    if a.file:
        fpath, ep = a.file, (a.ep or re.search(r'(EP\d+)', a.file).group(1))
    else:
        if not (a.ep and a.project_root):
            p.error('需要 --file 或 (--ep + --project-root)')
        ep = a.ep
        cands = sorted(glob.glob(os.path.join(a.project_root, '剧本', ep, f'{ep}*.md')))
        if not cands:
            print(f'❌ 未找到剧本: {a.project_root}/剧本/{ep}/{ep}*.md'); sys.exit(1)
        fpath = cands[0]
    if not os.path.exists(fpath):
        print(f'❌ 文件不存在: {fpath}'); sys.exit(1)

    content = open(fpath, encoding='utf-8').read()
    rows, seg_count = parse_lines(content)
    if not rows:
        print(f'❌ 未解析到任何台词行（说话行格式须为 **CHAR-###**[tag]：「...」）'); sys.exit(1)

    dlg = [r for r in rows if r[2] == 'dialogue']
    mono = [r for r in rows if r[2] == 'mono']
    narr = [r for r in rows if r[2] == 'narration']
    total = len(rows)
    ratio = 100.0 * len(dlg) / total

    floor = a.genre_floor if a.genre_floor is not None else (70.0 if ep.upper() == 'EP01' else 85.0)

    all_text = ''.join(r[3] for r in rows)
    n_chars = len(all_text)
    ellipsis_pk = all_text.count('…') * 1000 / n_chars
    dash_pk = all_text.count('—') * 1000 / n_chars
    bangs = all_text.count('！') + all_text.count('!')
    emo_n = len(EMO_RE.findall(all_text))

    # 同开头 2 字重复（对白行）
    heads = {}
    for _, _, _, t in dlg:
        h = PUNCT_RE.sub('', t)[:2]
        if h:
            heads.setdefault(h, []).append(t)
    head_viol = {h: ts for h, ts in heads.items() if len(ts) > 2}

    # 纯独白 SEG 及相邻性（Rule 38d：2 段相邻且合计 ≤4 行 → WARN 人工核验节拍
    # 合并豁免；≥3 段连发或合计 >4 行 → 硬失败）
    seg_kinds, seg_mono_n = {}, {}
    for seg, _, kind, _ in rows:
        seg_kinds.setdefault(seg, set()).add(kind)
        if kind == 'mono':
            seg_mono_n[seg] = seg_mono_n.get(seg, 0) + 1
    pure_mono_segs = sorted(s for s, ks in seg_kinds.items() if ks == {'mono'})
    mono_chains = []
    for s in pure_mono_segs:
        if mono_chains and mono_chains[-1][-1] == s - 1:
            mono_chains[-1].append(s)
        else:
            mono_chains.append([s])
    adj_fail, adj_warn = [], []
    for chain in mono_chains:
        if len(chain) < 2:
            continue
        n_lines = sum(seg_mono_n.get(s, 0) for s in chain)
        if len(chain) >= 3 or n_lines > 4:
            adj_fail.append((chain, n_lines))
        else:
            adj_warn.append((chain, n_lines))

    # 同角色跨镜头连续独白 run
    runs, cur_spk, cur_n = [], None, 0
    for _, spk, kind, _ in rows:
        if kind == 'mono' and spk == cur_spk:
            cur_n += 1
        elif kind == 'mono':
            if cur_n:
                runs.append((cur_spk, cur_n))
            cur_spk, cur_n = spk, 1
        else:
            if cur_n:
                runs.append((cur_spk, cur_n))
            cur_spk, cur_n = None, 0
    if cur_n:
        runs.append((cur_spk, cur_n))
    run_fail = [r for r in runs if r[1] > 4]
    run_warn = [r for r in runs if 3 <= r[1] <= 4]

    # 主角判词腔（说话行数最多的 CHAR-###）
    by_char = {}
    for _, spk, kind, t in rows:
        if spk.startswith('CHAR'):
            by_char.setdefault(spk, []).append(t)
    protagonist = max(by_char, key=lambda k: len(by_char[k])) if by_char else None
    cadence_hits = [t for t in by_char.get(protagonist, []) if verdict_cadence_hit(t)]

    tpl_hits = semantic_template_hits(rows)

    # VALIDATION 自报对比
    self_pct = None
    m = re.search(r'dialogue_(?:pct|ratio)[:：]\s*[^0-9]*([0-9.]+)\s*%', content)
    if m:
        self_pct = float(m.group(1))
    denom_game = bool(re.search(r'非豁免行|豁免.{0,6}行\s*=\s*\d+\s*行分母|[-−]\s*.{0,8}豁免', content))

    errors, warns = [], []
    if ratio < floor:
        errors.append(f'全口径对白占比 {ratio:.1f}% < 底线 {floor:.0f}%（对白{len(dlg)}/独白{len(mono)}/旁白{len(narr)}，总{total}行）')
    if ellipsis_pk > 20:
        errors.append(f'省略号 {ellipsis_pk:.1f}/千字 > 20（U+2026 逐字口径，Rule 36f）')
    for h, ts in head_viol.items():
        errors.append(f'同开头「{h}」重复 {len(ts)} 行 > 2（Rule 13）')
    for chain, n in adj_fail:
        errors.append(f'纯独白段连发 SEG{chain[0]:02d}-SEG{chain[-1]:02d}（{len(chain)}段/{n}行独白）超 Rule 38d 上限（≥3段或>4行不豁免）')
    for spk, n in run_fail:
        errors.append(f'{spk} 连续独白 {n} 行 > 4（Rule 38e 上限，含豁免放宽）')
    if denom_game:
        errors.append('VALIDATION 疑似剔分母算术（检出"非豁免行/豁免行=分母"字样，Rule 37 v2.3 禁止）')

    for chain, n in adj_warn:
        warns.append(f'相邻纯独白段 SEG{chain[0]:02d}/SEG{chain[-1]:02d}（合计{n}行）——仅"同一发现/推理/开场确认节拍"可合并豁免（Rule 38d），须人工核验')
    for spk, n in run_warn:
        warns.append(f'{spk} 连续独白 {n} 行（>2；仅豁免 b/c 连发可至 4，须人工核验豁免登记）')
    if dash_pk > 2:
        warns.append(f'破折号 {dash_pk:.1f}/千字 > 2（Rule 46c 口径 WARN，对声音卡片口头禅核实）')
    if bangs > 10:
        warns.append(f'感叹号 {bangs} > 10 警戒（Rule 36d）')
    if emo_n > 1:
        warns.append(f'直述情绪 {emo_n} 处 > 1（Rule 36c）')
    if cadence_hits:
        lvl = '⚠️ 超 Rule 47b 上限' if len(cadence_hits) > 3 else '带内'
        warns.append(f'主角 {protagonist} 判词腔 cadence 命中 {len(cadence_hits)} 处（{lvl}，启发式，转 R2 判词腔检测复核）:')
        warns += [f'    「{t}」' for t in cadence_hits]
    for seg, spk, name, t in tpl_hits:
        warns.append(f'语义模板[{name}] SEG{seg:02d} {spk}:「{t}」（Rule 36h，转 R2 复核）')
    if self_pct is not None and abs(self_pct - ratio) > 2:
        warns.append(f'VALIDATION 自报 {self_pct:.1f}% 与复算 {ratio:.1f}% 偏差 >2pp（疑口径游戏，须重做统计表）')

    print(f'📋 台词机检 — {ep}（{os.path.basename(fpath)}）')
    print(f'   spoken lines: {total} = 对白{len(dlg)} + 独白{len(mono)} + 旁白{len(narr)}')
    print(f'   全口径对白占比: {ratio:.1f}%（底线 {floor:.0f}%）｜ 台词字符: {n_chars}')
    print(f'   省略号 {ellipsis_pk:.1f}/千字 ｜ 破折号 {dash_pk:.1f}/千字 ｜ 感叹号 {bangs} ｜ 直述情绪 {emo_n}')
    print(f'   纯独白SEG: {pure_mono_segs or "无"} / 共{seg_count}段 ｜ 主角: {protagonist}')
    for e in errors:
        print(f'❌ {e}')
    for w in warns:
        print(f'⚠️  {w}' if not w.startswith('    ') else w)
    if errors:
        print(f'\n❌ {len(errors)} 个硬门控问题'); sys.exit(1)
    print(f'\n✅ 硬门控通过（{len(warns)} 条 WARN 转 R2 人工复核）'); sys.exit(0)


if __name__ == '__main__':
    main()
