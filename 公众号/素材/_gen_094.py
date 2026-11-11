# -*- coding: utf-8 -*-
"""094《Seedream 5.5 单张 0.28 元》正文两图 + 封面。纯本地 Pillow，零扣费。"""
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
ISSUE = '094'
EDITION = '2026-11-10'
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
    head(d, '0.28 元一张，摊到一部剧是多少',
         'Seedream 5.5 · 2K 方图编辑媒体口径 / 官方价目页未上')

    # 左：单价
    d.rounded_rectangle((72, 226, 470, 560), radius=16, fill=BOX)
    put(d, 102, 248, '2K 方图编辑', 24, TEAL, 'bold')
    put(d, 100, 292, '0.28', 104, RUST, 'number')
    put(d, 104, 408, '元 / 张', 30, RUST, 'bold')
    put(d, 102, 456, '上一代 ≥0.56 元/张', 22, INK, 'bold')
    put(d, 102, 490, '（按「不到一半」倒推）', 19, DIM)
    put(d, 102, 522, '计费：输入图 + 输出图，文本 Token 免费', 17, DIM)

    # 右：图账
    put(d, 512, 232, '一部剧的图账', 26, INK, 'bold')
    put(d, 512, 268, '角色 / 造型 / 场景 / 道具 / 首帧', 18, DIM)
    rows = [('100 张', 28, 60), ('300 张', 84, 180), ('500 张', 140, 300)]
    for i, (label, yuan, bar) in enumerate(rows):
        yy = 318 + i * 74
        put(d, 512, yy + 6, label, 23, INK, 'bold')
        d.rounded_rectangle((610, yy, 610 + bar, yy + 30), radius=6,
                            fill=TEAL if i < 2 else RUST)
        put_right(d, 1008, yy + 2, f'{yuan} 元', 24, INK, 'bold')
    put(d, 512, 548, '本号按 0.28 元/张算术，不含重试与筛选', 17, DIM)

    # 中下：多试几版
    d.rounded_rectangle((72, 590, 1008, 742), radius=16, fill=(238, 232, 218))
    put(d, 100, 610, '同角色出 4 版挑 1 版，多花 0.84 元', 32, INK, 'bold')
    put(d, 100, 658, '上一代出 4 版要 2.24 元以上。对定妆、气氛这种靠试错定方向的环节，', 22, INK)
    put(d, 100, 694, '差别不在省下的钱，在敢不敢多生成几版。', 22, RUST, 'bold')

    put(d, 72, 790, '预备量级', 20, DIM, 'bold')
    put(d, 72, 822, '一部 80—100 集的剧，角色形象、每套造型、场景基准与变体、道具、分镜首帧，', 21, INK)
    put(d, 72, 856, '通常是几百张的量级，按项目规模差异很大；500 张按本口径是 140 元。', 21, INK)
    put(d, 72, 930, '数据：新京报 11-09、新浪科技 11-09、澎湃 11-10 同场发布口径；张数与 4 版换算为本号算术。', 17, DIM)

    check_glyphs()
    save(im, '094_图1_单张摊图账_1080.png')


def chart2():
    BOXES.clear()
    im = Image.new('RGB', (W, 960), PAPER)
    d = ImageDraw.Draw(im)
    head(d, '三个新能力，能用在哪儿、别指望什么',
         'Seedream 5.5 / 透明素材 · 多轮编辑 · 小字中文')

    put(d, 96, 224, '能力', 19, DIM, 'bold')
    put(d, 404, 224, '短剧里怎么用', 19, DIM, 'bold')
    put(d, 740, 224, '别指望', 19, DIM, 'bold')

    rows = [
        ('RGBA 透明 + 分层', TEAL,
         '角色/道具合成少抠图',
         '边缘仍要目检'),
        ('多轮编辑像素级保持', RUST,
         '场景变体、道具新旧状态',
         '人脸与角度一致性'),
        ('小字中文渲染', GOLD,
         '道具标签、信息图',
         '当字幕方案用'),
    ]
    for i, (name, color, use, limit) in enumerate(rows):
        yy = 264 + i * 178
        d.line((72, yy, 1008, yy), fill=LINE, width=2)
        d.rectangle((72, yy + 22, 82, yy + 58), fill=color)
        put(d, 96, yy + 22, name, 27, color, 'bold')
        put(d, 96, yy + 66, ['透明通道', '改局部不动全局', '画中文小字'][i], 19, DIM)
        put(d, 404, yy + 28, use, 23, INK, right=724)
        put(d, 740, yy + 28, limit, 23, INK, right=1008)
    d.line((72, 264 + 3 * 178, 1008, 264 + 3 * 178), fill=LINE, width=2)

    d.rounded_rectangle((72, 812, 1008, 880), radius=14, fill=(238, 232, 218))
    put(d, 100, 830, '角色一致性仍靠参考图与提示词，模型只决定生成质量。', 24, RUST, 'bold')

    put(d, 72, 910, '数据：新京报 11-09、新浪科技 11-09 发布报道；能力描述为报道口径，未实测。', 17, DIM)

    check_glyphs()
    save(im, '094_图2_能力筛选_1080.png')


def cover():
    BOXES.clear()
    C_W, C_H = 900, 383
    im = Image.new('RGB', (C_W, C_H), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, DIM, 'bold', C_W - 20)
    put_right(d, C_W - 33, 24, f'{ISSUE} / 快讯', 17, DIM, 'body')

    put(d, 42, 66, '0.28', 88, RUST, 'number')
    put(d, 42, 168, '元 / 张', 24, RUST, 'bold')
    put(d, 42, 204, '2K 方图编辑', 19, INK, 'bold')
    d.line((42, 238, 366, 238), fill=LINE, width=2)
    put(d, 42, 254, '不到上一代一半', 20, INK, 'bold')
    put(d, 42, 286, '官方价目页未上', 17, DIM)

    def safe_center(cx, y, text, size, color=INK, kind='bold'):
        w = d.textlength(text, font=font(size, kind))
        assert w <= 430, (text, w)
        put(d, cx - w / 2, y, text, size, color, kind)

    safe_center(636, 54, 'Seedream 5.5', 28, INK, 'title')
    safe_center(636, 100, '短剧资产图', 40, RUST, 'title')
    safe_center(636, 158, '这笔账要重算', 40, INK, 'title')
    safe_center(636, 224, '造型多出几版，成本只多几毛', 20, INK, 'body')
    safe_center(636, 266, '透明素材 · 多轮编辑 · 小字中文', 18, DIM, 'body')
    safe_center(636, 322, '11-09 发布 / API 即将上线', 17, DIM, 'body')

    check_glyphs()
    save(im, f'封面_{ISSUE}_{EDITION.replace("-", "")}_900x383.png')


if __name__ == '__main__':
    {'chart1': chart1, 'chart2': chart2, 'cover': cover,
     'all': lambda: (chart1(), chart2(), cover())}[sys.argv[1] if len(sys.argv) > 1 else 'all']()
