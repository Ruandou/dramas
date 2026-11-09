# -*- coding: utf-8 -*-
"""090《红果加码知识短剧》正文两图 + 封面。纯本地 Pillow，零扣费。"""
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
WHITE = (255, 250, 240)

SONG, HIRA, MONO = _c.SONG, _c.HIRA, _c.MONO
GLYPHS: dict = {}
BOXES: list = []
ISSUE = '090'
EDITION = '2026-11-09'
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
    put(d, 100, 44, f'一人短剧厂牌 / 主稿 {ISSUE}', 21, DIM, 'bold')
    put_right(d, W - 72, 44, EDITION, 22, RUST, 'number')
    put(d, 72, 92, title, 46, INK, 'title')
    put(d, 72, 158, sub, 22, DIM)
    return 216


def dot_grid(d, x, y, total, filled, color, dot=12, gap=3, cols=15):
    for i in range(total):
        cx = x + (i % cols) * (dot + gap)
        cy = y + (i // cols) * (dot + gap)
        if i < filled:
            d.ellipse((cx, cy, cx + dot, cy + dot), fill=color)
        else:
            d.ellipse((cx, cy, cx + dot, cy + dot), outline=LINE, width=2)


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
    im = Image.new('RGB', (W, 980), PAPER)
    d = ImageDraw.Draw(im)
    y = head(d, '两个口袋：投资和活动金额', '果燃计划 vs 优质 AI 剧生产活动 3.0 / 2026-11')

    cards = [
        ('果燃计划', '项目投资', '30%—100%', '', '项目总金额的投入比例', '入选项目制，钱进制作环节', '解决「拍不拍得起」', TEAL),
        ('优质 AI 剧 3.0', '活动金额', '90—179', ' 分钟', '完结剧拿全额，300 分钟归零', '对已上线作品按时长给系数', '看「播得好不好」', GOLD),
    ]
    x0, w = 72, 448
    for i, (name, kind, big, suffix, line1, line2, line3, color) in enumerate(cards):
        x = x0 + i * (w + 40)
        d.rounded_rectangle((x, y, x + w, y + 560), radius=16, fill=BOX)
        d.rectangle((x, y, x + 10, y + 70), fill=color)
        put(d, x + 34, y + 24, name, 30, INK, 'bold')
        put(d, x + 34, y + 72, kind, 22, color, 'bold')
        wb = put(d, x + 34, y + 128, big, 42, color, 'number')
        if suffix:
            put(d, x + 34 + wb + 8, y + 144, suffix, 24, color)
        put(d, x + 34, y + 196, line1, 21, DIM)
        put(d, x + 34, y + 236, line2, 21, DIM)
        put(d, x + 34, y + 276, line3, 21, INK)
        d.line((x + 34, y + 340, x + w - 34, y + 340), fill=LINE, width=2)
        if i == 0:
            put(d, x + 34, y + 372, '不是分账', 30, RUST, 'bold')
            put(d, x + 34, y + 420, '不是保底采购价', 30, RUST, 'bold')
        else:
            put(d, x + 34, y + 372, '不是制作投资', 30, RUST, 'bold')
            put(d, x + 34, y + 420, '不覆盖立项成本', 30, RUST, 'bold')

    put(d, 72, 812, '两种钱性质不同：一个在前端，一个在后端；不能把投资款当收入预期。', 24, INK, 'bold')
    put(d, 72, 874, '数据：红果「红果有新知」活动报道（2026-11-09）；红果优质 AI 剧生产活动 3.0（本号 2026-11-02 拆解）。', 19, DIM)
    check_glyphs()
    save(im, f'090_图1_两个口袋_1080.png')


def chart2():
    BOXES.clear()
    im = Image.new('RGB', (W, 860), PAPER)
    d = ImageDraw.Draw(im)
    y = head(d, '近 150 部扶持：AI 剧约 13%', '果燃计划累计扶持 / 下半年 AI 微短剧立项近 20 部')

    dot_grid(d, 72, y + 10, 150, 20, TEAL)
    put(d, 470, y + 10, '累计扶持', 24, DIM, 'bold')
    put(d, 470, y + 52, '近 150 部', 42, INK, 'title')
    put(d, 470, y + 122, '其中 AI 剧近 20 部', 26, INK, 'bold')
    put(d, 470, y + 170, '20÷150≈13%', 32, TEAL, 'number')
    put(d, 470, y + 220, 'AI 扶持 2026 年下半年才开', 21, DIM)

    y2 = y + 300
    d.line((72, y2, W - 72, y2), fill=LINE, width=2)
    put(d, 72, y2 + 24, '真人剧样本', 22, DIM, 'bold')
    put(d, 72, y2 + 60, '《冒姓琅琊》《暗潮涌动》《长路初心》', 26, INK, 'bold')
    put(d, 72, y2 + 120, 'AI 剧点名', 22, DIM, 'bold')
    put(d, 72, y2 + 156, '《本草传奇》（熊召政） 《格萨尔王》（阿来）', 26, INK, 'bold')
    put(d, 72, y2 + 200, '公益系列（中国出生缺陷干预救助基金会等）', 24, INK)
    put(d, 72, y2 + 270, '数据：红果「红果有新知」活动报道（紫牛新闻 / 上观新闻，2026-11-09）。', 19, DIM)
    check_glyphs()
    save(im, f'090_图2_扶持构成_1080.png')


def cover():
    BOXES.clear()
    C_W, C_H = 900, 383
    im = Image.new('RGB', (C_W, C_H), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, DIM, 'bold', C_W - 20)
    put_right(d, C_W - 33, 24, f'{ISSUE} / 主稿', 17, DIM, 'body')

    dot_grid(d, 42, 72, 150, 20, TEAL, dot=7, gap=2)
    put(d, 42, 244, 'AI 20 / 150', 19, TEAL, 'number')
    put(d, 42, 270, '约 13%', 17, DIM)

    def safe_center(cx, y, text, size, color=INK, kind='bold'):
        w = d.textlength(text, font=font(size, kind))
        assert w <= 351, (text, w)
        put(d, cx - w / 2, y, text, size, color, kind)

    safe_center(450, 54, '红果加码知识短剧', 32, INK, 'title')
    safe_center(450, 104, '果燃计划', 34, RUST, 'title')
    safe_center(450, 150, '30%—100%', 48, RUST, 'title')
    safe_center(450, 228, '是什么钱', 32, INK, 'title')
    safe_center(450, 286, '项目投资，不是分账；个人能报吗', 20, DIM, 'body')
    safe_center(450, 316, '11-06 活动 / 11-09 报道', 18, DIM, 'body')

    put(d, 690, 92, '被点名的方向', 17, DIM, 'bold')
    for i, name in enumerate(('中医药', '法律', '医学', '古生物', '科幻', '公益')):
        put(d, 690, 122 + i * 34, name, 18, INK, 'bold')

    check_glyphs()
    save(im, f'封面_090_{EDITION.replace("-", "")}_900x383.png')


if __name__ == '__main__':
    {'chart1': chart1, 'chart2': chart2, 'cover': cover,
     'all': lambda: (chart1(), chart2(), cover())}[sys.argv[1] if len(sys.argv) > 1 else 'all']()
