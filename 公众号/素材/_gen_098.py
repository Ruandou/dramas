# -*- coding: utf-8 -*-
"""098《深圳第二批微短剧扶持》正文两图 + 封面。纯本地 Pillow，零扣费。"""
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
ISSUE = '098'
EDITION = '2026-11-12'
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
    head(d, '这批补什么，不补什么',
         '深圳 2026 第二批微短剧扶持 · 仅「产业活动」方向')

    d.rounded_rectangle((72, 232, 528, 700), radius=16, fill=BOX)
    put(d, 100, 254, '补', 26, TEAL, 'bold')
    put(d, 100, 292, '在深圳办过的国家级节庆活动', 17, DIM)
    left = [('活动范围', '深圳行政区域内经批准举办'),
            ('活动时间', '2026-01-01 至 10-31'),
            ('申报主体', '主办方或承办方之一'),
            ('票据时间', '2025-07-01 至 2026-10-31'),
            ('资助方式', '事后资助：场地、设备、宣推等')]
    for i, (name, note) in enumerate(left):
        yy = 336 + i * 70
        d.rectangle((100, yy + 6, 112, yy + 18), fill=TEAL)
        put(d, 128, yy, name, 21, INK, 'bold')
        put(d, 128, yy + 32, note, 18, DIM, right=506)

    d.rounded_rectangle((552, 232, 1008, 700), radius=16, fill=BOX)
    put(d, 580, 254, '不补', 26, RUST, 'bold')
    put(d, 580, 292, '拍剧、备案、播出都不在这轮', 17, DIM)
    right = ['拍剧制作费', '剧本 / 制作 / 播出补贴', '个人创作者', '没办过活动的制作方', '参展方、赞助方']
    for i, t in enumerate(right):
        yy = 336 + i * 66
        d.rectangle((580, yy + 6, 592, yy + 18), fill=RUST)
        put(d, 608, yy, t, 22, INK, right=988)

    d.rounded_rectangle((72, 730, 1008, 830), radius=16, fill=(238, 232, 218))
    put(d, 100, 752, '补的是「办过活动」的账，不是「要拍剧」的钱。', 26, INK, 'bold')
    put(d, 100, 792, '只做内容生产、没主办或承办这类活动，本批次没有可报项。', 20, RUST, 'bold')

    put(d, 72, 930, '数据：深圳市文化广电旅游体育局通知 2026-11-11；界面新闻、观点网同日。', 17, DIM)

    check_glyphs()
    save(im, '098_图1_补与不补_1080.png')


def chart2():
    BOXES.clear()
    im = Image.new('RGB', (W, 960), PAPER)
    d = ImageDraw.Draw(im)
    head(d, '申报路径，三天窗口',
         '网上填报 11-11 至 11-13 · 广东政务服务网')

    steps = [('① 找入口', '法人服务 - 按部门分类 - 深圳 - 文广旅体局 - 其他类别'),
             ('② 选项目', '深圳市微短剧专项资金（2026 年产业服务专项）'),
             ('③ 企业注册', '以企业为单位，绑定实名经办人'),
             ('④ 预审与后续', '驳回可补，3 个工作日内重交；审计、考察、审议、公示')]
    for i, (main, sub) in enumerate(steps):
        yy = 238 + i * 108
        d.rounded_rectangle((72, yy, 1008, yy + 92), radius=12, fill=BOX if i % 2 == 0 else PAPER,
                            outline=LINE, width=2)
        put(d, 100, yy + 14, main, 24, TEAL, 'bold', right=986)
        put(d, 100, yy + 52, sub, 18, INK, right=986)

    d.rounded_rectangle((72, 690, 1008, 812), radius=16, fill=(238, 232, 218))
    put(d, 100, 708, '时间窗', 24, INK, 'bold')
    put(d, 100, 746, '活动举办 2026-01-01 至 10-31 ／ 票据 2025-07-01 至 2026-10-31', 19, INK)
    put(d, 100, 778, '网上申报 11-11 至 11-13 ／ 同批次最多 3 项，每项不超过 7 天', 19, RUST, 'bold')

    put(d, 72, 880, '不收费、未委托中介；申报与评审全程可自行办理，遇收费代报可向局方举报。', 17, DIM)

    check_glyphs()
    save(im, '098_图2_申报路径_1080.png')


def cover():
    BOXES.clear()
    C_W, C_H = 900, 383
    im = Image.new('RGB', (C_W, C_H), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, DIM, 'bold', C_W - 20)
    put_right(d, C_W - 33, 24, f'{ISSUE} / 快讯', 17, DIM, 'body')

    put(d, 42, 66, '深圳第二批微短剧扶持', 20, DIM, 'bold')
    put(d, 42, 100, '只补产业活动', 40, RUST, 'title')
    put(d, 42, 156, '拍剧的报不了', 40, INK, 'title')
    d.line((42, 226, 390, 226), fill=LINE, width=2)
    put(d, 42, 244, '国家级节庆活动 · 事后资助', 18, INK, 'bold')
    put(d, 42, 276, '申报 11-11 至 11-13', 17, DIM)
    put(d, 42, 306, '广东政务服务网', 17, DIM)

    put(d, 440, 52, '先自查三件事', 20, DIM, 'bold')
    rows = [('主体', '深圳注册、做微短剧相关服务', TEAL),
            ('活动', '今年 1—10 月在深圳办过', TEAL),
            ('身份', '主办或承办方，不是参展方', RUST)]
    for i, (tag, text, color) in enumerate(rows):
        yy = 96 + i * 76
        put(d, 440, yy + 8, tag, 20, color, 'bold')
        put(d, 510, yy, text, 19, INK, right=860)

    check_glyphs()
    save(im, f'封面_{ISSUE}_{EDITION.replace("-", "")}_900x383.png')


if __name__ == '__main__':
    {'chart1': chart1, 'chart2': chart2, 'cover': cover,
     'all': lambda: (chart1(), chart2(), cover())}[sys.argv[1] if len(sys.argv) > 1 else 'all']()