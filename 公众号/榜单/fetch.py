#!/usr/bin/env python3
"""短剧榜单公开信号归档：抓取 -> 落库 -> 校验。

数据源为第三方转算指数，非平台官方口径，所有引用必须同时给出源 URL：
https://www.duanjugongcheng.com/cn/bangdan/YYYY-MM-DD[?board=N]

三种榜单（同一路径的 board 参数）：1=热播榜（当日热播指数）、2=好评榜（当日好评分）、3=预约榜（当日预约值）。
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import re
import sqlite3
import time
import urllib.error
import urllib.request
from datetime import date
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'raw'
DATA = ROOT / 'data'
DB = DATA / 'bangdan.sqlite'
SITE = 'https://www.duanjugongcheng.com'
UA = 'personal-short-drama-archive/1.0 (single daily request)'
SOURCE = 'duanjugongcheng/hongguo-hot'
SLEEP_SEC = 1.0

BOARDS = {1: ('热播榜', '当日热播指数'), 2: ('好评榜', '当日好评分'), 3: ('预约榜', '当日预约值')}

SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshot (
  edition_date TEXT NOT NULL,
  source       TEXT NOT NULL,
  board        INTEGER NOT NULL,
  rank         INTEGER NOT NULL,
  title        TEXT NOT NULL,
  genre        TEXT NOT NULL,
  listed_on    TEXT NOT NULL,
  metric_name  TEXT NOT NULL,
  metric_value INTEGER NOT NULL,
  is_new       INTEGER NOT NULL DEFAULT 0,
  raw_sha256   TEXT NOT NULL,
  fetched_at   TEXT NOT NULL,
  PRIMARY KEY (edition_date, source, board, rank)
);
CREATE INDEX IF NOT EXISTS idx_title ON snapshot (title, edition_date, board);
"""


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def editions() -> list[str]:
    xml = fetch(f'{SITE}/sitemap.xml').decode('utf-8', 'ignore')
    found = sorted(set(re.findall(r'/cn/bangdan/(\d{4}-\d{2}-\d{2})', xml)))
    assert found, 'sitemap 未发现任何榜单期次'
    return found


def strip_tags(fragment: str) -> str:
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', ' ', fragment))).strip()


def parse(page: str, edition: str) -> list[dict]:
    head = re.search(r'<title>([^<]*)', page)
    assert head, f'{edition} 缺少 title'
    y, m, d = edition.split('-')
    assert f'{y}年{int(m)}月{int(d)}日' in head.group(1), (edition, head.group(1))

    rows = []
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', page, re.S):
        cells = [strip_tags(c) for c in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
        if len(cells) != 5:
            continue
        rank, _cover, name_cell, genre, metric = cells
        # 单元格形如「剧名 上架 2026-10-13」；部分条目未公布上架日，此时无「上架」段
        if '上架' in name_cell:
            title, _, tail = name_cell.partition('上架')
            listed = tail.strip()
            assert not listed or re.fullmatch(r'\d{4}-\d{2}-\d{2}', listed), (edition, listed)
        else:
            title, listed = name_cell, ''
        title = title.strip()
        # 新剧条目在剧名后拼了「新」徽标，需剥离，否则同一部剧会被算成「新进 + 掉出」
        is_new = 1 if re.search(r'\s+新$', title) else 0
        title = re.sub(r'\s+新$', '', title)
        # metric 单元格为裸数字，该站未公布单位
        digits = re.sub(r'[^0-9]', '', metric)
        assert int(rank) == len(rows) + 1, (edition, rank)
        # 站点偶发占位行：标题与详情链接为空（2026-10-27 预约榜第 54 名）。
        # 用占位标题保住名次连续性，下游按「（无标题」前缀可排除。
        if not title:
            print(f'[{edition}] 第 {rank} 名标题为空，按占位处理', flush=True)
            title = f'（无标题 #{rank}）'
        assert genre and digits, (edition, cells)
        rows.append({
            'rank': int(rank),
            'title': title,
            'genre': genre,
            'listed_on': listed,
            'metric_value': int(digits),
            'is_new': is_new,
        })

    assert len(rows) >= 50, (edition, len(rows))
    assert [r['rank'] for r in rows] == list(range(1, len(rows) + 1)), edition
    return rows


def raw_path(edition: str, board: int) -> Path:
    return RAW / f'{edition}_b{board}.html.gz'


def store(conn: sqlite3.Connection, edition: str, board: int, rows: list[dict],
          digest: str, fetched_at: str) -> None:
    metric_name = BOARDS[board][1]
    conn.execute('DELETE FROM snapshot WHERE edition_date=? AND source=? AND board=?',
                 (edition, SOURCE, board))
    conn.executemany(
        'INSERT INTO snapshot VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
        [(edition, SOURCE, board, r['rank'], r['title'], r['genre'], r['listed_on'],
          metric_name, r['metric_value'], r['is_new'], digest, fetched_at) for r in rows],
    )
    conn.commit()


def ingest(conn: sqlite3.Connection, edition: str, board: int, page: str) -> int:
    rows = parse(page, edition)
    digest = hashlib.sha256(page.encode()).hexdigest()[:16]
    store(conn, edition, board, rows, digest, time.strftime('%Y-%m-%dT%H:%M:%S%z'))
    RAW.mkdir(parents=True, exist_ok=True)
    with gzip.open(raw_path(edition, board), 'wb', compresslevel=6) as fh:
        fh.write(page.encode())
    return len(rows)


def url_for(edition: str, board: int) -> str:
    base = f'{SITE}/cn/bangdan/{edition}'
    return base if board == 1 else f'{base}?board={board}'


def cmd_backfill(conn: sqlite3.Connection, board: int) -> None:
    want = editions()
    have = {r[0] for r in conn.execute(
        'SELECT DISTINCT edition_date FROM snapshot WHERE board=?', (board,))}
    todo = [e for e in want if e not in have]
    print(f'[board={board} {BOARDS[board][0]}] 期次 {len(want)}，已有 {len(have)}，待抓 {len(todo)}')
    absent, done = [], 0
    for i, edition in enumerate(todo, 1):
        try:
            page = fetch(url_for(edition, board)).decode('utf-8', 'ignore')
        except urllib.error.HTTPError as exc:
            # 好评榜/预约榜只有近期期次建页（2026-10-17 实测：老期次一律 404），属站点结构而非故障
            if exc.code != 404:
                raise
            absent.append(edition)
            print(f'[{i}/{len(todo)}] {edition} 该榜无此期（404），跳过')
        else:
            n = ingest(conn, edition, board, page)
            done += 1
            print(f'[{i}/{len(todo)}] {edition} {n} 行')
        if i < len(todo):
            time.sleep(SLEEP_SEC)
    if absent:
        print(f'[board={board} {BOARDS[board][0]}] 无此榜 {len(absent)} 期'
              f'（{absent[0]}~{absent[-1]}），入库 {done} 期')
        assert done, f'board={board} 全部 {len(absent)} 期均 404 —— 疑似站点结构变更，需人工核查'


def cmd_reparse(conn: sqlite3.Connection) -> None:
    """仅用 raw/ 归档重建数据库，不发起网络请求。文件名 {日期}_b{榜号}.html.gz。"""
    files = sorted(RAW.glob('*_b*.html.gz'))
    assert files, f'{RAW} 无归档'
    conn.execute('DROP TABLE IF EXISTS snapshot')
    conn.executescript(SCHEMA)
    total = 0
    for path in files:
        m = re.fullmatch(r'(\d{4}-\d{2}-\d{2})_b(\d+)\.html\.gz', path.name)
        assert m, f'归档文件名不合规：{path.name}'
        edition, board = m.group(1), int(m.group(2))
        page = gzip.open(path, 'rt', encoding='utf-8', errors='ignore').read()
        rows = parse(page, edition)
        digest = hashlib.sha256(page.encode()).hexdigest()[:16]
        store(conn, edition, board, rows, digest, f'reparse:{time.strftime("%Y-%m-%dT%H:%M:%S")}')
        total += len(rows)
    print(f'重建完成：{len(files)} 个归档 / {total} 行')


def cmd_today(conn: sqlite3.Connection) -> None:
    edition = date.today().isoformat()
    for board in BOARDS:
        page = fetch(url_for(edition, board)).decode('utf-8', 'ignore')
        n = ingest(conn, edition, board, page)
        print(f'{edition} board={board} {BOARDS[board][0]} 入库 {n} 行')
        time.sleep(SLEEP_SEC)


def cmd_verify(conn: sqlite3.Connection) -> None:
    per_edition = conn.execute(
        'SELECT edition_date, board, COUNT(*), MIN(rank), MAX(rank), MIN(metric_value) '
        'FROM snapshot GROUP BY edition_date, board ORDER BY edition_date, board'
    ).fetchall()
    bad = [r for r in per_edition if r[2] < 50 or r[3] != 1 or r[4] != r[2] or r[5] < 0]
    assert not bad, bad
    total = sum(r[2] for r in per_edition)
    span = (per_edition[0][0], per_edition[-1][0])
    dup = conn.execute(
        'SELECT COUNT(*) FROM (SELECT edition_date, board, title, COUNT(*) c FROM snapshot '
        'GROUP BY edition_date, board, title HAVING c > 1)'
    ).fetchone()[0]
    boards = conn.execute(
        'SELECT board, COUNT(DISTINCT edition_date) FROM snapshot GROUP BY board ORDER BY board'
    ).fetchall()
    print(f'PASS: {len(per_edition)} 个(日期,榜)组合 / {total} 行 / {span[0]}~{span[1]} / 组内重复标题 {dup}')
    print('  各榜覆盖期数：' + '、'.join(f'{BOARDS[b][0]} {n}' for b, n in boards))


def cmd_summary(conn: sqlite3.Connection, board: int = 1) -> None:
    rows = conn.execute('SELECT DISTINCT edition_date FROM snapshot WHERE board=? ORDER BY edition_date',
                        (board,)).fetchall()
    editions_list = [r[0] for r in rows]
    if len(editions_list) < 2:
        print('期次不足 2，无法比较')
        return
    latest, prev = editions_list[-1], editions_list[-2]
    sql = 'SELECT title FROM snapshot WHERE board=? AND edition_date=?'
    now = {r[0] for r in conn.execute(sql, (board, latest))}
    before = {r[0] for r in conn.execute(sql, (board, prev))}
    print(f'[{BOARDS[board][0]}] {prev} -> {latest}')
    print(f'  新进 {len(now - before)}：' + '、'.join(sorted(now - before)[:5]))
    print(f'  掉出 {len(before - now)}：' + '、'.join(sorted(before - now)[:5]))
    top = conn.execute(
        'SELECT genre, COUNT(*) c FROM snapshot WHERE board=? AND edition_date=? '
        'GROUP BY genre ORDER BY c DESC LIMIT 5', (board, latest)).fetchall()
    print('  题材前五：' + '、'.join(f'{g} {c}' for g, c in top))
    streak = conn.execute(
        'SELECT title, COUNT(*) n FROM snapshot WHERE board=? GROUP BY title '
        'HAVING n >= 5 ORDER BY n DESC, title LIMIT 5', (board,)).fetchall()
    print('  上榜期次最多：' + '、'.join(f'{t}({n})' for t, n in streak))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['backfill', 'today', 'verify', 'summary', 'reparse'])
    ap.add_argument('--board', type=int, default=1, choices=sorted(BOARDS))
    args = ap.parse_args()
    DATA.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.executescript(SCHEMA)
    try:
        if args.cmd == 'backfill':
            cmd_backfill(conn, args.board)
        elif args.cmd == 'summary':
            cmd_summary(conn, args.board)
        else:
            {'today': cmd_today, 'reparse': cmd_reparse, 'verify': cmd_verify}[args.cmd](conn)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
