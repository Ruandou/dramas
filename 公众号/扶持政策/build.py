#!/usr/bin/env python3
"""生成微短剧扶持台账静态页。用法：python3 build.py [--output dist]"""
import argparse
import html
import shutil
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'policy.yaml'

TYPE_LABEL = {'gov': '政府', 'platform': '平台'}
FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' fill='%23f3eee4'/%3E"
    "%3Crect x='6' y='6' width='7' height='20' fill='%23ae422c'/%3E%3C/svg%3E")
HEADERS = '''/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
'''
IND_LABEL = {
    'yes': ('个人可申', 'yes'),
    'partial': ('部分可申', 'partial'),
    'entity': ('需主体', 'entity'),
    'no': ('个人不可', 'no'),
}
IND_FILTER = {'yes', 'partial'}


def load():
    with DATA.open(encoding='utf-8') as f:
        doc = yaml.safe_load(f)
    doc['updated'] = str(doc['updated'])
    for item in doc['items'] + doc.get('closed', []):
        if item.get('deadline') is not None:
            item['deadline'] = str(item['deadline'])
        if 'individual' in item:
            item['individual'] = {True: 'yes', False: 'no'}.get(
                item['individual'], str(item['individual']))
    return doc


def days_left(updated, deadline):
    if not deadline:
        return None
    return (date.fromisoformat(deadline) - date.fromisoformat(updated)).days


def sort_items(items):
    dated = sorted([i for i in items if i['deadline']], key=lambda i: i['deadline'])
    rolling = [i for i in items if not i['deadline']]
    return dated + rolling


def esc(s):
    return html.escape(str(s), quote=True)


def badge_individual(value):
    label, cls = IND_LABEL[value]
    return f'<span class="badge badge--{cls}">{label}</span>'


def render_card(item, updated):
    left = days_left(updated, item['deadline'])
    if item['deadline']:
        dl = item['deadline'][5:].replace('-', '-')
        dday = f'剩 {left} 天' if left is not None and left >= 0 else '已截止'
        date_html = f'<dd class="date">{dl}<span class="countdown">{dday}</span></dd>'
    else:
        date_html = '<dd class="date">滚动<span class="countdown">按公告</span></dd>'

    note = item.get('individual_note', '')
    return f'''
    <article class="card card--{item['type']}" data-type="{item['type']}" data-individual="{item['individual']}">
      <div class="card__bar"></div>
      <div class="card__body">
        <div class="card__top">
          <span class="issuer">{esc(item['issuer'])}</span>
          <span class="badge badge--type">{TYPE_LABEL[item['type']]}</span>
          {badge_individual(item['individual'])}
          <span class="region">{esc(item['region'])}</span>
        </div>
        <h2 class="card__title">{esc(item['title'])}</h2>
        <p class="benefit">{esc(item['benefit'])}</p>
        <dl class="meta">
          <div><dt>谁能申</dt><dd>{esc(item['eligibility'])}</dd></div>
          <div><dt>截止</dt>{date_html}</div>
          <div><dt>入口</dt><dd>{esc(item['entry'])}</dd></div>
        </dl>
        <div class="card__foot">
          <span class="ev ev--{item['evidence'].lower()}">证据 {item['evidence']}</span>
          <span class="hint">{esc(note)}</span>
          <a href="{esc(item['url'])}" target="_blank" rel="noopener">原文</a>
        </div>
      </div>
    </article>'''


def render_closed(item):
    return f'''
      <li>
        <span class="closed-issuer">{esc(item['issuer'])}</span>
        <span class="closed-title">{esc(item['title'])}</span>
        <span class="closed-date">{esc(item['deadline'][5:])}</span>
        <span class="closed-note">{esc(item['note'])}</span>
        <a href="{esc(item['url'])}" target="_blank" rel="noopener">原文</a>
      </li>'''


def build(doc):
    updated = doc['updated']
    items = sort_items(doc['items'])
    closed = doc.get('closed', [])
    gov = sum(1 for i in items if i['type'] == 'gov')
    plat = sum(1 for i in items if i['type'] == 'platform')
    personal = sum(1 for i in items if i['individual'] == 'yes')
    partial = sum(1 for i in items if i['individual'] == 'partial')
    personal_total = personal + partial

    cards = ''.join(render_card(i, updated) for i in items)
    closed_rows = ''.join(render_closed(i) for i in closed)

    page = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(doc['title'])} · 一人短剧厂牌</title>
<meta name="description" content="{esc(doc['subtitle'])}">
<link rel="icon" href="{FAVICON}">
<style>
  :root {{
    --paper:#f3eee4; --white:#fffaf0; --ink:#2c2925; --dim:#756d61;
    --line:#d4c9b8; --rust:#ae422c; --teal:#28695e; --gold:#b9853d; --grey:#8f8576;
    --mono:"SF Mono",Menlo,Consolas,monospace;
    --serif:"Songti SC","Noto Serif SC","Source Han Serif SC",serif;
    --sans:"PingFang SC","Hiragino Sans GB","Noto Sans SC",system-ui,sans-serif;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--paper); color:var(--ink); font-family:var(--sans);
         -webkit-font-smoothing:antialiased; line-height:1.65; }}
  .wrap {{ max-width:1080px; margin:0 auto; padding:0 24px 80px; }}
  header {{ padding:44px 0 8px; }}
  .brand {{ display:flex; align-items:center; gap:10px; font-size:13px; color:var(--dim);
            letter-spacing:.08em; }}
  .brand::before {{ content:""; width:11px; height:22px; background:var(--rust); display:block; }}
  h1 {{ font-family:var(--serif); font-size:52px; line-height:1.15; margin:22px 0 10px;
        letter-spacing:.01em; font-weight:700; }}
  .sub {{ font-size:17px; color:var(--dim); max-width:640px; margin:0 0 8px; }}
  .stamp {{ font-family:var(--mono); font-size:12px; color:var(--grey); letter-spacing:.04em; }}

  .stats {{ display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:var(--line);
           border:1px solid var(--line); border-radius:12px; overflow:hidden; margin:30px 0 8px; }}
  .stat {{ background:var(--white); padding:18px 20px; }}
  .stat b {{ display:block; font-family:var(--mono); font-size:32px; line-height:1.1; font-weight:600; }}
  .stat span {{ font-size:12px; color:var(--dim); letter-spacing:.06em; }}
  .stat--rust b {{ color:var(--rust); }} .stat--teal b {{ color:var(--teal); }}
  .stat--gold b {{ color:var(--gold); }}

  .rail {{ margin:26px 0 6px; border-top:2px solid var(--line); padding-top:0; }}
  .rail__row {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }}
  .stop {{ padding:14px 0 0; position:relative; }}
  .stop::before {{ content:""; position:absolute; top:-7px; left:0; width:12px; height:12px;
                   border-radius:50%; background:var(--paper); border:3px solid var(--grey); }}
  .stop--now::before {{ border-color:var(--rust); }}
  .stop--end::before {{ border-color:var(--gold); }}
  .stop time {{ font-family:var(--mono); font-size:15px; font-weight:600; }}
  .stop p {{ margin:2px 0 0; font-size:13px; color:var(--dim); }}

  .filters {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center;
             margin:26px 0 18px; padding-top:18px; border-top:1px solid var(--line); }}
  .filters button {{ font:inherit; font-size:13px; padding:7px 15px; border-radius:999px;
                    border:1px solid var(--line); background:transparent; color:var(--dim);
                    cursor:pointer; transition:.15s; }}
  .filters button:hover {{ border-color:var(--dim); color:var(--ink); }}
  .filters button[aria-pressed="true"] {{ background:var(--ink); border-color:var(--ink);
                                        color:var(--paper); }}
  .filters .count {{ margin-left:auto; font-family:var(--mono); font-size:12px; color:var(--grey); }}

  .card {{ display:flex; background:var(--white); border:1px solid var(--line); border-radius:14px;
           overflow:hidden; margin-bottom:14px; }}
  .card[hidden] {{ display:none; }}
  .card__bar {{ width:4px; flex:none; background:var(--rust); }}
  .card--platform .card__bar {{ background:var(--teal); }}
  .card__body {{ padding:20px 24px 16px; flex:1; min-width:0; }}
  .card__top {{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; }}
  .issuer {{ font-size:13px; font-weight:600; letter-spacing:.04em; }}
  .region {{ margin-left:auto; font-family:var(--mono); font-size:11px; color:var(--grey); }}
  .badge {{ font-size:11px; padding:2px 8px; border-radius:999px; letter-spacing:.04em; }}
  .badge--type {{ background:rgba(174,66,44,.09); color:var(--rust); }}
  .card--platform .badge--type {{ background:rgba(40,105,94,.1); color:var(--teal); }}
  .badge--yes {{ background:rgba(40,105,94,.12); color:var(--teal); font-weight:600; }}
  .badge--partial {{ background:rgba(185,133,61,.14); color:#8a5f22; font-weight:600; }}
  .badge--entity {{ background:rgba(117,109,97,.12); color:var(--dim); }}
  .badge--no {{ background:rgba(174,66,44,.1); color:#8b3a29; }}
  .card__title {{ font-family:var(--serif); font-size:25px; line-height:1.3; margin:10px 0 6px;
                 font-weight:700; }}
  .benefit {{ margin:0 0 16px; font-size:15px; color:#4a443c; }}
  .meta {{ display:grid; grid-template-columns:1.4fr .7fr 1.2fr; gap:14px; margin:0;
           padding-top:14px; border-top:1px dashed var(--line); }}
  .meta div {{ min-width:0; }}
  .meta dt {{ font-size:11px; color:var(--grey); letter-spacing:.1em; margin-bottom:2px; }}
  .meta dd {{ margin:0; font-size:13px; }}
  .date {{ font-family:var(--mono); font-size:16px; font-weight:600; }}
  .countdown {{ display:block; font-family:var(--sans); font-size:11px; color:var(--rust);
                font-weight:400; margin-top:1px; }}
  .card__foot {{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-top:14px;
                font-size:11px; color:var(--grey); }}
  .ev {{ font-family:var(--mono); padding:1px 6px; border:1px solid var(--line); border-radius:4px; }}
  .ev--a {{ color:var(--teal); border-color:rgba(40,105,94,.35); }}
  .ev--b {{ color:var(--gold); border-color:rgba(185,133,61,.4); }}
  .card__foot .hint {{ flex:1; min-width:180px; }}
  .card__foot a {{ color:var(--rust); text-decoration:none; border-bottom:1px solid rgba(174,66,44,.3); }}

  .closed {{ margin:34px 0 0; }}
  .closed summary {{ cursor:pointer; font-size:14px; color:var(--dim); padding:14px 0;
                    border-top:1px solid var(--line); list-style:none; }}
  .closed summary::-webkit-details-marker {{ display:none; }}
  .closed summary::before {{ content:"＋"; margin-right:8px; color:var(--grey); }}
  .closed[open] summary::before {{ content:"－"; }}
  .closed ul {{ list-style:none; margin:0; padding:0; }}
  .closed li {{ display:grid; grid-template-columns:110px 1fr 60px 1.6fr 40px; gap:12px;
               align-items:baseline; padding:10px 0; border-bottom:1px solid var(--line);
               font-size:13px; color:var(--dim); }}
  .closed-title {{ color:var(--ink); }}
  .closed-date {{ font-family:var(--mono); color:var(--rust); }}
  .closed-note {{ font-size:12px; }}
  .closed a {{ color:var(--grey); text-decoration:none; font-size:12px; }}

  .how {{ margin:44px 0 0; padding:22px 24px; background:var(--ink); color:#bdb3a1;
          border-radius:14px; }}
  .how h3 {{ margin:0 0 10px; color:#f0c588; font-size:15px; letter-spacing:.06em; }}
  .how ol {{ margin:0; padding-left:18px; font-size:13px; line-height:1.9; }}
  .how b {{ color:#efe6d6; font-weight:600; }}

  footer {{ margin-top:34px; padding-top:18px; border-top:1px solid var(--line);
            font-size:12px; color:var(--grey); line-height:1.9; }}
  footer b {{ color:var(--dim); font-weight:600; }}

  @media (max-width:720px) {{
    .wrap {{ padding:0 18px 60px; }}
    h1 {{ font-size:34px; }}
    .sub {{ font-size:15px; }}
    .stats {{ grid-template-columns:repeat(2,1fr); }}
    .stat b {{ font-size:26px; }}
    .meta {{ grid-template-columns:1fr 1fr; }}
    .meta div:last-child {{ grid-column:1 / -1; }}
    .card__body {{ padding:16px 16px 14px; }}
    .card__title {{ font-size:21px; }}
    .closed li {{ grid-template-columns:1fr 1fr; }}
    .closed-note {{ grid-column:1 / -1; }}
    .rail__row {{ display:block; }}
    .stop {{ padding:10px 0 10px 26px; border-left:2px solid var(--line); margin-left:5px; }}
    .stop:last-child {{ grid-column:auto; }}
    .stop::before {{ top:16px; left:-8px; }}
    .stop p {{ margin:1px 0 0; }}
  }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="brand">一人短剧厂牌 · 台账</div>
    <h1>{esc(doc['title'])}</h1>
    <p class="sub">{esc(doc['subtitle'])}</p>
    <p class="stamp">更新于 {esc(updated)} ｜ {len(items)} 个还开着 ｜ {len(closed)} 个已关闭</p>
  </header>

  <section class="stats" aria-label="统计">
    <div class="stat stat--rust"><b>{gov + plat}</b><span>还开着的口子</span></div>
    <div class="stat"><b>{gov}</b><span>政府扶持</span></div>
    <div class="stat stat--teal"><b>{plat}</b><span>平台扶持</span></div>
    <div class="stat stat--gold"><b>{personal_total}</b><span>个人可申</span></div>
  </section>

  <section class="rail" aria-label="近期窗口">
    <div class="rail__row">
      <div class="stop"><time>11-01</time><p>公众号小说改编签约开窗</p></div>
      <div class="stop stop--now"><time>11-18</time><p>上海专项申报截止</p></div>
      <div class="stop stop--end"><time>12-31</time><p>微信 Q4 激励与小说签约截止</p></div>
    </div>
  </section>

  <div class="filters" role="group" aria-label="筛选">
    <button data-filter="all" aria-pressed="true">全部</button>
    <button data-filter="gov" aria-pressed="false">政府</button>
    <button data-filter="platform" aria-pressed="false">平台</button>
    <button data-filter="personal" aria-pressed="false">个人可申（{personal_total}）</button>
    <span class="count" id="count">共 {len(items)} 条</span>
  </div>

  <main id="list">
    {cards}
  </main>

  <details class="closed">
    <summary>已关闭 {len(closed)} 条（留档，别当机会）</summary>
    <ul>{closed_rows}
    </ul>
  </details>

  <section class="how">
    <h3>拿到任何一条政策，先看四行</h3>
    <ol>
      <li><b>申报主体</b>：个人、个体户、企业、机构，四者不通用。</li>
      <li><b>完成时间区间</b>：补过去一年的成片，还是给未来项目。</li>
      <li><b>备案与上线</b>：要不要备案号、要不要上线证明。</li>
      <li><b>奖励还是补贴</b>：奖励是先干成再给，补贴是先投入后报。</li>
    </ol>
  </section>

  <footer>
    <p><b>口径</b>：只收还能申报或参与的条目；「最高」均为评审上限，不等于到手金额。证据 A 为政府或平台原文，B 为主流媒体转述，C 为二手汇总仅作线索。</p>
    <p><b>时效</b>：政策随时调整，申报以官方最新公告为准。台账下次更新随公众号发文同步。</p>
    <p><b>说明</b>：本页不构成申报建议或法律意见。数据源文件 policy.yaml，本页由 build.py 生成。</p>
  </footer>
</div>
<script>
  const buttons = document.querySelectorAll('.filters button');
  const cards = Array.from(document.querySelectorAll('#list .card'));
  const count = document.getElementById('count');
  function apply(filter) {{
    let shown = 0;
    cards.forEach(card => {{
      const type = card.dataset.type;
      const ind = card.dataset.individual;
      const ok = filter === 'all' || type === filter ||
                 (filter === 'personal' && (ind === 'yes' || ind === 'partial'));
      card.hidden = !ok;
      if (ok) shown++;
    }});
    count.textContent = '共 ' + shown + ' 条';
  }}
  buttons.forEach(btn => btn.addEventListener('click', () => {{
    buttons.forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
    apply(btn.dataset.filter);
  }}));
</script>
</body>
</html>
'''

    return {'index.html': page, '404.html': render_404(), '_headers': HEADERS}


def render_404():
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>页面不存在 · 一人短剧厂牌</title>
<meta name="robots" content="noindex">
<link rel="icon" href="{FAVICON}">
<style>
  :root {{ --paper:#f3eee4; --paper2:#fffaf0; --ink:#2c2925; --dim:#756d61; --rust:#ae422c;
          --serif:"Songti SC","Noto Serif SC","Source Han Serif SC",serif;
          --sans:"PingFang SC","Hiragino Sans GB","Noto Sans SC",system-ui,sans-serif; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; min-height:100vh; display:flex; align-items:center; background:var(--paper);
         color:var(--ink); font-family:var(--sans); -webkit-font-smoothing:antialiased; }}
  .wrap {{ max-width:720px; margin:0 auto; padding:40px 24px; width:100%; }}
  .brand {{ display:flex; align-items:center; gap:10px; font-size:13px; color:var(--dim);
            letter-spacing:.08em; }}
  .brand::before {{ content:""; width:11px; height:22px; background:var(--rust); display:block; }}
  .code {{ font-family:var(--serif); font-size:112px; line-height:1; margin:34px 0 0;
           color:var(--rust); letter-spacing:.02em; }}
  h1 {{ font-family:var(--serif); font-size:30px; line-height:1.3; margin:16px 0 8px; }}
  p {{ color:var(--dim); font-size:15px; margin:0 0 28px; }}
  a {{ display:inline-block; padding:10px 22px; border:1px solid var(--ink); border-radius:999px;
       color:var(--ink); text-decoration:none; font-size:14px; }}
  a:hover {{ background:var(--ink); color:var(--paper2); }}
</style>
</head>
<body>
<div class="wrap">
  <div class="brand">一人短剧厂牌 · 台账</div>
  <p class="code">404</p>
  <h1>这条不在台账里</h1>
  <p>可能已经关闭，也可能链接打错了。还开着的口子都在首页。</p>
  <a href="/">回台账首页</a>
</div>
</body>
</html>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', default=str(ROOT / 'dist'))
    ap.add_argument('--check', action='store_true', help='只校验产物与数据是否一致，不写盘')
    args = ap.parse_args()
    out_dir = Path(args.output)
    files = build(load())
    if args.check:
        stale = [name for name, content in files.items()
                 if not (out_dir / name).exists()
                 or (out_dir / name).read_text(encoding='utf-8') != content]
        if stale:
            print('产物过期：' + '、'.join(stale) + '（跑 python3 build.py 重建）')
            raise SystemExit(1)
        print(f'产物与数据一致：{len(files)} 个文件')
        return
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    for name, content in files.items():
        (out_dir / name).write_text(content, encoding='utf-8')
        print(name, f'{len(content.encode()) / 1024:.1f} KB')
    print(f"打开：open '{out_dir / 'index.html'}'")


if __name__ == '__main__':
    main()
