(() => {
  'use strict';
  const CATEGORIES = { all: '全部资源', policies: '地方与扶持', platforms: '分发平台', models: '生成模型', tools: '制作工具' };
  const ICONS = { policies: 'place', platforms: 'platform', models: 'model', tools: 'tool', all: 'search' };
  const ACCESS = { public: '公开入口', invitation: '定向邀约', business: '商务对接', unknown: '入口待确认', not_applicable: '不适用' };
  const LIFECYCLE = { listed: '在列', historical: '历史记录', unknown: '收录状态待确认' };
  const VERIFIED = { unverified: '待核验', partial: '部分核验', verified: '有完整核验记录' };
  const TIMING = { upcoming: '尚未开始', current: '在已记录的起止日期内', ended: '日期已结束', unknown: '日期不完整 / 待确认' };
  const HISTORY = { import: '汇编导入 / 迁移（非核验）', correction: '资料修订', review: '字段核验', 'metadata-review': '元数据核验' };
  const META = { title: '名称', access: '参与方式', lifecycle: '收录状态', 'window.kind': '日期类型', 'window.start': '开始日期', 'window.end': '结束日期' };
  const FILTERS = ['q', 'group', 'region', 'eligibility', 'market', 'access', 'api', 'environment', 'lifecycle', 'timing', 'grade', 'verification'];
  const CONFIG = {
    policies: { heading: ['去哪里落地，', '先看条件再出发。'], intro: '按地区、主体条件和参与方式查找扶持与拍摄载体。', group: '资料类型', eyebrow: '地方资源 / POLICY & LOCATION', placeholder: '搜索政策、地区或拍摄基地', note: '公开入口不等于人人可申；日期窗口不等于申报期，主体资格请逐条核对。' },
    platforms: { heading: ['作品去哪里，', '找到合适的入口。'], intro: '从国内到海外，查看市场、内容形态与投稿合作方式。', group: '市场范围', eyebrow: '作品分发 / DISTRIBUTION', placeholder: '搜索平台、公司或投稿需求', note: '入口描述沿用原资料；未查到自助入口不等于不接合作，接入方式与核验状态分别标注。' },
    models: { heading: ['为下一组镜头，', '找到合适的模型。'], intro: '按生成能力、接入方式查找。版本、规格和价格放在一处看。', group: '生成能力', eyebrow: '制作资源 / MODEL DIRECTORY', placeholder: '搜索名称、公司或用途，例如：视频 角色', note: '规格与接入方式沿用原资料；核验状态单列，不用来源等级代替核验。' },
    tools: { heading: ['把制作接起来，', '找到顺手的工具。'], intro: '从剧本到交付，按制作环节和运行环境查找。', group: '制作环节', eyebrow: '制作工具 / PRODUCTION TOOLS', placeholder: '搜索工具名称、类型或制作需求', note: '同一工具可能对应多个制作环节，保留用途记录；运行环境只依据原资料字段。' },
    all: { heading: ['从一个关键词，', '找到所需资源。'], intro: '同时检索地方与扶持、分发平台、生成模型和制作工具。', eyebrow: '全部资料 / RESOURCE SEARCH', placeholder: '搜索名称、地区、能力或条件', note: '资源收录不等于推荐。查看完整条目，核对条件、来源与适用范围。' },
  };
  const text = value => value == null ? '' : String(value);
  const array = value => Array.isArray(value) ? value : [];
  const fieldValue = (record, key) => text(array(record.fields).find(item => item.key === key)?.value);
  const normalize = value => text(value).normalize('NFKC').toLocaleLowerCase();
  const contains = (value, query) => normalize(query).trim().split(/\s+/).filter(Boolean).every(token => normalize(value).includes(token));
  const summaryText = record => fieldValue(record, 'use') || fieldValue(record, 'benefit') || fieldValue(record, 'format') || fieldValue(record, 'note') || fieldValue(record, 'entry');
  function safeURL(value) {
    if (typeof value !== 'string' || !/^https?:\/\//i.test(value) || /[\x00-\x20\x7f\\<>]/.test(value)) return null;
    const authority = value.match(/^https?:\/\/([^/?#]+)/i)?.[1];
    if (!authority || authority.includes('@')) return null;
    try {
      const url = new URL(value);
      return url.hostname && !url.username && !url.password ? url.href : null;
    } catch (_) { return null; }
  }
  function verification(record) {
    if (record.last_verified_at) return 'verified';
    if (array(record.fields).some(item => item.verified_at) || Object.values(record.metadata_verification || {}).some(item => item.verified_at)) return 'partial';
    return 'unverified';
  }
  function apiSupport(record) {
    const clauses = fieldValue(record, 'api').split(/[，,；;。\n/|]+/);
    const negative = /无官方\s*API|无\s*API|不支持|未支持|暂不|不提供|未提供|不开放|未开放|未开源|不开源|非开源|闭源|不确定|待确认|待核验|not\s+(?:available|supported|open)|no\s+(?:official\s+)?api/i;
    return { api: clauses.some(part => /[✓✔\u2705]/u.test(part) && !negative.test(part)), open: clauses.some(part => /开源/.test(part) && !negative.test(part)) };
  }
  function fieldTokens(record, key) {
    return [...new Set(fieldValue(record, key).split(/[,，、;；/|\n]+/).map(part => part.trim()).filter(Boolean))];
  }
  const environments = record => fieldTokens(record, 'environment');
  const markets = record => fieldTokens(record, 'market');
  function shanghaiDay(now = new Date()) {
    const parts = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(now);
    const get = type => parts.find(part => part.type === type).value;
    return `${get('year')}-${get('month')}-${get('day')}`;
  }
  function validDay(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    const date = new Date(`${value}T00:00:00Z`);
    return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value;
  }
  function windowKind(record) {
    const kind = record.window?.kind;
    if (kind === 'application') return record.access === 'public' ? '申报期' : record.access === 'invitation' ? '定向邀约期' : record.access === 'business' ? '商务对接期' : '申请时间（入口待确认）';
    return { incentive: '激励期', contract: '签约期', validity: '政策有效期' }[kind] || '相关时间';
  }
  function windowPhase(record, today) {
    const start = record.window?.start, end = record.window?.end;
    if (validDay(end) && end < today) return 'ended';
    if (validDay(start) && start > today) return 'upcoming';
    if (validDay(start) && validDay(end) && start <= today && today <= end) return 'current';
    return 'unknown';
  }
  function windowStatus(record, today) {
    const window = record.window;
    if (!window || (!validDay(window.start) && !validDay(window.end))) return '时间待确认';
    const label = windowKind(record);
    if (validDay(window.end) && window.end < today) return `${label}已结束 · ${window.end}`;
    if (validDay(window.start) && window.start > today) return `${label} ${window.start} 开始`;
    if (validDay(window.end)) return `${label} ${window.end === today ? '今日' : window.end} ${window.kind === 'application' ? '截止' : '结束'}`;
    return `${label} ${window.start} 起 · 结束时间待确认`;
  }
  function deadlineEvents(records, today) {
    return records.flatMap(record => ['start', 'end'].flatMap(edge => {
      const date = record.window?.[edge];
      return validDay(date) && date >= today ? [{ record, date, edge, days: Math.round((Date.parse(date) - Date.parse(today)) / 86400000), label: `${windowKind(record)} · ${edge === 'start' ? '开始' : record.window.kind === 'application' ? '截止' : '结束'}` }] : [];
    })).sort((a, b) => a.date.localeCompare(b.date) || text(a.record.title).localeCompare(text(b.record.title), 'zh-CN') || a.edge.localeCompare(b.edge));
  }
  function contentChanges(records) {
    return records.flatMap(record => array(record.history).filter(event => event.kind === 'correction' || (['review', 'metadata-review'].includes(event.kind) && Object.hasOwn(event, 'before') && Object.hasOwn(event, 'after') && JSON.stringify(event.before) !== JSON.stringify(event.after))).map(event => ({ record, event }))).sort((a, b) => text(b.event.at).localeCompare(text(a.event.at)));
  }
  function readState(search, pathname = '') {
    const params = new URLSearchParams(search);
    const category = params.get('category');
    const oldCategory = Object.hasOwn(CATEGORIES, category) ? category : /^\/policies(?:\.html)?\/?$/.test(pathname) ? 'policies' : 'all';
    const requested = params.get('view');
    const view = ['home', 'search', 'policies', 'platforms', 'models', 'tools'].includes(requested) ? requested : oldCategory !== 'all' ? oldCategory : params.has('category') || params.has('q') ? 'search' : 'home';
    const state = { view, category: Object.hasOwn(CONFIG, view) ? view : 'all', id: params.get('id') || '', sort: params.get('sort') === 'name' ? 'name' : 'catalog' };
    FILTERS.forEach(key => { state[key] = params.get(key) || ''; });
    const allowed = { grade: ['', 'A', 'B', 'C', 'unknown'], verification: ['', ...Object.keys(VERIFIED)], access: ['', ...Object.keys(ACCESS)], api: ['', 'available', 'api', 'open', 'other'], lifecycle: ['', ...Object.keys(LIFECYCLE)], timing: ['', ...Object.keys(TIMING)] };
    Object.entries(allowed).forEach(([key, values]) => { if (!values.includes(state[key])) state[key] = ''; });
    if (state.category === 'all') state.group = '';
    if (state.category !== 'models') state.api = '';
    else if (!state.lifecycle && params.get('history') === '0') state.lifecycle = 'listed';
    if (state.category !== 'tools') state.environment = '';
    if (state.category !== 'platforms') state.market = '';
    if (state.category !== 'policies') { state.region = ''; state.eligibility = ''; state.timing = ''; }
    return state;
  }
  function queryFor(state) {
    const params = new URLSearchParams({ view: state.view || (state.category === 'all' ? 'search' : state.category) || 'home' });
    FILTERS.forEach(key => { if (state[key]) params.set(key, state[key]); });
    if (state.sort === 'name') params.set('sort', 'name');
    if (state.id) params.set('id', state.id);
    return `?${params}`;
  }
  function matches(record, state, today = shanghaiDay()) {
    if (state.category !== 'all' && record.category !== state.category) return false;
    if (state.group && state.category !== 'all' && record.group !== state.group) return false;
    if (state.grade) {
      const grades = array(record.sources).map(source => source.grade).filter(grade => ['A', 'B', 'C'].includes(grade));
      if (state.grade === 'unknown' ? grades.length > 0 : !grades.includes(state.grade)) return false;
    }
    if (state.verification && verification(record) !== state.verification) return false;
    if (state.access && (record.access || 'unknown') !== state.access) return false;
    if (state.lifecycle && (record.lifecycle || 'unknown') !== state.lifecycle) return false;
    if (state.category === 'policies') {
      if (state.region && !contains(fieldValue(record, 'region') || fieldValue(record, 'issuer'), state.region)) return false;
      if (state.eligibility && !contains(fieldValue(record, 'eligibility'), state.eligibility)) return false;
      if (state.timing && windowPhase(record, today) !== state.timing) return false;
    }
    if (state.category === 'platforms' && state.market && !markets(record).includes(state.market)) return false;
    if (state.category === 'tools' && state.environment && !environments(record).includes(state.environment)) return false;
    if (state.category === 'models') {
      const support = apiSupport(record);
      if (state.api === 'available' && !support.api && !support.open) return false;
      if (state.api === 'api' && !support.api) return false;
      if (state.api === 'open' && !support.open) return false;
      if (state.api === 'other' && (support.api || support.open)) return false;
    }
    return contains([record.title, record.group, CATEGORIES[record.category], ...array(record.tags), ...array(record.notes), ...array(record.fields).flatMap(item => [item.label, item.value]), ...array(record.sources).flatMap(item => [item.label, item.scope])].join(' '), state.q);
  }
  function selectRecords(records, state, today) {
    const selected = records.filter(record => matches(record, state, today));
    return state.sort === 'name' ? selected.sort((a, b) => a.title.localeCompare(b.title, 'zh-CN', { numeric: true })) : selected;
  }
  function relatedRecords(records, record) {
    const ids = new Set(array(record.related_ids));
    return records.filter(other => other.id !== record.id && (ids.has(other.id) || (record.entity_id && other.entity_id === record.entity_id)));
  }
  const helpers = { safeURL, verification, apiSupport, environments, markets, matches, shanghaiDay, validDay, windowKind, windowPhase, windowStatus, deadlineEvents, readState, queryFor, selectRecords, contentChanges, relatedRecords, summaryText };
  if (typeof module !== 'undefined' && module.exports) module.exports = helpers;
  if (typeof document === 'undefined') return;

  const $ = id => document.getElementById(id);
  const node = (tag, className, value) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (value != null) element.textContent = text(value);
    return element;
  };
  function icon(name) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.classList.add('icon'); svg.setAttribute('aria-hidden', 'true');
    const use = document.createElementNS(svg.namespaceURI, 'use'); use.setAttribute('href', `#i-${name}`); svg.append(use);
    return svg;
  }
  let doc;
  try { doc = JSON.parse($('catalog-data').textContent); }
  catch (_) { $('home-view').hidden = true; $('load-error').hidden = false; return; }
  const records = array(doc.records).filter(record => Object.hasOwn(CONFIG, record.category) && record.category !== 'all');
  const byId = new Map(records.map(record => [record.id, record]));
  let state = readState(location.search, location.pathname);
  let today = shanghaiDay();
  let controlsCategory;
  const displayValue = value => value == null ? '未记录' : typeof value === 'object' ? JSON.stringify(value, null, 2) : text(value);
  function linkTo(label, next, className = '') {
    const link = node('a', className, label); link.href = queryFor(next); return link;
  }
  function recordLink(record, label = record.title, className = '') {
    const link = linkTo(label, { ...state, id: record.id }, className); link.dataset.recordLink = record.id; return link;
  }
  function externalLink(url, label) {
    const safe = safeURL(url);
    if (!safe) return node('span', 'muted', `${label}（无安全可用链接）`);
    const link = node('a', '', label); link.href = safe; link.target = '_blank'; link.rel = 'noopener noreferrer'; link.append(icon('external')); return link;
  }
  function pair(parent, label, value) { parent.append(node('dt', '', label), node('dd', 'preserve-lines', value)); }
  const positions = new Map();
  let entryId = crypto.randomUUID(), restoringPosition = false;
  function rememberPosition() {
    if (restoringPosition) return;
    positions.set(entryId, { scroll: window.scrollY, focusId: document.activeElement.id, recordId: document.activeElement.dataset.recordLink || '', openEvidence: [...document.querySelectorAll('.field-evidence[open]')].map(item => item.id) });
  }
  function savePosition() {
    rememberPosition();
    history.replaceState({ catalog: true, entryId, ...positions.get(entryId) }, '', location.href);
  }
  function navigate(next, hash = '') {
    const pageChanged = next.view !== state.view || next.id !== state.id;
    savePosition();
    state = next;
    const target = `${location.pathname}${queryFor(state)}${hash}`;
    if (target !== `${location.pathname}${location.search}${location.hash}`) {
      entryId = crypto.randomUUID();
      history.pushState({ catalog: true, entryId, scroll: 0 }, '', target);
    }
    render();
    if (hash) revealAnchor(hash);
    else if (pageChanged) { window.scrollTo({ top: 0, behavior: 'instant' }); $('main').focus({ preventScroll: true }); }
    rememberPosition();
  }
  function homeFeeds() {
    const changes = $('change-feed'); changes.replaceChildren();
    for (const { record, event } of contentChanges(records).slice(0, 3)) {
      const article = node('article', 'change-item');
      const date = node('time', 'change-date', text(event.at).slice(5, 10).replace('-', '.')); date.dateTime = event.at; date.append(node('small', '', text(event.at).slice(0, 4)));
      const body = node('div'), heading = node('h3'), summary = node('p');
      heading.append(recordLink(record, `${fieldValue(record, 'region') || fieldValue(record, 'issuer') || record.group} · ${record.title}`));
      summary.append(node('span', 'change-kind', event.kind === 'correction' ? '资料修订' : '内容更新'), document.createTextNode(event.summary || `${event.field || '字段'}内容已修改，查看修改记录。`));
      body.append(heading, summary); article.append(date, body, icon('arrow')); changes.append(article);
    }
    if (!changes.children.length) changes.append(node('p', 'muted', '尚无内容变更记录。首次收录与例行巡检不计入变更。'));
    const dates = $('date-feed'); dates.replaceChildren();
    for (const event of deadlineEvents(records, today).slice(0, 3)) {
      const article = node('article', 'date-item'), date = node('time', 'date-square'); date.dateTime = event.date; date.title = event.date;
      date.append(node('small', '', `${Number(event.date.slice(5, 7))}月`), node('strong', '', event.date.slice(8, 10)));
      const body = node('div'), meta = node('p', 'date-meta'), heading = node('h3');
      meta.append(node('span', '', event.label + (event.record.access === 'invitation' ? ' · 邀约' : '')), node('span', 'days', event.days === 0 ? '今天' : `${event.days} 天后`));
      heading.append(recordLink(event.record, `${fieldValue(event.record, 'region') || event.record.group} · ${event.record.title}`)); body.append(meta, heading); article.append(date, body); dates.append(article);
    }
    if (!dates.children.length) dates.append(node('p', 'muted', '暂无已记录的后续日期，请查看条目的时间说明。'));
  }
  function selectControl(parent, key, label, choices) {
    const wrapper = node('label', 'category-select', label), select = node('select'); select.id = `filter-${key}`; select.dataset.filter = key;
    for (const [value, name] of [['', '全部'], ...choices]) { const option = node('option', '', name); option.value = value; select.append(option); }
    wrapper.append(select); parent.append(wrapper);
  }
  function textControl(parent, key, label, placeholder) {
    const wrapper = node('label', 'category-select', label), input = node('input'); input.type = 'search'; input.id = `filter-${key}`; input.dataset.filter = key; input.placeholder = placeholder; input.autocomplete = 'off'; wrapper.append(input); parent.append(wrapper);
  }
  function buildControls() {
    const target = $('category-filters'); target.replaceChildren();
    if (state.category !== 'all') {
      const section = node('fieldset'), legend = node('legend', '', CONFIG[state.category].group), options = node('div', 'group-options');
      const categoryRecords = records.filter(record => record.category === state.category);
      for (const group of ['', ...new Set(categoryRecords.map(record => record.group).filter(Boolean))]) {
        const label = node('label', 'group-option'), input = node('input'); input.type = 'radio'; input.name = 'group'; input.value = group; input.dataset.filter = 'group';
        label.append(input, node('span', '', group || '全部'), node('span', '', categoryRecords.filter(record => !group || record.group === group).length)); options.append(label);
      }
      section.append(legend, options); target.append(section);
    }
    if (state.category === 'policies') {
      const keywords = node('form', 'keyword-filters'); keywords.id = 'policy-keywords';
      textControl(keywords, 'region', '地区关键词', '例如：上海 / 横琴');
      textControl(keywords, 'eligibility', '主体条件关键词', '例如：企业 / 剧组');
      keywords.append(node('button', '', '应用关键词')); target.append(keywords);
      selectControl(target, 'timing', '日期状态（不代表可申报）', Object.entries(TIMING));
    }
    if (state.category === 'policies' || state.category === 'platforms') selectControl(target, 'access', '参与 / 接入方式', Object.entries(ACCESS).filter(([key]) => key !== 'not_applicable'));
    if (state.category === 'platforms') selectControl(target, 'market', '目标市场（原资料标注）', [...new Set(records.filter(record => record.category === 'platforms').flatMap(markets))].map(value => [value, value]));
    if (state.category === 'models') selectControl(target, 'api', 'API / 开源', [['available', '支持 API 或开源'], ['api', '资料标注支持 API'], ['open', '资料标注开源'], ['other', '未明确支持']]);
    if (state.category === 'tools') selectControl(target, 'environment', '运行环境（原资料标注）', [...new Set(records.filter(record => record.category === 'tools').flatMap(environments))].sort().map(value => [value, value]));
    selectControl(target, 'lifecycle', '收录状态', Object.entries(LIFECYCLE));
    const advanced = node('details', 'filter-evidence'); advanced.append(node('summary', '', '来源与核验筛选'));
    selectControl(advanced, 'grade', '来源等级', [['A', '含 A 级来源'], ['B', '含 B 级来源'], ['C', '含 C 级来源'], ['unknown', '未标等级']]);
    selectControl(advanced, 'verification', '核验状态', Object.entries(VERIFIED)); target.append(advanced);
    target.append(node('p', 'filter-note', state.category === 'policies' ? '主体搜索只匹配已记录的资格字段。日期按上海时区计算，不确认当前可申请。' : '“在列”是收录状态，不保证当前可用。来源等级不等于事实核验。'));
    controlsCategory = state.category;
  }
  function updateControls() {
    if (controlsCategory !== state.category) buildControls();
    for (const control of $('category-filters').querySelectorAll('[data-filter]')) {
      const value = state[control.dataset.filter] || '';
      if (control.type === 'radio') control.checked = control.value === value;
      else {
        if (control.tagName === 'SELECT' && value && ![...control.options].some(option => option.value === value)) { const option = node('option', '', `${value}（当前无条目）`); option.value = value; control.append(option); }
        control.value = value;
      }
    }
    if (state.grade || state.verification) $('category-filters').querySelector('.filter-evidence').open = true;
  }
  function resourceCard(record) {
    const card = node('article', 'resource-card'); card.dataset.id = record.id;
    const top = node('div', 'resource-top'), group = node('span', 'resource-group'); group.append(icon(ICONS[record.category]), document.createTextNode(record.group || CATEGORIES[record.category]));
    top.append(group, node('span', 'verification', VERIFIED[verification(record)]));
    const heading = node('h2'); heading.append(recordLink(record));
    const company = node('p', 'resource-company', fieldValue(record, 'company') || fieldValue(record, 'issuer') || CATEGORIES[record.category]);
    if (record.lifecycle === 'historical') company.append(node('span', 'history-badge', record.category === 'models' ? '历史版本' : '历史记录'));
    const use = node('p', 'resource-use', summaryText(record) || '查看收录信息与来源。'), specs = node('dl', 'resource-specs');
    const keys = { models: [['specs', '规格'], ['api', '接入']], policies: [['region', '地区'], ['eligibility', '主体']], platforms: [['market', '市场'], ['entry', '入口']], tools: [['type', '类型'], ['environment', '环境']] }[record.category];
    for (const [key, label] of keys) {
      let value = fieldValue(record, key);
      if (key === 'api') value = value === '✓' ? '资料标注支持 API' : value || '资料未标注';
      if (value) pair(specs, label, value);
    }
    card.append(top, heading, company, use, specs);
    if (record.category === 'policies' || record.category === 'platforms') {
      const status = node('div', 'policy-status'); status.append(node('span', 'verification', ACCESS[record.access] || ACCESS.unknown));
      if (record.category === 'policies') status.append(node('span', 'muted', windowStatus(record, today)));
      card.append(status);
    }
    const bottom = node('div', 'resource-bottom'); bottom.append(node('span', '', `${array(record.sources).length} 个来源 · 原资料 ${record.reported_as_of || '日期未记录'}`));
    const link = recordLink(record, '查看详情'); link.append(icon('arrow')); bottom.append(link); card.append(bottom); return card;
  }
  function activeFilters() {
    const labels = { q: `搜索：${state.q}`, group: state.group, region: `地区：${state.region}`, eligibility: `主体：${state.eligibility}`, market: `市场：${state.market}`, access: ACCESS[state.access], api: { available: '支持 API 或开源', api: '支持 API', open: '开源', other: '接入未明确' }[state.api], environment: state.environment, lifecycle: LIFECYCLE[state.lifecycle], timing: TIMING[state.timing], grade: `来源：${state.grade}`, verification: VERIFIED[state.verification] };
    $('active-filters').replaceChildren();
    for (const key of FILTERS.filter(key => state[key])) {
      const button = node('button', 'filter-chip', labels[key]); button.type = 'button'; button.setAttribute('aria-label', `移除筛选：${labels[key]}`); button.append(icon('close'));
      button.addEventListener('click', () => { navigate({ ...state, [key]: '', id: '' }); $('listing-q').focus({ preventScroll: true }); }); $('active-filters').append(button);
    }
  }
  function renderDocuments() {
    const target = $('document-notes'); target.replaceChildren();
    for (const item of array(doc.documents).filter(item => state.category === 'all' || item.category === state.category)) {
      const details = node('details', 'document-note'); details.append(node('summary', '', `${CATEGORIES[item.category] || '资料'} · 汇编附注`), node('p', 'muted', '原始汇编背景，不是核验结论。'));
      for (const block of array(item.blocks).filter(block => block.type === 'text' && text(block.text).trim())) details.append(node('p', 'preserve-lines', block.text));
      target.append(details);
    }
  }
  function renderListing() {
    const config = CONFIG[state.category];
    $('breadcrumb-current').textContent = state.category === 'all' ? '搜索结果' : CATEGORIES[state.category];
    $('listing-eyebrow').textContent = config.eyebrow;
    $('listing-title').replaceChildren(document.createTextNode(config.heading[0]), node('span', '', config.heading[1]));
    $('listing-intro').textContent = config.intro;
    $('listing-total').textContent = records.filter(record => state.category === 'all' || record.category === state.category).length;
    $('listing-total-label').textContent = state.category === 'tools' ? '用途记录 / 非独立产品数' : '收录记录 / 含历史资料';
    $('listing-icon').setAttribute('href', `#i-${ICONS[state.category]}`);
    $('listing-q').placeholder = config.placeholder; $('listing-q').value = state.q; $('sort').value = state.sort;
    $('evidence-note').textContent = config.note;
    document.querySelector('.filter-panel').setAttribute('aria-label', `筛选${CATEGORIES[state.category]}`);
    updateControls(); activeFilters();
    const selected = selectRecords(records, state, today);
    $('result-count').replaceChildren(document.createTextNode('找到 '), node('strong', '', selected.length), document.createTextNode(' 条记录'));
    $('resource-list').replaceChildren(...selected.map(resourceCard)); $('empty-results').hidden = selected.length > 0;
    $('shown-count').textContent = `已显示全部 ${selected.length} 条记录 · 不代表独立产品或开放机会数`;
    renderDocuments();
  }
  function section(id, title) { const item = node('section', 'detail-section'); item.id = id; item.append(node('h2', '', title)); return item; }
  function proofBlock(record, proof, at) {
    const block = node('div', 'proof-block');
    if (at) block.append(node('p', 'muted', `核验时间：${at}`));
    if (Object.hasOwn(proof, 'value')) block.append(node('p', 'preserve-lines', `对应字段值：${displayValue(proof.value)}`));
    block.append(node('blockquote', 'proof-quote preserve-lines', proof.quote || '未记录摘录'));
    const source = array(record.sources).find(item => item.id === proof.source_id);
    if (source) block.append(externalLink(source.url, `${source.id} · ${source.label || '原始来源'}`));
    else block.append(node('p', 'muted', `来源未关联：${proof.source_id || '未记录'}`));
    if (proof.note) block.append(node('p', 'preserve-lines', proof.note));
    return block;
  }
  function renderDetail() {
    const record = byId.get(state.id), content = $('detail-content'); content.replaceChildren();
    $('detail-back').href = queryFor({ ...state, id: '' }); $('detail-back').textContent = state.view === 'home' ? '← 返回发现资源' : '← 返回筛选结果';
    const category = record?.category || 'all'; $('detail-category').href = queryFor(readState(`?category=${category}`)); $('detail-category').textContent = CATEGORIES[category]; $('detail-current').textContent = '资源详情';
    if (!record) {
      const empty = node('div', 'empty-state'); const title = node('h1', '', '没有找到这个条目'); title.id = 'detail-title';
      empty.append(title, node('p', '', '链接可能有误，或这条资料已移出目录。可以返回分类重新查找。'), linkTo('查看全部资源', readState('?view=search'), 'detail-link')); content.append(empty); return;
    }
    const heading = node('header', 'detail-heading');
    const title = node('h1', '', record.title); title.id = 'detail-title';
    const status = node('div', 'detail-status'); status.append(node('span', 'verification', VERIFIED[verification(record)]), node('span', 'verification', LIFECYCLE[record.lifecycle] || LIFECYCLE.unknown), node('span', 'muted', `原资料截至 ${record.reported_as_of || '未提供'}`));
    heading.append(node('p', 'detail-kicker', `${CATEGORIES[record.category]} / ${record.group || '未分组'}`), title, status, node('p', 'detail-summary', summaryText(record) || '查看已收录的条件与来源。'));
    const layout = node('div', 'detail-layout'), main = node('div', 'detail-main'), aside = node('aside', 'detail-aside');
    const facts = section('facts', { policies: '支持条件与参与入口', platforms: '市场与接入方式', models: '能力、规格与接入', tools: '制作用途与运行环境' }[record.category]);
    if (record.category === 'policies' || record.category === 'platforms') {
      facts.append(node('p', 'policy-status', record.access === 'invitation' ? '定向邀约，不是公开报名；须先核对名单与主体条件。' : `${ACCESS[record.access] || ACCESS.unknown} · ${record.access === 'public' ? '仍需核对主体资格与原文条件。' : '请按下方原资料确认接入条件。'}`));
    }
    if (record.category === 'policies' || record.window) {
      facts.append(node('p', 'policy-status', windowStatus(record, today)));
      if (record.window) facts.append(node('p', 'muted', `${windowKind(record)}：${record.window.start || '起始日未记录'} 至 ${record.window.end || '结束日未记录'}（按上海日期 ${today} 判断，不代表开放申报）`));
    }
    const fields = node('dl', 'detail-fields');
    for (const field of array(record.fields)) {
      const value = node('dd');
      const display = field.key === 'individual' ? ({ yes: '原资料标注：个人可参与', no: '原资料标注：个人不可直接参与', entity: '原资料标注：需要主体', partial: '原资料标注：部分环节可参与' }[field.value] || field.value) : field.value;
      if (safeURL(field.value)) value.append(externalLink(field.value, field.value)); else value.append(node('div', 'preserve-lines', display == null || display === '' ? '未提供' : display));
      const ref = node('a', 'field-proof-link', field.verified_at ? '查看字段核验证据' : '待核验 · 查看字段来源'); ref.href = `#evidence-${encodeURIComponent(field.key)}`; value.append(ref);
      fields.append(node('dt', '', field.label || field.key), value);
    }
    if (!fields.children.length) facts.append(node('p', 'muted', '暂无结构化字段，请查看来源。'));
    facts.append(fields); main.append(facts);
    const notes = section('notes', '适用说明与待核问题');
    for (const note of array(record.notes)) notes.append(node('p', 'preserve-lines', note));
    if (!record.notes?.length) notes.append(node('p', 'muted', '暂无额外备注；不代表已完成核验。'));
    main.append(notes);
    const sources = section('sources', '来源与适用范围');
    sources.append(node('p', 'muted', 'A / B / C 沿用汇编的来源等级，不等于字段已核验。官网链接也不自动证明整条参数。'));
    for (const source of array(record.sources)) {
      const row = node('div', 'source-row'); row.id = `source-${encodeURIComponent(source.id)}`;
      const head = node('div', 'source-heading'); head.append(node('span', 'verification', `${source.id} / ${source.grade || '未分级'}`), externalLink(source.url, source.label || '原始来源'));
      row.append(head, node('p', 'preserve-lines', `适用范围：${source.scope || '未标注'}`), node('p', 'source-address', source.url)); sources.append(row);
    }
    if (!record.sources?.length) sources.append(node('p', 'muted', '未附原始来源，使用前需要补证。')); main.append(sources);
    const evidence = section('evidence', '字段与元数据核验');
    evidence.append(node('p', 'muted', '来源关联、原文摘录与核验时间分别展示；部分字段有证据，不表示整条已核验。'));
    for (const field of array(record.fields)) {
      const item = node('details', 'field-evidence'); item.id = `evidence-${encodeURIComponent(field.key)}`;
      const summary = node('summary', '', `${field.label || field.key} · ${field.verified_at ? `字段核验 ${field.verified_at}` : '待核验'}`); summary.id = `${item.id}-summary`; item.append(summary);
      item.append(node('p', 'preserve-lines', `当前字段值：${displayValue(field.value)}`));
      for (const id of array(field.source_ids)) {
        const source = array(record.sources).find(source => source.id === id);
        if (source) { const link = node('a', 'detail-link', `${id} · ${source.label || '来源'} [${source.grade || '未分级'}]`); link.href = `#source-${encodeURIComponent(id)}`; item.append(link); }
        else item.append(node('p', 'muted', `${id} · 来源缺失`));
      }
      if (!field.source_ids?.length) item.append(node('p', 'muted', '未关联字段来源'));
      if (field.verification) item.append(proofBlock(record, field.verification, field.verified_at));
      else item.append(node('p', 'muted', '尚无字段核验摘录。'));
      evidence.append(item);
    }
    const metaKeys = ['title', 'access', 'lifecycle', ...(record.window ? ['window.kind', 'window.start', 'window.end'] : [])];
    for (const key of metaKeys) {
      const proof = record.metadata_verification?.[key], item = node('details', 'field-evidence'); item.id = `metadata-${key}`;
      const summary = node('summary', '', `${META[key]}（元数据） · ${proof?.verified_at ? `核验 ${proof.verified_at}` : '待核验'}`); summary.id = `${item.id}-summary`; item.append(summary);
      if (proof) item.append(proofBlock(record, proof, proof.verified_at));
      else item.append(node('p', 'muted', '暂无此项核验记录。'));
      evidence.append(item);
    }
    main.append(evidence);
    const historySection = section('history', '修改与核验记录');
    historySection.append(node('p', 'muted', '导入时间不是事实变更或核验时间；下方按记录时间倒序展示。'));
    for (const event of array(record.history).slice().sort((a, b) => text(b.at).localeCompare(text(a.at)))) {
      const item = node('article', 'history-item'); item.append(node('h3', '', HISTORY[event.kind] || event.kind), node('p', 'muted', event.at || '时间未记录'), node('p', 'preserve-lines', event.summary || event.note || '未提供说明'));
      if (event.field) item.append(node('p', '', `字段：${array(record.fields).find(field => field.key === event.field)?.label || META[event.field] || event.field}`));
      const values = node('dl', 'history-values');
      if (Object.hasOwn(event, 'before')) pair(values, '修改前', displayValue(event.before));
      if (Object.hasOwn(event, 'after')) pair(values, '修改后', displayValue(event.after));
      item.append(values); if (event.quote) item.append(proofBlock(record, event)); historySection.append(item);
    }
    if (!record.history?.length) historySection.append(node('p', 'muted', '暂无修改记录。'));
    if (record.origin?.file) historySection.append(node('p', 'muted preserve-lines', `迁移出处：${record.origin.file}${record.origin.row_at_import ? ` · 原第 ${record.origin.row_at_import} 行` : ''}。这是历史溯源位置，不是当前维护入口。`));
    main.append(historySection);
    const related = section('related', '关联条目'), links = node('div', 'related-links');
    for (const other of relatedRecords(records, record)) {
      const link = recordLink(other, '', 'related-card'); link.append(node('span', 'detail-kicker', `${CATEGORIES[other.category]} / ${other.group}`), node('strong', '', other.title), icon('arrow')); links.append(link);
    }
    related.append(links.children.length ? links : node('p', 'muted', '暂无已建立的关联条目。')); main.append(related);
    const toc = node('nav', 'detail-toc'); toc.setAttribute('aria-label', '详情页目录'); toc.append(node('h2', '', '本页内容'));
    for (const [id, label] of [['facts', '条件 / 能力 / 入口'], ['notes', '适用说明'], ['sources', '来源与范围'], ['evidence', '核验证据'], ['history', '修改记录'], ['related', '关联条目']]) { const link = node('a', '', label); link.href = `#${id}`; toc.append(link); }
    const meta = node('dl', 'detail-meta'); pair(meta, '原资料截至', record.reported_as_of || '未提供'); pair(meta, '首次导入', record.imported_at || '未记录'); pair(meta, '内容变更', record.updated_at || '暂无变更记录'); pair(meta, '最近完整核验', record.last_verified_at || '尚未核验'); pair(meta, '记录 ID', record.id);
    aside.append(toc, meta, node('p', 'muted', '来源等级不是核验结果；在列不保证当前可用。'));
    if (record.tags?.length) aside.append(node('p', 'record-tags', record.tags.join(' · ')));
    layout.append(main, aside); content.append(heading, layout);
  }
  function renderMaintenance() {
    const target = $('maintenance'), maintenance = doc.maintenance || {}, coverage = maintenance.coverage || {}, meta = node('dl', 'detail-meta');
    target.append(node('p', 'muted', '每日限量轮转，不代表全库每天复核。读回正文、网页变化、人工事实核验分别记录；机器离线不能保证当日执行。'));
    pair(meta, '统计日期（北京时间）', maintenance.day || '尚无统计'); pair(meta, '巡检统计生成', maintenance.generated_at || '尚未生成'); pair(meta, '最近读回正文日期', maintenance.last_success_day || '尚无成功读回'); pair(meta, '统计日尝试 / 全部来源', `${coverage.sources_attempted_today ?? 0} / ${coverage.total_sources ?? '未知'}`); pair(meta, '统计日读回正文', coverage.sources_inspected_today ?? 0); pair(meta, '从未读回正文', coverage.sources_never_inspected ?? '未知'); pair(meta, '待审正文版本', maintenance.pending_count ?? 0); pair(meta, '需人工查看的来源', maintenance.manual_required_count ?? 0); pair(meta, '抓取失败的来源', maintenance.failure_count ?? 0);
    target.append(meta);
  }
  function render() {
    $('home-view').hidden = state.view !== 'home' || Boolean(state.id);
    $('listing-view').hidden = state.view === 'home' || Boolean(state.id);
    $('detail-view').hidden = !state.id;
    for (const link of document.querySelectorAll('[data-nav]')) {
      const current = byId.get(state.id)?.category || state.view;
      if (link.dataset.nav === current) link.setAttribute('aria-current', 'page'); else link.removeAttribute('aria-current');
    }
    if (state.id) renderDetail(); else if (state.view === 'home') homeFeeds(); else renderListing();
    document.title = `${state.id ? byId.get(state.id)?.title || '条目未找到' : state.view === 'home' ? '发现资源' : CATEGORIES[state.category]} · 一人短剧厂牌`;
  }
  function revealAnchor(hash) {
    let id;
    try { id = decodeURIComponent(hash.slice(1)); } catch (_) { return; }
    const target = $(id) || $(hash.slice(1));
    if (!target) return;
    if (target.tagName === 'DETAILS') { target.open = true; target.querySelector('summary').focus({ preventScroll: true }); }
    else if (target.id === 'main') target.focus({ preventScroll: true });
    target.scrollIntoView({ block: 'start' });
  }
  document.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || link.target) return;
    const href = link.getAttribute('href') || '';
    if (href.startsWith('#')) {
      event.preventDefault(); savePosition(); entryId = crypto.randomUUID();
      history.pushState({ catalog: true, entryId, scroll: window.scrollY }, '', href);
      revealAnchor(href); rememberPosition(); return;
    }
    if (!href.startsWith('?')) return;
    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin || url.pathname !== location.pathname) return;
    event.preventDefault(); navigate(readState(url.search, url.pathname), url.hash);
  });
  $('home-search').addEventListener('submit', event => { event.preventDefault(); navigate({ ...readState('?view=search'), q: $('home-q').value.trim() }); });
  $('listing-search').addEventListener('submit', event => { event.preventDefault(); navigate({ ...state, q: $('listing-q').value.trim(), id: '' }); });
  $('category-filters').addEventListener('change', event => { if (event.target.dataset.filter && event.target.type !== 'search') navigate({ ...state, [event.target.dataset.filter]: event.target.value, id: '' }); });
  $('category-filters').addEventListener('submit', event => {
    event.preventDefault();
    navigate({ ...state, region: $('filter-region').value.trim(), eligibility: $('filter-eligibility').value.trim(), id: '' });
  });
  $('sort').addEventListener('change', event => navigate({ ...state, sort: event.target.value }));
  $('reset-filters').addEventListener('click', () => navigate({ ...readState(`?view=${state.view}`), q: state.q, sort: state.sort }));
  $('clear-search').addEventListener('click', () => { navigate(readState(`?view=${state.view}`)); $('listing-q').focus(); });
  $('toggle-filters').addEventListener('click', () => { const expanded = document.querySelector('.filter-panel').classList.toggle('filters-open'); $('toggle-filters').setAttribute('aria-expanded', text(expanded)); $('toggle-filters').textContent = expanded ? '收起筛选' : '展开筛选'; });
  window.addEventListener('scroll', rememberPosition, { passive: true });
  document.addEventListener('focusin', rememberPosition);
  document.addEventListener('toggle', rememberPosition, true);
  window.addEventListener('popstate', event => {
    // The toggle event may still be queued when history navigation starts.
    rememberPosition();
    restoringPosition = true;
    entryId = event.state?.entryId || crypto.randomUUID();
    const saved = positions.get(entryId) || event.state;
    state = readState(location.search, location.pathname); render();
    for (const id of saved?.openEvidence || []) if ($(id)) $(id).open = true;
    requestAnimationFrame(() => {
      if (saved?.scroll != null) window.scrollTo({ top: saved.scroll, behavior: 'instant' }); else if (location.hash) revealAnchor(location.hash);
      const focus = saved?.recordId ? [...document.querySelectorAll('[data-record-link]')].find(link => link.dataset.recordLink === saved.recordId && link.getClientRects().length) : $(saved?.focusId);
      if (focus?.getClientRects().length) focus.focus({ preventScroll: true }); else $('main').focus({ preventScroll: true });
      restoringPosition = false; rememberPosition();
    });
  });
  window.addEventListener('hashchange', () => { if (!restoringPosition) revealAnchor(location.hash); });
  window.addEventListener('pagehide', savePosition);
  document.addEventListener('keydown', event => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault(); if (state.id) navigate(readState('?view=search')); $(state.view === 'home' ? 'home-q' : 'listing-q').focus();
    }
  });
  function refreshDay() {
    const next = shanghaiDay();
    if (next !== today) { today = next; render(); }
  }
  document.addEventListener('visibilitychange', () => { if (!document.hidden) refreshDay(); });
  setInterval(refreshDay, 60000);
  for (const count of document.querySelectorAll('[data-count]')) count.textContent = records.filter(record => record.category === count.dataset.count).length;
  $('edition-day').textContent = doc.reported_as_of || '未记录';
  if (validDay(doc.reported_as_of)) $('edition-day').dateTime = doc.reported_as_of;
  history.scrollRestoration = 'manual';
  renderMaintenance(); render(); savePosition();
  if (location.hash) requestAnimationFrame(() => revealAnchor(location.hash));
})();
