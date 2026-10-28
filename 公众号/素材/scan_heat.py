#!/usr/bin/env python3
"""选题扫描：关键词资讯搜索（360 资讯，按时间排序）+ 新浪滚动兜底，不扫热榜。

用「短剧 / AI短剧 / 红果 / 微短剧 / AI漫剧」逐词搜索，并用新浪科技/娱乐/财经
滚动流做交叉；同一选题至少 2 家互不隶属的媒体同题报道才写入
公众号/素材/候选池.md；每条记录搜索词 / 媒体 / 发布时间 / 查询时间。
去重状态与日志放仓库外。只在 10:00—19:00 时段运行；机器休眠唤醒后由 launchd 补跑。
"""
import argparse
import hashlib
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POOL_PATH = ROOT / '公众号' / '素材' / '候选池.md'
STATE_DIR = Path.home() / '.local' / 'state' / 'yiren-heat-scan'
SEEN_PATH = STATE_DIR / 'seen.json'
LAST_PATH = STATE_DIR / 'last_run'

KEYWORDS = ('短剧', 'AI短剧', '红果', '微短剧', 'AI漫剧')
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'

POOL_HEADER = """# 候选池

来源：360 资讯关键词新闻搜索（短剧 / AI短剧 / 红果 / 微短剧 / AI漫剧，按时间排序）+ 新浪科技/娱乐/财经滚动流交叉；另有一层 Qoder 定时 Agent 用 WebSearch 补充（每日 4 次），条目格式相同。不扫热榜。
规则：同一选题至少 2 家互不隶属的媒体同题报道才写入（同一家多条、同集团频道、同篇通稿转载都只算 1 个来源）；每条带搜索词、媒体、发布时间、查询时间。
搜索只说明有动静，过门仍需人工核：24—72 小时、≥2 个独立信源、可复查的阅读/榜单凭据。
"""


def now():
    return datetime.now()


def fetch_text(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode('utf-8', 'ignore')


def compact(text):
    return re.sub(r'\s+', '', text or '')


def matched_keywords(*texts):
    text = compact(' '.join(texts))
    return [k for k in KEYWORDS if k in text]


def make_item(platform, source_key, title, url, metric, keywords, time_text=''):
    return {
        'platform': platform,
        'source_key': source_key,
        'title': (title or '').strip(),
        'url': url or '',
        'metric': metric,
        'keywords': keywords,
        'time': time_text,
    }


def parse_time_text(text):
    text = (text or '').strip()
    if not text:
        return ''
    base = now()
    try:
        if text == '刚刚':
            return base.strftime('%Y-%m-%d %H:%M:%S')
        m = re.match(r'(\d+)\s*分钟前', text)
        if m:
            return (base - timedelta(minutes=int(m.group(1)))).strftime('%Y-%m-%d %H:%M:%S')
        m = re.match(r'(\d+)\s*小时前', text)
        if m:
            return (base - timedelta(hours=int(m.group(1)))).strftime('%Y-%m-%d %H:%M:%S')
        m = re.match(r'今天\s*(\d{1,2}):(\d{2})', text)
        if m:
            return base.replace(hour=int(m.group(1)), minute=int(m.group(2)),
                                second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
        m = re.match(r'昨天\s*(\d{1,2}):(\d{2})', text)
        if m:
            day = base - timedelta(days=1)
            return day.replace(hour=int(m.group(1)), minute=int(m.group(2)),
                               second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
        m = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})(?:\s+(\d{1,2}):(\d{2}))?', text)
        if m:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                            int(m.group(4) or 0), int(m.group(5) or 0)).strftime('%Y-%m-%d %H:%M:%S')
        m = re.match(r'(\d{1,2})-(\d{1,2})(?:\s+(\d{1,2}):(\d{2}))?', text)
        if m:
            return datetime(base.year, int(m.group(1)), int(m.group(2)),
                            int(m.group(3) or 0), int(m.group(4) or 0)).strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return ''
    return ''


def domain_of(url):
    try:
        return urllib.parse.urlsplit(url).hostname or ''
    except ValueError:
        return ''


def source_key_of(url):
    host = domain_of(url)
    if host == 'sina.com' or host.endswith('.sina.com.cn') or host == 'sina.com.cn':
        return 'sina'
    return host


NOISE_WORDS = ('炒红果', '糖葫芦', '山楂', '果丹皮', '做法', '美味')


def fetch_news_search():
    items = []
    seen_urls = set()
    for query in KEYWORDS:
        url = 'https://news.so.com/ns?' + urllib.parse.urlencode({
            'q': query, 'pn': 1, 'rn': 20, 'j': 0, 'rad': '', 'sort': 1,
        })
        page = fetch_text(url)
        for block in re.findall(r'<li[^>]*res-list[^>]*>.*?</li>', page, re.S):
            m = re.search(r'<a[^>]*href="([^"]+)"[^>]*title="([^"]+)"', block)
            if not m:
                continue
            link = m.group(1)
            if link.startswith('/'):
                link = 'https://news.so.com' + link
            if link in seen_urls:
                continue
            seen_urls.add(link)
            title = html.unescape(m.group(2)).strip()
            if any(word in title for word in NOISE_WORDS):
                continue
            kws = matched_keywords(title)
            if not kws:
                continue
            site = re.search(r'<cite[^>]*class="sitename"[^>]*>(.*?)</cite>', block, re.S)
            site = html.unescape(re.sub(r'<[^>]+>', '', site.group(1))).strip() if site else ''
            if not site:
                site = domain_of(link)
            tm = re.search(r'class="[^"]*time[^"]*"[^>]*>([^<]+)<', block)
            tm = tm.group(1).strip() if tm else ''
            stamp = parse_time_text(tm)
            if stamp and not is_fresh(stamp, hours=36):
                continue
            items.append(make_item(site or '未署名', source_key_of(link), title, link,
                                   tm or '时间未给', kws, stamp))
    return items


SINA_ROLL_LIDS = (('科技', 2515), ('娱乐', 2514), ('财经', 2516))


def fetch_sina_roll():
    items = []
    seen_urls = set()
    for channel, lid in SINA_ROLL_LIDS:
        url = 'https://feed.mix.sina.com.cn/api/roll/get?' + urllib.parse.urlencode({
            'pageid': 153, 'lid': lid, 'k': '', 'num': 50, 'page': 1,
        })
        data = json.loads(fetch_text(url))
        for entry in (data.get('result') or {}).get('data') or []:
            title = (entry.get('title') or entry.get('stitle') or '').strip()
            kws = matched_keywords(title)
            if not kws:
                continue
            link = entry.get('url') or entry.get('wapurl') or ''
            if not link or link in seen_urls:
                continue
            seen_urls.add(link)
            stamp = ''
            if entry.get('ctime'):
                try:
                    stamp = datetime.fromtimestamp(int(entry['ctime'])).strftime('%Y-%m-%d %H:%M:%S')
                except (TypeError, ValueError, OSError):
                    pass
            if stamp and not is_fresh(stamp, hours=36):
                continue
            media = (entry.get('media_name') or '').strip() or domain_of(link)
            metric = f'{channel}滚动，发布 {stamp}' if stamp else f'{channel}滚动，时间未给'
            items.append(make_item(media or '未署名', 'sina', title, link,
                                   metric, kws, stamp))
    return items


def is_fresh(stamp, hours=36):
    try:
        return datetime.strptime(stamp, '%Y-%m-%d %H:%M:%S') >= now() - timedelta(hours=hours)
    except (TypeError, ValueError):
        return True


def norm_title(text):
    text = re.sub(r'^【[^】]*】', '', text or '')
    return re.sub(r'[\s\W_]+', '', text).lower()


def bigrams(text):
    return {text[i:i + 2] for i in range(len(text) - 1)}


def lcs_len(a, b):
    if len(a) < len(b):
        a, b = b, a
    prev = [0] * (len(b) + 1)
    for ch in a:
        cur = [0]
        for j, other in enumerate(b, 1):
            cur.append(prev[j - 1] + 1 if ch == other else max(prev[j], cur[-1]))
        prev = cur
    return prev[-1]


def same_topic(a, b):
    na, nb = norm_title(a), norm_title(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    short, long = sorted((na, nb), key=len)
    if len(short) >= 6 and short in long:
        return True
    if len(short) >= 8:
        left, right = bigrams(na), bigrams(nb)
        if len(left & right) / len(left | right) >= 0.5:
            return True
    return lcs_len(na, nb) >= 8


def cluster_topics(items):
    parent = list(range(len(items)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if not (set(items[i]['keywords']) & set(items[j]['keywords'])):
                continue
            if same_topic(items[i]['title'], items[j]['title']):
                union(i, j)

    clusters = {}
    for i, item in enumerate(items):
        clusters.setdefault(find(i), []).append(item)
    return list(clusters.values())


def topic_key(cluster):
    rep = max(cluster, key=lambda it: len(norm_title(it['title'])))
    digest = hashlib.sha1(norm_title(rep['title']).encode('utf-8')).hexdigest()[:16]
    return f'topic:{digest}', rep['title']


def already_seen(title, seen):
    return any(same_topic(title, entry.get('title') or '') for entry in seen.values())


def select_candidates(clusters, seen):
    candidates = []
    for cluster in clusters:
        source_keys = {it['source_key'] for it in cluster}
        if len(source_keys) < 2:
            continue
        key, title = topic_key(cluster)
        if key in seen or already_seen(title, seen):
            continue
        platforms = []
        for item in cluster:
            if item['platform'] not in platforms:
                platforms.append(item['platform'])
        keywords = []
        for item in cluster:
            for kw in item['keywords']:
                if kw not in keywords:
                    keywords.append(kw)
        candidates.append({
            'key': key,
            'title': max(cluster, key=lambda it: len(it['title']))['title'],
            'platforms': platforms,
            'source_keys': source_keys,
            'keywords': keywords,
            'items': cluster,
        })
    candidates.sort(key=lambda c: (-len(c['source_keys']), -len(c['items'])))
    return candidates


def metrics_summary(items):
    parts = []
    seen = set()
    for item in items:
        key = (item['platform'], item['metric'])
        if key in seen:
            continue
        seen.add(key)
        parts.append(f"{item['platform']} {item['metric']}")
    return '；'.join(parts)


def source_status_text(status):
    return ' / '.join(f'{name} {value}' for name, value in status.items())


def render_section(candidates, scan_dt, status):
    lines = []
    if not candidates:
        lines.append(f"\n<!-- {scan_dt:%Y-%m-%d %H:%M} 扫描：{source_status_text(status)}；候选 0 -->\n")
        return ''.join(lines)

    lines.append(f"\n## {scan_dt:%Y-%m-%d %H:%M} 扫描（候选 {len(candidates)} 条）\n")
    lines.append(f"<!-- 源状态：{source_status_text(status)} -->\n")
    for cand in candidates:
        lines.append(f"\n### {cand['title']}\n\n")
        lines.append(f"- 搜索词：{'、'.join(cand['keywords'])}\n")
        lines.append(f"- 平台：{' / '.join(cand['platforms'])}（独立来源 {len(cand['source_keys'])} 个）\n")
        lines.append(f"- 查询时间：{scan_dt:%Y-%m-%d %H:%M}\n")
        lines.append(f"- 可见指标：{metrics_summary(cand['items'])}\n")
        lines.append('- 来源条目：\n')
        for item in cand['items']:
            lines.append(f"  - [{item['platform']}] {item['title']}（{item['metric']}）{item['url']}\n")
    return ''.join(lines)


def load_seen():
    if SEEN_PATH.exists():
        try:
            return json.loads(SEEN_PATH.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            pass
    return {}


def prune_seen(seen):
    cutoff = (now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    return {k: v for k, v in seen.items() if (v.get('first_seen') or '') >= cutoff}


def collect():
    items = []
    status = {}
    seen_urls = set()
    sources = (
        ('360资讯', fetch_news_search),
        ('新浪滚动', fetch_sina_roll),
    )
    for name, fetcher in sources:
        try:
            batch = fetcher()
        except Exception as exc:
            status[name] = '不可用'
            print(f'[warn] {name}: {exc}', file=sys.stderr)
            continue
        kept = [it for it in batch if it['url'] and it['url'] not in seen_urls]
        seen_urls.update(it['url'] for it in kept)
        items.extend(kept)
        status[name] = f'{len(batch)} 条'
    return items, status


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--if-due', action='store_true', help='距上次运行不足 55 分钟则跳过')
    parser.add_argument('--window', default='10-19', help='允许运行的小时窗口，如 10-19')
    parser.add_argument('--notify', action='store_true', help='有新候选时发 macOS 通知')
    args = parser.parse_args()

    start_h, end_h = (int(x) for x in args.window.split('-'))
    if not start_h <= now().hour <= end_h:
        return 0

    if args.if_due and LAST_PATH.exists():
        try:
            if time.time() - LAST_PATH.stat().st_mtime < 55 * 60:
                return 0
        except OSError:
            pass

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    seen = prune_seen(load_seen())
    items, status = collect()
    if all(value == '不可用' for value in status.values()):
        print(f'[{now():%H:%M}] 所有源均失败，未写入候选池', file=sys.stderr)
        return 1

    candidates = select_candidates(cluster_topics(items), seen)
    scanned_at = now()
    if not POOL_PATH.exists():
        POOL_PATH.write_text(POOL_HEADER, encoding='utf-8')
    POOL_PATH.open('a', encoding='utf-8').write(render_section(candidates, scanned_at, status))

    for cand in candidates:
        seen[cand['key']] = {
            'first_seen': scanned_at.strftime('%Y-%m-%d %H:%M:%S'),
            'title': cand['title'],
        }
    SEEN_PATH.write_text(json.dumps(seen, ensure_ascii=False, indent=0), encoding='utf-8')
    LAST_PATH.touch()

    print(f'[{scanned_at:%H:%M}] {source_status_text(status)}；候选 {len(candidates)} 条')
    for cand in candidates[:10]:
        print(f"  {cand['title']}（{len(cand['source_keys'])} 个独立来源）")

    if args.notify and candidates:
        import subprocess
        top = candidates[0]
        script = (
            'display notification ' + json.dumps(top['title'][:40], ensure_ascii=False)
            + ' with title "候选池：新增 %d 条" subtitle "%d 个独立来源"' % (
                len(candidates), len(top['source_keys']))
        )
        subprocess.run(['/usr/bin/osascript', '-e', script], check=False)
    return 0


if __name__ == '__main__':
    sys.exit(main())
