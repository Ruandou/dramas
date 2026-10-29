#!/usr/bin/env python3
"""Read-only catalog source inspection (stdlib, Python 3.9+, macOS/Linux).

    python3 maintain.py scan --if-due --limit 20 --timeout 12
    python3 maintain.py report [--output /explicit/path/summary.json]
    python3 maintain.py dismiss q00000001 --reason 'Compared locally; cosmetic edit'

All commands accept --state-dir (default ~/.local/state/yiren-catalog).
The lazy catalog adapter expects catalog.load() -> {"records": [...]} and calls
catalog.validate(doc). Records use id/title/category/fields/sources/window and
provenance dates; sources use id/url/grade/label/scope. No canonical data is written.

State v1: sources keyed by SHA256(URL without fragment), an append-only review
queue, run counts and Shanghai daily-success date. Each source has separate
attempt/success timestamps, latest observation and an explicitly accepted
comparison baseline. Immutable UTF-8 raw/normalized text snapshots and hashes
live ONLY in the state directory. First observations are unverified candidates.
Dismissal needs a reason and accepts ONLY that observation as a comparison
baseline; it neither verifies facts nor changes catalog.last_verified_at. Other
pending observations remain pending, even on errors, reversion or later runs.

Networking is sequential: public HTTP(S) GET only, no proxies/cookies/accounts,
no APIs, no GitHub fetches (manual review instead), verified TLS, DNS validated
and IP pinned, redirect targets revalidated, 2 MiB body limit. DNS runs in a
bounded stdlib child process; socket operations share a per-source time budget.
JS shells, login/challenge pages, PDFs and unsupported responses require manual
inspection. HTTP errors/timeouts are NOT declarations that a resource is dead.
A successful batch is NOT full coverage or factual verification. Scheduling,
publication, model calls and commits are intentionally outside this CLI.
"""

import argparse
from contextlib import contextmanager
from datetime import date, datetime, timezone
import fcntl
import hashlib
from html.parser import HTMLParser
import http.client
import ipaddress
import json
import math
import os
from pathlib import Path
import re
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import parse_qsl, unquote, urljoin, urlsplit, urlunsplit
from zoneinfo import ZoneInfo

SHANGHAI = ZoneInfo('Asia/Shanghai')
DEFAULT_STATE_DIR = Path.home() / '.local' / 'state' / 'yiren-catalog'
MAX_BYTES = 2 * 1024 * 1024
MAX_REDIRECTS = 5
MIN_TEXT = 80
HASH = re.compile(r'^[0-9a-f]{64}$')
STATUSES = {'inspected', 'failure', 'manual_required'}


class MaintenanceError(Exception):
    """Only controlled, non-sensitive messages may cross the CLI boundary."""


class InspectionError(Exception):
    def __init__(self, reason, status='manual_required'):
        self.reason, self.status = reason, status
        super().__init__(reason)


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def timestamp(now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise MaintenanceError('An aware datetime is required')
    return now.astimezone(timezone.utc).isoformat()


def local_day(stamp):
    return datetime.fromisoformat(stamp).astimezone(SHANGHAI).date().isoformat()


class VisibleText(HTMLParser):
    """Ignore executable, styling, hidden and non-rendered fallback content."""
    OMIT = {'script', 'style', 'head', 'template', 'noscript'}
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.stack = [], []
        self.password = False

    def handle_starttag(self, tag, attrs):
        attrs = {key: value or '' for key, value in attrs}
        if tag == 'input' and attrs.get('type', '').lower() == 'password':
            self.password = True
        hidden = (tag in self.OMIT or 'hidden' in attrs or
                  attrs.get('aria-hidden') == 'true' or
                  bool(re.search(r'display\s*:\s*none|visibility\s*:\s*hidden',
                                 attrs.get('style', ''), re.I)))
        if tag not in self.VOID:
            if len(self.stack) >= 256:
                raise InspectionError('html_nesting_limit')
            self.stack.append((tag, hidden or bool(self.stack and self.stack[-1][1])))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data):
        if not self.stack or not self.stack[-1][1]:
            self.parts.append(data)


def normalize_text(raw, content_type='text/html'):
    if content_type == 'text/plain':
        return ' '.join(raw.split()), False
    parser = VisibleText()
    parser.feed(raw)
    parser.close()
    return ' '.join(' '.join(parser.parts).split()), parser.password


def inspect_text(body, content_type, charset='utf-8'):
    """Returns decoded source and normalized text, never a verified fact."""
    if len(body) > MAX_BYTES:
        raise InspectionError('body_too_large')
    if body.lstrip().startswith(b'%PDF') or content_type not in {
            'text/html', 'application/xhtml+xml', 'text/plain'}:
        raise InspectionError('unsupported_content')
    try:
        raw = body.decode(charset, errors='strict')
    except (UnicodeError, LookupError):
        raise InspectionError('unknown_or_invalid_encoding') from None
    text, password = normalize_text(raw, content_type)
    challenge = re.search(
        r'captcha|verify (?:that )?you are human|checking your browser|'
        r'just a moment|access denied|enable javascript|javascript (?:is )?required|'
        r'(?:sign|log) in to (?:continue|access|view)|please (?:sign|log) in|'
        r'登录后|请先登录|请登录|人机验证|安全验证|访问过于频繁|访问受限', text, re.I)
    if password or challenge:
        raise InspectionError('login_or_challenge')
    if len(text) < MIN_TEXT:
        raise InspectionError('empty_or_js_shell')
    return raw, text


def checked_url(url):
    """Syntactic/public-source policy, before DNS; never include URL in errors."""
    try:
        if not isinstance(url, str) or any(ord(c) < 33 for c in url) or '\\' in url:
            raise ValueError
        p = urlsplit(url)
        host = (p.hostname or '').encode('idna').decode('ascii').lower().rstrip('.')
        port = p.port
        if p.scheme not in {'http', 'https'} or not host or p.username is not None or p.password is not None:
            raise ValueError
        if port not in {None, 80 if p.scheme == 'http' else 443}:
            raise ValueError
        if '%' in host or '.' not in host and ':' not in host:
            raise ValueError
    except (ValueError, UnicodeError):
        raise InspectionError('unsafe_url') from None
    if host.endswith(('.localhost', '.local', '.internal', '.home', '.test', '.invalid')):
        raise InspectionError('nonpublic_host')
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        if not public_ip(address):
            raise InspectionError('nonpublic_address')
    if any(host == domain or host.endswith('.' + domain) for domain in (
            'github.com', 'githubusercontent.com', 'github.dev', 'github.io')):
        raise InspectionError('github_manual_review')
    if any(host == domain or host.endswith('.' + domain) for domain in (
            'docs.google.com', 'drive.google.com', 'accounts.google.com',
            'notion.so', 'atlassian.net', 'doc.weixin.qq.com', 'feishu.cn', 'larksuite.com')):
        raise InspectionError('authenticated_service_manual_review')
    path = unquote(p.path).lower()
    if (host.startswith(('api.', 'accounts.', 'login.', 'auth.')) or
            re.search(r'/(?:api|login|signin|sign-in|oauth|admin|private|account)(?:/|$)', path)):
        raise InspectionError('account_or_api_manual_review')
    if any(re.search(r'token|secret|password|signature|credential|auth|api.?key|session|ticket', key, re.I)
           for key, _ in parse_qsl(p.query, keep_blank_values=True)):
        raise InspectionError('credential_query')
    netloc = ('[' + host + ']') if ':' in host else host
    return urlunsplit((p.scheme, netloc, p.path or '/', p.query, ''))


def public_ip(address):
    # Block IPv4-mapped/transition IPv6 too; don't permit a tunnel to private IPv4.
    return (address.is_global and not address.is_multicast and
            not address.is_reserved and not address.is_unspecified and
            not (isinstance(address, ipaddress.IPv6Address) and
                 (address.ipv4_mapped or address.sixtofour or address.teredo)))


def resolve_public(host, port, timeout):
    """Kill a stuck resolver on timeout rather than leaving unbounded threads."""
    code = ('import json,socket,sys; '
            'print(json.dumps(socket.getaddrinfo(sys.argv[1],int(sys.argv[2]),'
            'type=socket.SOCK_STREAM)))')
    try:
        result = subprocess.run([sys.executable, '-I', '-c', code, host, str(port)],
                                capture_output=True, timeout=timeout, check=True)
        addresses = json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        raise InspectionError('timeout', 'failure') from None
    except (subprocess.CalledProcessError, OSError, ValueError):
        raise InspectionError('dns_error', 'failure') from None
    if not addresses:
        raise InspectionError('dns_error', 'failure')
    for family, _, _, _, address in addresses:
        if family not in {socket.AF_INET, socket.AF_INET6} or not public_ip(ipaddress.ip_address(address[0])):
            raise InspectionError('nonpublic_dns')
    return addresses


def remaining(deadline):
    budget = deadline - time.monotonic()
    if budget <= 0:
        raise InspectionError('timeout', 'failure')
    return budget


def download(url, timeout=12):
    """Fetch public text without a cookie jar, proxy, API credential or redirect bypass."""
    deadline = time.monotonic() + timeout
    current = url
    try:
        for hop in range(MAX_REDIRECTS + 1):
            current = checked_url(current)
            p = urlsplit(current)
            port = 443 if p.scheme == 'https' else 80
            addresses = resolve_public(p.hostname, port, remaining(deadline))
            connection = http.client.HTTPConnection(p.hostname, port, timeout=remaining(deadline))
            connection.auto_open = 0  # Only our validated/pinned socket may connect.
            sock, response, timer = None, None, None
            try:
                family, socktype, proto, _, address = addresses[0]
                # Defense in depth if a resolver adapter is substituted.
                if not all(public_ip(ipaddress.ip_address(a[4][0])) for a in addresses):
                    raise InspectionError('nonpublic_dns')
                sock = socket.socket(family, socktype, proto)
                sock.settimeout(remaining(deadline))
                sock.connect(tuple(address))
                if p.scheme == 'https':
                    sock.settimeout(remaining(deadline))
                    sock = ssl.create_default_context().wrap_socket(sock, server_hostname=p.hostname)
                connection.sock = sock

                def abort_slow_response():
                    # A per-recv timeout alone does not bound trickling HTTP headers.
                    try:
                        sock.shutdown(socket.SHUT_RDWR)
                    except OSError:
                        pass

                timer = threading.Timer(remaining(deadline), abort_slow_response)
                timer.daemon = True
                timer.start()
                target = p.path + ('?' + p.query if p.query else '')
                sock.settimeout(remaining(deadline))
                connection.request('GET', target, headers={
                    'User-Agent': 'YirenCatalogInspector/1.0 (read-only)',
                    'Accept': 'text/html,text/plain,application/xhtml+xml',
                    'Accept-Encoding': 'identity', 'Connection': 'close'})
                sock.settimeout(remaining(deadline))
                response = connection.getresponse()
                if response.status in {301, 302, 303, 307, 308}:
                    location = response.getheader('Location')
                    if not location or hop == MAX_REDIRECTS:
                        raise InspectionError('redirect_limit_or_missing_location')
                    target_url = checked_url(urljoin(current, location))
                    if p.scheme == 'https' and urlsplit(target_url).scheme != 'https':
                        raise InspectionError('tls_downgrade')
                    current = target_url
                    continue
                if response.status != 200:
                    raise InspectionError('http_' + str(response.status),
                                          'manual_required' if response.status in {401, 403, 429} else 'failure')
                content_type = response.headers.get_content_type()
                if content_type not in {'text/html', 'application/xhtml+xml', 'text/plain'}:
                    raise InspectionError('unsupported_content')
                if response.getheader('Content-Encoding', 'identity').lower() != 'identity':
                    raise InspectionError('unsupported_encoding')
                length = response.getheader('Content-Length')
                if length and (not length.isdigit() or int(length) > MAX_BYTES):
                    raise InspectionError('body_too_large_or_invalid_length')
                chunks, size = [], 0
                while True:
                    sock.settimeout(remaining(deadline))
                    chunk = response.read1(min(65536, MAX_BYTES + 1 - size))
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > MAX_BYTES:
                        raise InspectionError('body_too_large')
                    chunks.append(chunk)
                if length and size != int(length):
                    raise InspectionError('incomplete_response', 'failure')
                remaining(deadline)
                raw, text = inspect_text(b''.join(chunks), content_type,
                                         response.headers.get_content_charset() or 'utf-8')
                remaining(deadline)
                return {'raw': raw, 'text': text, 'url': current}
            finally:
                if timer is not None:
                    timer.cancel()
                    timer.join()
                if response is not None:
                    response.close()
                connection.close()
                if sock is not None:
                    sock.close()
    except InspectionError:
        raise
    except (TimeoutError, socket.timeout):
        raise InspectionError('timeout', 'failure') from None
    except ssl.SSLError:
        raise InspectionError('tls_error', 'failure') from None
    except (OSError, http.client.HTTPException, ValueError):
        reason = 'timeout' if time.monotonic() >= deadline else 'network_error'
        raise InspectionError(reason, 'failure') from None
    raise InspectionError('redirect_limit_or_missing_location')


def new_state():
    return {'version': 1, 'sources': {}, 'queue': {}, 'run_count': 0,
            'last_success_day': None, 'last_run': None}


def valid_stamp(value):
    return isinstance(value, str) and datetime.fromisoformat(value).tzinfo is not None


def require(condition):
    # Unlike assert, persistent-state safety checks must also run under python -O.
    if not condition:
        raise ValueError('Invalid local state')


def id_list(value):
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def validate_snapshot(value, root):
    if value is None:
        return
    require(isinstance(value, dict) and valid_stamp(value['inspected_at']))
    require(isinstance(value['source_url'], str) and id_list(value['record_ids']))
    for kind in ('raw', 'text'):
        hash_value = value[kind + '_sha256']
        require(isinstance(hash_value, str) and HASH.fullmatch(hash_value))
        require(value[kind + '_path'] == 'snapshots/' + hash_value + '.txt')
        path = root / value[kind + '_path']
        require(path.is_file() and not path.is_symlink() and not path.parent.is_symlink())


def read_state(root):
    path = root / 'state.json'
    if not path.exists() and not path.is_symlink():
        # A genuinely new state is fine; lost state beside preserved evidence isn't.
        if (root / 'snapshots').exists() and any((root / 'snapshots').iterdir()):
            raise MaintenanceError('Missing state.json beside existing snapshots; restore state before continuing')
        return new_state()
    try:
        require(not path.is_symlink())
        state = json.loads(path.read_text(encoding='utf-8'))
        require(state['version'] == 1 and isinstance(state['sources'], dict))
        require(isinstance(state['queue'], dict) and type(state['run_count']) is int and state['run_count'] >= 0)
        if state['last_success_day'] is not None:
            date.fromisoformat(state['last_success_day'])
        run = state['last_run']
        if run is not None:
            require(isinstance(run, dict) and valid_stamp(run['started_at']))
            date.fromisoformat(run['day'])
            for field in ('attempted', 'successful', 'failure', 'manual_required',
                          'total_sources', 'not_attempted_in_batch'):
                require(type(run[field]) is int and run[field] >= 0)
            require(run['attempted'] == run['successful'] + run['failure'] + run['manual_required'])
        for key, source in state['sources'].items():
            require(HASH.fullmatch(key) and isinstance(source['url'], str))
            require(id_list(source['record_ids']) and id_list(source['source_ids']))
            require(source['status'] in STATUSES and isinstance(source['reason'], str))
            require(valid_stamp(source['last_attempt_at']))
            require(source['last_successful_inspection_at'] is None or valid_stamp(source['last_successful_inspection_at']))
            for name in ('accepted_baseline', 'latest_observation'):
                validate_snapshot(source[name], root)
        require(set(state['queue']) == {'q' + str(n + 1).zfill(8) for n in range(len(state['queue']))})
        for key, item in state['queue'].items():
            require(item['id'] == key)
            require(item['source_key'] in state['sources'] and id_list(item['record_ids']))
            require(item['status'] in {'pending', 'dismissed'})
            require(item['kind'] in {'baseline_candidate', 'content_change'})
            require(valid_stamp(item['first_seen_at']) and valid_stamp(item['last_seen_at']))
            validate_snapshot(item['before'], root)
            require(item['after'] is not None)
            validate_snapshot(item['after'], root)
            if item['status'] == 'dismissed':
                require(valid_stamp(item['resolved_at']) and isinstance(item['reason'], str) and item['reason'].strip())
        return state
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        raise MaintenanceError('Damaged or unsupported local state; preserve it and restore from backup') from None


@contextmanager
def state_lock(root):
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock_path = root / '.lock'
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise MaintenanceError('Another maintenance invocation holds the state lock') from None
        yield
    finally:
        os.close(fd)  # Keep the inode: unlinking creates a lock race.


def atomic_json(path, value):
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def store_text(root, text):
    sha = digest(text)
    directory = root / 'snapshots'
    if directory.is_symlink():
        raise MaintenanceError('Snapshot directory must not be a symlink')
    directory.mkdir(exist_ok=True, mode=0o700)
    path = directory / (sha + '.txt')
    data = text.encode('utf-8')
    if path.exists() or path.is_symlink():
        if path.is_symlink() or path.read_bytes() != data:
            raise MaintenanceError('Snapshot integrity failure; existing evidence was not overwritten')
    else:
        fd, temporary = tempfile.mkstemp(prefix='.snapshot-', dir=directory)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.link(temporary, path)
            directory_fd = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            os.unlink(temporary)
    return sha, 'snapshots/' + path.name


def records_of(doc):
    if not isinstance(doc, dict) or not isinstance(doc.get('records'), list):
        raise MaintenanceError('catalog.load() must return a document with a records list')
    return doc['records']


def source_index(doc):
    sources = {}
    for record in records_of(doc):
        for source in record['sources']:
            raw_url = source['url']
            # Invalid URLs still get coverage/manual entries, without printing secrets.
            try:
                canonical = checked_url(raw_url)
            except InspectionError:
                canonical = raw_url.split('#', 1)[0]
            key = digest(canonical)
            entry = sources.setdefault(key, {'url': raw_url, 'record_ids': [], 'source_ids': []})
            if record['id'] not in entry['record_ids']:
                entry['record_ids'].append(record['id'])
            if source['id'] not in entry['source_ids']:
                entry['source_ids'].append(source['id'])
    return sources


def parsed_date(value):
    try:
        return date.fromisoformat(str(value)) if value else None
    except ValueError:
        return None


def select_sources(doc, index, state, limit, day):
    today = date.fromisoformat(day)
    near = {r['id'] for r in records_of(doc)
            if (end := parsed_date((r.get('window') or {}).get('end'))) is not None
            and 0 <= (end - today).days <= 14}
    oldest = sorted(index, key=lambda key: (
        state['sources'].get(key, {}).get('last_attempt_at', ''), key))
    urgent = [key for key in oldest if near.intersection(index[key]['record_ids'])]
    # Reserve at least half for rotation; with limit=1 alternate urgent/rotation.
    quota = limit // 2 if limit > 1 else int(state['run_count'] % 2 == 0)
    chosen = urgent[:quota]
    return (chosen + [key for key in oldest if key not in chosen])[:limit]


def observe(state, root, key, entry, result, stamp):
    source = state['sources'][key]
    snapshot = {'source_url': checked_url(entry['url']), 'record_ids': entry['record_ids'][:],
                'final_url': checked_url(result.get('url', entry['url'])), 'inspected_at': stamp}
    for kind in ('raw', 'text'):
        sha, path = store_text(root, result[kind])
        snapshot[kind + '_sha256'], snapshot[kind + '_path'] = sha, path
    baseline = source['accepted_baseline']
    previous = baseline or source['latest_observation']
    source['latest_observation'] = snapshot
    source['last_successful_inspection_at'] = stamp
    source['status'], source['reason'] = 'inspected', 'text_observed_not_verified'
    if baseline and baseline['text_sha256'] == snapshot['text_sha256']:
        return
    pending = next((item for item in state['queue'].values()
                    if item['source_key'] == key and item['status'] == 'pending'
                    and item['after']['text_sha256'] == snapshot['text_sha256']), None)
    if pending:
        pending['last_seen_at'] = stamp
        pending['record_ids'] = sorted(set(pending['record_ids']) | set(entry['record_ids']))
        return
    item_id = 'q' + str(len(state['queue']) + 1).zfill(8)
    state['queue'][item_id] = {
        'id': item_id, 'source_key': key, 'record_ids': entry['record_ids'][:],
        'kind': 'content_change' if previous else 'baseline_candidate',
        'status': 'pending', 'before': previous, 'after': snapshot,
        'first_seen_at': stamp, 'last_seen_at': stamp}


def scan(doc, state_dir=DEFAULT_STATE_DIR, *, if_due=False, limit=20, timeout=12,
         now=None, downloader=None):
    if not 1 <= limit <= 1000 or not math.isfinite(timeout) or not 0 < timeout <= 120:
        raise MaintenanceError('limit must be 1..1000 and timeout must be >0..120 seconds')
    root = Path(state_dir).expanduser().resolve()
    stamp = timestamp(now)
    day = local_day(stamp)
    index = source_index(doc)
    downloader = downloader or download
    with state_lock(root):
        state = read_state(root)
        if if_due and state['last_success_day'] == day:
            return {'skipped': True, 'reason': 'successful_batch_already_today',
                    'summary': make_report(doc, state, stamp)}
        if not (root / 'state.json').exists():
            atomic_json(root / 'state.json', state)
        selected = select_sources(doc, index, state, limit, day)
        run = {'started_at': stamp, 'day': day, 'attempted': 0, 'successful': 0,
               'failure': 0, 'manual_required': 0, 'total_sources': len(index),
               'not_attempted_in_batch': len(index) - len(selected)}
        for key in selected:
            entry = index[key]
            source = state['sources'].setdefault(key, {
                'url': '<withheld until public URL validation>', 'record_ids': [], 'source_ids': [],
                'last_successful_inspection_at': None, 'accepted_baseline': None,
                'latest_observation': None})
            source.update(record_ids=entry['record_ids'][:], source_ids=entry['source_ids'][:],
                          last_attempt_at=timestamp(now))
            try:
                url = checked_url(entry['url'])
                source['url'] = url
                result = downloader(url, timeout)
            except InspectionError as error:
                source['status'], source['reason'] = error.status, error.reason
                run[error.status] += 1
            except (OSError, http.client.HTTPException):
                source['status'], source['reason'] = 'failure', 'network_error'
                run['failure'] += 1
            else:
                inspected_at = timestamp(now)
                # Disk failures must stop the run, not masquerade as network failures.
                observe(state, root, key, entry, result, inspected_at)
                run['successful'] += 1
                state['last_success_day'] = local_day(inspected_at)
            run['attempted'] += 1
            state['last_run'] = run.copy()
            # Persist each completed attempt, so interruption retains evidence/progress.
            atomic_json(root / 'state.json', state)
        state['run_count'] += 1
        state['last_run'] = run
        atomic_json(root / 'state.json', state)
        return {'skipped': False, 'run': run, 'summary': make_report(doc, state, timestamp(now))}


def make_report(doc, state, stamp):
    index = source_index(doc)
    records = records_of(doc)
    day = local_day(stamp)
    today = date.fromisoformat(day)
    attempted, inspected, today_attempted, today_inspected = set(), set(), set(), set()
    issues = []
    for key, entry in index.items():
        source = state['sources'].get(key)
        if not source:
            continue
        attempted.add(key)
        if local_day(source['last_attempt_at']) == day:
            today_attempted.add(key)
        success = source['last_successful_inspection_at']
        if success:
            inspected.add(key)
            if local_day(success) == day:
                today_inspected.add(key)
        if source['status'] != 'inspected':
            issues.append({'source_key': key, 'record_ids': entry['record_ids'],
                           'status': source['status'], 'reason': source['reason'],
                           'last_attempt_at': source['last_attempt_at'],
                           'last_successful_inspection_at': success})
    queue = [{'id': item['id'], 'source_key': item['source_key'],
              'record_ids': item['record_ids'], 'kind': item['kind'],
              'first_seen_at': item['first_seen_at'], 'last_seen_at': item['last_seen_at'],
              'before_sha256': (item['before'] or {}).get('text_sha256'),
              'after_sha256': item['after']['text_sha256']}
             for item in state['queue'].values() if item['status'] == 'pending']
    deadlines, upcoming, unknown = [], [], []
    unverified = []
    for record in records:
        if not record.get('last_verified_at'):
            fields = record.get('fields', [])
            metadata = ['title', 'access', 'lifecycle']
            if record.get('window'):
                metadata += ['window.kind', 'window.start', 'window.end']
            unverified.append({
                'record_id': record['id'], 'total_field_count': len(fields),
                'unverified_field_count': sum(not field.get('verified_at') for field in fields),
                'unverified_metadata': [key for key in metadata
                                        if not record.get('metadata_verification', {}).get(key)]})
        window = record.get('window') or {}
        end = parsed_date(window.get('end'))
        start = parsed_date(window.get('start'))
        if window and not end:
            unknown.append(record['id'])
        if end:
            days = (end - today).days
            if days <= 14:
                deadlines.append({'record_id': record['id'], 'end': end.isoformat(),
                                  'days_remaining': days, 'status': 'overdue' if days < 0 else 'upcoming'})
        if start and 0 <= (start - today).days <= 14:
            upcoming.append({'record_id': record['id'], 'start': start.isoformat()})
    full = sum(bool(record['sources']) and all(
        key in inspected for key, entry in index.items() if record['id'] in entry['record_ids'])
        for record in records)
    return {
        'generated_at': stamp, 'day': day, 'last_success_day': state['last_success_day'],
        'notice': 'Text inspection only: not fact verification, availability certification, or full-catalog freshness.',
        'coverage': {'total_records': len(records), 'total_sources': len(index),
                     'sources_attempted_ever': len(attempted), 'sources_inspected_ever': len(inspected),
                     'sources_never_attempted': len(index) - len(attempted),
                     'sources_never_inspected': len(index) - len(inspected),
                     'sources_attempted_today': len(today_attempted),
                     'sources_inspected_today': len(today_inspected),
                     'records_all_sources_inspected_ever': full,
                     'records_without_sources': sum(not r['sources'] for r in records)},
        'last_run': state['last_run'], 'issues': issues,
        'pending_count': len(queue), 'pending': queue,
        'deadlines': sorted(deadlines, key=lambda x: (x['end'], x['record_id'])),
        'upcoming_starts': upcoming, 'windows_without_end': unknown,
        'unverified_count': len(unverified), 'unverified_facts': unverified}


def public_summary(report):
    """Explicit export allowlist: counts and timestamps only; no texts/URLs/IDs."""
    return {'generated_at': report['generated_at'], 'day': report['day'],
            'last_success_day': report['last_success_day'],
            'coverage': report['coverage'], 'pending_count': report['pending_count'],
            'failure_count': sum(i['status'] == 'failure' for i in report['issues']),
            'manual_required_count': sum(i['status'] == 'manual_required' for i in report['issues']),
            'overdue_count': sum(d['status'] == 'overdue' for d in report['deadlines']),
            'upcoming_deadline_count': sum(d['status'] == 'upcoming' for d in report['deadlines']),
            'unverified_count': report['unverified_count']}


def report(doc, state_dir=DEFAULT_STATE_DIR, *, now=None, output=None):
    root = Path(state_dir).expanduser().resolve()
    with state_lock(root):
        result = make_report(doc, read_state(root), timestamp(now))
        if output:
            path = Path(output).expanduser().absolute()
            if root == path.resolve() or root in path.resolve().parents:
                raise MaintenanceError('Summary export must be outside the private state directory')
            if not path.parent.is_dir() or path.is_symlink():
                raise MaintenanceError('Summary output needs an existing parent and a non-symlink path')
            summary = public_summary(result)
            if path.exists():
                try:
                    previous = json.loads(path.read_text(encoding='utf-8'))
                    require(isinstance(previous, dict) and previous.keys() == summary.keys())
                    require(isinstance(previous['coverage'], dict) and
                            previous['coverage'].keys() == summary['coverage'].keys())
                except (OSError, ValueError, KeyError, TypeError):
                    raise MaintenanceError('Refusing to overwrite a non-summary file; choose a new output path') from None
            atomic_json(path, summary)
        return result


def dismiss(queue_id, reason, state_dir=DEFAULT_STATE_DIR, *, now=None):
    if not reason or not reason.strip() or len(reason) > 2000:
        raise MaintenanceError('Dismissal requires a nonempty reason of at most 2000 characters')
    root = Path(state_dir).expanduser().resolve()
    with state_lock(root):
        state = read_state(root)
        item = state['queue'].get(queue_id)
        if not item or item['status'] != 'pending':
            raise MaintenanceError('Review item not found or already dismissed')
        for kind in ('raw', 'text'):
            data = (root / item['after'][kind + '_path']).read_bytes()
            if hashlib.sha256(data).hexdigest() != item['after'][kind + '_sha256']:
                raise MaintenanceError('Snapshot integrity failure; review was not applied')
        item.update(status='dismissed', reason=reason.strip(), resolved_at=timestamp(now))
        state['sources'][item['source_key']]['accepted_baseline'] = item['after']
        atomic_json(root / 'state.json', state)
        return {'id': queue_id, 'status': 'dismissed', 'canonical_data_changed': False,
                'notice': 'Comparison baseline acknowledged only; facts remain unverified.'}


def load_catalog():
    try:
        from catalog import load, validate
        doc = load()
        result = validate(doc)
        if result is False or isinstance(result, (list, tuple)) and result:
            raise MaintenanceError('Catalog validation failed; no inspection was performed')
        records_of(doc)
        return doc
    except MaintenanceError:
        raise
    except Exception:
        raise MaintenanceError('Catalog unavailable or invalid; provide catalog.load() and catalog.validate(doc)') from None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--state-dir', default=str(DEFAULT_STATE_DIR))
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('scan', 'report', 'dismiss'):
        command = commands.add_parser(name)
        command.add_argument('--state-dir', default=argparse.SUPPRESS)
        if name == 'scan':
            command.add_argument('--if-due', action='store_true')
            command.add_argument('--limit', type=int, default=20)
            command.add_argument('--timeout', type=float, default=12)
        elif name == 'report':
            command.add_argument('--output', help='Explicit counts/timestamps-only JSON export')
        else:
            command.add_argument('queue_id')
            command.add_argument('--reason', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'dismiss':
            result = dismiss(args.queue_id, args.reason, args.state_dir)
        elif args.command == 'report':
            result = report(load_catalog(), args.state_dir, output=args.output)
        else:
            result = scan(load_catalog(), args.state_dir, if_due=args.if_due,
                          limit=args.limit, timeout=args.timeout)
        print(json.dumps(result, ensure_ascii=False))
        run = result.get('run', {})
        return int(bool(run.get('attempted')) and not run.get('successful'))
    except (MaintenanceError, OSError):
        error = sys.exc_info()[1]
        message = str(error) if isinstance(error, MaintenanceError) else 'Local state I/O failed; evidence was not intentionally removed'
        print(json.dumps({'error': message}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
