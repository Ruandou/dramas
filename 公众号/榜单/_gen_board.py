#!/usr/bin/env python3
"""「厂牌榜」主图生成：一页多榜（热播 / 连续在榜 / 今日新进 / 预约）。

数据来自本地归档 data/bangdan.sqlite（第三方转算指数，非平台官方口径）。
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '素材'))
from importlib import import_module

_fonts = import_module('_gen_charts_006')

OUT = Path(__file__).resolve().parents[1] / '素材'
DB = Path(__file__).resolve().parent / 'data' / 'bangdan.sqlite'

PAPER, WHITE, INK = '#f3eee4', '#fffaf0', '#2c2925'
DIM, LINE, RUST, TEAL, GOLD = '#756d61', '#d4c9b8', '#ae422c', '#28695e', '#b9853d'
FONTS = {'body': (_fonts.HIRA, 0), 'bold': (_fonts.HIRA, 2),
         'title': (_fonts.SONG, 1), 'number': (_fonts.MONO, 1)}

EDITION = '2026-10-15'
ISSUE = '001'
W = 1080
GLYPHS: dict = {}
BOXES: list = []


def font(size, kind='body'):
    path, index = FONTS[kind]
    return _fonts.f(path, size, index=index)


def put(d, x, y, text, size=28, color=INK, kind='body', right=W - 72):
    ff = font(size, kind)
    width = d.textlength(text, font=ff)
    assert x >= 0 and x + width <= right + 0.1, (text, x, width, right)
    box = d.textbbox((x, y), text, font=ff, anchor='lt')
    assert box[0] >= 0 and box[2] <= d._image.width and box[3] <= d._image.height, (text, box)
    for other, b in BOXES:
        if min(box[2], b[2]) > max(box[0], b[0]) and min(box[3], b[3]) > max(box[1], b[1]):
            raise AssertionError(f'文本重叠: {text!r} / {other!r}')
    BOXES.append((text, box))
    GLYPHS.setdefault(FONTS[kind], set()).update(text)
    d.text((x, y), text, font=ff, fill=color, anchor='lt')
    return box[3]


def fit(d, text, size, kind='body', limit=340):
    """按宽度截断到 limit 像素，末尾加省略号。"""
    ff = font(size, kind)
    if d.textlength(text, font=ff) <= limit:
        return text
    while text and d.textlength(text + '…', font=ff) > limit:
        text = text[:-1]
    return text + '…'


def query(sql, args=()):
    conn = sqlite3.connect(DB)
    try:
        return conn.execute(sql, args).fetchall()
    finally:
        conn.close()


def up_to(edition, board, limit):
    return query('SELECT rank, title, genre, metric_value, is_new FROM snapshot '
                 'WHERE board=? AND edition_date=? ORDER BY rank LIMIT ?',
                 (board, edition, limit))


def board_rows(board, limit):
    return up_to(EDITION, board, limit)


def streak_rows(limit):
    """在榜期数：同一剧在采样期次中出现的次数。不用 is_new 过滤——
    该标记是剧名单元格里的展示徽标，同一部剧在不同期次会变，过滤会漏计。"""
    return query('SELECT title, COUNT(*) n, MIN(rank) best FROM snapshot '
                 'WHERE board=1 GROUP BY title HAVING n >= 20 '
                 'ORDER BY n DESC, best ASC LIMIT ?', (limit,))


def new_entries(limit):
    editions = [r[0] for r in query('SELECT DISTINCT edition_date FROM snapshot WHERE board=1 '
                                    'ORDER BY edition_date')]
    idx = editions.index(EDITION)
    assert idx > 0, f'{EDITION} 是该榜最早一期，无双期对比'
    prev = editions[idx - 1]
    return query('SELECT rank, title, genre, metric_value FROM snapshot '
                 'WHERE board=1 AND edition_date=? AND title NOT IN '
                 '(SELECT title FROM snapshot WHERE board=1 AND edition_date=?) '
                 'ORDER BY rank LIMIT ?', (EDITION, prev, limit))


def section(d, y, label, note, color):
    put(d, 72, y, label, 34, INK, 'title')
    put(d, 72 + d.textlength(label, font=font(34, 'title')) + 18, y + 12, note, 21, DIM)
    d.line((72, y + 50, W - 72, y + 50), fill=color, width=3)
    return y + 72


def row_badge(d, y, rank, color):
    d.rounded_rectangle((72, y, 108, y + 34), radius=8, fill=color)
    w = d.textlength(str(rank), font=font(24, 'number'))
    put(d, 90 - w / 2, y + 5, str(rank), 24, WHITE, 'number')


def list_rows(d, y, rows, color):
    for r in rows:
        rank, title, genre, value = r[0], r[1], r[2], r[3]
        row_badge(d, y, rank, color if rank <= 3 else '#a2988a')
        put(d, 124, y + 2, fit(d, title, 29, 'bold', 610), 29, INK, 'bold', 738)
        put(d, 748, y + 6, fit(d, genre, 21, 'body', 122), 21, DIM, 'body', 872)
        v = f'{value}'
        put(d, 1008 - d.textlength(v, font=font(28, 'number')), y + 3, v, 28, color, 'number')
        if r is not rows[-1]:
            d.line((124, y + 48, W - 72, y + 48), fill='#e6ded0', width=1)
        y += 56
    return y + 18


def build():
    main_rows = board_rows(1, 12)
    streak = streak_rows(6)
    fresh = new_entries(6)
    booking = board_rows(3, 6)

    im = Image.new('RGB', (W, 2400), PAPER)
    d = ImageDraw.Draw(im)

    d.rectangle((72, 44, 83, 66), fill=RUST)
    put(d, 100, 44, f'一人短剧厂牌 / 厂牌榜 {ISSUE}', 21, DIM, 'bold')
    put(d, W - 72 - d.textlength(EDITION, font=font(22, 'number')), 44, EDITION, 22, RUST, 'number')
    put(d, 72, 98, '短剧榜单一页：谁在榜、谁掉队、谁在排号', 47, INK, 'title')
    put(d, 72, 168, '红果短剧 · 第三方转算指数 · 口径与盲区见图末', 24, DIM)

    y = 232
    y = section(d, y, '当日热播榜', 'TOP12 / 当日热播指数', RUST)
    y = list_rows(d, y, main_rows, RUST)

    y = section(d, y, '长期在榜', '跨 79 期采样 / 在榜期数最多', TEAL)
    for title, n, best in streak:
        d.rounded_rectangle((72, y, 118, y + 34), radius=8, fill=TEAL)
        w = d.textlength(str(n), font=font(23, 'number'))
        put(d, 95 - w / 2, y + 5, str(n), 23, WHITE, 'number')
        put(d, 134, y + 2, fit(d, title, 29, 'bold', 650), 29, INK, 'bold', 784)
        put(d, 796, y + 6, f'最高第 {best}', 22, DIM)
        if (title, n, best) is not streak[-1]:
            d.line((134, y + 48, W - 72, y + 48), fill='#e6ded0', width=1)
        y += 56
    y += 18

    y = section(d, y, '今日新进', '对比前一采样日新上榜', TEAL)
    y = list_rows(d, y, fresh, TEAL)

    y = section(d, y, '预约榜', 'TOP6 / 当日预约值', GOLD)
    y = list_rows(d, y, booking, GOLD)

    y += 6
    put(d, 72, y, '口径：热播指数与预约值均为第三方转算指标，来源 duanjugongcheng.com；', 21, DIM)
    put(d, 72, y + 32, '2026-09 前为周一采样，“在榜期数”是采样命中次数，非连续天数。', 21, DIM)
    put(d, 72, y + 64, '本页不代表平台官方排名，也不构成任何投资参考。', 21, DIM)

    for (path, index), chars in GLYPHS.items():
        ff = TTFont(path, fontNumber=index)
        cmap = ff.getBestCmap()
        missing = sorted(c for c in chars if ord(c) not in cmap)
        ff.close()
        assert not missing, (path, index, missing)

    im = im.crop((0, 0, W, int(y + 110)))
    dest = OUT / f'榜001_主榜_{EDITION.replace("-", "")}_1080.png'
    OUT.mkdir(parents=True, exist_ok=True)
    im.quantize(colors=192, method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.NONE).save(dest, optimize=True)
    print(dest.name, im.size, f'{dest.stat().st_size / 1024:.1f} KB')
    print(f'PASS: 字形覆盖、量宽、边界、不重叠；{len(BOXES)} 个文本框')


def cover():
    """公众号封面 900x383，主文案须落在中央 383x383 分享裁切区内（宽度实测 <=351）。"""
    C_W, C_H = 900, 383
    im = Image.new('RGB', (C_W, C_H), PAPER)
    d = ImageDraw.Draw(im)
    cw = font(23, 'bold')
    put(d, 33, 28, '一人短剧厂牌', 19, DIM, 'bold', C_W - 20)
    put(d, 700, 28, f'{ISSUE} / 周一', 18, DIM, 'body', C_W - 30)

    def safe_center(cx, y, text, size, color=INK, kind='bold'):
        ff = font(size, kind)
        width = d.textlength(text, font=ff)
        assert width <= 351, (text, width)
        put(d, cx - width / 2, y, text, size, color, kind, cx + width / 2 + 1)

    safe_center(450, 74, '厂牌榜', 30, TEAL)
    safe_center(450, 122, '新剧一天冲榜', 48, INK, 'title')
    safe_center(450, 196, '老剧坐了 38 期', 48, RUST, 'title')
    safe_center(450, 300, '79 期采样 · 红果热播榜 / 预约榜', 21, DIM, 'body')

    # 两侧排名条：名次徽标 + 数据条，避开中央裁切区
    for i, (x, width, color) in enumerate([(38, 168, RUST), (38, 132, TEAL), (38, 104, GOLD)]):
        y = 96 + i * 62
        d.rounded_rectangle((x, y, x + 34, y + 34), radius=8, fill=color)
        w = d.textlength(str(i + 1), font=font(22, 'number'))
        put(d, x + 17 - w / 2, y + 5, str(i + 1), 22, WHITE, 'number')
        d.rounded_rectangle((x + 46, y + 6, x + 46 + width, y + 28), radius=6, fill=color)
    for i, width in enumerate((150, 118, 92)):
        y = 102 + i * 62
        d.rounded_rectangle((C_W - 38 - width, y, C_W - 38, y + 22), radius=6, fill='#c2b7a6')

    for (path, index), chars in GLYPHS.items():
        ff = TTFont(path, fontNumber=index)
        cmap = ff.getBestCmap()
        missing = sorted(c for c in chars if ord(c) not in cmap)
        ff.close()
        assert not missing, (path, index, missing)

    dest = OUT / f'封面_榜{ISSUE}_{EDITION.replace("-", "")}_900x383.png'
    OUT.mkdir(parents=True, exist_ok=True)
    im.quantize(colors=192, method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.NONE).save(dest, optimize=True)
    print(dest.name, im.size, f'{dest.stat().st_size / 1024:.1f} KB')
    print('PASS: 字形覆盖、量宽、中央安全区、边界')


def genre_rows(limit):
    return query('SELECT ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) r, genre, COUNT(*) n '
                 'FROM snapshot WHERE board=1 AND edition_date=? GROUP BY genre '
                 'ORDER BY n DESC, genre LIMIT ?', (EDITION, limit))


def poster():
    """贴图版：拆成三张统一 3:4 竖版页（贴图滑动浏览，单张过长预览会被裁）。"""
    main_rows = board_rows(1, 18)
    streak = streak_rows(8)
    fresh = new_entries(10)
    booking = board_rows(3, 10)
    genres = genre_rows(6)
    files = []

    P_H = 1440  # 三页统一 3:4，滑动时比例不跳

    def new_canvas():
        BOXES.clear()  # 每页独立做重叠检查；GLYPHS 跨页累计
        return Image.new('RGB', (W, P_H), PAPER), None

    def draw_on(im):
        return ImageDraw.Draw(im)

    def head(d, title, sub):
        d.rectangle((72, 44, 83, 66), fill=RUST)
        put(d, 100, 44, f'一人短剧厂牌 / 厂牌榜 {ISSUE}', 21, DIM, 'bold')
        put(d, W - 72 - d.textlength(EDITION, font=font(22, 'number')), 44, EDITION, 22, RUST, 'number')
        put(d, 72, 92, title, 46, INK, 'title')
        put(d, 72, 158, sub, 24, DIM)
        return 216

    def save(im, content_bottom, name, foot_lines):
        d = draw_on(im)
        y = P_H - 34 - 32 * len(foot_lines)
        assert content_bottom < y - 20, (name, content_bottom, y)
        d.line((72, y - 18, W - 72, y - 18), fill=LINE, width=2)
        for line in foot_lines:
            put(d, 72, y, line, 21, DIM)
            y += 32
        OUT.mkdir(parents=True, exist_ok=True)
        dest = OUT / name
        im.quantize(colors=192, method=Image.Quantize.MEDIANCUT,
                    dither=Image.Dither.NONE).save(dest, optimize=True)
        files.append((dest.name, im.size, dest.stat().st_size))

    im, _ = new_canvas()
    d = draw_on(im)
    y = head(d, '当日热播榜', 'TOP18 / 当日热播指数 · 第三方转算')
    y = list_rows(d, y, main_rows, RUST)
    save(im, y, f'榜{ISSUE}_贴图1_热播榜_1080.png',
         ['口径：指数为第三方转算指标，非平台官方排名，不构成投资参考。'])

    im, _ = new_canvas()
    d = draw_on(im)
    y = head(d, '长期在榜', '跨 79 期采样 / 在榜期数最多')
    for title, n, best in streak:
        d.rounded_rectangle((72, y, 118, y + 34), radius=8, fill=TEAL)
        w = d.textlength(str(n), font=font(23, 'number'))
        put(d, 95 - w / 2, y + 5, str(n), 23, WHITE, 'number')
        put(d, 134, y + 2, fit(d, title, 29, 'bold', 650), 29, INK, 'bold', 784)
        put(d, 796, y + 6, f'最高第 {best}', 22, DIM)
        if (title, n, best) is not streak[-1]:
            d.line((134, y + 48, W - 72, y + 48), fill='#e6ded0', width=1)
        y += 56
    y += 24
    y = section(d, y, '今日新进', '对比前一采样日新上榜', TEAL)
    y = list_rows(d, y, fresh, TEAL)
    save(im, y, f'榜{ISSUE}_贴图2_长期在榜与新进_1080.png',
         ['“在榜期数”为采样命中次数，非连续天数。'])

    im, _ = new_canvas()
    d = draw_on(im)
    y = head(d, '预约榜', 'TOP10 / 当日预约值')
    y = list_rows(d, y, booking, GOLD)
    y += 24
    y = section(d, y, '当日题材分布', 'TOP100 上榜部数 / 前 6', GOLD)
    for i, genre, n in genres:
        row_badge(d, y, i, GOLD if i <= 3 else '#a2988a')
        put(d, 124, y + 2, genre, 29, INK, 'bold', 740)
        txt = f'{n}'
        put(d, 1008 - d.textlength(txt, font=font(28, 'number')), y + 3, txt, 28, GOLD, 'number')
        if (i, genre, n) is not genres[-1]:
            d.line((124, y + 48, W - 72, y + 48), fill='#e6ded0', width=1)
        y += 56
    y += 18
    save(im, y, f'榜{ISSUE}_贴图3_预约榜与题材_1080.png', [
        '来源 duanjugongcheng.com/cn/bangdan/' + EDITION + '，第三方转算指数。',
        '该站未公布指数单位与权重；预约值含义官方未说明，仅原样呈现。',
        '本号不做好评榜：当日仅 9 分（32 部）与 10 分（68 部）两档，区分度不足。',
    ])

    for (path, index), chars in GLYPHS.items():
        ff = TTFont(path, fontNumber=index)
        cmap = ff.getBestCmap()
        missing = sorted(c for c in chars if ord(c) not in cmap)
        ff.close()
        assert not missing, (path, index, missing)

    for name, size, nbytes in files:
        print(name, size, f'{nbytes / 1024:.1f} KB')
    print(f'PASS: 字形覆盖、量宽、边界、不重叠；{len(BOXES)} 个文本框')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        EDITION = sys.argv[1]
    if len(sys.argv) > 2:
        ISSUE = sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else 'build'
    {'build': build, 'cover': cover, 'poster': poster}[mode]()
