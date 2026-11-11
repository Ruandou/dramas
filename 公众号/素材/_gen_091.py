# -*- coding: utf-8 -*-
"""091《火龙漫剧月保底》正文两图 + 封面。纯本地 Pillow，零扣费。"""
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
ISSUE = '091'
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
    put(d, 100, 44, f'一人短剧厂牌 / 主稿 {ISSUE}', 21, DIM, 'bold')
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
    y = head(d, '3000 元按月拆：100 元每分钟', '火龙漫剧 L2 签约作者 / 每月 30 分钟全网首发')

    rows = [
        ('1000 元档', '33', '元/分钟', '每月全网首发，更新超 30 分钟', TEAL),
        ('3000 元档', '100', '元/分钟', '再加当月新增催更 / 收藏超 2000 人', RUST),
    ]
    top = 226
    for i, (name, big, unit, cond, color) in enumerate(rows):
        yy = top + i * 218
        d.rounded_rectangle((72, yy, W - 72, yy + 190), radius=16, fill=BOX)
        d.rectangle((72, yy, 84, yy + 190), fill=color)
        put(d, 112, yy + 24, name, 30, color, 'bold')
        put(d, 112, yy + 74, cond, 22, DIM)
        put(d, 112, yy + 118, '认证门槛：单专辑播放超 10 万' if i == 0 else '签约后按账号每月发，可叠加分成', 21, INK)
        wb = put(d, 500, yy + 42, big, 76, color, 'number')
        put(d, 500 + wb + 14, yy + 84, unit, 26, color, 'bold')

    yy = top + 2 * 218
    d.rounded_rectangle((72, yy, W - 72, yy + 92), radius=14, fill=(238, 232, 218))
    put(d, 112, yy + 22, '30 分钟 ÷ 30 天 = 每天 1 分钟', 34, INK, 'bold')
    put_right(d, W - 112, yy + 32, '要排进日历的固定产能', 22, DIM)

    yy += 120
    put(d, 72, yy, '横向对照', 22, DIM, 'bold')
    put(d, 72, yy + 36, '火龙此前 S+ 级 AI 仿真人剧单分钟最高保底 1 万元', 26, INK, 'bold')
    put(d, 72, yy + 78, '100 元/分钟是它的 1/100；口径不同，只作量级参照', 24, RUST, 'bold')

    put(d, 72, 942, '数据：短剧自习室 11-05、骨朵 AI 11-06 报道；每分钟单价与每天 1 分钟为本号算术。', 19, DIM)
    check_glyphs()
    save(im, '091_图1_保底拆分钟_1080.png')


def chart2():
    BOXES.clear()
    im = Image.new('RGB', (W, 960), PAPER)
    d = ImageDraw.Draw(im)
    y = head(d, '四种百分比，各算各的', '火龙漫剧创作者计划 / 不能相加成一个总分成')

    put(d, 72, y, '激励项', 20, DIM, 'bold')
    put(d, 500, y, '数值', 20, DIM, 'bold')
    put(d, 690, y, '挂在什么基数上', 20, DIM, 'bold')

    rows = [
        ('L2 账号等级', '20%', '分成系数上浮', TEAL, '短剧研究僧写作「20% 分成补贴」'),
        ('IP 改编独家', '15%', '叠加分成激励', RUST, '非独家不享'),
        ('系列化独家', '10% / 15%', '第二季 / 第三季起', GOLD, '两季间隔 ≤1 个月'),
        ('题材激励', '20% / 10%', '独家 / 非独家', TEAL, '乘基础分成收益'),
    ]
    top = y + 40
    for i, (name, val, base, color, note) in enumerate(rows):
        yy = top + i * 112
        d.line((72, yy, W - 72, yy), fill=LINE, width=2)
        d.rectangle((72, yy + 20, 80, yy + 52), fill=color)
        put(d, 96, yy + 18, name, 27, INK, 'bold')
        put(d, 96, yy + 60, note, 19, DIM)
        put(d, 500, yy + 22, val, 30, color, 'number')
        put(d, 690, yy + 24, base, 23, INK)

    yy = top + 4 * 112
    d.line((72, yy, W - 72, yy), fill=LINE, width=2)
    d.rounded_rectangle((72, yy + 24, W - 72, yy + 128), radius=14, fill=(238, 232, 218))
    put(d, 100, yy + 44, '分成收益＝有效播放时长×时长单价×类型系数', 22, INK, 'bold')
    put(d, 100, yy + 84, '×版权系数×账号等级系数', 22, INK, 'bold')

    put(d, 72, yy + 160, '20%、15%、10% 各挂不同基数，加起来当总分成是错的。', 24, RUST, 'bold')
    put(d, 72, 910, '数据：短剧研究僧 11-04、骨朵 AI 11-06 报道；分项归并为本号整理。', 19, DIM)
    check_glyphs()
    save(im, '091_图2_分成拆项_1080.png')


def cover():
    BOXES.clear()
    C_W, C_H = 900, 383
    im = Image.new('RGB', (C_W, C_H), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, DIM, 'bold', C_W - 20)
    put_right(d, C_W - 33, 24, f'{ISSUE} / 主稿', 17, DIM, 'body')

    put(d, 42, 66, '30', 78, TEAL, 'number')
    put(d, 42, 152, '分钟 / 月', 20, TEAL, 'bold')
    put(d, 42, 184, '= 每天 1 分钟', 17, DIM)
    d.line((42, 218, 366, 218), fill=LINE, width=2)
    put(d, 42, 236, '33—100 元 / 分钟', 21, RUST, 'bold')
    put(d, 42, 270, '按月发，不按单部', 17, DIM)

    def safe_center(cx, y, text, size, color=INK, kind='bold'):
        w = d.textlength(text, font=font(size, kind))
        assert w <= 351, (text, w)
        put(d, cx - w / 2, y, text, size, color, kind)

    safe_center(520, 54, '火龙漫剧', 30, INK, 'title')
    safe_center(520, 100, '月保底', 34, RUST, 'title')
    safe_center(520, 148, '3000 元封顶', 46, RUST, 'title')
    safe_center(520, 222, '先过', 24, INK, 'body')
    safe_center(520, 254, '单专辑 10 万播放', 30, INK, 'title')
    safe_center(520, 318, '腾讯视频 / 11-05 发布', 18, DIM, 'body')

    put(d, 748, 92, '拿保底要过', 17, DIM, 'bold')
    for i, name in enumerate(('原创账号', '累计 10 集', '全网首发', '月增 2000 人')):
        put(d, 748, 122 + i * 34, name, 18, INK, 'bold')

    check_glyphs()
    save(im, f'封面_{ISSUE}_{EDITION.replace("-", "")}_900x383.png')


if __name__ == '__main__':
    {'chart1': chart1, 'chart2': chart2, 'cover': cover,
     'all': lambda: (chart1(), chart2(), cover())}[sys.argv[1] if len(sys.argv) > 1 else 'all']()
