# -*- coding: utf-8 -*-
"""097《红果上线 AI 剧角色确权》正文两图 + 封面。纯本地 Pillow，零扣费。"""
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
ISSUE = '097'
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


def arrow_down(d, cx, y, color=DIM):
    d.polygon([(cx - 8, y), (cx + 8, y), (cx, y + 12)], fill=color)


def chart1():
    BOXES.clear()
    im = Image.new('RGB', (W, 960), PAPER)
    d = ImageDraw.Draw(im)
    head(d, '三类来源，一条确权路径',
         '红果《AI剧虚拟形象创编与确权能力上线公告》2026-11-09 18:00')

    d.rounded_rectangle((72, 232, 500, 580), radius=16, fill=BOX)
    put(d, 100, 254, '虚拟形象从哪来', 24, TEAL, 'bold')
    items = [('真人授权', '肖像与表演相关权益'),
             ('上游 IP 授权', '改编权与授权链'),
             ('原创创作', '著作权登记等材料')]
    for i, (name, note) in enumerate(items):
        yy = 300 + i * 82
        d.rectangle((100, yy + 6, 112, yy + 18), fill=TEAL)
        put(d, 128, yy, name, 24, INK, 'bold', right=478)
        put(d, 128, yy + 38, note, 18, DIM, right=478)
    put(d, 100, 556, '三类都可能涉及肖像、美术设计等权益', 17, DIM, right=478)

    steps = [('发布前提报', '虚拟形象 + 对应权属材料'),
             ('平台审核', '材料是否齐全、对得上'),
             ('形成确权记录', '供后续使用与风险处置参考')]
    for i, (main, sub) in enumerate(steps):
        yy = 238 + i * 116
        d.rounded_rectangle((548, yy, 1008, yy + 88), radius=12, fill=PAPER, outline=LINE, width=2)
        put(d, 576, yy + 14, f'{i + 1}. {main}', 24, RUST, 'bold', right=986)
        put(d, 576, yy + 52, sub, 18, DIM, right=986)
        if i < 2:
            arrow_down(d, 778, yy + 92, RUST)

    d.rounded_rectangle((72, 616, 1008, 726), radius=16, fill=(238, 232, 218))
    put(d, 100, 636, '确权记录只辅助权属留存，不等于平台兜底；', 24, INK, 'bold')
    put(d, 100, 676, '内容上线与分发，仍要符合平台规则和法律法规。', 24, RUST, 'bold')

    put(d, 72, 900, '数据：短剧创作者中心公告页（2026-11-09 18:00）；新浪科技、IT之家 2026-11-11 报道。', 17, DIM)

    check_glyphs()
    save(im, '097_图1_确权路径_1080.png')


def chart2():
    BOXES.clear()
    im = Image.new('RGB', (W, 990), PAPER)
    d = ImageDraw.Draw(im)
    head(d, '能挡什么，挡不住什么',
         '确权记录的边界 / 按公告原文口径')

    d.rounded_rectangle((72, 232, 528, 580), radius=16, fill=BOX)
    put(d, 100, 254, '能挡', 26, TEAL, 'bold')
    put(d, 172, 260, '上线后说不清来源', 17, DIM)
    left = ['真人 / IP / 原创，材料先留档', '多集复用一个形象，有记录可依', '出现争议时，处置有据可查']
    for i, t in enumerate(left):
        yy = 306 + i * 84
        d.rectangle((100, yy + 6, 112, yy + 18), fill=TEAL)
        put(d, 128, yy, t, 22, INK, right=506)

    d.rounded_rectangle((552, 232, 1008, 580), radius=16, fill=BOX)
    put(d, 580, 254, '挡不住', 26, RUST, 'bold')
    put(d, 664, 260, '别把记录当保险', 17, DIM)
    right = ['不等于内容过审', '不等于平台兜底版权风险', '不替代著作权登记']
    for i, t in enumerate(right):
        yy = 306 + i * 84
        d.rectangle((580, yy + 6, 592, yy + 18), fill=RUST)
        put(d, 608, yy, t, 22, INK, right=988)

    d.rounded_rectangle((72, 616, 1008, 812), radius=16, fill=(238, 232, 218))
    put(d, 100, 636, '制作方三条', 26, INK, 'bold')
    tips = ['先把角色来源盘清：合同、授权链、原创材料',
            '多集复用一个角色，先确权再开工',
            '改外观、换素材后，重新核对是否还对得上材料']
    for i, t in enumerate(tips):
        yy = 684 + i * 42
        put(d, 100, yy, f'0{i + 1}', 20, RUST, 'number')
        put(d, 148, yy, t, 21, INK, right=986)

    put(d, 72, 918, '数据：红果公告原文 2026-11-09；公告未写审核时限、材料清单细则与申诉流程。', 17, DIM)

    check_glyphs()
    save(im, '097_图2_能挡什么_1080.png')


def cover():
    BOXES.clear()
    C_W, C_H = 900, 383
    im = Image.new('RGB', (C_W, C_H), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, DIM, 'bold', C_W - 20)
    put_right(d, C_W - 33, 24, f'{ISSUE} / 快讯', 17, DIM, 'body')

    put(d, 42, 66, '红果新公告', 20, DIM, 'bold')
    put(d, 42, 100, 'AI 剧角色', 40, RUST, 'title')
    put(d, 42, 156, '先确权，再发剧', 40, INK, 'title')
    d.line((42, 226, 380, 226), fill=LINE, width=2)
    put(d, 42, 244, '发布前交权属材料', 19, INK, 'bold')
    put(d, 42, 278, '真人 / IP / 原创 三类来源', 17, DIM)
    put(d, 42, 308, '公告 11-09 18:00 · 媒体 11-11', 17, DIM)

    d.rounded_rectangle((430, 52, 860, 330), radius=18, fill=(238, 232, 218))
    put(d, 460, 76, '确权 ≠ 免审', 34, RUST, 'title')
    lines = [('能挡', '来源说不清、争议无据'),
             ('挡不住', '内容过审、平台兜底'),
             ('仍要看', '平台规则与法律法规')]
    for i, (tag, text) in enumerate(lines):
        yy = 146 + i * 58
        put(d, 460, yy, tag, 20, TEAL if i == 0 else RUST, 'bold')
        put(d, 548, yy, text, 20, INK, right=832)

    check_glyphs()
    save(im, f'封面_{ISSUE}_{EDITION.replace("-", "")}_900x383.png')


if __name__ == '__main__':
    {'chart1': chart1, 'chart2': chart2, 'cover': cover,
     'all': lambda: (chart1(), chart2(), cover())}[sys.argv[1] if len(sys.argv) > 1 else 'all']()