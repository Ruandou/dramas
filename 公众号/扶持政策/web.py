"""Render the local resource library. No fetching or data mutation occurs here."""
import html
import json
import re
from urllib.parse import urlsplit


FAVICON = '<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 32 32%22%3E%3Crect width=%2232%22 height=%2232%22 rx=%225%22 fill=%22%23112842%22/%3E%3Cpath d=%22M6 7h20v5H6zM13 16l9 5-9 5z%22 fill=%22white%22/%3E%3Cpath d=%22m11 7-3 5m10-5-3 5m10-5-3 5%22 stroke=%22%23112842%22 stroke-width=%222%22/%3E%3C/svg%3E">'


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
    title = esc(doc.get('title') or '短剧资源库')
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <meta name="description" content="查找短剧扶持、分发平台、模型与制作工具；逐字段查看来源和核验状态。">
  <title>{title} · 一人短剧厂牌</title>
  {FAVICON}
  <link rel="stylesheet" href="/catalog.css">
  <script src="/catalog.js" defer></script>
</head>
<body>
  <a class="skip skip-link" href="#main">跳到主要内容</a>
  <svg class="svg-defs" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><defs>
    <symbol id="i-search" viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></symbol>
    <symbol id="i-arrow" viewBox="0 0 24 24"><path d="M5 12h14m-6-6 6 6-6 6"/></symbol>
    <symbol id="i-external" viewBox="0 0 24 24"><path d="M14 4h6v6m0-6L10 14M9 5H4v15h15v-5"/></symbol>
    <symbol id="i-place" viewBox="0 0 24 24"><path d="M5 21V5l7-3 7 3v16M2 21h20M9 8h1m4 0h1M9 12h1m4 0h1M10 21v-5h4v5"/></symbol>
    <symbol id="i-platform" viewBox="0 0 24 24"><rect x="3" y="3" width="12" height="15" rx="2"/><path d="m8 8 4 3-4 3zM18 6h3v15H9"/></symbol>
    <symbol id="i-model" viewBox="0 0 24 24"><path d="m12 2 9 5-9 5-9-5zM3 12l9 5 9-5M3 17l9 5 9-5"/></symbol>
    <symbol id="i-tool" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/><rect x="7" y="3" width="3" height="6" rx="1"/><rect x="14" y="9" width="3" height="6" rx="1"/><rect x="8" y="15" width="3" height="6" rx="1"/></symbol>
    <symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v6l4 2"/></symbol>
    <symbol id="i-close" viewBox="0 0 24 24"><path d="m6 6 12 12M18 6 6 18"/></symbol>
    <symbol id="i-video" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="m10 9 5 3-5 3z"/></symbol>
  </defs></svg>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="?view=home" aria-label="一人短剧厂牌，资源库首页"><span class="brand-symbol" aria-hidden="true"><i></i><i></i><i></i><b></b></span><span>一人短剧厂牌<small>短剧资源库</small></span></a>
      <nav class="main-nav" aria-label="主导航">
        <a href="?view=home" data-nav="home">发现资源</a>
        <a href="?view=policies" data-nav="policies">地方与扶持</a>
        <a href="?view=platforms" data-nav="platforms">分发平台</a>
        <a href="?view=models" data-nav="models">生成模型</a>
        <a href="?view=tools" data-nav="tools">制作工具</a>
      </nav>
      <a class="header-archive" href="/policies.html">扶持台账 <svg class="icon" aria-hidden="true"><use href="#i-external"/></svg></a>
    </div>
  </header>
  <main id="main" class="page" tabindex="-1">
    <section id="load-error" class="load-error" role="alert" hidden>
      <h1>资料暂时未能加载</h1><p>请重新加载页面；也可以先查看扶持台账中的来源与条件。</p><a class="text-link" href="/policies.html">打开扶持台账 →</a>
    </section>
    <section id="home-view" aria-labelledby="home-title">
      <div class="intro"><div><p class="eyebrow">为短剧创作者准备的资源索引</p><h1 id="home-title">把时间留给创作。<span>找资源，来这里。</span></h1></div><p class="intro-side">从落地筹备到制作发行<br>把分散的信息，放到一起。</p></div>
      <section class="search-deck" aria-label="全库搜索">
        <form id="home-search" role="search"><label class="sr-only" for="home-q">搜索资源，空格分隔多个关键词</label><svg class="icon" aria-hidden="true"><use href="#i-search"/></svg><input id="home-q" name="q" type="search" placeholder="搜索模型、平台、地区或制作需求" autocomplete="off"><kbd aria-hidden="true">⌘ K</kbd><button type="submit">搜索资源 <svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></button></form>
        <div class="quick-search"><span>快速查找</span><a href="?view=models&amp;q=Seedance">Seedance</a><a href="?view=models&amp;api=open">开源模型</a><a href="?view=policies&amp;q=上海">上海扶持</a><a href="?view=platforms&amp;group=海外">短剧出海</a></div>
      </section>
      <div class="category-grid" aria-label="资源分类">
        <a class="category-card" href="?view=policies"><div class="category-top"><span class="category-icon"><svg class="icon" aria-hidden="true"><use href="#i-place"/></svg></span><span class="category-count" data-count="policies">—</span></div><h2>地方与扶持 <svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></h2><p>去哪里落地，谁可以申请</p><div class="category-bottom">地区 / 主体资格 / 申报期限</div></a>
        <a class="category-card" href="?view=platforms"><div class="category-top"><span class="category-icon"><svg class="icon" aria-hidden="true"><use href="#i-platform"/></svg></span><span class="category-count" data-count="platforms">—</span></div><h2>分发平台 <svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></h2><p>作品去哪里，怎样接入</p><div class="category-bottom">国内外市场 / 投稿与合作</div></a>
        <a class="category-card category-featured" href="?view=models"><div class="category-top"><span class="category-icon"><svg class="icon" aria-hidden="true"><use href="#i-model"/></svg></span><span class="category-count" data-count="models">—</span></div><h2>生成模型 <svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></h2><p>找到适合这一个镜头的能力</p><div class="category-bottom">视频 / 图像 / 语音 / 音乐</div></a>
        <a class="category-card" href="?view=tools"><div class="category-top"><span class="category-icon"><svg class="icon" aria-hidden="true"><use href="#i-tool"/></svg></span><span class="category-count" data-count="tools">—</span></div><h2>制作工具 <svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></h2><p>把剧本、画面和声音接起来</p><div class="category-bottom">制作环节 / 运行环境</div></a>
      </div>
      <div class="home-columns">
        <section class="updates panel" id="updates" aria-labelledby="updates-title"><div class="section-heading"><div><p class="eyebrow">信息在变化，记录也在更新</p><h2 id="updates-title">最近内容变更</h2></div><span class="subtle-tag">不含例行巡检</span></div><div id="change-feed"><p class="muted">正在读取变更记录…</p></div><div class="panel-footer"><span class="status-dot" aria-hidden="true"></span><span>有改动，留出处；有疑问，标待核。</span><a href="#about">了解收录方式 →</a></div></section>
        <aside class="calendar panel" aria-labelledby="calendar-title"><div class="section-heading"><div><p class="eyebrow">提前留意，不错过时间</p><h2 id="calendar-title">接下来的日期</h2></div><svg class="icon muted" aria-hidden="true"><use href="#i-clock"/></svg></div><div id="date-feed"><p class="muted">正在读取日期…</p></div><p class="calendar-note">申报、签约、激励和有效期分别标注。<br>日期明确，不等于人人都能参与。</p></aside>
      </div>
      <section class="model-strip" aria-labelledby="browse-title"><div><span class="mini-icon"><svg class="icon" aria-hidden="true"><use href="#i-model"/></svg></span><h2 id="browse-title">从制作需求找模型</h2><p>先看能做什么，再看怎么接入。</p></div><div class="model-shortcuts"><a href="?view=models&amp;group=视频生成">生成视频 <span>→</span></a><a href="?view=models&amp;group=图像生成">设计画面 <span>→</span></a><a href="?view=models&amp;group=语音%20%2F%20配音%20TTS">角色配音 <span>→</span></a><a href="?view=models&amp;group=音乐">制作配乐 <span>→</span></a></div></section>
      <details class="maintenance-panel" id="maintenance-panel"><summary>每日限量巡检记录 <span>不等于事实核验</span></summary><div id="maintenance"></div></details>
    </section>
    <section id="listing-view" aria-labelledby="listing-title" hidden>
      <nav class="breadcrumb" aria-label="当前位置"><a href="?view=home">资源库</a><span aria-hidden="true">/</span><span id="breadcrumb-current" aria-current="page">资源目录</span></nav>
      <div class="listing-heading"><div><p class="eyebrow" id="listing-eyebrow">短剧制作 / RESOURCE DIRECTORY</p><h1 id="listing-title">按制作需求，<span>找到合适的资源。</span></h1><p id="listing-intro">先看用途与条件，再看来源与核验记录。</p></div><div class="index-stamp"><svg class="icon" aria-hidden="true"><use id="listing-icon" href="#i-model"/></svg><span id="listing-total">—</span><small id="listing-total-label">资源记录 / 含历史条目</small></div></div>
      <form id="listing-search" class="listing-search" role="search"><svg class="icon" aria-hidden="true"><use href="#i-search"/></svg><label class="sr-only" for="listing-q">搜索名称、地区或用途，空格分隔多个关键词</label><input type="search" id="listing-q" name="q" placeholder="搜索名称、地区或制作需求" autocomplete="off"><button type="submit">查找</button></form>
      <div class="listing-layout">
        <aside class="filter-panel" aria-label="筛选资源">
          <div class="filter-title"><h2>筛选</h2><button type="button" class="text-button filter-toggle" id="toggle-filters" aria-controls="category-filters" aria-expanded="false">展开筛选</button><button type="button" class="text-button" id="reset-filters">重置</button></div>
          <div id="category-filters"></div>
          <div class="filter-foot"><span class="status-dot" aria-hidden="true"></span>数据有出处，选择有依据。</div>
        </aside>
        <div class="results">
          <div class="results-heading"><p id="result-count" role="status" aria-live="polite">正在读取资料…</p><label class="sort-label" for="sort">排序<select id="sort"><option value="catalog">目录顺序</option><option value="name">名称 A–Z</option></select></label></div>
          <div id="active-filters" class="active-filters"></div>
          <p class="evidence-note" id="evidence-note"><span class="note-mark" aria-hidden="true">i</span>用途与条件沿用原资料；核验状态单列，不用来源等级代替核验。</p>
          <div id="resource-list" class="resource-grid"></div>
          <div id="empty-results" class="empty-state" hidden><svg class="icon" aria-hidden="true"><use href="#i-search"/></svg><h2>还没有找到匹配的资源</h2><p>试试更短的名称，或减少筛选条件；空格分隔的关键词需同时匹配。</p><button type="button" id="clear-search">清除搜索与筛选</button></div>
          <div class="list-bottom"><span id="shown-count"></span><a href="#listing-title">回到顶部 ↑</a></div>
        </div>
      </div>
      <div class="listing-end" id="document-notes"></div>
    </section>
    <section id="detail-view" aria-labelledby="detail-title" hidden>
      <nav class="breadcrumb" aria-label="当前位置"><a href="?view=home">资源库</a><span aria-hidden="true">/</span><a id="detail-category" href="?view=home">资源目录</a><span aria-hidden="true">/</span><span id="detail-current" aria-current="page">资源详情</span></nav>
      <a class="detail-back" id="detail-back" href="?view=home">← 返回资源目录</a>
      <div id="detail-content"></div>
    </section>
    <section class="about-strip" id="about" aria-label="收录说明"><div><strong>找资源，也看来源。</strong><p>这是资料索引，不是推荐榜。未核验会明确标注，原文入口始终保留。</p></div><div class="edition"><span>原资料汇编截至</span><time id="edition-day">{esc(doc.get('reported_as_of') or '未提供')}</time><small>不代表今日已复核</small></div></section>
    <noscript><section class="noscript-panel"><h2>静态来源目录</h2><p>当前未启用 JavaScript，无法使用搜索、筛选与日期提醒。下方可查原始来源，或进入 <a href="/policies.html">扶持台账</a>。导入资料不等于核验。</p>{source_fallback(doc.get('records', []))}</section></noscript>
  </main>
  <footer class="site-footer"><span>一人短剧厂牌 <span class="footer-slash">/</span> 短剧资源库</span><span>收录不等于推荐，巡检不等于核验。</span><a href="/policies.html">扶持台账 ↗</a></footer>
  <script type="application/json" id="catalog-data">{embedded_json(doc)}</script>
</body>
</html>'''
