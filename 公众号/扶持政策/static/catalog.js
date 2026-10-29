/* Local-only catalogue: text nodes for content, explicit HTTP(S) source links. */
(function () {
  'use strict';
  const CATEGORIES = {
    all: ['全部资源', '从筹备到交付，按用途查找'],
    policies: ['地方与扶持', '找扶持 · 找落地'],
    platforms: ['分发平台', '找发行 · 找观众'],
    models: ['模型', '找生成能力 · 核对版本与接入'],
    tools: ['制作工具', '从剧本到后期，把作品做完']
  };
  const ACCESS = { public: '公开入口', invitation: '定向邀约', business: '商务对接', unknown: '接入待确认', not_applicable: '接入不适用' };
  const LIFECYCLE = { listed: '在列', historical: '历史记录', unknown: '收录状态待确认' };
  const HISTORY = { import: '汇编导入 / 迁移', correction: '内容纠正', review: '核验记录' };
  const FILTERS = ['q', 'group', 'grade', 'verification', 'access', 'api', 'environment', 'lifecycle'];
  const text = value => value == null ? '' : String(value);
  const array = value => Array.isArray(value) ? value : [];
  const fieldValue = (record, key) => text(array(record.fields).find(field => field.key === key)?.value);
  const normalize = value => text(value).normalize('NFKC').toLocaleLowerCase();

  function safeURL(value) {
    if (typeof value !== 'string' || !/^https?:\/\//i.test(value) || /[\x00-\x20\x7f\\]/.test(value)) return null;
    const authority = value.match(/^https?:\/\/([^/?#]+)/i)?.[1];
    if (!authority || authority.includes('@')) return null;
    try {
      const url = new URL(value);
      return url.hostname && !url.username && !url.password ? url.href : null;
    } catch (_) { return null; }
  }

  function verification(record) {
    if (record.last_verified_at) return 'verified';
    if (array(record.fields).some(field => field.verified_at) || Object.values(record.metadata_verification || {}).some(proof => proof.verified_at)) return 'partial';
    return 'unverified';
  }

  function apiSupport(record) {
    // Only the dedicated API field is evidence; "无官方 API" is not support.
    const value = fieldValue(record, 'api');
    const clauses = value.split(/[，,；;。\n/|]+/);
    const negative = /无官方\s*API|无\s*API|不支持|未支持|暂不|不提供|未提供|不开放|未开放|未开源|不开源|非开源|闭源|不确定|待确认|待核验|not\s+(?:available|supported|open)|no\s+(?:official\s+)?api/i;
    return {
      api: clauses.some(part => /[✓✔✅]/u.test(part) && !negative.test(part)),
      open: clauses.some(part => /开源/.test(part) && !negative.test(part))
    };
  }

  function environments(record) {
    // Deliberately use environment, never tool type, entry, API, or category.
    return [...new Set(fieldValue(record, 'environment').split(/[,，、;；/|\n]+/).map(part => part.trim()).filter(Boolean))];
  }

  function matches(record, state) {
    if (state.category !== 'all' && record.category !== state.category) return false;
    if (state.group && state.category !== 'all' && text(record.group) !== state.group) return false;
    if (state.grade) {
      const grades = array(record.sources).map(source => source.grade).filter(grade => ['A', 'B', 'C'].includes(grade));
      if (state.grade === 'unknown' ? grades.length > 0 : !grades.includes(state.grade)) return false;
    }
    if (state.verification && verification(record) !== state.verification) return false;
    if (state.access && (record.access || 'unknown') !== state.access) return false;
    if (state.category === 'models') {
      if (state.lifecycle && (record.lifecycle || 'unknown') !== state.lifecycle) return false;
      const support = apiSupport(record);
      if (state.api === 'available' && !support.api && !support.open) return false;
      if (state.api === 'api' && !support.api) return false;
      if (state.api === 'open' && !support.open) return false;
      if (state.api === 'other' && (support.api || support.open)) return false;
    }
    if (state.category === 'tools' && state.environment && !environments(record).includes(state.environment)) return false;
    const haystack = normalize([record.title, record.group, CATEGORIES[record.category]?.[0],
      ...array(record.tags), ...array(record.notes), ...array(record.fields).flatMap(field => [field.label, field.value]),
      ...array(record.sources).flatMap(source => [source.label, source.scope])].join(' '));
    return normalize(state.q).trim().split(/\s+/).filter(Boolean).every(token => haystack.includes(token));
  }

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
    if (kind === 'application') {
      if (record.access === 'invitation') return '定向邀约期';
      if (record.access === 'business') return '商务对接期';
      if (record.access !== 'public') return '申请时间（入口待确认）';
      return '申报期';
    }
    return { incentive: '激励期', contract: '签约期', validity: '政策有效期' }[kind] || '相关时间';
  }

  function windowStatus(record, today) {
    const window = record.window;
    if (!window || (!validDay(window.start) && !validDay(window.end))) return '时间待确认';
    const label = windowKind(record);
    if (validDay(window.end) && window.end < today) return `${label}已结束 · ${window.end}`;
    if (validDay(window.start) && window.start > today) return `${label} ${window.start} 开始`;
    if (validDay(window.end)) {
      const suffix = window.kind === 'application' ? '截止' : '结束';
      return `${label} ${window.end === today ? '今日' : window.end} ${suffix}`;
    }
    return `${label} ${window.start} 起 · 结束时间待确认`;
  }

  function deadlineEvents(records, today) {
    const events = [];
    records.forEach(record => {
      const window = record.window;
      if (!window) return;
      ['start', 'end'].forEach(edge => {
        const date = window[edge];
        if (validDay(date) && date >= today) {
          events.push({ record, date, edge, label: `${windowKind(record)} · ${edge === 'start' ? '开始' : window.kind === 'application' ? '截止' : '结束'}` });
        }
      });
    });
    // No date-based deduplication: different records and both edges survive.
    return events.sort((a, b) => a.date.localeCompare(b.date) || text(a.record.title).localeCompare(text(b.record.title), 'zh-CN') || a.edge.localeCompare(b.edge));
  }

  function readState(search, pathname = '') {
    const params = new URLSearchParams(search);
    const category = params.get('category');
    const fallback = /^\/policies(?:\.html)?\/?$/.test(pathname) ? 'policies' : 'all';
    const state = { category: Object.hasOwn(CATEGORIES, category) ? category : fallback, id: params.get('id') || '' };
    FILTERS.forEach(key => { state[key] = params.get(key) || ''; });
    const allowed = {
      grade: ['', 'A', 'B', 'C', 'unknown'], verification: ['', 'unverified', 'partial', 'verified'],
      access: ['', ...Object.keys(ACCESS)], api: ['', 'available', 'api', 'open', 'other'], lifecycle: ['', ...Object.keys(LIFECYCLE)]
    };
    Object.entries(allowed).forEach(([key, values]) => { if (!values.includes(state[key])) state[key] = ''; });
    if (state.category === 'all') state.group = '';
    if (state.category !== 'models') { state.api = ''; state.lifecycle = ''; }
    if (state.category !== 'tools') state.environment = '';
    return state;
  }

  function queryFor(state) {
    const params = new URLSearchParams();
    params.set('category', state.category);
    FILTERS.forEach(key => { if (state[key]) params.set(key, state[key]); });
    if (state.id) params.set('id', state.id);
    return `?${params.toString()}`;
  }

  const helpers = { safeURL, verification, apiSupport, environments, matches, shanghaiDay, validDay, windowKind, windowStatus, deadlineEvents, readState, queryFor };
  if (typeof module !== 'undefined' && module.exports) module.exports = helpers;
  if (typeof document === 'undefined') return;

  const $ = id => document.getElementById(id);
  const node = (tag, className, value) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (value != null) element.textContent = text(value);
    return element;
  };
  const appendText = (parent, tag, className, value) => { const child = node(tag, className, value); parent.append(child); return child; };
  let doc;
  try { doc = JSON.parse($('catalog-data').textContent); }
  catch (_) { $('result-count').textContent = '本地资料无法读取，请通过扶持台账查看政策。'; return; }
  const records = array(doc.records).filter(record => Object.hasOwn(CATEGORIES, record.category) && record.category !== 'all');
  const byId = new Map(records.map(record => [text(record.id), record]));
  const rowById = new Map();
  let state = readState(window.location.search, window.location.pathname);
  let today = shanghaiDay();
  let currentMatches = [];
  if (state.id && byId.has(state.id)) state.category = byId.get(state.id).category;

  function persist(push = false) {
    const next = `${window.location.pathname}${queryFor(state)}${window.location.hash}`;
    if (next !== `${window.location.pathname}${window.location.search}${window.location.hash}`) {
      window.history[push ? 'pushState' : 'replaceState'](null, '', next);
    }
  }

  function recordLink(record, label, className) {
    const link = node('a', className, label || record.title);
    link.href = queryFor({ category: record.category, id: text(record.id) });
    link.addEventListener('click', event => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      state = readState(link.search);
      render(true);
      persist(true);
    });
    return link;
  }

  function sourceLink(source) {
    const url = safeURL(source.url);
    if (!url) return node('span', 'muted', `${source.label || source.id || '来源'}（无安全可用链接）`);
    const link = node('a', 'source-link', source.label || source.id || new URL(url).hostname);
    link.href = url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.append(node('span', 'external-arrow', ' ↗'));
    return link;
  }

  function pair(parent, label, value) {
    const item = node('div');
    item.append(node('dt', '', label), node('dd', '', value));
    parent.append(item);
  }

  function verificationLabel(record) {
    return { unverified: '未核验', partial: '部分字段核验', verified: '有核验记录' }[verification(record)];
  }

  function proofBlock(record, proof) {
    const block = node('div', 'proof-block');
    block.append(node('blockquote', 'preserve-lines', proof.quote));
    const source = array(record.sources).find(item => item.id === proof.source_id);
    if (source) block.append(sourceLink(source));
    if (proof.note) block.append(node('p', 'muted preserve-lines', proof.note));
    return block;
  }

  function historyRow(record, item) {
    const li = node('li');
    li.append(node('span', 'history-kind', HISTORY[item.kind] || '其他记录'), node('span', 'utility', item.at || '时间未记录'), node('p', 'preserve-lines', item.summary || '未提供说明'));
    if (item.field) li.append(node('p', 'preserve-lines', `${item.field}：${text(item.before)} → ${text(item.after)}`));
    if (item.quote) li.append(proofBlock(record, item));
    return li;
  }

  function makeDossier(record) {
    const dossier = node('div', 'dossier');
    const head = node('div', 'dossier-heading');
    head.append(node('span', 'utility record-id', record.id), recordLink(record, '条目直链 ↗', 'text-link'));
    dossier.append(head);
    const status = node('p', 'dossier-status');
    status.append(node('span', 'badge', ACCESS[record.access] || ACCESS.unknown));
    if (record.category === 'models' || record.lifecycle === 'historical') {
      status.append(node('span', record.lifecycle === 'historical' ? 'badge badge-rust' : 'badge', LIFECYCLE[record.lifecycle] || LIFECYCLE.unknown));
    }
    if (record.access === 'invitation') status.append(node('span', 'caution', '仅限定向邀约，不是公开申报入口。'));
    dossier.append(status);
    if (record.category === 'policies' || record.window) {
      const time = node('p', 'window-note', windowStatus(record, today));
      if (record.window) time.append(node('span', 'muted', `；原文日期：${validDay(record.window.start) ? record.window.start : '开始待确认'} → ${validDay(record.window.end) ? record.window.end : '结束待确认'}`));
      dossier.append(time);
    }
    const fields = node('dl', 'field-list');
    array(record.fields).forEach(field => {
      const row = node('div', 'field-row');
      row.append(node('dt', '', field.label || field.key));
      const value = node('dd', 'field-value');
      const url = safeURL(field.value);
      if (url) value.append(sourceLink({ url, label: field.value }));
      else value.append(node('div', 'preserve-lines', field.value || '未提供'));
      const refs = node('div', 'field-provenance');
      const sourceIds = array(field.source_ids);
      if (!sourceIds.length) refs.append(node('span', '', '未关联字段来源'));
      sourceIds.forEach(id => {
        const source = array(record.sources).find(item => item.id === id);
        const ref = node('span', 'field-reference');
        ref.append(node('span', 'utility', `${id} · `));
        if (source) ref.append(sourceLink(source), node('span', '', ` [${['A', 'B', 'C'].includes(source.grade) ? source.grade : '未标等级'}]`));
        else ref.append(node('span', '', '来源缺失'));
        refs.append(ref);
      });
      refs.append(node('span', '', field.verified_at ? `字段核验：${field.verified_at}` : '字段未核验'));
      value.append(refs);
      if (field.verified_at && field.verification) value.append(proofBlock(record, field.verification));
      row.append(value);
      fields.append(row);
    });
    if (!array(record.fields).length) fields.append(node('div', 'muted', '尚无结构化字段。请查看原始来源。'));
    dossier.append(fields);
    Object.entries(record.metadata_verification || {}).forEach(([key, proof]) => {
      const label = { title: '名称', access: '接入方式', lifecycle: '收录状态', 'window.kind': '日期类型', 'window.start': '开始日期', 'window.end': '结束日期' }[key] || key;
      appendText(dossier, 'h4', 'dossier-label', `${label}核验 · ${proof.verified_at}`);
      dossier.append(proofBlock(record, proof));
    });
    if (array(record.tags).length) dossier.append(node('p', 'record-tags', array(record.tags).join(' · ')));
    if (array(record.notes).length) {
      appendText(dossier, 'h4', 'dossier-label', '条目备注');
      const notes = node('ul', 'notes-list');
      array(record.notes).forEach(note => notes.append(node('li', 'preserve-lines', note)));
      dossier.append(notes);
    }
    const sourceDetails = node('details', 'source-details');
    sourceDetails.append(node('summary', '', `原始来源与适用范围 · ${array(record.sources).length}`));
    const sources = node('ol', 'source-list');
    array(record.sources).forEach(source => {
      const item = node('li');
      const heading = node('div', 'source-heading');
      heading.append(node('span', 'utility', `${source.id || '未编号'} / ${['A', 'B', 'C'].includes(source.grade) ? source.grade : '未标等级'}`), sourceLink(source));
      item.append(heading, node('p', 'muted preserve-lines', `适用范围：${source.scope || '未标注'}`));
      const url = safeURL(source.url);
      if (url) item.append(node('p', 'source-address utility', url));
      sources.append(item);
    });
    sourceDetails.append(node('p', 'filter-help', '来源等级沿用汇编标注，不代表已核验。字段核验请看字段旁的记录。'), sources);
    if (!array(record.sources).length) sourceDetails.append(node('p', 'muted', '未附原始来源，使用前需要补证。'));
    dossier.append(sourceDetails);
    appendText(dossier, 'h4', 'dossier-label', '时间与出处');
    const dates = node('dl', 'date-metadata');
    pair(dates, '原文截至', record.reported_as_of || '未提供');
    pair(dates, '首次导入', record.imported_at || '未记录');
    pair(dates, '内容变更', record.updated_at || '暂无变更记录');
    pair(dates, '最近核验', record.last_verified_at || '未核验');
    if (record.origin?.file) pair(dates, '导入来源', record.origin.file);
    if (record.origin?.row_at_import) pair(dates, '导入前行号', record.origin.row_at_import);
    dossier.append(dates);
    const related = array(record.related_ids).map(id => byId.get(text(id))).filter(Boolean);
    if (related.length) {
      const links = node('div', 'related-links');
      links.append(node('span', 'dossier-label', '关联条目'));
      related.forEach(item => links.append(recordLink(item, item.title, 'text-link')));
      dossier.append(links);
    }
    const history = node('details', 'record-history');
    history.append(node('summary', '', '此条目变更记录'));
    const historyList = node('ul', 'history-list');
    array(record.history).forEach(item => historyList.append(historyRow(record, item)));
    if (!array(record.history).length) historyList.append(node('li', 'muted', '暂无记录。导入时间不等于核验时间。'));
    history.append(historyList);
    dossier.append(history);
    return dossier;
  }

  function makeRow(record) {
    const details = node('details', 'record-row');
    details.id = `record-${encodeURIComponent(text(record.id))}`;
    details.dataset.recordId = text(record.id);
    const summary = node('summary', 'record-summary');
    const main = node('span', 'record-main');
    const name = node('span', 'record-title', record.title || '未命名条目');
    main.append(name);
    if (record.lifecycle === 'historical') main.append(node('span', 'historical-label', '历史记录'));
    const brief = fieldValue(record, record.category === 'policies' ? 'benefit' : record.category === 'platforms' ? 'format' : 'use') || fieldValue(record, 'capabilities');
    main.append(node('span', 'record-brief', brief || '展开查看条件与原始出处'));
    const fact = node('span', 'record-fact');
    if (record.category === 'policies') {
      fact.append(node('span', '', ACCESS[record.access] || ACCESS.unknown), node('span', 'fact-secondary', windowStatus(record, today)));
    } else if (record.category === 'models') {
      fact.append(node('span', '', fieldValue(record, 'api') || 'API 情况待确认'), node('span', 'fact-secondary', fieldValue(record, 'company')));
    } else if (record.category === 'tools') {
      fact.append(node('span', '', fieldValue(record, 'environment') || '环境待确认'), node('span', 'fact-secondary', fieldValue(record, 'price')));
    } else {
      fact.append(node('span', '', fieldValue(record, 'market') || record.group), node('span', 'fact-secondary', ACCESS[record.access] || ACCESS.unknown));
    }
    const evidence = node('span', 'record-evidence');
    const grades = [...new Set(array(record.sources).map(source => source.grade).filter(grade => ['A', 'B', 'C'].includes(grade)))].sort();
    evidence.append(node('span', 'source-grade', grades.length ? `来源 ${grades.join(' / ')}` : '来源未分级'), node('span', 'verification-state', verificationLabel(record)));
    const expand = node('span', 'expand-mark', '+');
    expand.setAttribute('aria-hidden', 'true');
    summary.append(main, fact, evidence, expand);
    details.append(summary);
    let built = false;
    const ensureDossier = () => { if (!built) { details.append(makeDossier(record)); built = true; } };
    // Build on interaction, not in bulk; the index stays light even with many entries.
    details.addEventListener('toggle', () => {
      if (!details.isConnected) return;
      if (details.open) {
        ensureDossier();
        state.id = text(record.id);
        persist();
      } else if (state.id === text(record.id)) { state.id = ''; persist(); }
    });
    if (state.id === text(record.id)) { ensureDossier(); details.open = true; }
    rowById.set(text(record.id), details);
    return details;
  }

  function fillSelect(select, values, selected, fallback) {
    select.replaceChildren(node('option', '', fallback));
    select.firstChild.value = '';
    values.forEach(value => { const option = node('option', '', value); option.value = value; select.append(option); });
    if (selected && !values.includes(selected)) { const option = node('option', '', `${selected}（当前无条目）`); option.value = selected; select.append(option); }
    select.value = selected || '';
  }

  function updateControls() {
    const categoryRecords = records.filter(record => record.category === state.category);
    const groups = [...new Set(categoryRecords.map(record => text(record.group)).filter(Boolean))];
    fillSelect($('group'), groups, state.group, '全部分组');
    fillSelect($('environment'), [...new Set(records.filter(record => record.category === 'tools').flatMap(environments))].sort((a, b) => a.localeCompare(b, 'zh-CN')), state.environment, '全部环境');
    $('group-control').hidden = state.category === 'all';
    $('api-control').hidden = state.category !== 'models';
    $('lifecycle-control').hidden = state.category !== 'models';
    $('environment-control').hidden = state.category !== 'tools';
    FILTERS.forEach(key => { $(key === 'q' ? 'search' : key).value = state[key] || ''; });
    document.querySelectorAll('.category-link').forEach(link => {
      const active = link.dataset.category === state.category;
      if (active) link.setAttribute('aria-current', 'page'); else link.removeAttribute('aria-current');
      link.href = queryFor({ ...state, category: link.dataset.category, group: '', api: '', environment: '', lifecycle: '', id: '' });
    });
    $('directory-title').textContent = CATEGORIES[state.category][0];
    $('category-kicker').textContent = CATEGORIES[state.category][1];
  }

  function renderDeadlines() {
    const relevant = currentMatches.filter(record => record.category === 'policies' || record.window);
    const events = deadlineEvents(relevant, today);
    $('deadline-panel').hidden = !relevant.length;
    $('deadline-count').textContent = `${events.length} 个未来 / 当日节点`;
    $('deadline-context').textContent = `按上海日期 ${today} 重算，基于当前筛选。这里只提示原文日期，不确认当前可申请。`;
    const list = $('deadline-list');
    list.replaceChildren();
    events.forEach(event => {
      const item = node('li', 'deadline-event');
      item.append(node('time', 'utility', event.date), recordLink(event.record, event.record.title), node('span', 'event-kind', event.label), node('span', 'muted', `${ACCESS[event.record.access] || ACCESS.unknown} · ${verificationLabel(event.record)}`));
      list.append(item);
    });
    if (!events.length) list.append(node('li', 'muted', '当前筛选中没有已知的未来日期节点。可展开条目查看已结束的时间窗口。'));
    const unknown = relevant.filter(record => !validDay(record.window?.start) || !validDay(record.window?.end)).length;
    $('deadline-unknown').textContent = unknown ? `${unknown} 条记录缺少完整起止日期。日期未知不代表滚动开放。` : '申报、激励、签约、有效期分别标注，不混作申报截止。';
  }

  function renderDocuments() {
    const target = $('document-notes');
    target.replaceChildren();
    const documents = array(doc.documents).filter(item => state.category === 'all' || item.category === state.category);
    documents.forEach(item => {
      const details = node('details', 'document-note');
      details.append(node('summary', '', `${CATEGORIES[item.category]?.[0] || '汇编'} / ${item.title || '原文附注'}`));
      const body = node('div', 'document-note-body');
      const prose = array(item.blocks).filter(block => block.type === 'text' && text(block.text).trim());
      prose.forEach(block => body.append(node('p', 'preserve-lines', block.text)));
      if (!prose.length) body.append(node('p', 'muted', '本篇未附文字说明。表格内容请查阅资源条目。'));
      details.append(body);
      target.append(details);
    });
    if (!documents.length) target.append(node('p', 'muted', '当前分类暂无汇编附注。'));
  }

  function renderMaintenance() {
    const maintenance = doc.maintenance || {};
    const metadata = node('dl', 'date-metadata');
    const coverage = maintenance.coverage || {};
    pair(metadata, '巡检统计生成', maintenance.generated_at || '尚未生成');
    pair(metadata, '最近读回正文日期', maintenance.last_success_day || '尚无成功读回');
    pair(metadata, '统计日期（北京时间）', maintenance.day || '尚无统计');
    pair(metadata, '统计日尝试 / 全部来源', `${coverage.sources_attempted_today ?? 0} / ${coverage.total_sources ?? '未知'}`);
    pair(metadata, '统计日读回正文', coverage.sources_inspected_today ?? 0);
    pair(metadata, '从未读回正文', coverage.sources_never_inspected ?? '未知');
    pair(metadata, '待审正文版本', maintenance.pending_count ?? 0);
    pair(metadata, '需人工查看的来源', maintenance.manual_required_count ?? 0);
    pair(metadata, '抓取失败的来源', maintenance.failure_count ?? 0);
    $('maintenance').append(node('p', 'filter-help', '每日限量轮转，不代表全库每天复核。正文读回、网页变化、人工事实核验分开记录；机器离线时不能保证当日执行。'), metadata);
    const changes = records.flatMap(record => array(record.history).map(item => ({ record, item })));
    changes.sort((a, b) => text(b.item.at).localeCompare(text(a.item.at)));
    const sections = [ ['correction', '内容纠正'], ['review', '核验记录'], ['import', '汇编导入 / 迁移（不算内容纠正）'] ];
    sections.forEach(([kind, title]) => {
      const items = changes.filter(change => change.item.kind === kind);
      const details = node('details', 'change-group');
      details.append(node('summary', '', `${title} · ${items.length}`));
      const list = node('ul', 'history-list');
      items.forEach(({ record, item }) => {
        const li = node('li');
        li.append(node('span', 'utility', item.at || '时间未记录'), recordLink(record, record.title), node('p', 'preserve-lines', item.summary || '未提供说明'));
        list.append(li);
      });
      if (!items.length) list.append(node('li', 'muted', '暂无记录。'));
      details.append(list);
      $('change-list').append(details);
    });
  }

  function reset(category = 'all') {
    state = readState(`?category=${encodeURIComponent(category)}`);
    render();
    persist(true);
  }

  function render(focusRecord = false) {
    updateControls();
    currentMatches = records.filter(record => matches(record, state));
    $('result-count').textContent = `${currentMatches.length} 条匹配 · 展开条目查看条件与出处`;
    const list = $('record-list');
    list.replaceChildren();
    rowById.clear();
    const groups = new Map();
    currentMatches.forEach(record => {
      const key = `${record.category}\u0000${record.group || '未分组'}`;
      if (!groups.has(key)) groups.set(key, { category: record.category, name: record.group || '未分组', records: [] });
      groups.get(key).records.push(record);
    });
    const ordered = [...groups.values()].sort((a, b) => Object.keys(CATEGORIES).indexOf(a.category) - Object.keys(CATEGORIES).indexOf(b.category));
    ordered.forEach(group => {
      const section = node('section', 'index-group');
      const heading = node('div', 'group-heading');
      heading.append(node('h3', '', `${state.category === 'all' ? `${CATEGORIES[group.category][0]} / ` : ''}${group.name}`), node('span', 'utility', `${group.records.length} 条`));
      section.append(heading);
      group.records.forEach(record => section.append(makeRow(record)));
      list.append(section);
    });
    if (!currentMatches.length) {
      const empty = node('div', 'empty-state');
      empty.append(node('h3', '', '没有找到匹配的资源'), node('p', '', '减少关键词，或重置筛选后重新选择分类。多个关键词需要同时匹配。'));
      const button = node('button', 'primary-button', '重置全部筛选');
      button.type = 'button';
      button.addEventListener('click', () => { reset(); $('search').focus(); });
      empty.append(button);
      list.append(empty);
    }
    const notice = $('deep-link-notice');
    notice.replaceChildren();
    if (state.id && !rowById.has(state.id)) {
      const message = node('div', 'deep-link-message');
      message.append(node('p', '', byId.has(state.id) ? '链接中的条目不符合当前筛选。' : '没有找到此链接对应的条目，可重置筛选后搜索。'));
      if (byId.has(state.id)) message.append(recordLink(byId.get(state.id), '清除筛选并查看该条目', 'text-link'));
      notice.append(message);
    }
    renderDeadlines();
    renderDocuments();
    if (focusRecord && rowById.has(state.id)) {
      const row = rowById.get(state.id);
      requestAnimationFrame(() => {
        row.querySelector('summary').focus({ preventScroll: true });
        row.scrollIntoView({ block: 'start', behavior: 'auto' });
      });
    }
  }

  document.querySelectorAll('.category-link').forEach(link => link.addEventListener('click', event => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    state = readState(link.search);
    render();
    persist(true);
  }));
  $('filters').addEventListener('submit', event => { event.preventDefault(); state.q = $('search').value; state.id = ''; render(); persist(); });
  $('search').addEventListener('input', () => { state.q = $('search').value; state.id = ''; render(); persist(); });
  $('filters').addEventListener('change', event => {
    if (event.target.tagName !== 'SELECT') return;
    state[event.target.name] = event.target.value;
    state.id = '';
    render();
    persist(true);
  });
  $('reset').addEventListener('click', () => { reset(); $('search').focus(); });
  window.addEventListener('popstate', () => { state = readState(window.location.search, window.location.pathname); render(Boolean(state.id)); });
  // Recompute across Shanghai midnight, including a tab resumed after suspension.
  function refreshDay() {
    const nextDay = shanghaiDay();
    if (nextDay !== today) { today = nextDay; render(); }
  }
  window.setInterval(refreshDay, 60000);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) refreshDay(); });
  renderMaintenance();
  render(Boolean(state.id));
  persist();
}());
