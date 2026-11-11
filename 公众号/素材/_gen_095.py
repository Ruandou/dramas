# -*- coding: utf-8 -*-
"""095《京东被曝内测「追剧福利社」》正文两图 + 封面。纯本地 Pillow，零扣费。"""
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
ISSUE = '095'
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
    im = Image.new('RGB', (W, 990), PAPER)
    d = ImageDraw.Draw(im)
    head(d, '已经有了什么，还缺什么',
         '京东追剧福利社 · 媒体实测与报道口径 / 官方未回应')

    put(d, 100, 232, '已经有了', 26, TEAL, 'bold')
    put(d, 232, 238, '实测可见', 18, DIM)
    put(d, 580, 232, '还缺', 26, RUST, 'bold')
    put(d, 652, 238, '截至 11-11 报道', 18, DIM)

    d.rounded_rectangle((72, 272, 528, 660), radius=16, fill=BOX)
    left = ['微信小程序上架，可搜索', '全免费观看', '都市 / 悬疑 / 战神 / 重生等标签',
            '单剧几十集到上百集', '上下滑屏 / 倍速 / 收藏 / 历史']
    for i, t in enumerate(left):
        yy = 296 + i * 70
        d.rectangle((100, yy + 6, 112, yy + 18), fill=TEAL)
        put(d, 128, yy, t, 22, INK, right=508)

    d.rounded_rectangle((552, 272, 1008, 660), radius=16, fill=BOX)
    right = [('电商跳转入口', '澎湃、读佳实测均未见'),
             ('京东 App 入口', '新浪科技 11-10：暂未看到'),
             ('京东官方回应', '新浪科技、澎湃求证未回应'),
             ('供片窗 / 分账条款', '无公告、无招募入口')]
    for i, (name, note) in enumerate(right):
        yy = 296 + i * 88
        d.rectangle((580, yy + 6, 592, yy + 18), fill=RUST)
        put(d, 608, yy, name, 24, INK, 'bold', right=988)
        put(d, 608, yy + 38, note, 18, DIM, right=988)

    d.rounded_rectangle((72, 690, 1008, 800), radius=16, fill=(238, 232, 218))
    put(d, 100, 710, '「剧中同款直接买，京东发货」', 30, INK, 'bold')
    put(d, 100, 756, '目前仍是产品介绍文案，不是已上线功能。', 22, RUST, 'bold')

    put(d, 72, 930, '数据：读佳 11-10、新浪科技 11-10、澎湃 11-11 报道与实测；京东官方未回应。', 17, DIM)

    check_glyphs()
    save(im, '095_图1_已有还缺_1080.png')


def chart2():
    BOXES.clear()
    im = Image.new('RGB', (W, 960), PAPER)
    d = ImageDraw.Draw(im)
    head(d, '红果向外导流，京东向内带货',
         '免费短剧的两种生意 / 制作方视角')

    def card(x0, x1, color, name, steps, note):
        d.rounded_rectangle((x0, 236, x1, 700), radius=16, fill=BOX)
        put(d, x0 + 28, 258, name, 25, color, 'bold', right=x1 - 20)
        cx = (x0 + x1) // 2
        for i, (main, sub) in enumerate(steps):
            yy = 316 + i * 86
            put(d, x0 + 28, yy, main, 23, INK, 'bold', right=x1 - 20)
            put(d, x0 + 28, yy + 34, sub, 18, DIM, right=x1 - 20)
            if i < len(steps) - 1:
                arrow_down(d, cx, yy + 62, color)
        put(d, x0 + 28, 662, note, 19, color, 'bold', right=x1 - 20)

    card(72, 528, TEAL, '红果 · 内容流量向外',
         [('聚追剧流量', '日活 1.68 亿（QuestMobile 7 月口径）'),
          ('AI 画面识别「搜同款」', '播放页弹出入口'),
          ('一键跳抖音小店', '暂停剧集即可跳转'),
          ('商家承接履约', '平台只做导流')],
         '平台不承担供应链')
    card(552, 1008, RUST, '京东 · 自营供应链向内',
         [('免费短剧聚注意力', '全免费，无付费解锁'),
          ('看剧领福利、领券', '产品介绍口径'),
          ('剧中同款下单', '介绍口径 · 实测未见入口'),
          ('京东发货', '自营履约，不跳外部')],
         '目标是商品转化，不是卖剧')

    d.rounded_rectangle((72, 730, 1008, 830), radius=16, fill=(238, 232, 218))
    put(d, 100, 750, '对制作方：供片窗还没开，分账条款也没有；', 24, INK, 'bold')
    put(d, 100, 788, '短期更可能是采购 / 定制，不是开放上传。', 24, RUST, 'bold')

    put(d, 72, 910, '数据：读佳 11-10、澎湃 11-11；红果日活为媒体引述的 QuestMobile 2026-07 口径。', 17, DIM)

    check_glyphs()
    save(im, '095_图2_两条带货路径_1080.png')


def cover():
    BOXES.clear()
    C_W, C_H = 900, 383
    im = Image.new('RGB', (C_W, C_H), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, DIM, 'bold', C_W - 20)
    put_right(d, C_W - 33, 24, f'{ISSUE} / 快讯', 17, DIM, 'body')

    put(d, 42, 70, '京东内测', 20, DIM, 'bold')
    put(d, 42, 100, '追剧福利社', 42, RUST, 'title')
    put(d, 42, 162, '免费短剧＋电商带货', 19, INK, 'bold')
    d.line((42, 200, 330, 200), fill=LINE, width=2)
    put(d, 42, 216, '微信小程序已上架', 17, DIM)
    put(d, 42, 246, '官方未回应', 17, DIM)
    put(d, 42, 276, '电商入口实测未见', 17, DIM)

    put(d, 400, 60, '剧是入口，货是目的', 26, INK, 'title')
    steps = [('免费看剧', '实测', TEAL), ('看剧领福利', '介绍', TEAL),
             ('剧中同款下单', '介绍 · 未见入口', RUST), ('京东发货', '介绍', RUST)]
    for i, (t, tag, color) in enumerate(steps):
        yy = 104 + i * 66
        d.rounded_rectangle((400, yy, 680, yy + 44), radius=10,
                            outline=color, width=2,
                            fill=PAPER if i >= 2 else BOX)
        w = d.textlength(t, font=font(22, 'bold'))
        put(d, 540 - w / 2, yy + 10, t, 22, color, 'bold')
        put(d, 696, yy + 13, tag, 16, DIM, right=867)
        if i < 3:
            arrow_down(d, 540, yy + 48, DIM)

    check_glyphs()
    save(im, f'封面_{ISSUE}_{EDITION.replace("-", "")}_900x383.png')


if __name__ == '__main__':
    {'chart1': chart1, 'chart2': chart2, 'cover': cover,
     'all': lambda: (chart1(), chart2(), cover())}[sys.argv[1] if len(sys.argv) > 1 else 'all']()