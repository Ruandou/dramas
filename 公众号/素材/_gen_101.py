# -*- coding: utf-8 -*-
"""101《Screenburn Writers Room》正文两图 + 封面。纯本地 Pillow，零扣费。"""
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
ISSUE = '101'
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
    im = Image.new('RGB', (W, 990), PAPER)
    d = ImageDraw.Draw(im)
    head(d, '三档价目，一条合约',
         'Screenburn Writers Room · 官方价目页 2026-11-13')

    cards = [
        ('Free', '0', '私人测试，需邀请码', TEAL),
        ('Studio', '350', '5 席位；加 5 席 350', GOLD),
        ('Writers Room', '1,350', '需签 12 个月合约', RUST),
    ]
    xs = [(72, 372), (390, 690), (708, 1008)]
    for (x0, x1), (name, price, note, color) in zip(xs, cards):
        d.rounded_rectangle((x0, 232, x1, 560), radius=16, fill=BOX)
        put(d, x0 + 24, 252, name, 23, color, 'bold', right=x1 - 16)
        put(d, x0 + 20, 300, price, 46, color, 'number')
        unit = '美元/月' if price != '0' else '美元'
        put(d, x0 + 24, 366, unit, 17, DIM)
        put(d, x0 + 24, 404, note, 16, INK, right=x1 - 16)

    d.rounded_rectangle((72, 592, 1008, 760), radius=16, fill=(238, 232, 218))
    put(d, 100, 612, 'Writers Room 的四条细则', 24, INK, 'bold')
    rows = ['含 Studio 全部能力；每月生成一季剧本',
            '额外一季随时买，同样 1,350 美元',
            '当月未用额度不结转',
            '写出来的剧本归作者所有']
    for i, t in enumerate(rows):
        yy = 656 + i * 26
        put(d, 100, yy, '·', 18, RUST, 'bold')
        put(d, 122, yy, t, 18, INK, right=986)

    put(d, 72, 820, '官方格式：60—100 集、单集 1—3 分钟竖屏短剧；专利状态为申请中。', 17, DIM)
    put(d, 72, 854, '免费档为私人测试，不是注册即用。', 17, DIM)

    check_glyphs()
    save(im, '101_图1_三档价目_1080.png')


def chart2():
    BOXES.clear()
    im = Image.new('RGB', (W, 960), PAPER)
    d = ImageDraw.Draw(im)
    head(d, '一年账，和它不覆盖的部分',
         '按官方标价折算 / 本号算术')

    d.rounded_rectangle((72, 232, 528, 500), radius=16, fill=BOX)
    put(d, 100, 252, 'Writers Room 一年', 24, INK, 'bold')
    put(d, 100, 300, '16,200', 52, RUST, 'number')
    put(d, 330, 330, '美元起', 22, RUST, 'bold')
    put(d, 100, 376, '1,350 × 12 个月，不含加季', 19, INK)
    put(d, 100, 420, '按每月一季、每季 80 集摊：', 18, DIM)
    put(d, 100, 452, '一集约 17 美元剧本成本', 19, RUST, 'bold')

    d.rounded_rectangle((552, 232, 1008, 500), radius=16, fill=BOX)
    put(d, 580, 252, '它包含 / 不包含', 24, INK, 'bold')
    inc = ['剧本生成（按月一季）', 'Studio 团队席位']
    exc = ['拍摄、配音、后期', '视频模型调用', '人工改稿']
    put(d, 580, 300, '包含', 18, TEAL, 'bold')
    for i, t in enumerate(inc):
        put(d, 580, 330 + i * 28, '· ' + t, 18, INK, right=988)
    put(d, 580, 396, '不包含', 18, RUST, 'bold')
    for i, t in enumerate(exc):
        put(d, 580, 426 + i * 26, '· ' + t, 18, INK, right=988)

    d.rounded_rectangle((72, 532, 1008, 700), radius=16, fill=(238, 232, 218))
    put(d, 100, 552, '对一人厂牌，先比一件事：自己写一季要多久。', 24, INK, 'bold')
    put(d, 100, 596, '外包一季剧本的报价高于 1,350 美元 + 改稿时间，这笔账才成立；', 20, INK)
    put(d, 100, 632, '只是省打字时间，12 个月合约会先把你绑住。', 20, RUST, 'bold')

    put(d, 72, 780, '数据：Screenburn 官方价目页；Broadcast 2026-11-12（80 集、约 29,000 词、数小时为厂商口径）。', 17, DIM)
    put(d, 72, 814, '17 美元/集与 16,200 美元为本号按官方标价算术，非官方公布单价。', 17, DIM)

    check_glyphs()
    save(im, '101_图2_一年账_1080.png')


def cover():
    BOXES.clear()
    C_W, C_H = 900, 383
    im = Image.new('RGB', (C_W, C_H), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, DIM, 'bold', C_W - 20)
    put_right(d, C_W - 33, 24, f'{ISSUE} / 快讯', 17, DIM, 'body')

    put(d, 42, 66, 'Screenburn Writers Room', 20, DIM, 'bold')
    put(d, 42, 100, 'AI 写整季剧本', 40, RUST, 'title')
    put(d, 42, 156, '1,350 美元/月', 40, INK, 'title')
    d.line((42, 226, 400, 226), fill=LINE, width=2)
    put(d, 42, 244, '合约 12 个月 · 每月一季', 18, INK, 'bold')
    put(d, 42, 276, '不含拍摄、配音、模型调用', 17, DIM)
    put(d, 42, 306, '一年 16,200 美元起', 17, RUST)

    d.rounded_rectangle((420, 52, 860, 330), radius=18, fill=(238, 232, 218))
    put(d, 450, 76, '先算三笔', 22, DIM, 'bold')
    rows = [('一季', '80 集 / 约 2.9 万词', TEAL),
            ('一集', '约 17 美元剧本成本', RUST),
            ('一年', '16,200 美元起', GOLD)]
    for i, (tag, text, color) in enumerate(rows):
        yy = 128 + i * 66
        put(d, 450, yy + 6, tag, 22, color, 'bold')
        put(d, 510, yy, text, 20, INK, right=830)

    check_glyphs()
    save(im, f'封面_{ISSUE}_{EDITION.replace("-", "")}_900x383.png')


if __name__ == '__main__':
    {'chart1': chart1, 'chart2': chart2, 'cover': cover,
     'all': lambda: (chart1(), chart2(), cover())}[sys.argv[1] if len(sys.argv) > 1 else 'all']()