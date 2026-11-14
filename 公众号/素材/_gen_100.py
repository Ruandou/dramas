# -*- coding: utf-8 -*-
"""100《微博剧有引力 4.0》正文两图 + 封面。纯本地 Pillow，零扣费。"""
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
ISSUE = '100'
EDITION = '2026-11-13'
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
    im = Image.new('RGB', (W, 960), PAPER)
    d = ImageDraw.Draw(im)
    head(d, '保底三档，真人只按 A 级',
         '微博剧有引力 4.0 · 2026 年 10 月后上线')

    rows = [
        ('S', '红果 / 抖音榜单 TOP200', '3000 元', RUST),
        ('A', '全网播放 ≥ 5000 万', '2000 元', TEAL),
        ('B', '全网播放 ≥ 3000 万', '1000 元', GOLD),
    ]
    put(d, 100, 236, 'AI 剧', 20, DIM, 'bold')
    put_right(d, 1008, 236, '保底金额', 20, DIM, 'bold')
    for i, (tag, cond, amount, color) in enumerate(rows):
        yy = 274 + i * 128
        d.rounded_rectangle((72, yy, 1008, yy + 108), radius=14, fill=BOX)
        d.rectangle((100, yy + 34, 154, yy + 76), fill=color)
        w = d.textlength(tag, font=font(26, 'bold'))
        put(d, 127 - w / 2, yy + 40, tag, 26, PAPER, 'bold')
        put(d, 190, yy + 26, cond, 23, INK, right=760)
        put(d, 190, yy + 64, '内容要求', 16, DIM)
        put_right(d, 980, yy + 34, amount, 32, color, 'bold')

    d.rounded_rectangle((72, 680, 1008, 790), radius=16, fill=(238, 232, 218))
    put(d, 100, 700, '真人短剧统一适用 A 级：保底 2000 元', 24, INK, 'bold')
    put(d, 100, 740, '别把 AI 剧 S 档 3000 元套给所有真人剧。', 21, RUST, 'bold')

    put(d, 72, 850, '数据：微博短剧频道 2026-11-02 官方长图；激励范围以平台审核结果为准。', 17, DIM)

    check_glyphs()
    save(im, '100_图1_保底三档_1080.png')


def chart2():
    BOXES.clear()
    im = Image.new('RGB', (W, 990), PAPER)
    d = ImageDraw.Draw(im)
    head(d, '阶梯分成，看的是站内播放',
         '门槛：2026 年 7 月后上线 · 全网播放超 100 万')

    tiers = [('<50 万', '100%'), ('50—100 万', '110%'), ('100—200 万', '200%'),
             ('200—300 万', '220%'), ('300—500 万', '300%'), ('>500 万', '400%')]
    for i, (rng, pct) in enumerate(tiers):
        col = i % 2
        row = i // 2
        x0 = 72 + col * 486
        yy = 236 + row * 132
        d.rounded_rectangle((x0, yy, x0 + 450, yy + 108), radius=12, fill=BOX)
        put(d, x0 + 26, yy + 18, rng, 20, DIM)
        put(d, x0 + 24, yy + 50, pct, 40, RUST if i >= 4 else TEAL, 'number')
        put(d, x0 + 150, yy + 60, '分成', 18, INK, 'bold')

    d.rounded_rectangle((72, 660, 1008, 790), radius=16, fill=(238, 232, 218))
    put(d, 100, 680, '400% 是分成倍率，不是播放单价，也不等于 50 万到手。', 22, INK, 'bold')
    put(d, 100, 720, '每部过审剧集的播放分成上限是 50 万元；上限不是保底。', 20, RUST, 'bold')

    put(d, 72, 840, '参与门槛看全网播放，分成档位看站内播放，两个口径别混。', 17, DIM)
    put(d, 72, 874, '数据：微博短剧频道 2026-11-02 官方长图；结算基数公开长图未给。', 17, DIM)

    check_glyphs()
    save(im, '100_图2_阶梯分成_1080.png')


def cover():
    BOXES.clear()
    C_W, C_H = 900, 383
    im = Image.new('RGB', (C_W, C_H), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, DIM, 'bold', C_W - 20)
    put_right(d, C_W - 33, 24, f'{ISSUE} / 快讯', 17, DIM, 'body')

    put(d, 42, 66, '微博剧有引力 4.0', 20, DIM, 'bold')
    put(d, 42, 100, '保底三档', 40, RUST, 'title')
    put(d, 42, 156, '分成最高 400%', 40, INK, 'title')
    d.line((42, 226, 400, 226), fill=LINE, width=2)
    put(d, 42, 244, '报名到 12-31 · 分账到 2027-01-31', 18, INK, 'bold')
    put(d, 42, 276, '真人统一按 A 级 2000 元', 17, DIM)
    put(d, 42, 306, '50 万是上限，不是保底', 17, RUST)

    d.rounded_rectangle((420, 52, 860, 330), radius=18, fill=(238, 232, 218))
    put(d, 450, 76, '三档保底', 22, DIM, 'bold')
    rows = [('S', '3000 元'), ('A', '2000 元'), ('B', '1000 元')]
    for i, (tag, amt) in enumerate(rows):
        yy = 122 + i * 62
        put(d, 450, yy + 6, tag, 24, TEAL, 'bold')
        put(d, 510, yy, amt, 24, INK, 'bold')
        put(d, 640, yy + 6, ['榜单 TOP200', '全网 5000 万+', '全网 3000 万+'][i], 17, DIM, right=830)

    check_glyphs()
    save(im, f'封面_{ISSUE}_{EDITION.replace("-", "")}_900x383.png')


if __name__ == '__main__':
    {'chart1': chart1, 'chart2': chart2, 'cover': cover,
     'all': lambda: (chart1(), chart2(), cover())}[sys.argv[1] if len(sys.argv) > 1 else 'all']()