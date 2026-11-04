#!/usr/bin/env python3
"""074《AI 短剧，真的赚钱吗》配图与封面。纯本地 Pillow，零扣费。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def funnel_dots():
    im, d = page('每 1000 部新剧，只有 13 部回本', '2026 上半年 22.19 万部 AI 短剧 / 投中网口径 / 本号折算', '01', 980)

    put(d, 72, 238, '按 1000 部新剧折算', 23, INK, 'bold', 1008)

    cols, rows, step, r = 40, 25, 21, 6
    x0, y0 = 120, 290
    for i in range(cols * rows):
        cx = x0 + (i % cols) * step
        cy = y0 + (i // cols) * step
        if i < 5:
            color = TEAL
        elif i < 13:
            color = RUST
        elif i < 54:
            color = GOLD
        else:
            color = '#d8cfc0'
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)

    legend = [
        (72, 820, TEAL, '破亿 5 部', '0.48%'),
        (300, 820, RUST, '回本 13 部', '1.3%'),
        (540, 820, GOLD, '破千万 54 部', '5.4%'),
        (790, 820, '#d8cfc0', '其余 946 部', ''),
    ]
    for lx, ly, color, name, pct in legend:
        d.rectangle((lx, ly + 4, lx + 14, ly + 18), fill=color)
        put(d, lx + 22, ly, name, 17, INK, 'bold', lx + 220)
        if pct:
            put(d, lx + 150, ly, pct, 15, DIM, 'body', lx + 230)

    footer(d, 872, [
        '来源：投中网 2026-11-04；破千万约 1.2 万部、回本 2900 部、破亿 1055 部。',
        '折算：5.4% / 1.3% / 0.48%；原文破千万写 5.8%，差异在分母。',
    ])
    return im


def cost_stack():
    im, d = page('平台与投流占成本 82.5%', 'AI 短剧全链路成本 / 投中网测算 / 2026-11-04', '02', 1000)

    put(d, 72, 238, '全链路成本', 23, INK, 'bold', 1008)

    x0, span, top, bot = 72, 936, 280, 372
    segs = [
        (0.825, RUST, '平台与投流 82.5%'),
        (0.140, TEAL, '制作等 14%'),
        (0.035, GREY, '3.5%'),
    ]
    x = x0
    for ratio, color, label in segs:
        w = span * ratio
        d.rectangle((x, top, x + w, bot), fill=color)
        if ratio > 0.08:
            tw = d.textlength(label, font=font(20, 'bold'))
            put(d, x + (w - tw) / 2, top + 24, label, 20, WHITE, 'bold', x + w - 4)
        x += w
    put(d, x - 60, bot + 10, '3.5%', 15, DIM, 'body', 1008)

    put(d, 72, 430, '制作成本内部', 20, INK, 'bold', 1008)
    stats = [
        ('token', '约 40%', RUST),
        ('人工调整', '约 45%', GOLD),
        ('IP', '10%—15%', TEAL),
    ]
    for i, (name, pct, color) in enumerate(stats):
        cx = 72 + i * 312
        d.rounded_rectangle((cx, 470, cx + 288, 620), radius=10, fill=WHITE)
        d.rounded_rectangle((cx, 470, cx + 288, 476), radius=3, fill=color)
        put(d, cx + 20, 492, name, 20, DIM, 'body', cx + 270)
        put(d, cx + 20, 530, pct, 38, color, 'bold', cx + 270)
        put(d, cx + 20, 586, '投中网测算', 15, GREY, 'body', cx + 270)

    d.rounded_rectangle((72, 664, 1008, 780), radius=10, fill='#efe6d6')
    put(d, 100, 682, '省下的是制作费，转成了投流费', 22, RUST, 'bold', 986)
    put(d, 100, 718, '2026 年行业投流日耗 1.5—1.7 亿元，流量成本同比 +100%；制作方从利润留存方变成费用经手方。', 17, DIM, 'body', 986)

    footer(d, 808, [
        '来源：投中网 2026-11-04；分项相加不足 100%，3.5% 为未列项。',
        '制作成本内部 40% / 45% / 10—15% 为投中网测算；未取得原始方法。',
    ])
    return im


def cover_074():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 540)

    put(d, 36, 78, 'AI 短剧 · 2026', 20, GOLD, 'bold', 540)
    put(d, 32, 106, '5% 盈利', 58, '#f6efe2', 'title', 540)
    put(d, 36, 190, '平台与投流', 28, GOLD, 'bold', 540)
    put(d, 36, 226, '占成本 82.5%', 28, '#e07a5f', 'bold', 540)
    put(d, 36, 280, '降本九成，不等于赚钱', 22, '#e8dfcf', 'bold', 540)
    put(d, 36, 328, '22.19 万部新剧，1.3% 回本', 17, '#bdb3a1', 'body', 540)

    d.line((560, 70, 560, 330), fill='#4a443b', width=2)

    put(d, 590, 76, '每 100 个制作方', 17, '#c9c0b0', 'bold', 864)
    put(d, 590, 100, '约 5 个可能盈利', 16, '#bdb3a1', 'body', 864)
    cols, rows, step, r = 10, 10, 17, 5
    for i in range(cols * rows):
        cx = 600 + (i % cols) * step
        cy = 132 + (i // cols) * step
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=TEAL if i < 5 else '#4a443b')

    put(d, 590, 310, '花旗估算，投中网转述', 14, '#bdb3a1', 'body', 864)
    put(d, 590, 334, '不是统计公报', 14, '#e07a5f', 'body', 864)

    im.save(OUT / '封面_074_AI短剧盈利_900x383.png')
    print('封面 074 OK', im.size)


if __name__ == '__main__':
    im = funnel_dots()
    im.save(OUT / '074_图1_漏斗_1080.png')
    print('图1 OK', im.size)
    im = cost_stack()
    im.save(OUT / '074_图2_成本_1080.png')
    print('图2 OK', im.size)
    cover_074()
