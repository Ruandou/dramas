import copy
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import import_catalog
from catalog import load, markdown_exports, review, safe_url, validate, value, window_state
from import_catalog import identity, sources


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        live = load()
        # Replay immutable migration inputs, not the subsequently maintained records.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            materials = root / '素材'
            materials.mkdir()
            (root / 'data').mkdir()
            for document in live['documents']:
                (materials / document['filename']).write_text(
                    document['provenance']['original_text'], encoding='utf-8')
            (root / 'data' / 'policy.yaml').write_text(
                live['migration_archive']['policy_yaml'], encoding='utf-8')
            (materials / '扶持政策台账.md').write_text(
                live['migration_archive']['ledger_markdown'], encoding='utf-8')
            with patch.object(import_catalog, 'MATERIALS', materials), \
                 patch.object(import_catalog, 'ROOT', root):
                records, documents = [], []
                for filename in import_catalog.CONFIG:
                    imported, document = import_catalog.import_document(filename, live['imported_at'])
                    records.extend(imported)
                    documents.append(document)
                policies, archive = import_catalog.import_policies(live['imported_at'])
                records = policies + records
                import_catalog.relate(records)
        doc = {key: live[key] for key in ('schema_version', 'title', 'reported_as_of', 'imported_at')}
        doc.update(documents=documents, records=records, migration_archive=archive)
        cls.doc = validate(doc)
        cls.by_id = {r['id']: r for r in cls.doc['records']}

    def test_live_catalog_validates(self):
        doc = load()
        self.assertIs(validate(doc), doc)

    def test_import_coverage(self):
        self.assertEqual(Counter(r['kind'] for r in self.doc['records']),
                         {'policy': 15, 'place': 71, 'platform': 73, 'model': 91, 'tool-use': 80})
        self.assertEqual(len({r['id'] for r in self.doc['records']}), 330)
        self.assertTrue(all(not r['last_verified_at'] for r in self.doc['records']))
        self.assertTrue(all(not f['verified_at'] for r in self.doc['records'] for f in r['fields']))

    def test_migration_is_not_verification(self):
        for r in self.doc['records']:
            self.assertEqual(r['history'][0]['kind'], 'import')
            self.assertTrue(r['provenance'])
            self.assertTrue(all(s['scope'] for s in r['sources']))
        self.assertIn('ledger_markdown', self.doc['migration_archive'])

    def test_unknown_deadline_is_not_rolling(self):
        self.assertEqual(window_state(self.by_id['sz-2025'], '2026-10-29'), 'unknown')
        self.assertEqual(window_state(self.by_id['wx-novel'], '2026-10-29'), 'upcoming')
        self.assertEqual(self.by_id['wx-novel']['access'], 'invitation')
        self.assertEqual(self.by_id['wx-q4']['window']['kind'], 'incentive')

    def test_inclusive_deadline(self):
        self.assertEqual(window_state(self.by_id['sh-2026'], '2026-11-18'), 'current')
        self.assertEqual(window_state(self.by_id['sh-2026'], '2026-11-19'), 'ended')

    def test_window_without_start_or_end_is_unknown(self):
        record = copy.deepcopy(self.by_id['sh-2026'])
        record['window'] = {'kind': 'application', 'start': None, 'end': None}
        self.assertEqual(window_state(record, '2026-10-29'), 'unknown')

    def test_specific_corrections(self):
        self.assertNotIn('30%', value(self.by_id['sz-2025'], 'benefit'))
        self.assertIn('园区最高500', value(self.by_id['sz-2025'], 'benefit'))
        self.assertEqual(self.by_id['dy-guarantee']['sources'][0]['grade'], 'B')
        self.assertIn('不超过40元', value(self.by_id['hq-2026'], 'benefit'))

    def test_explicit_lifecycle_not_substring(self):
        records = {r['title']: r for r in self.doc['records']}
        self.assertEqual(records['Veo 3.1']['lifecycle'], 'listed')
        self.assertEqual(records['Veo 3']['lifecycle'], 'historical')
        self.assertEqual(records['DramaWave']['lifecycle'], 'listed')
        self.assertIn('未查到', value(records['GoodShort'], 'entry'))

    def test_shared_product_not_duplicate_count(self):
        comfy = [r for r in self.doc['records'] if r['kind'] == 'tool-use' and r['title'].startswith('ComfyUI')]
        self.assertEqual(len(comfy), 3)
        self.assertEqual(len({r['entity_id'] for r in comfy}), 1)
        self.assertTrue(all(len(r['related_ids']) >= 2 for r in comfy))

    def test_related_policies(self):
        sz = self.by_id['sz-2025']
        self.assertTrue(sz['related_ids'])
        other = self.by_id[sz['related_ids'][0]]
        self.assertIn('sz-2025', other['related_ids'])

    def test_generated_exports_do_not_claim_all_verified(self):
        exports = markdown_exports(self.doc)
        self.assertEqual(len(exports), 5)
        self.assertIn('0/', exports['模型清单.md'])
        self.assertNotIn('逐行复核 91 条', exports['模型清单.md'])
        self.assertIn('500万元', exports['扶持政策台账.md'])
        self.assertIn('腾讯智影', exports['工具清单.md'])
        self.assertIn('检索空档', exports['短剧政策地图.md'])

    def test_validation_rejects_broken_references(self):
        broken = copy.deepcopy(self.doc)
        broken['records'][0]['related_ids'].append('missing')
        with self.assertRaises(ValueError):
            validate(broken)
        broken = copy.deepcopy(self.doc)
        broken['records'][0]['fields'][0]['source_ids'] = ['missing']
        with self.assertRaises(ValueError):
            validate(broken)

    def test_cannot_fake_verification(self):
        broken = copy.deepcopy(self.doc)
        broken['records'][0]['fields'][0]['verified_at'] = '2026-10-29T12:00:00+08:00'
        with self.assertRaises(ValueError):
            validate(broken)
        broken = copy.deepcopy(self.doc)
        broken['records'][0]['last_verified_at'] = '2026-10-29T12:00:00+08:00'
        with self.assertRaises(ValueError):
            validate(broken)

    def test_review_audits_before_after_and_partial(self):
        doc = copy.deepcopy(self.doc)
        r = doc['records'][0]
        f = r['fields'][0]
        before = f['value']
        review(doc, r['id'], f['key'], r['sources'][0]['id'], '测试用原文摘录', '测试值', '仅单元测试，不改底库')
        self.assertEqual(r['history'][-1]['before'], before)
        self.assertEqual(r['history'][-1]['after'], '测试值')
        self.assertIsNone(r['last_verified_at'])
        self.assertTrue(f['verified_at'])
        self.assertTrue(r['updated_at'])

    def test_complete_review_uses_oldest_proof_time(self):
        for oldest_key in ('benefit', 'title'):
            with self.subTest(oldest_key=oldest_key):
                doc = copy.deepcopy(self.doc)
                r = next(r for r in doc['records'] if r['id'] == 'sh-2026')
                keys = [f['key'] for f in r['fields']] + [
                    'title', 'access', 'lifecycle', 'window.kind', 'window.start', 'window.end']
                oldest = '2026-10-29T12:00:00+08:00'
                newest = '2026-10-30T12:00:00+08:00'
                for key in keys:
                    self.assertIsNone(r['last_verified_at'])
                    at = oldest if key == oldest_key else newest
                    with patch('catalog.timestamp', return_value=at):
                        review(doc, r['id'], key, r['sources'][0]['id'], '单元测试摘录')
                self.assertEqual(r['last_verified_at'], oldest)
                with patch('catalog.timestamp', return_value=newest):
                    review(doc, r['id'], oldest_key, r['sources'][0]['id'], '单元测试复核摘录')
                self.assertEqual(r['last_verified_at'], newest)

    def test_reviewed_value_cannot_silently_drift(self):
        doc = copy.deepcopy(self.doc)
        r = doc['records'][0]
        f = r['fields'][0]
        review(doc, r['id'], f['key'], r['sources'][0]['id'], '单元测试摘录')
        f['value'] += '人工改值'
        with self.assertRaises(ValueError):
            validate(doc)

    def test_window_and_access_can_be_reviewed(self):
        doc = copy.deepcopy(self.doc)
        r = next(r for r in doc['records'] if r['id'] == 'wx-novel')
        review(doc, r['id'], 'window.end', r['sources'][0]['id'], '单元测试延期摘录', '2027-01-31')
        self.assertEqual(r['window']['end'], '2027-01-31')
        self.assertEqual(r['metadata_verification']['window.end']['value'], '2027-01-31')
        self.assertIsNone(r['last_verified_at'])
        self.assertEqual(r['access'], 'invitation')

    def test_sources_keep_multiple_links(self):
        src = sources('A｜[甲](https://example.com/a)、[乙](https://example.com/b)', 'A')
        self.assertEqual(len(src), 2)
        self.assertEqual(src[0]['label'], '甲')
        self.assertTrue(safe_url(src[1]['url']))

    def test_unsafe_urls(self):
        for url in ['javascript:alert(1)', 'https://user:secret@example.com/', 'https://example.com/\nattack', 'https://example.com/<tag>']:
            self.assertFalse(safe_url(url))

    def test_ids_stable_without_row_number(self):
        self.assertEqual(identity('model', '模型名称'), identity('model', '模型名称'))
        self.assertNotEqual(identity('model', '模型名称'), identity('tool', '模型名称'))


if __name__ == '__main__':
    unittest.main()
