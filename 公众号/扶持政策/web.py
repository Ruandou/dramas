"""Render the local resource library. No fetching or data mutation occurs here."""
import html
import json
import re
from urllib.parse import urlsplit


CATEGORIES = {
    'all': ('全部资源', '从筹备到交付'),
    'policies': ('地方与扶持', '找扶持 · 找落地'),
    'platforms': ('分发平台', '找发行 · 找观众'),
    'models': ('模型', '找生成能力'),
    'tools': ('制作工具', '把作品做完'),
}


def esc(value):
    return html.escape('' if value is None else str(value), quote=True)


def safe_url(value):
    """Allow only explicit HTTP(S) URLs, without credentials or control chars."""
    if not isinstance(value, str) or re.search(r'[\x00-\x20\x7f\\]', value):
        return None
    if not re.match(r'^https?://', value, re.IGNORECASE):
        return None
    try:
        parsed = urlsplit(value)
        if not parsed.hostname or parsed.username is not None or parsed.password is not None:
            return None
        _ = parsed.port  # Reject malformed ports, too.
    except ValueError:
        return None
    return value


def embedded_json(doc):
    """JSON script content must not be able to close its containing element."""
    return (json.dumps(doc, ensure_ascii=False, allow_nan=False)
            .replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
            .replace('\u2028', '\\u2028').replace('\u2029', '\\u2029'))


def source_fallback(records):
    items = []
    for record in records:
        sources = []
        for source in record.get('sources', []):
            label = esc(source.get('label') or source.get('id') or '原始来源')
            url = safe_url(source.get('url'))
            link = (f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{label}</a>'
                    if url else f'{label}（无安全可用链接）')
            sources.append(f'<li>{link} · 来源等级 {esc(source.get("grade", "未知"))}</li>')
        items.append(f'<details><summary>{esc(record.get("title", "未命名条目"))}</summary>'
                     f'<p>原文截至：{esc(record.get("reported_as_of") or "未提供")}；'
                     f'最近核验：{esc(record.get("last_verified_at") or "未核验")}。来源等级不代表核验状态。</p>'
                     f'<ul>{"".join(sources) or "<li>未附来源</li>"}</ul></details>')
    return ''.join(items) or '<p>资料尚未收录。可先查看扶持台账。</p>'


def render(doc):
    """Return a complete HTML document with local CSS/JS and inert embedded data."""
    title = esc(doc.get('title') or '短剧资料库')
    nav = ''.join(
        f'<a class="category-link" data-category="{key}" href="?category={key}">'
        f'<span>{name}</span><small>{hint}</small><span class="category-arrow" aria-hidden="true">↗</span></a>'
        for key, (name, hint) in CATEGORIES.items()
    )
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <meta name="description" content="查找短剧扶持、分发平台、模型与制作工具；逐字段查看来源和核验状态。">
  <title>{title} · 一人短剧厂牌</title>
  <link rel="stylesheet" href="/catalog.css">
  <script src="/catalog.js" defer></script>
</head>
<body>
  <a class="skip-link" href="#directory">跳到资源目录</a>
  <div class="page-shell">
    <header class="masthead">
      <a class="brand" href="/" aria-label="一人短剧厂牌，资料库首页"><span class="brand-mark" aria-hidden="true">剧</span><span>一人短剧厂牌<small>短剧资料库</small></span></a>
      <nav class="header-links" aria-label="快捷导航"><a href="/policies.html">扶持台账 <span aria-hidden="true">↗</span></a><a href="#reading-guide">查阅说明</a></nav>
    </header>
    <main>
      <section class="hero" aria-labelledby="page-title">
        <div><p class="eyebrow">短剧制作 / 资源索引</p><h1 id="page-title">做短剧，<br>先把信息查明白。</h1></div>
        <div class="hero-note"><p>去哪里申请，在哪里分发，<br>用什么生成，怎样完成制作。</p><p class="muted">先找入口，再看条件。每一条信息，<br class="desktop-break">都保留回到原始出处的路。</p><p class="edition">原文汇编截至 <span>{esc(doc.get('reported_as_of') or '未提供')}</span><br><span class="muted">不是今日核验结论</span></p></div>
      </section>
      <div class="library-layout">
        <aside class="category-rail"><p class="rail-label">资源目录</p><nav aria-label="资源分类">{nav}</nav><p class="rail-note">收录 ≠ 推荐<br>来源等级 ≠ 已核验</p><a class="rail-policy" href="/policies.html">打开扶持台账 ↗</a></aside>
        <section class="directory" id="directory" tabindex="-1" aria-labelledby="directory-title">
          <div class="directory-heading"><div><p class="eyebrow" id="category-kicker">资源索引</p><h2 id="directory-title">全部资源</h2></div><a class="text-link" href="#collection-notes">汇编附注 ↓</a></div>
          <form id="filters" role="search" aria-label="筛选资料库">
            <label class="search-label" for="search">搜索名称、地区、能力或条件</label>
            <div class="search-box"><span aria-hidden="true">⌕</span><input type="search" id="search" name="q" placeholder="试试：杭州 扶持 / 视频 开源" autocomplete="off" aria-describedby="search-help"><button type="submit">查找</button></div>
            <p class="filter-help" id="search-help">空格分隔多个关键词，结果需同时包含全部关键词。</p>
            <div class="filter-grid">
              <label id="group-control" hidden>分组<select id="group" name="group"><option value="">全部分组</option></select></label>
              <label>来源等级<select id="grade" name="grade"><option value="">全部等级</option><option value="A">含 A 级来源</option><option value="B">含 B 级来源</option><option value="C">含 C 级来源</option><option value="unknown">未标等级</option></select></label>
              <label>核验状态<select id="verification" name="verification"><option value="">全部状态</option><option value="unverified">未核验</option><option value="partial">仅部分字段有核验</option><option value="verified">有条目核验记录</option></select></label>
              <label id="access-control">接入方式<select id="access" name="access"><option value="">全部方式</option><option value="public">公开入口</option><option value="invitation">定向邀约</option><option value="business">商务对接</option><option value="unknown">待确认</option><option value="not_applicable">不适用</option></select></label>
              <label id="api-control" hidden>API / 开源<select id="api" name="api"><option value="">全部接入情况</option><option value="available">明确支持 / 开源</option><option value="api">明确支持 API</option><option value="open">明确开源</option><option value="other">未明确支持</option></select></label>
              <label id="environment-control" hidden>运行环境<select id="environment" name="environment"><option value="">全部环境</option></select></label>
              <label id="lifecycle-control" hidden>收录状态<select id="lifecycle" name="lifecycle"><option value="">含历史记录</option><option value="listed">在列</option><option value="historical">历史记录</option><option value="unknown">待确认</option></select></label>
            </div>
            <div class="results-bar"><p id="result-count" role="status" aria-live="polite">正在读取本地资料…</p><button type="button" id="reset" class="reset-button">重置筛选</button></div>
          </form>
          <div id="deep-link-notice"></div>
          <details class="deadline-panel" id="deadline-panel"><summary><span>日期提醒</span><span id="deadline-count" class="muted"></span></summary><div class="deadline-body"><p id="deadline-context" class="filter-help"></p><ul id="deadline-list"></ul><p id="deadline-unknown" class="filter-help"></p></div></details>
          <div id="record-list"></div>
          <section class="collection-notes" id="collection-notes" aria-labelledby="notes-title"><h2 id="notes-title">汇编附注</h2><p class="muted">保留原始汇编中的文字背景，不是已核验结论或推荐。表内信息请在上方条目中逐项查证。</p><div id="document-notes"></div></section>
        </section>
      </div>
      <section id="reading-guide" class="reading-guide" aria-labelledby="guide-title"><h2 id="guide-title">信息有出处，使用有边界。</h2><div class="guide-columns"><div><h3>先看接入条件</h3><p>公开入口不等于人人可申；定向邀约不属于公开申报。无日期表示时间待确认，不表示滚动开放。签约期、激励期与政策有效期也不是申报期。</p></div><div><h3>再看证据与时间</h3><p>A / B / C 是汇编标注的来源等级，不是核验结果。原文截至、首次导入、内容变更、最近核验分别记录；导入不会自动变成核验。</p></div><div><h3>最后回到原文</h3><p>模型的在列状态不保证当前可用，历史记录会明确标注。价格、地区、资格与接入方式，以来源页面的最新说明为准。</p></div></div><details class="maintenance-panel"><summary>维护与变更记录</summary><div id="maintenance"></div><div id="change-list"></div></details></section>
      <noscript><section class="noscript-panel"><h2>静态来源目录</h2><p>当前未启用 JavaScript，无法使用筛选与实时日期提醒。下方可查原始来源，或进入 <a href="/policies.html">扶持台账</a>。导入资料不等于核验。</p>{source_fallback(doc.get('records', []))}</section></noscript>
    </main>
    <footer><span>一人短剧厂牌 / 短剧资料库</span><span>找资源，也留证据。</span><a href="#page-title">回到页首 ↑</a></footer>
  </div>
  <script type="application/json" id="catalog-data">{embedded_json(doc)}</script>
</body>
</html>'''
