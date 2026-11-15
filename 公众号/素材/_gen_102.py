# -*- coding: utf-8 -*-
"""102《红果剧本新政》正文两图 + 封面。纯本地 Pillow，零扣费。"""
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
ISSUE = '102'
EDITION = '2026-11-14'
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
    head(d, 'S / A / B 三档对照',
         '红果《【AI剧】编剧和剧本合作政策》2026 年 11 月版')

    cards = [
        ('S 级', '1.5', '保底 · 分两笔发放', '保留超保底分成', RUST),
        ('A 级', '0', '无保底 · 进入分本池', '选中并全集交付后纯分成', TEAL),
        ('B 级', '—', '不予合作', '按媒体政策截图口径', DIM),
    ]
    xs = [(72, 372), (390, 690), (708, 1008)]
    for (x0, x1), (name, num, line1, line2, color) in zip(xs, cards):
        d.rounded_rectangle((x0, 232, x1, 536), radius=16, fill=BOX)
        put(d, x0 + 24, 252, name, 26, color, 'bold', right=x1 - 16)
        if num != '—':
            put(d, x0 + 20, 300, num, 48, color, 'number')
            put(d, x0 + 24, 366, '万元 / 部' if num != '0' else '元', 17, DIM)
        else:
            put(d, x0 + 24, 316, '不合作', 30, DIM, 'bold')
        put(d, x0 + 24, 420, line1, 18, INK, right=x1 - 16)
        put(d, x0 + 24, 456, line2, 17, DIM, right=x1 - 16)

    d.rounded_rectangle((72, 568, 1008, 730), radius=16, fill=(238, 232, 218))
    put(d, 100, 588, '保底资格：只看本剧本前 30 集质量', 26, INK, 'bold')
    put(d, 100, 632, '不再参考编剧历史评级或过往成绩。', 21, RUST, 'bold')
    put(d, 100, 675, '首次交前 30 集供评级；最终完稿不少于 70 集、7 万字。', 20, INK)

    put(d, 72, 780, '来源：DataEye短剧观察 2026-11-12 澎湃号原稿所附完整政策长图。', 17, DIM)
    put(d, 72, 814, '长图载明 11 月 13 日起生效；具体发放以双方签署的合同约定为准。', 17, DIM)
    put(d, 72, 848, '本号已核对媒体所附截图，尚未取得官方原页。', 17, DIM)

    check_glyphs()
    save(im, '102_图1_三档对照_1080.png')


def chart2():
    BOXES.clear()
    im = Image.new('RGB', (W, 990), PAPER)
    d = ImageDraw.Draw(im)
    head(d, 'S 级保底到账节奏',
         '保底合计 1.5 万元 / 部；具体以双方签署的合同约定为准')

    d.rounded_rectangle((72, 236, 1008, 346), radius=16, fill=(238, 232, 218))
    put(d, 100, 258, '先被承制方选中，再按条件分两笔到账', 30, INK, 'bold')
    put(d, 100, 306, '保底金额不等于签约时一次到手金额。', 20, DIM)

    cards = [(72, 531, '第一笔 · 25%', '3750',
              '承制方选中剧本，', '完成合同签署 / 绑定后发放。'),
             (549, 1008, '第二笔 · 75%', '11250',
              '按合同完成全集交付，', '通过平台安全审核后发放。')]
    for x0, x1, label, amount, condition1, condition2 in cards:
        d.rounded_rectangle((x0, 380, x1, 654), radius=16, fill=BOX)
        put(d, x0 + 28, 402, label, 25, RUST, 'bold', right=x1 - 24)
        put(d, x0 + 28, 452, amount, 48, INK, 'number')
        put(d, x0 + 28, 514, '元', 20, DIM)
        put(d, x0 + 28, 564, condition1, 21, INK, right=x1 - 24)
        put(d, x0 + 28, 602, condition2, 21, INK, right=x1 - 24)

    d.rounded_rectangle((72, 704, 1008, 844), radius=16, fill=(238, 232, 218))
    put(d, 100, 724, '若按“两笔各 7500 元”安排预算', 24, INK, 'bold')
    put(d, 100, 766, '首笔到账会高估 3750 元', 29, RUST, 'bold')
    put(d, 100, 810, '7500 - 3750 = 3750 元（本号复算）', 20, INK)

    put(d, 72, 900, '来源：澎湃号·DataEye短剧观察 2026-11-12 稿内政策长图 §2.2。', 17, DIM)
    put(d, 72, 934, '本号按媒体所附截图核对；尚未取得官方原页。', 17, DIM)

    check_glyphs()
    save(im, '102_图2_改了什么_1080.png')


def cover():
    BOXES.clear()
    C_W, C_H = 900, 383
    im = Image.new('RGB', (C_W, C_H), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, DIM, 'bold', C_W - 20)
    put_right(d, C_W - 33, 24, f'{ISSUE} / 快讯', 17, DIM, 'body')

    put(d, 42, 66, '红果剧本新政', 20, DIM, 'bold')
    put(d, 42, 100, 'S 级保底', 40, RUST, 'title')
    put(d, 42, 156, '1.5 万元', 40, INK, 'title')
    d.line((42, 226, 400, 226), fill=LINE, width=2)
    put(d, 42, 244, 'A 级零保底 · B 级不合作', 18, INK, 'bold')
    put(d, 42, 276, '保底只看前 30 集质量', 17, DIM)
    put(d, 42, 306, '本文据媒体截图核对', 17, RUST)

    d.rounded_rectangle((420, 52, 860, 330), radius=18, fill=(238, 232, 218))
    put(d, 450, 76, '三档一眼看', 22, DIM, 'bold')
    rows = [('S', '1.5 万保底，分两笔', RUST),
            ('A', '零保底，入池待选', TEAL),
            ('B', '不予合作', DIM)]
    for i, (tag, text, color) in enumerate(rows):
        yy = 128 + i * 66
        put(d, 450, yy + 6, tag, 24, color, 'bold')
        put(d, 510, yy, text, 20, INK, right=830)

    check_glyphs()
    save(im, f'封面_{ISSUE}_{EDITION.replace("-", "")}_900x383.png')


if __name__ == '__main__':
    {'chart1': chart1, 'chart2': chart2, 'cover': cover,
     'all': lambda: (chart1(), chart2(), cover())}[sys.argv[1] if len(sys.argv) > 1 else 'all']()
