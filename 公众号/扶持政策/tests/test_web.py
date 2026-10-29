"""Frontend contract/security tests; Node exercises the same helpers as the browser."""
import importlib.util
import json
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('resource_web', ROOT / 'web.py')
web = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(web)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.attrs = []
        self.embedded = ''
        self.in_data = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        self.attrs.append((tag, attrs))
        if tag == 'script' and attrs.get('id') == 'catalog-data':
            self.in_data = True

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_data = False

    def handle_data(self, data):
        if self.in_data:
            self.embedded += data


def record(**changes):
    result = {
        'id': 'local-policy', 'entity_id': 'local', 'category': 'policies',
        'kind': 'policy', 'title': '地方扶持', 'group': '政府扶持',
        'fields': [{'key': 'benefit', 'label': '支持', 'value': '按条件申报', 'source_ids': ['s1'], 'verified_at': None}],
        'sources': [{'id': 's1', 'url': 'https://example.com/policy?q=1&x=2', 'grade': 'A', 'label': '政策原文', 'scope': '支持条件'}],
        'tags': [], 'access': 'public', 'lifecycle': 'listed',
        'window': {'kind': 'application', 'start': '2026-10-29', 'end': '2026-10-29'},
        'reported_as_of': '2026-10-29', 'imported_at': '2026-10-29T18:00:00+08:00',
        'updated_at': None, 'last_verified_at': None, 'notes': [], 'related_ids': [],
        'history': [{'kind': 'import', 'at': '2026-10-29T18:00:00+08:00', 'summary': '首次迁移'}],
        'provenance': {'file': '原始汇编.md', 'row': 42},
    }
    result.update(changes)
    return result


def document(records=None):
    return {'title': '短剧资料库', 'schema_version': 1, 'reported_as_of': '2026-10-29',
            'records': [record()] if records is None else records,
            'documents': [{'title': '制作工具汇编', 'category': 'tools', 'blocks': [{'type': 'text', 'text': '保留的原始说明'}]}]}


class RenderTests(unittest.TestCase):
    def test_complete_local_document_and_legacy_entry(self):
        output = web.render(document())
        parser = PageParser()
        parser.feed(output)
        self.assertTrue(output.startswith('<!doctype html>'))
        self.assertIn('做短剧，<br>先把信息查明白。', output)
        self.assertIn(('script', {'src': '/catalog.js', 'defer': None}), parser.attrs)
        self.assertIn(('link', {'rel': 'stylesheet', 'href': '/catalog.css'}), parser.attrs)
        self.assertIn('href="/policies.html"', output)
        self.assertIn('扶持台账', output)
        categories = [attrs['data-category'] for _, attrs in parser.attrs if 'data-category' in attrs]
        self.assertEqual(categories, ['all', 'policies', 'platforms', 'models', 'tools'])
        self.assertEqual(json.loads(parser.embedded), document())

    def test_render_does_not_mutate_input(self):
        doc = document()
        before = json.dumps(doc, ensure_ascii=False)
        web.render(doc)
        self.assertEqual(json.dumps(doc, ensure_ascii=False), before)

    def test_html_escape(self):
        self.assertEqual(web.esc('<a x="x">&\''), '&lt;a x=&quot;x&quot;&gt;&amp;&#x27;')
        self.assertEqual(web.esc(None), '')

    def test_json_script_injection_roundtrip(self):
        attack = '</script><img src=x onerror="alert(1)"><script>bad\u2028\u2029&'
        doc = document([record(title=attack, notes=[attack], provenance={'file': attack, 'row': 1})])
        doc['title'] = attack
        doc['reported_as_of'] = attack
        doc['documents'][0]['blocks'][0]['text'] = attack
        output = web.render(doc)
        parser = PageParser()
        parser.feed(output)
        self.assertEqual(parser.tags.count('script'), 2)
        self.assertNotIn('img', parser.tags)
        self.assertNotIn('<', parser.embedded)
        self.assertNotIn('&', parser.embedded)
        self.assertNotIn('\u2028', parser.embedded)
        self.assertEqual(json.loads(parser.embedded), doc)
        self.assertIn('&lt;/script&gt;', output)

    def test_safe_source_url_allowlist(self):
        for url in ['https://example.com/a?x=1&y=2', 'http://example.com', 'HTTPS://example.com/path', 'https://example.com/#section']:
            with self.subTest(url=url):
                self.assertEqual(web.safe_url(url), url)
        for url in [None, '', 'javascript:alert(1)', 'data:text/html,x', '//example.com', '/relative',
                    'https:///example.com', 'https://example.com\\@evil.test',
                    'https://user:pass@example.com', 'https://@example.com',
                    ' https://example.com', 'https://example.com\n', 'https://example.com:bad',
                    'https://[broken', 'https://example.com/\x00test', 'file:///etc/passwd']:
            with self.subTest(url=url):
                self.assertIsNone(web.safe_url(url))

    def test_fallback_does_not_link_unsafe_urls(self):
        doc = document([record(title='<img onerror=bad>', sources=[
            {'id': 'evil', 'url': 'javascript:alert(1)', 'label': '<script>bad</script>', 'grade': '\" onclick=bad'},
            {'id': 'good', 'url': 'https://example.com/?q=%22&x=2', 'label': '官网', 'grade': 'A'},
        ])])
        output = web.render(doc)
        parser = PageParser()
        parser.feed(output)
        hrefs = [attrs['href'] for _, attrs in parser.attrs if 'href' in attrs]
        self.assertFalse(any(href.startswith('javascript:') for href in hrefs))
        self.assertNotIn('img', parser.tags)
        self.assertIn('无安全可用链接', output)
        self.assertIn('https://example.com/?q=%22&x=2', hrefs)
        self.assertIn('未核验', output)
        self.assertIn('来源等级不代表核验状态', output)

    def test_noscript_and_empty_document(self):
        output = web.render(document([]))
        self.assertIn('<noscript>', output)
        self.assertIn('无法使用筛选与实时日期提醒', output)
        self.assertIn('资料尚未收录', output)
        self.assertIn('role="status"', output)
        self.assertIn('aria-live="polite"', output)
        self.assertIn('class="skip-link"', output)

    def test_asset_security_and_accessibility_invariants(self):
        js = (ROOT / 'static/catalog.js').read_text()
        css = (ROOT / 'static/catalog.css').read_text()
        self.assertNotIn('innerHTML', js)
        self.assertNotIn('insertAdjacentHTML', js)
        self.assertNotIn('fetch(', js)
        self.assertIn('textContent', js)
        self.assertIn("node('details'", js)
        self.assertIn('prefers-reduced-motion', css)
        self.assertIn(':focus-visible', css)
        self.assertIn('@media (max-width: 720px)', css)
        self.assertEqual(css.count('{'), css.count('}'))
        for colour in ['#f3eee4', '#fffaf0', '#2c2925', '#ae422c', '#28695e', '#d4c9b8']:
            self.assertIn(colour, css)


@unittest.skipUnless(shutil.which('node'), 'Node required for browser-helper tests')
class BrowserLogicTests(unittest.TestCase):
    def run_js(self, script):
        prelude = (f'const h = require({json.dumps(str(ROOT / "static/catalog.js"))});\n'
                   'const assert = require("node:assert/strict");\n'
                   f'const base = {json.dumps(record(), ensure_ascii=False)};\n'
                   'const state = h.readState("?category=all");\n')
        result = subprocess.run(['node', '-e', prelude + script], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_and_token_search(self):
        self.run_js('''
const r = {...base, title: '杭州视频扶持', fields: [{key:'benefit', label:'补助', value:'公开项目，个人可申请'}]};
assert.equal(h.matches(r, {...state, q:'杭州 个人'}), true);
assert.equal(h.matches(r, {...state, q:'杭州 北京'}), false);
assert.equal(h.matches(r, {...state, q:'  杭州   视频  '}), true);
assert.equal(h.matches({...r, title:'API Video'}, {...state, q:'api VIDEO'}), true);
assert.equal(h.matches(r, {...state, q:'<script>'}), false);
''')

    def test_category_specific_groups(self):
        self.run_js('''
assert.equal(h.matches(base, {...state, category:'policies', group:'政府扶持'}), true);
assert.equal(h.matches(base, {...state, category:'policies', group:'平台扶持'}), false);
assert.equal(h.matches(base, {...state, category:'tools'}), false);
assert.equal(h.matches(base, {...state, group:'国内'}), true);
assert.equal(h.readState('?category=all&group=国内').group, '');
''')

    def test_grades_do_not_imply_verification(self):
        self.run_js('''
assert.equal(h.verification(base), 'unverified');
assert.equal(h.matches(base, {...state, grade:'A', verification:'unverified'}), true);
assert.equal(h.matches(base, {...state, grade:'A', verification:'verified'}), false);
assert.equal(h.matches(base, {...state, grade:'B'}), false);
assert.equal(h.matches({...base, sources:[]}, {...state, grade:'unknown'}), true);
assert.equal(h.verification({...base, history:[{kind:'review', at:'2026-10-30'}]}), 'unverified');
assert.equal(h.verification({...base, fields:[{verified_at:'2026-10-30'}]}), 'partial');
assert.equal(h.verification({...base, last_verified_at:'2026-10-30'}), 'verified');
assert.equal(h.verification({...base, metadata_verification:{access:{verified_at:'2026-10-30'}}}), 'partial');
''')

    def test_legacy_policy_path_defaults_to_policies(self):
        self.run_js('''
assert.equal(h.readState('', '/policies.html').category, 'policies');
assert.equal(h.readState('', '/policies').category, 'policies');
assert.equal(h.readState('', '/').category, 'all');
assert.equal(h.readState('?category=tools', '/policies.html').category, 'tools');
''')

    def test_model_api_uses_positive_evidence_not_api_substring(self):
        self.run_js('''
const model = value => ({...base, category:'models', fields:[{key:'api', value}]});
for (const value of ['无官方API', '无官方 API', 'API 待确认', '暂不支持 API', '未开源', '非开源', '闭源', '✓ 暂不支持 API']) {
  assert.deepEqual(h.apiSupport(model(value)), {api:false, open:false}, value);
  assert.equal(h.matches(model(value), {...state, category:'models', api:'available'}), false, value);
}
for (const value of ['✓ 官方 API', '✓', '✓ API / 部分地区可用']) {
  assert.equal(h.apiSupport(model(value)).api, true, value);
}
assert.deepEqual(h.apiSupport(model('开源，可本地部署')), {api:false, open:true});
assert.equal(h.matches(model('无官方API / 开源'), {...state, category:'models', api:'available'}), true);
assert.equal(h.matches(model('无官方API / 开源'), {...state, category:'models', api:'api'}), false);
assert.equal(h.matches(model('开源'), {...state, category:'models', api:'open'}), true);
assert.deepEqual(h.apiSupport({...base, title:'✓ API', fields:[{key:'capabilities', value:'✓ API'}]}), {api:false, open:false});
''')

    def test_tools_environment_is_not_inferred_from_api(self):
        self.run_js('''
const tool = {...base, category:'tools', fields:[{key:'type',value:'API 工具'}, {key:'environment',value:'Web / macOS、Windows'}, {key:'api',value:'✓'}]};
assert.deepEqual(h.environments(tool), ['Web', 'macOS', 'Windows']);
assert.equal(h.matches(tool, {...state, category:'tools', environment:'Web'}), true);
assert.equal(h.matches(tool, {...state, category:'tools', environment:'API'}), false);
assert.equal(h.matches(tool, {...state, category:'tools', api:'other'}), true);
assert.equal(h.readState('?category=tools&api=available').api, '');
assert.equal(h.readState('?category=models&environment=Web').environment, '');
''')

    def test_historical_lifecycle_is_explicit_not_guessed_from_title(self):
        self.run_js('''
const veo = {...base, category:'models', title:'Veo 3.1', lifecycle:'listed', fields:[{key:'api',value:'✓ 部分地区'}]};
assert.equal(h.matches(veo, {...state, category:'models', lifecycle:'listed'}), true);
assert.equal(h.matches(veo, {...state, category:'models', lifecycle:'historical'}), false);
assert.equal(h.matches({...veo, lifecycle:'historical'}, {...state, category:'models', lifecycle:'historical'}), true);
''')

    def test_shanghai_day_and_date_validation(self):
        self.run_js('''
assert.equal(h.shanghaiDay(new Date('2026-10-29T15:59:59Z')), '2026-10-29');
assert.equal(h.shanghaiDay(new Date('2026-10-29T16:00:00Z')), '2026-10-30');
assert.equal(h.validDay('2026-02-30'), false);
assert.equal(h.validDay('2026-10-29'), true);
assert.equal(h.validDay('2024-02-29'), true);
assert.equal(h.validDay(null), false);
''')

    def test_same_day_events_are_not_deduplicated(self):
        self.run_js('''
const second = {...base, id:'other', title:'另一个扶持'};
const events = h.deadlineEvents([base, second], '2026-10-29');
assert.equal(events.length, 4);
assert.equal(events.filter(e => e.edge === 'end').length, 2);
assert.equal(h.deadlineEvents([base, second], '2026-10-30').length, 0);
assert.equal(h.deadlineEvents([{...base, window:null}], '2026-10-29').length, 0);
assert.match(h.windowStatus(base, '2026-10-29'), /今日.*截止/);
assert.match(h.windowStatus(base, '2026-10-30'), /已结束/);
''')

    def test_window_kinds_remain_distinct(self):
        self.run_js('''
for (const [kind, label] of Object.entries({application:'申报期', incentive:'激励期', contract:'签约期', validity:'政策有效期'})) {
  const r = {...base, window:{kind, start:'2026-10-29', end:'2026-11-01'}};
  assert.equal(h.windowKind(r), label);
  assert.ok(h.windowStatus(r, '2026-10-29').includes(label));
  const labels = h.deadlineEvents([r], '2026-10-29').map(e => e.label).join(' ');
  if (kind !== 'application') assert.ok(!labels.includes('申报'));
}
''')

    def test_invitation_is_never_public_application(self):
        self.run_js('''
const invitation = {...base, access:'invitation'};
assert.equal(h.windowKind(invitation), '定向邀约期');
assert.ok(!h.windowStatus(invitation, '2026-10-29').includes('申报'));
assert.equal(h.matches(invitation, {...state, access:'public'}), false);
assert.equal(h.matches(invitation, {...state, access:'invitation'}), true);
assert.equal(h.windowKind({...base, access:'unknown'}), '申请时间（入口待确认）');
''')

    def test_missing_dates_are_unknown_not_rolling(self):
        self.run_js('''
for (const window of [null, {kind:'application', start:null, end:null}, {kind:'application', start:'not-a-date', end:null}]) {
  assert.equal(h.windowStatus({...base, window}, '2026-10-29'), '时间待确认');
}
assert.match(h.windowStatus({...base, window:{kind:'incentive', start:'2026-10-01', end:null}}, '2026-10-29'), /结束时间待确认/);
''')

    def test_url_filters_and_deep_link_roundtrip(self):
        self.run_js('''
const before = h.readState('?category=models&id=含空格%20%26%3Cscript%3E&q=视频%20生成&group=视频生成&grade=A&verification=unverified&access=business&api=available&lifecycle=historical');
assert.deepEqual(h.readState(h.queryFor(before)), before);
assert.equal(h.readState('?category=policies&id=abc').id, 'abc');
assert.equal(h.readState('?category=__proto__').category, 'all');
assert.equal(h.readState('?category=constructor').category, 'all');
assert.equal(h.readState('?category=models&grade=BAD&api=unknown').grade, '');
assert.equal(h.readState('?category=models&grade=BAD&api=unknown').api, '');
''')

    def test_client_source_url_allowlist(self):
        self.run_js('''
for (const value of ['javascript:alert(1)', 'data:text/html,x', '//evil.test', '/path', 'https:///example.com', 'https://user:pass@example.com', 'https://@example.com', 'https://example.com:bad', 'https://example.com\\n', 'https://example.com\\\\@evil.test', null]) {
  assert.equal(h.safeURL(value), null, String(value));
}
assert.equal(h.safeURL('https://example.com/a?b=1&c=2'), 'https://example.com/a?b=1&c=2');
assert.equal(h.safeURL('http://example.com'), 'http://example.com/');
''')


if __name__ == '__main__':
    unittest.main()
