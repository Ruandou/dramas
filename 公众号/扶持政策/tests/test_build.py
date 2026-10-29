import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build
from catalog import load, markdown_exports


class BuildTests(unittest.TestCase):
    def test_public_payload_excludes_migration_archives(self):
        doc = load()
        public = build.public_data(doc)
        self.assertNotIn('migration_archive', public)
        self.assertTrue(all('provenance' not in r for r in public['records']))
        self.assertTrue(all('provenance' not in d for d in public['documents']))
        self.assertEqual(len(public['records']), len(doc['records']))
        self.assertIn('history', public['records'][0])
        for record, original in zip(public['records'], doc['records']):
            with self.subTest(record_id=record['id']):
                self.assertEqual(record['origin'], {
                    key: val for key, val in original['provenance'].items()
                    if key in ('file', 'row_at_import')})

    def test_exports_share_canonical_fields(self):
        doc = copy.deepcopy(load())
        r = next(r for r in doc['records'] if r['id'] == 'sz-2025')
        f = next(f for f in r['fields'] if f['key'] == 'benefit')
        f.pop('verification', None)
        f['verified_at'] = None
        r['last_verified_at'] = None
        f['value'] = '仅单测：新支持口径'
        texts = build.exports(doc)
        ledger = next(v for k, v in texts.items() if k.name == '扶持政策台账.md')
        policy = next(v for k, v in texts.items() if k.name == 'policy.yaml')
        public = build.public_data(doc)
        self.assertIn(f['value'], ledger)
        self.assertIn(f['value'], policy)
        self.assertIn(f['value'], json.dumps(public, ensure_ascii=False))

    def test_build_deterministic_and_keeps_policy_entry(self):
        with patch.dict(sys.modules, {'web': SimpleNamespace(render=lambda d: '<html>test</html>')}):
            first = build.build(load())
            second = build.build(load())
        self.assertEqual(first, second)
        self.assertEqual(first['index.html'], first['policies.html'])
        self.assertIn('catalog.json', first)
        self.assertIn('frame-ancestors', first['_headers'])

    def test_main_preserves_unrelated_files_and_checks_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / 'user-file.txt'
            marker.write_text('keep')
            generated = root / 'note.md'
            with patch.object(build, 'build', return_value={'index.html': 'hello'}), \
                 patch.object(build, 'exports', return_value={generated: 'generated'}), \
                 patch.object(sys, 'argv', ['build.py', '--output', tmp]):
                build.main()
            self.assertEqual(marker.read_text(), 'keep')
            self.assertEqual(generated.read_text(), 'generated')
            generated.write_text('manual change')
            with patch.object(build, 'build', return_value={'index.html': 'hello'}), \
                 patch.object(build, 'exports', return_value={generated: 'generated'}), \
                 patch.object(sys, 'argv', ['build.py', '--output', tmp, '--check']):
                with self.assertRaises(SystemExit):
                    build.main()
            self.assertEqual(generated.read_text(), 'manual change')


if __name__ == '__main__':
    unittest.main()
