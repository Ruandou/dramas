"""Offline stdlib tests: python3 -B -m unittest discover -s tests -p test_maintain.py."""
import copy
from datetime import datetime, timedelta, timezone
from email.message import Message
import importlib.util
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch
from contextlib import redirect_stdout

MODULE = Path(__file__).resolve().parents[1] / 'maintain.py'
SPEC = importlib.util.spec_from_file_location('catalog_maintenance_under_test', MODULE)
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)
NOW = datetime(2026, 10, 29, 2, 0, tzinfo=timezone.utc)
URL = 'https://public.example.org/policy'
TEXT_A = 'This public resource offers a documented application process and eligibility information. ' * 3
TEXT_B = TEXT_A + 'The application window has a new end date; a human must check its meaning.'


def record(identifier='r1', url=URL, end=None, start=None):
    return {'id': identifier, 'title': 'Public resource', 'category': 'policy',
            'fields': [{'label': 'Eligibility', 'value': 'Not verified'}],
            'sources': [{'id': 's-' + identifier, 'url': url, 'grade': 'A',
                         'label': 'Official page', 'scope': 'eligibility'}],
            'window': {'kind': 'fixed', 'start': start, 'end': end} if end or start else None,
            'last_verified_at': None, 'reported_as_of': '2026-10-20',
            'imported_at': '2026-10-29', 'updated_at': '2026-10-29'}


def document(*records):
    return {'records': list(records or [record()])}


def fetched(text=TEXT_A):
    return {'raw': '<html><body>' + text + '</body></html>', 'text': text, 'url': URL}


class StateTestCase(unittest.TestCase):
    def setUp(self):
        # An accidentally unmocked network operation must fail, never go online.
        self.net_guard = patch.object(socket, 'socket', side_effect=AssertionError('External network forbidden'))
        self.net_guard.start()
        self.dns_guard = patch.object(m, 'resolve_public', side_effect=AssertionError('External DNS forbidden'))
        self.dns_guard.start()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'state'
        self.doc = document()
        self.downloader = Mock(return_value=fetched())

    def tearDown(self):
        self.dns_guard.stop()
        self.net_guard.stop()
        self.temp.cleanup()

    def scan(self, doc=None, **kwargs):
        kwargs.setdefault('now', NOW)
        kwargs.setdefault('downloader', self.downloader)
        return m.scan(doc or self.doc, self.root, **kwargs)

    def state(self):
        return m.read_state(self.root)


class OfflineTest(StateTestCase):
    def test_no_state_report_is_unverified_without_creating_state_json(self):
        result = m.report(self.doc, self.root, now=NOW)
        self.assertEqual(result['coverage']['sources_never_attempted'], 1)
        self.assertEqual(result['unverified_count'], 1)
        self.assertEqual(result['pending_count'], 0)
        self.assertIsNone(result['last_success_day'])
        self.assertFalse((self.root / 'state.json').exists())

    def test_initial_baseline_is_candidate_with_private_artifacts_and_no_catalog_mutation(self):
        before = copy.deepcopy(self.doc)
        result = self.scan()
        state = self.state()
        source = next(iter(state['sources'].values()))
        item = state['queue']['q00000001']
        self.assertEqual(result['run']['successful'], 1)
        self.assertIsNone(source['accepted_baseline'])
        self.assertEqual(item['kind'], 'baseline_candidate')
        self.assertIsNone(item['before'])
        self.assertEqual(item['status'], 'pending')
        self.assertEqual(item['after']['source_url'], URL)
        self.assertEqual(item['after']['record_ids'], ['r1'])
        self.assertEqual(self.doc, before)
        self.assertNotIn('last_verified_at', source)
        for kind in ('raw', 'text'):
            path = self.root / item['after'][kind + '_path']
            self.assertEqual(m.digest(path.read_text()), item['after'][kind + '_sha256'])
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual((self.root / 'state.json').stat().st_mode & 0o777, 0o600)
        self.assertEqual(result['summary']['unverified_count'], 1)

    def test_repeated_baseline_idempotent_and_change_before_acceptance_keeps_both(self):
        self.scan()
        self.scan(now=NOW + timedelta(days=1))
        self.assertEqual(len(self.state()['queue']), 1)
        self.downloader.return_value = fetched(TEXT_B)
        self.scan(now=NOW + timedelta(days=2))
        state = self.state()
        self.assertEqual(len(state['queue']), 2)
        change = state['queue']['q00000002']
        self.assertEqual(change['kind'], 'content_change')
        self.assertEqual(change['before']['text_sha256'], m.digest(TEXT_A))
        self.assertIsNone(next(iter(state['sources'].values()))['accepted_baseline'])
        self.scan(now=NOW + timedelta(days=3))
        self.assertEqual(len(self.state()['queue']), 2)

    def test_dismissal_accepts_only_comparison_baseline_and_pending_survives(self):
        self.scan()
        response = m.dismiss('q00000001', 'Baseline read; not fact verification', self.root, now=NOW)
        self.assertFalse(response['canonical_data_changed'])
        self.downloader.return_value = fetched(TEXT_B)
        self.scan(now=NOW + timedelta(days=1))
        self.scan(now=NOW + timedelta(days=2))
        state = self.state()
        source = next(iter(state['sources'].values()))
        self.assertEqual(source['accepted_baseline']['text_sha256'], m.digest(TEXT_A))
        self.assertEqual(len(state['queue']), 2)
        self.assertEqual(state['queue']['q00000002']['status'], 'pending')
        self.downloader.side_effect = m.InspectionError('timeout', 'failure')
        self.scan(now=NOW + timedelta(days=3))
        state = self.state()
        source = next(iter(state['sources'].values()))
        self.assertEqual(source['last_attempt_at'], m.timestamp(NOW + timedelta(days=3)))
        self.assertEqual(source['last_successful_inspection_at'], m.timestamp(NOW + timedelta(days=2)))
        self.assertEqual(state['queue']['q00000002']['status'], 'pending')
        self.downloader.side_effect = None
        self.downloader.return_value = fetched(TEXT_A)  # Page reverted; unresolved change remains.
        self.scan(now=NOW + timedelta(days=4))
        self.assertEqual(self.state()['queue']['q00000002']['status'], 'pending')
        m.dismiss('q00000002', 'Explicit comparison acknowledgment', self.root, now=NOW)
        self.assertIsNone(self.doc['records'][0]['last_verified_at'])
        self.assertEqual(self.state()['queue']['q00000001']['reason'], 'Baseline read; not fact verification')

    def test_dismiss_does_not_close_other_pending_versions_or_duplicate_them(self):
        self.scan()
        self.downloader.return_value = fetched(TEXT_B)
        self.scan()
        text_c = TEXT_B + ' Further details.'
        self.downloader.return_value = fetched(text_c)
        self.scan()
        m.dismiss('q00000002', 'Acknowledge B, not C', self.root, now=NOW)
        self.scan()
        self.assertEqual(len(self.state()['queue']), 3)
        self.assertEqual(self.state()['queue']['q00000003']['status'], 'pending')
        self.assertEqual(self.state()['queue']['q00000001']['status'], 'pending')

    def test_dismiss_requires_reason_and_intact_snapshot(self):
        self.scan()
        original = (self.root / 'state.json').read_bytes()
        for identifier, reason in [('q00000001', '  '), ('q00000999', 'Not present')]:
            with self.assertRaises(m.MaintenanceError):
                m.dismiss(identifier, reason, self.root)
            self.assertEqual((self.root / 'state.json').read_bytes(), original)
        item = self.state()['queue']['q00000001']
        (self.root / item['after']['text_path']).write_text('tampered')
        with self.assertRaisesRegex(m.MaintenanceError, 'integrity'):
            m.dismiss('q00000001', 'Should fail', self.root)
        self.assertEqual((self.root / 'state.json').read_bytes(), original)

    def test_failure_or_manual_only_does_not_satisfy_daily_due(self):
        for error in (m.InspectionError('timeout', 'failure'), m.InspectionError('http_403')):
            self.downloader.side_effect = error
            result = self.scan(if_due=True)
            self.assertFalse(result['skipped'])
            self.assertIsNone(self.state()['last_success_day'])
        self.downloader.side_effect = None
        self.scan(if_due=True)
        count = self.downloader.call_count
        result = self.scan(if_due=True)
        self.assertTrue(result['skipped'])
        self.assertEqual(self.downloader.call_count, count)

    def test_shanghai_boundary_and_catchup(self):
        before_midnight = datetime(2026, 10, 29, 15, 59, tzinfo=timezone.utc)
        after_midnight = before_midnight + timedelta(minutes=2)
        self.scan(now=before_midnight, if_due=True)
        self.assertEqual(self.state()['last_success_day'], '2026-10-29')
        result = self.scan(now=after_midnight, if_due=True)
        self.assertFalse(result['skipped'])
        self.assertEqual(self.state()['last_success_day'], '2026-10-30')
        self.assertTrue(self.scan(now=after_midnight + timedelta(hours=1), if_due=True)['skipped'])
        self.assertFalse(self.scan(now=after_midnight + timedelta(days=3), if_due=True)['skipped'])

    def test_partial_coverage_deduplicates_fetch_and_maps_every_record(self):
        doc = document(record('a'), record('b', URL + '#section'),
                       record('c', 'https://second.example.org/policy'), record('d', 'https://third.example.org/policy'))
        result = self.scan(doc, limit=1)
        self.assertEqual(result['run']['attempted'], 1)
        self.assertEqual(result['run']['not_attempted_in_batch'], 2)
        self.assertEqual(result['summary']['coverage']['total_sources'], 3)
        self.assertEqual(result['summary']['coverage']['sources_never_attempted'], 2)
        self.scan(doc, limit=20)
        state = self.state()
        matching = [s for s in state['sources'].values() if 'a' in s['record_ids']]
        self.assertEqual(matching[0]['record_ids'], ['a', 'b'])
        self.assertEqual(matching[0]['source_ids'], ['s-a', 's-b'])
        self.assertEqual(len(state['queue']), 3)
        result = m.report(doc, self.root, now=NOW)
        self.assertEqual(result['coverage']['records_all_sources_inspected_ever'], 4)

    def test_near_deadline_priority_and_oldest_rotation_cannot_starve(self):
        records = [record('normal-' + str(n), 'https://public.example.org/' + str(n)) for n in range(8)]
        records += [record('urgent', 'https://public.example.org/urgent', end='2026-11-02')]
        doc = document(*records)
        self.scan(doc, limit=2)
        self.assertEqual(self.downloader.call_args_list[0].args[0], 'https://public.example.org/urgent')
        for day in range(1, 9):
            self.scan(doc, now=NOW + timedelta(days=day), limit=2)
        self.assertEqual(len(self.state()['sources']), 9)

    def test_limit_one_rotates_even_with_urgent_source(self):
        doc = document(record('urgent', end='2026-11-02'), record('other', 'https://other.example.org/'))
        self.scan(doc, limit=1)
        self.scan(doc, limit=1)
        self.assertEqual(len(self.state()['sources']), 2)

    def test_deadlines_and_unverified_facts_are_distinct_from_inspection(self):
        doc = document(record('past', end='2026-10-28'), record('today', end='2026-10-29'),
                       record('14days', end='2026-11-12'), record('15days', end='2026-11-13'),
                       record('future-start', start='2026-11-01'))
        doc['records'][-1]['sources'] = []
        self.scan(doc)
        result = m.report(doc, self.root, now=NOW)
        self.assertEqual({d['record_id'] for d in result['deadlines']}, {'past', 'today', '14days'})
        self.assertEqual(result['deadlines'][0]['status'], 'overdue')
        self.assertEqual(result['upcoming_starts'], [{'record_id': 'future-start', 'start': '2026-11-01'}])
        self.assertEqual(result['windows_without_end'], ['future-start'])
        self.assertEqual(result['unverified_count'], 5)
        self.assertEqual(result['coverage']['records_without_sources'], 1)

    def test_partial_success_satisfies_due_but_exposes_failures(self):
        doc = document(record(), record('second', 'https://second.example.org/'))
        self.downloader.side_effect = [fetched(), m.InspectionError('http_404', 'failure')]
        result = self.scan(doc, if_due=True)
        self.assertEqual(result['run']['successful'], 1)
        self.assertEqual(result['run']['failure'], 1)
        self.assertEqual(len(result['summary']['issues']), 1)
        self.assertTrue(self.scan(doc, if_due=True)['skipped'])
        self.assertNotIn('"status": "dead"', json.dumps(result))

    def test_damaged_state_fails_without_erase_or_fetch(self):
        self.root.mkdir()
        for data in ('{broken', '{}', json.dumps({'version': 999})):
            (self.root / 'state.json').write_text(data)
            with self.assertRaisesRegex(m.MaintenanceError, 'Damaged'):
                self.scan()
            self.assertEqual((self.root / 'state.json').read_text(), data)
        self.downloader.assert_not_called()

    def test_missing_state_with_existing_evidence_is_not_reset(self):
        self.scan()
        (self.root / 'state.json').unlink()
        with self.assertRaisesRegex(m.MaintenanceError, 'Missing state'):
            self.scan()

    def test_lock_blocks_concurrent_mutations_and_reports(self):
        with m.state_lock(self.root):
            with self.assertRaisesRegex(m.MaintenanceError, 'lock'):
                self.scan()
            with self.assertRaisesRegex(m.MaintenanceError, 'lock'):
                m.report(self.doc, self.root)
        self.scan()
        self.assertTrue((self.root / '.lock').exists())

    def test_atomic_state_failure_retains_previous_json(self):
        self.scan()
        before = (self.root / 'state.json').read_bytes()
        with patch.object(m.os, 'replace', side_effect=OSError('simulated disk error')):
            with self.assertRaises(OSError):
                m.atomic_json(self.root / 'state.json', {'unexpected': 'replacement'})
        self.assertEqual((self.root / 'state.json').read_bytes(), before)
        self.assertFalse(list(self.root.glob('.state.json.*')))

    def test_snapshot_interruption_leaves_no_partial_final_file_and_can_retry(self):
        self.root.mkdir()
        with patch.object(m.os, 'fsync', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                m.store_text(self.root, TEXT_A)
        self.assertEqual(list((self.root / 'snapshots').iterdir()), [])
        sha, path = m.store_text(self.root, TEXT_A)
        self.assertEqual((self.root / path).read_text(), TEXT_A)
        self.assertEqual(sha, m.digest(TEXT_A))
        self.assertEqual(m.store_text(self.root, TEXT_A), (sha, path))

    def test_first_scan_interruption_after_snapshot_can_retry_without_reset(self):
        original_store = m.store_text

        def interrupted(root, text):
            original_store(root, text)
            raise OSError('interrupted before queue persistence')

        with patch.object(m, 'store_text', side_effect=interrupted):
            with self.assertRaises(OSError):
                self.scan()
        self.assertTrue((self.root / 'state.json').exists())
        self.assertEqual(self.state()['queue'], {})
        self.assertEqual(self.scan()['run']['successful'], 1)
        self.assertEqual(len(self.state()['queue']), 1)

    def test_snapshot_publish_does_not_overwrite_concurrent_evidence(self):
        self.root.mkdir()
        original_link = m.os.link

        def collision(source, target):
            Path(target).write_text('existing evidence')
            original_link(source, target)

        with patch.object(m.os, 'link', side_effect=collision):
            with self.assertRaises(FileExistsError):
                m.store_text(self.root, TEXT_A)
        self.assertEqual((self.root / 'snapshots' / (m.digest(TEXT_A) + '.txt')).read_text(), 'existing evidence')
        self.assertFalse(list((self.root / 'snapshots').glob('.snapshot-*')))

    def test_explicit_public_summary_contains_counts_only_and_scan_exports_nothing(self):
        self.scan()
        output = Path(self.temp.name) / 'public-summary.json'
        result = m.report(self.doc, self.root, now=NOW, output=output)
        exported = json.loads(output.read_text())
        self.assertEqual(exported, m.public_summary(result))
        for forbidden in (URL, TEXT_A, 'source_key', 'record_ids', 'q00000001', 'reason'):
            self.assertNotIn(forbidden, output.read_text())
        self.assertFalse((MODULE.parent / 'summary.json').exists())
        with self.assertRaises(m.MaintenanceError):
            m.report(self.doc, self.root, output=self.root / 'state.json')
        m.report(self.doc, self.root, now=NOW, output=output)  # Existing summary can refresh.
        output.write_text(json.dumps(self.doc))
        original = output.read_bytes()
        with self.assertRaisesRegex(m.MaintenanceError, 'non-summary'):
            m.report(self.doc, self.root, now=NOW, output=output)
        self.assertEqual(output.read_bytes(), original)

    def test_unsafe_urls_and_error_details_do_not_leak_secrets(self):
        secret = 'VERY_PRIVATE_TOKEN_123'
        doc = document(record(url='https://name:' + secret + '@public.example.org/'))
        result = self.scan(doc)
        self.downloader.assert_not_called()
        self.assertNotIn(secret, json.dumps(result))
        self.assertNotIn(secret, (self.root / 'state.json').read_text())
        self.downloader.side_effect = OSError(secret)
        result = self.scan()
        self.assertNotIn(secret, json.dumps(result))

    def test_cli_lazy_catalog_validation_defaults_and_json(self):
        fake_catalog = types.SimpleNamespace(load=Mock(return_value=self.doc), validate=Mock(return_value=None))
        with patch.dict(sys.modules, {'catalog': fake_catalog}), patch.object(m, 'download', self.downloader):
            out = io.StringIO()
            with redirect_stdout(out):
                code = m.main(['--state-dir', str(self.root), 'scan', '--if-due'])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out.getvalue())['run']['successful'], 1)
            fake_catalog.validate.assert_called_once_with(self.doc)
            self.assertEqual(self.downloader.call_args.args[1], 12)
        fake_catalog.validate.side_effect = ValueError('secret validation details')
        with patch.dict(sys.modules, {'catalog': fake_catalog}), redirect_stdout(io.StringIO()) as out:
            self.assertEqual(m.main(['report', '--state-dir', str(self.root)]), 2)
            self.assertNotIn('secret validation details', out.getvalue())

    def test_invalid_scan_bounds_and_naive_time(self):
        for arguments in ({'limit': 0}, {'timeout': -1}, {'timeout': float('nan')},
                          {'timeout': 121}, {'now': datetime(2026, 10, 29)}):
            with self.assertRaises(m.MaintenanceError):
                self.scan(**arguments)
        self.downloader.assert_not_called()

    def test_default_batch_is_twenty_and_github_is_manual_without_a_request(self):
        doc = document(*(record(str(n), 'https://public.example.org/' + str(n)) for n in range(25)))
        result = self.scan(doc)
        self.assertEqual(result['run']['attempted'], 20)
        self.assertEqual(result['run']['not_attempted_in_batch'], 5)
        self.downloader.reset_mock()
        result = self.scan(document(record(url='https://github.com/org/repository')))
        self.downloader.assert_not_called()
        self.assertEqual(result['run']['manual_required'], 1)
        self.assertEqual(result['summary']['issues'][0]['reason'], 'github_manual_review')

    def test_nested_state_damage_and_queue_gaps_are_not_overwritten(self):
        self.scan()
        original = self.state()
        broken_source = copy.deepcopy(original)
        next(iter(broken_source['sources'].values())).pop('last_successful_inspection_at')
        broken_queue = copy.deepcopy(original)
        item = broken_queue['queue'].pop('q00000001')
        item['id'] = 'q00000003'
        broken_queue['queue']['q00000003'] = item
        for state in (broken_source, broken_queue):
            m.atomic_json(self.root / 'state.json', state)
            before = (self.root / 'state.json').read_bytes()
            with self.assertRaisesRegex(m.MaintenanceError, 'Damaged'):
                self.scan()
            self.assertEqual((self.root / 'state.json').read_bytes(), before)

    def test_success_clock_crossing_midnight_uses_inspection_not_start_day(self):
        before = '2026-10-29T15:59:59+00:00'
        after = '2026-10-29T16:00:01+00:00'
        with patch.object(m, 'timestamp', side_effect=[before, before, after, after]):
            self.scan()
        source = next(iter(self.state()['sources'].values()))
        self.assertEqual(source['last_attempt_at'], before)
        self.assertEqual(source['last_successful_inspection_at'], after)
        self.assertEqual(self.state()['last_success_day'], '2026-10-30')

    def test_partial_field_proofs_remain_distinct_from_record_verification(self):
        doc = document()
        doc['records'][0]['fields'][0]['verified_at'] = NOW.isoformat()
        result = m.report(doc, self.root, now=NOW)
        self.assertEqual(result['unverified_count'], 1)
        self.assertEqual(result['unverified_facts'][0]['unverified_field_count'], 0)
        self.assertIn('title', result['unverified_facts'][0]['unverified_metadata'])

    def test_disk_failures_stop_instead_of_becoming_network_issues(self):
        self.scan()
        original = (self.root / 'state.json').read_bytes()
        self.downloader.return_value = fetched(TEXT_B)
        with patch.object(m, 'store_text', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                self.scan()
        self.assertEqual((self.root / 'state.json').read_bytes(), original)


class NormalizerTests(unittest.TestCase):
    def test_script_style_hidden_and_whitespace_normalization(self):
        raw = ('<html><head><title>Ignore</title></head><body><script>secret()</script>'
               '<style>.hidden{}</style><p> A&nbsp; public \n policy </p><span>details</span>'
               '<div hidden>Hidden child <b>hidden too</b></div>'
               '<div style="display: none">Excluded</div><noscript>Enable JavaScript</noscript></body></html>')
        self.assertEqual(m.normalize_text(raw), ('A public policy details', False))

    def test_boolean_type_and_style_attributes_do_not_abort_inspection(self):
        raw = '<input type><div style>' + TEXT_A + '</div>'
        self.assertEqual(m.normalize_text(raw), (' '.join(TEXT_A.split()), False))
        self.assertEqual(m.inspect_text(raw.encode(), 'text/html')[1], ' '.join(TEXT_A.split()))

    def test_empty_shell_login_antibot_and_unsupported_are_manual(self):
        for body, kind in ((b'<div id="root"></div><script>render()</script>', 'text/html'),
                           (b'<h1>Enable JavaScript</h1>', 'text/html'),
                           (b'<h1>Just a moment; verify you are human</h1>', 'text/html'),
                           (('<input type="password">' + TEXT_A).encode(), 'text/html'),
                           (b'%PDF-1.7 data', 'text/plain'), (b'{}', 'application/json')):
            with self.subTest(body=body[:40]):
                with self.assertRaises(m.InspectionError) as caught:
                    m.inspect_text(body, kind)
                self.assertEqual(caught.exception.status, 'manual_required')

    def test_adversarial_html_nesting_is_bounded(self):
        with self.assertRaisesRegex(m.InspectionError, 'html_nesting_limit'):
            m.normalize_text('<div>' * 257 + TEXT_A)

    def test_plain_text_charset_and_size_limit(self):
        self.assertEqual(m.inspect_text(TEXT_A.encode(), 'text/plain')[1], ' '.join(TEXT_A.split()))
        chinese = '公开政策内容需要人工核对，自动巡检不代表事实准确。' * 10
        self.assertEqual(m.inspect_text(chinese.encode('gb18030'), 'text/plain', 'gb18030')[1], chinese)
        with self.assertRaisesRegex(m.InspectionError, 'too_large'):
            m.inspect_text(b'x' * (m.MAX_BYTES + 1), 'text/plain')


class URLTests(unittest.TestCase):
    def test_protocol_credentials_private_loopback_and_nonpublic_services(self):
        invalid = ['file:///etc/passwd', 'ftp://example.org/a', 'javascript:alert(1)',
                   'http://localhost/', 'http://127.0.0.1/', 'http://10.1.1.1/',
                   'http://169.254.169.254/', 'http://[::1]/', 'http://[fe80::1]/',
                   'http://[::ffff:127.0.0.1]/', 'http://192.168.1.1/', 'http://100.64.0.1/',
                   'https://user:secret@example.org/', 'https://example.org:8443/',
                   'https://example.org/?access_token=secret', 'https://example.org/login',
                   'https://api.example.org/data', 'https://docs.google.com/document/x',
                   'https://github.com/owner/repo', 'https://raw.githubusercontent.com/x',
                   'https://example.org/\\@localhost', 'https://example.org/\r\nX:evil',
                   'http://work.local/', 'http://intranet/']
        for url in invalid:
            with self.subTest(url=url), self.assertRaises(m.InspectionError):
                m.checked_url(url)
        self.assertEqual(m.checked_url('https://Example.ORG:443?article=23#part'),
                         'https://example.org/?article=23')

    def test_dns_mixed_public_private_rejected_and_resolver_is_bounded(self):
        addresses = [[socket.AF_INET, socket.SOCK_STREAM, 6, '', ['93.184.216.34', 443]],
                     [socket.AF_INET, socket.SOCK_STREAM, 6, '', ['127.0.0.1', 443]]]
        completed = types.SimpleNamespace(stdout=json.dumps(addresses).encode())
        with patch.object(m.subprocess, 'run', return_value=completed) as resolve:
            with self.assertRaisesRegex(m.InspectionError, 'nonpublic_dns'):
                m.resolve_public('example.org', 443, 4)
            self.assertEqual(resolve.call_args.kwargs['timeout'], 4)
        with patch.object(m.subprocess, 'run', side_effect=subprocess.TimeoutExpired('dns', 4)):
            with self.assertRaisesRegex(m.InspectionError, 'timeout'):
                m.resolve_public('example.org', 443, 4)


class FakeResponse:
    def __init__(self, status=200, body=None, **headers):
        self.status = status
        self.body = io.BytesIO((TEXT_A.encode() if body is None else body))
        self.headers = Message()
        self.headers['Content-Type'] = headers.pop('Content-Type', 'text/html; charset=utf-8')
        for name, value in headers.items():
            self.headers[name] = value

    def getheader(self, name, default=None):
        return self.headers.get(name, default)

    def read1(self, size):
        return self.body.read(size)

    def close(self):
        self.body.close()


class DownloaderTests(StateTestCase):
    def network(self, responses, dns=None):
        sockets = Mock()
        connection = Mock()
        connection.getresponse.side_effect = responses
        addresses = dns or [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 80))]
        return sockets, connection, addresses

    def fetch_with(self, responses, url='http://public.example.org/', dns=None):
        sockets, connection, addresses = self.network(responses, dns)
        with patch.object(m.socket, 'socket', return_value=sockets), \
                patch.object(m, 'resolve_public', return_value=addresses) as resolver, \
                patch.object(m.http.client, 'HTTPConnection', return_value=connection):
            result = m.download(url, 2)
        return result, sockets, connection, resolver

    def test_redirect_to_private_or_github_never_connects_to_target(self):
        for target in ('http://127.0.0.1/', 'http://169.254.169.254/',
                       'https://github.com/o/r', 'https://account:secret@example.org/'):
            with self.subTest(target=target):
                sockets, connection, addresses = self.network([FakeResponse(302, Location=target)])
                with patch.object(m.socket, 'socket', return_value=sockets), \
                        patch.object(m, 'resolve_public', return_value=addresses) as resolver, \
                        patch.object(m.http.client, 'HTTPConnection', return_value=connection):
                    with self.assertRaises(m.InspectionError):
                        m.download('http://public.example.org/')
                self.assertEqual(resolver.call_count, 1)
                self.assertEqual(sockets.connect.call_count, 1)

    def test_safe_redirect_resolves_again_and_connects_only_pinned_ip(self):
        result, sock, connection, resolver = self.fetch_with([
            FakeResponse(302, Location='http://other.example.org/page'), FakeResponse()])
        self.assertEqual(result['url'], 'http://other.example.org/page')
        self.assertEqual(resolver.call_count, 2)
        for call in sock.connect.call_args_list:
            self.assertEqual(call.args[0][0], '93.184.216.34')
        headers = connection.request.call_args.kwargs['headers']
        self.assertNotIn('Authorization', headers)
        self.assertNotIn('Cookie', headers)
        self.assertEqual(connection.auto_open, 0)

    def test_redirect_dns_private_is_rechecked(self):
        _, connection, public = self.network([FakeResponse(302, Location='http://second.example.org/')])
        private = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('10.0.0.1', 80))]
        sock = Mock()
        with patch.object(m.socket, 'socket', return_value=sock), \
                patch.object(m, 'resolve_public', side_effect=[public, private]), \
                patch.object(m.http.client, 'HTTPConnection', return_value=connection):
            with self.assertRaisesRegex(m.InspectionError, 'nonpublic_dns'):
                m.download('http://public.example.org/')
            self.assertEqual(sock.connect.call_count, 1)

    def test_redirect_limit_and_oversize_chunked_body(self):
        with self.assertRaisesRegex(m.InspectionError, 'redirect_limit'):
            self.fetch_with([FakeResponse(302, Location='/next')] * (m.MAX_REDIRECTS + 1))
        for response in (FakeResponse(body=b'a' * (m.MAX_BYTES + 1)),
                         FakeResponse(**{'Content-Length': str(m.MAX_BYTES + 1)})):
            with self.assertRaisesRegex(m.InspectionError, 'too_large'):
                self.fetch_with([response])

    def test_403_timeout_pdf_encoding_and_incomplete_content(self):
        for response, status in ((FakeResponse(403), 'manual_required'),
                                 (FakeResponse(404), 'failure'),
                                 (FakeResponse(**{'Content-Type': 'application/pdf'}), 'manual_required'),
                                 (FakeResponse(**{'Content-Encoding': 'gzip'}), 'manual_required'),
                                 (FakeResponse(body=b'partial', **{'Content-Length': '200'}), 'failure')):
            with self.assertRaises(m.InspectionError) as caught:
                self.fetch_with([response])
            self.assertEqual(caught.exception.status, status)
        with self.assertRaises(m.InspectionError) as caught:
            self.fetch_with([TimeoutError('credentials must not appear')])
        self.assertEqual(caught.exception.reason, 'timeout')

    def test_trickling_response_has_deadline_shutdown_and_timer_cleanup(self):
        timers = []

        class ImmediateTimer:
            def __init__(self, interval, callback):
                self.interval, self.callback = interval, callback
                self.cancelled, self.joined = False, False
                timers.append(self)

            def start(self):
                self.callback()

            def cancel(self):
                self.cancelled = True

            def join(self):
                self.joined = True

        with patch.object(m.threading, 'Timer', ImmediateTimer):
            _, sock, _, _ = self.fetch_with([FakeResponse()])
        sock.shutdown.assert_called_once_with(socket.SHUT_RDWR)
        self.assertTrue(0 < timers[0].interval <= 2)
        self.assertTrue(timers[0].cancelled and timers[0].joined)

    def test_tls_uses_default_context_and_server_hostname_and_no_downgrade(self):
        context = Mock()
        context.wrap_socket.return_value = Mock()
        with patch.object(m.ssl, 'create_default_context', return_value=context) as tls:
            self.fetch_with([FakeResponse()], url='https://public.example.org/')
            tls.assert_called_once_with()
            self.assertEqual(context.wrap_socket.call_args.kwargs['server_hostname'], 'public.example.org')
            with self.assertRaisesRegex(m.InspectionError, 'tls_downgrade'):
                self.fetch_with([FakeResponse(302, Location='http://public.example.org/')],
                                url='https://public.example.org/')


if __name__ == '__main__':
    unittest.main()
