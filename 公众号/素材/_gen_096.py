# -*- coding: utf-8 -*-
"""096《三家短剧公司财报摆一起》正文两图 + 封面。纯本地 Pillow，零扣费。"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from importlib import import_module

_c = import_module('_gen_charts_006')

OUT = HERE
PAPER, INK, DIM, LINE, BOX = _c.PAPER, _c.INK, _c.DIM, _c.LINE, _c.BOX
RUST, TEAL, GOLD = (174, 66, 44), (40, 105, 94), (185, 133, 61)

SONG, HIRA, MONO = _c.SONG, _c.HIRA, _c.MONO
GLYPHS: dict = {}
BOXES: list = []
ISSUE = '096'
EDITION = '2026-11-11'
W = 1080


def font(size, kind='body'):
    path, index = {'body': (HIRA, 0), 'bold': (HIRA, 2),
                   'title': (SONG, 1), 'number': (MONO, 1)}[kind]
    return _c.f(path, size, index=index)


def put(d, x, y, text, size=28, color=INK, kind='body', right=None):
    ff = font(size, kind)
    width = d.textlength(text, font=ff)
    if right is not None:
        assert x + width <= right + 0.1, (text, x, width, right)
    box = d.textbbox((x, y), text, font=ff, anchor='lt')
    assert box[0] >= 0 and box[2] <= d._image.width and box[3] <= d._image.height, (text, box)
    for other, b in BOXES:
        if min(box[2], b[2]) > max(box[0], b[0]) and min(box[3], b[3]) > max(box[1], b[1]):
            raise AssertionError(f'文本重叠: {text!r} / {other!r}')
    BOXES.append((text, box))
    GLYPHS.setdefault((kind, size), set()).update(text)
    d.text((x, y), text, font=ff, fill=color, anchor='lt')
    return width


def put_right(d, x_right, y, text, size=28, color=INK, kind='body'):
    w = d.textlength(text, font=font(size, kind))
    return put(d, x_right - w, y, text, size, color, kind)


def head(d, title, sub):
    d.rectangle((72, 44, 83, 66), fill=RUST)
    put(d, 100, 44, f'一人短剧厂牌 / 快讯 {ISSUE}', 21, DIM, 'bold')
    put_right(d, W - 72, 44, EDITION, 22, RUST, 'number')
    put(d, 72, 92, title, 44, INK, 'title')
    put(d, 72, 158, sub, 22, DIM)
    return 216


def save(im, name):
    dest = OUT / name
    im.quantize(colors=192, method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.NONE).save(dest, optimize=True)
    print(dest.name, im.size, f'{dest.stat().st_size / 1024:.1f} KB')


def check_glyphs():
    for (kind, size), chars in GLYPHS.items():
        path, index = {'body': (HIRA, 0), 'bold': (HIRA, 2),
                       'title': (SONG, 1), 'number': (MONO, 1)}[kind]
        ff = TTFont(path, fontNumber=index)
        cmap = ff.getBestCmap()
        missing = sorted(c for c in chars if ord(c) not in cmap)
        ff.close()
        assert not missing, (path, index, missing)


def chart1():
    BOXES.clear()
    im = Image.new('RGB', (W, 990), PAPER)
    d = ImageDraw.Draw(im)
    head(d, '三家短剧公司，六个数字',
         '2026 半年报 / 三季报 · 上海证券报 11-11 汇总')

    cards = [
        ('昆仑万维', '15.35', '+163.28%', '260.94 万元', '扣非 -15.46 亿元', '65.10%', '58.18 亿元', RUST),
        ('掌阅科技', '11.85', '+41.45%', '-6,840.91 万元', '归母净利', '64.20%', '17.82 亿元', TEAL),
        ('中文在线', '4.11', '+108.72%', '-1.32 亿元', '归母净利', '46.11%', '3.84 亿元', GOLD),
    ]
    xs = [(72, 372), (390, 690), (708, 1008)]
    for (x0, x1), (name, inc, growth, profit, pnote, rate, fee, color) in zip(xs, cards):
        d.rounded_rectangle((x0, 230, x1, 700), radius=16, fill=BOX)
        put(d, x0 + 24, 252, name, 27, color, 'bold', right=x1 - 18)
        put(d, x0 + 24, 296, '上半年短剧收入', 18, DIM)
        put(d, x0 + 22, 322, inc, 46, INK, 'number')
        w = d.textlength('亿元', font=font(20, 'bold'))
        put(d, x0 + 22 + d.textlength(inc, font=font(46, 'number')) + 6, 344, '亿元', 20, INK, 'bold')
        assert x0 + 22 + d.textlength(inc, font=font(46, 'number')) + 6 + w <= x1 - 18
        put(d, x0 + 24, 382, growth, 22, color, 'bold', right=x1 - 18)
        d.line((x0 + 24, 424, x1 - 24, 424), fill=LINE, width=2)
        put(d, x0 + 24, 444, '前三季归母', 18, DIM)
        put(d, x0 + 24, 470, profit, 25, INK, 'bold', right=x1 - 18)
        put(d, x0 + 24, 506, pnote, 17, DIM, right=x1 - 18)
        d.line((x0 + 24, 540, x1 - 24, 540), fill=LINE, width=2)
        put(d, x0 + 24, 560, '销售费用率', 18, DIM)
        put(d, x0 + 20, 586, rate, 46, color, 'number')
        put(d, x0 + 24, 650, f'销售费用 {fee}', 17, DIM, right=x1 - 18)

    d.rounded_rectangle((72, 730, 1008, 850), radius=16, fill=(238, 232, 218))
    put(d, 100, 750, '口径：收入是上半年业务线数字；利润和费用率是前三季全公司。', 23, INK, 'bold')
    put(d, 100, 788, '两段不能直接相除；三家业务线范围也不同，只能横着看方向。', 21, RUST, 'bold')

    put(d, 72, 930, '数据：上海证券报 2026-11-11《AI短剧爆火背后：技术降本 流量“烧钱”》对三季报的摘引。', 17, DIM)

    check_glyphs()
    save(im, '096_图1_三家六个数字_1080.png')


def chart2():
    BOXES.clear()
    im = Image.new('RGB', (W, 960), PAPER)
    d = ImageDraw.Draw(im)
    head(d, '每收 100 元，多少花在销售上',
         '2026 前三季 · 销售费用 ÷ 营业收入')

    rows = [
        ('昆仑万维', 65.10, '58.18 亿元', RUST),
        ('掌阅科技', 64.20, '17.82 亿元', TEAL),
        ('中文在线', 46.11, '3.84 亿元', GOLD),
    ]
    for i, (name, pct, fee, color) in enumerate(rows):
        yy = 250 + i * 158
        put(d, 72, yy, name, 26, INK, 'bold')
        put_right(d, 1008, yy + 2, f'{pct:.2f}%', 30, color, 'number')
        bar_max = 520
        d.rounded_rectangle((72, yy + 44, 72 + bar_max, yy + 78), radius=8, fill=(232, 226, 212))
        w = int(bar_max * pct / 70.0)
        d.rounded_rectangle((72, yy + 44, 72 + w, yy + 78), radius=8, fill=color)
        put(d, 72, yy + 92, f'销售费用 {fee}', 18, DIM)

    d.rounded_rectangle((72, 740, 1008, 862), radius=16, fill=(238, 232, 218))
    put(d, 100, 760, '昆仑单季：58.18 - 33.39 = 24.79 亿元（本号算术）', 24, INK, 'bold')
    put(d, 100, 798, '一个季度的销售费用，是上半年两个季度的 74%，费用率还在往上。', 21, RUST, 'bold')

    put(d, 72, 910, '数据：上海证券报 11-11；上半年 33.39 亿元与 62.31% 见本号 055（10-29 昆仑三季报拆解）。', 17, DIM)

    check_glyphs()
    save(im, '096_图2_费用率横条_1080.png')


def cover():
    BOXES.clear()
    C_W, C_H = 900, 383
    im = Image.new('RGB', (C_W, C_H), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, DIM, 'bold', C_W - 20)
    put_right(d, C_W - 33, 24, f'{ISSUE} / 快讯', 17, DIM, 'body')

    put(d, 42, 66, '三家短剧公司', 20, DIM, 'bold')
    put(d, 42, 100, '收入涨 41%—163%', 40, RUST, 'title')
    put(d, 42, 162, '利润没跟上', 40, INK, 'title')
    d.line((42, 232, 400, 232), fill=LINE, width=2)
    put(d, 42, 250, '昆仑 / 掌阅 / 中文在线', 19, INK, 'bold')
    put(d, 42, 286, '上半年短剧收入与前三季利润', 17, DIM)
    put(d, 42, 316, '上海证券报 11-11 汇总', 17, DIM)

    put(d, 470, 52, '前三季销售费用率', 20, DIM, 'bold')
    rows = [('昆仑万维', '65.10%', RUST), ('掌阅科技', '64.20%', TEAL), ('中文在线', '46.11%', GOLD)]
    for i, (name, pct, color) in enumerate(rows):
        yy = 96 + i * 74
        put(d, 470, yy + 10, name, 22, INK, 'bold')
        put_right(d, 860, yy, pct, 40, color, 'number')
    put(d, 470, 330, '每收 100 元，最多 65 元花在销售', 18, RUST, 'bold')

    check_glyphs()
    save(im, f'封面_{ISSUE}_{EDITION.replace("-", "")}_900x383.png')


if __name__ == '__main__':
    {'chart1': chart1, 'chart2': chart2, 'cover': cover,
     'all': lambda: (chart1(), chart2(), cover())}[sys.argv[1] if len(sys.argv) > 1 else 'all']()
