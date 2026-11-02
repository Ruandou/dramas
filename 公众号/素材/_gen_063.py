#!/usr/bin/env python3
"""063《红果 AI 剧 3.0》配图与封面。纯本地 Pillow。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def duration_zones():
    im, d = page('90—179 分钟才是全额区', '红果「优质AI剧生产活动 3.0」/ 2026-11-01 生效 / 单位：分钟', '01', 1060)

    x0, span, top, bot = 72, 936, 276, 356
    total = 330.0
    zones = [
        (30, GREY, '0—30', '归零'),
        (60, GOLD, '30—90', '非全额'),
        (90, TEAL, '90—180', '全额'),
        (120, GOLD, '180—300', '非全额'),
        (30, RUST, '≥300', '归零'),
    ]
    x = x0
    for val, color, name, tag in zones:
        w = span * val / total
        d.rectangle((x, top, x + w, bot), fill=color)
        tw = d.textlength(name, font=font(19, 'bold'))
        if w >= tw + 12:
            put(d, x + (w - tw) / 2, top + 14, name, 19, WHITE, 'bold', x + w - 4)
            tw2 = d.textlength(tag, font=font(17, 'body'))
            if w >= tw2 + 12:
                put(d, x + (w - tw2) / 2, top + 46, tag, 17, WHITE, 'body', x + w - 4)
        else:
            put(d, x + 2, top + 22, name, 15, WHITE, 'bold', x + w - 1)
        x += w

    # 轴刻度
    ticks = [(0, '0'), (30, '30'), (90, '90'), (180, '180'), (300, '300')]
    for minute, label in ticks:
        tx = x0 + span * minute / total
        d.line((tx, bot, tx, bot + 8), fill=GREY, width=2)
        tw = d.textlength(label, font=font(18, 'number'))
        put(d, tx - tw / 2, bot + 14, label, 18, DIM, 'number', tx + tw / 2 + 1)

    put(d, 72, 410, '完结剧看单部总时长；连载剧看当月周更时长。90 含、180 不含。', 21, DIM, 'body', 1008)

    # 集数换算
    put(d, 72, 486, '按集数换算：先算分钟，再定集数', 26, INK, 'bold', 1008)

    rows = [
        ('单集 1 分钟', '179 集 = 179 分钟', '全额区', TEAL),
        ('单集 1 分钟', '300 集 = 300 分钟', '系数 0', RUST),
        ('单集 45 秒', '239 集 ≈ 179 分钟', '全额区', TEAL),
        ('单集 45 秒', '240 集 = 180 分钟', '越线', RUST),
    ]
    for i, (unit, calc, result, color) in enumerate(rows):
        ry = 538 + i * 74
        d.rounded_rectangle((72, ry, 1008, ry + 58), radius=10, fill=WHITE)
        put(d, 96, ry + 15, unit, 19, DIM, 'bold', 300)
        put(d, 270, ry + 13, calc, 23, INK, 'body', 760)
        put(d, 790, ry + 14, result, 21, color, 'bold', 990)

    # 两个提醒
    d.rounded_rectangle((72, 852, 504, 938), radius=12, fill=INK)
    put(d, 96, 868, '8 万是活动金额上限', 22, '#f0c588', 'bold', 492)
    put(d, 96, 902, '不是到手价，也不是采购价。', 18, '#bdb3a1', 'body', 492)

    d.rounded_rectangle((528, 852, 1008, 938), radius=12, fill=WHITE)
    put(d, 552, 868, '30—90、180—300 系数', 20, INK, 'bold', 996)
    put(d, 552, 902, '未公布，只能确认不是归零。', 18, DIM, 'body', 996)

    footer(d, 956, [
        '来源：腾讯新闻·短剧研究僧（2026-10-31）；短剧自习室转引漫剧有数（2026-10-30）。',
        '集数换算与边界判断为本号复算；官方公告原文未取得。',
    ])
    return im


def cover_063():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 860)

    put(d, 36, 78, '红果 AI 剧 3.0 · 11-01 生效', 20, GOLD, 'bold', 860)
    put(d, 32, 116, '90—179 分钟', 64, '#f6efe2', 'title', 620)
    put(d, 36, 200, '才拿全额', 40, GOLD, 'bold', 620)
    put(d, 36, 262, '300 分钟以上归零', 30, '#e07a5f', 'bold', 620)
    put(d, 36, 316, '先算总时长，再定集数', 22, '#bdb3a1', 'body', 620)

    d.line((650, 70, 650, 330), fill='#4a443b', width=2)
    items = ['完结剧 90—180', '连载剧 周更 <180', '1000 集模型失效', '8 万不是到手价']
    for i, item in enumerate(items):
        yy = 92 + i * 62
        d.line((684, yy + 14, 700, yy + 30), fill=RUST, width=4)
        d.line((700, yy + 30, 718, yy + 2), fill=RUST, width=4)
        put(d, 710, yy, item, 22, '#f0e8d8', 'bold', 894)

    im.save(OUT / '封面_063_90到179才全额_900x383.png')
    print('封面 OK', im.size)


if __name__ == '__main__':
    im = duration_zones()
    im.save(OUT / '063_图1_时长区间_1080.png')
    print('图1 OK', im.size)
    cover_063()
