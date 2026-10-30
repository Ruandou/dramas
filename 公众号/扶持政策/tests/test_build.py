import copy
import json
import shutil
import subprocess
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
        public = build.public_data(doc)
        self.assertIn(f['value'], ledger)
        self.assertIn(f['value'], json.dumps(public, ensure_ascii=False))

    def test_exports_only_markdown_reading_copies(self):
        self.assertEqual({path.name for path in build.exports(load())}, {
            '扶持政策台账.md', '短剧政策地图.md', '分发平台清单.md', '模型清单.md', '工具清单.md',
        })

    def test_json_only_build_without_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / '扶持政策'
            root.mkdir()
            for name in ('build.py', 'catalog.py', 'web.py'):
                shutil.copy2(build.ROOT / name, root / name)
            shutil.copytree(build.ROOT / 'static', root / 'static')
            (root / 'data').mkdir()
            for name in ('catalog.json', 'maintenance.json'):
                shutil.copy2(build.ROOT / 'data' / name, root / 'data' / name)
            original = (root / 'data' / 'catalog.json').read_bytes()
            code = (
                "import runpy, sys; sys.modules['yaml'] = None; "
                "sys.path.insert(0, sys.argv[1]); "
                "sys.argv = [sys.argv[1] + '/build.py'] + sys.argv[2:]; "
                "runpy.run_path(sys.argv[0], run_name='__main__')"
            )
            for flags in ((), ('--check',)):
                result = subprocess.run(
                    [sys.executable, '-B', '-c', code, str(root), *flags],
                    capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual({path.name for path in (root / 'data').iterdir()}, {
                'catalog.json', 'maintenance.json',
            })
            self.assertEqual(len(list((root / 'dist').iterdir())), 7)
            self.assertEqual(len(list((Path(tmp) / '素材').iterdir())), 5)
            self.assertEqual((root / 'data' / 'catalog.json').read_bytes(), original)
            public = json.loads((root / 'dist' / 'catalog.json').read_text(encoding='utf-8'))
            self.assertEqual(public['records'], build.public_data(load())['records'])
            self.assertNotIn('migration_archive', public)

    def test_build_deterministic_and_keeps_policy_entry(self):
        with patch.dict(sys.modules, {'web': SimpleNamespace(render=lambda d: '<html>test</html>', FAVICON='<link rel="icon">')}):
            first = build.build(load())
            second = build.build(load())
        self.assertEqual(first, second)
        self.assertEqual(first['index.html'], first['policies.html'])
        self.assertIn('catalog.json', first)
        self.assertIn('<link rel="icon">', first['404.html'])
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
