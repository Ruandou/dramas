import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import deploy


class DeployTests(unittest.TestCase):
    def test_changed_files_detects_diff_and_missing(self):
        local = {name: "a" for name in deploy.FILES}
        remote = dict(local)
        self.assertEqual(deploy.changed_files(local, remote), [])
        remote["catalog.json"] = "b"
        remote["404.html"] = None
        self.assertEqual(deploy.changed_files(local, remote), ["catalog.json", "404.html"])

    def test_hashes_marks_missing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text("x", encoding="utf-8")
            result = deploy.hashes(root)
            self.assertEqual(result["index.html"], deploy.sha256(root / "index.html"))
            self.assertIsNone(result["catalog.json"])

    def test_parse_deployment_url(self):
        output = "✨ Deployment complete! Take a peek over at https://f822e7c4.duanju-policy.pages.dev"
        self.assertEqual(deploy.parse_deployment_url(output),
                         "https://f822e7c4.duanju-policy.pages.dev")
        self.assertIsNone(deploy.parse_deployment_url("no url"))

    def test_fingerprint_ignores_generated_at_but_not_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = {"maintenance": {"generated_at": "2026-11-10T08:00:00+00:00",
                                    "coverage": {"sources_inspected_today": 5}}}
            (root / "catalog.json").write_text(json.dumps(data), encoding="utf-8")
            first = deploy.fingerprint("catalog.json", root)
            data["maintenance"]["generated_at"] = "2026-11-10T16:00:00+00:00"
            (root / "catalog.json").write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(deploy.fingerprint("catalog.json", root), first)
            data["maintenance"]["coverage"]["sources_inspected_today"] = 6
            (root / "catalog.json").write_text(json.dumps(data), encoding="utf-8")
            self.assertNotEqual(deploy.fingerprint("catalog.json", root), first)

            page = ('<script type="application/json" id="catalog-data">'
                    + json.dumps(data) + '</script>')
            (root / "policies.html").write_text(page, encoding="utf-8")
            with_ts = deploy.fingerprint("policies.html", root)
            data["maintenance"]["generated_at"] = "2026-11-10T17:00:00+00:00"
            page = ('<script type="application/json" id="catalog-data">'
                    + json.dumps(data) + '</script>')
            (root / "policies.html").write_text(page, encoding="utf-8")
            self.assertEqual(deploy.fingerprint("policies.html", root), with_ts)

    def test_copy_verified_writes_identical_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src, dst = root / "src", root / "dst"
            src.mkdir()
            for name in deploy.FILES:
                (src / name).write_bytes(name.encode())
            with patch.object(deploy, "DIST", src), patch.object(deploy, "MIRROR", dst):
                deploy.copy_verified()
            for name in deploy.FILES:
                self.assertEqual((dst / name).read_bytes(), (src / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
