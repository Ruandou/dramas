#!/usr/bin/env python3
"""055《月流水近 1 亿美元，三季度亏 10.85 亿：短剧的钱分四层》配图与封面。纯本地 Pillow。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def hdash(d, x1, x2, y, fill=LINE, dash=8, gap=6):
    x = x1
    while x < x2:
        d.line((x, y, min(x + dash, x2), y), fill=fill, width=1)
        x += dash + gap


def vdash(d, x, y1, y2, fill=LINE, dash=8, gap=6):
    y = y1
    while y < y2:
        d.line((x, y, x, min(y + dash, y2)), fill=fill, width=1)
        y += dash + gap


def calibers():
    im, d = page('四个口径，四个数', '昆仑万维 2026 三季报 / 金额单位：亿元', '01', 1070)

    put(d, 72, 244, 'A · 流水年化 vs 全部营收', 20, DIM, 'bold', 1008)

    x0, maxw, maxv = 300, 600, 90
    rows = [
        ('流水年化', '1 亿美元/月，乘 12，按 1:7', 84.0, GOLD, '84.00 亿'),
        ('前三季营收', '89.37 亿元，全公司', 89.37, INK, '89.37 亿'),
    ]
    for i, (name, detail, val, color, label) in enumerate(rows):
        y = 286 + i * 92
        put(d, 72, y + 2, name, 21, INK, 'bold', 292)
        put(d, 72, y + 28, detail, 16, DIM, 'body', 294)
        w = maxw * val / maxv
        d.rectangle((x0, y, x0 + w, y + 46), fill=color)
        tw = d.textlength(label, font=font(23, 'bold'))
        put(d, x0 + w - tw - 12, y + 10, label, 23, WHITE, 'bold', x0 + w - 4)

    ex1, ex2 = x0 + maxw * 84 / maxv, x0 + maxw * 89.37 / maxv
    d.line((ex1, 448, ex2, 448), fill=RUST, width=2)
    d.line((ex1, 440, ex1, 456), fill=RUST, width=2)
    d.line((ex2, 440, ex2, 456), fill=RUST, width=2)
    put(d, 650, 452, '差 5.37 亿元（6.0%）', 18, RUST, 'bold', 1008)
    put(d, 72, 478, '两个数几乎一样大：一个是流水年化，一个是已确认收入。', 18, DIM, 'body', 1008)

    put(d, 72, 536, 'B · 利润在零线下方', 20, DIM, 'bold', 1008)

    zero = 620
    d.line((zero, 576, zero, 752), fill=INK, width=2)
    negs = [
        ('扣非 · 前三季', -15.46, 600, '-15.46 亿'),
        ('Q3 归母 · 推算', -10.85, 690, '-10.85 亿'),
    ]
    for name, val, y, label in negs:
        put(d, 72, y + 8, name, 20, INK, 'bold', 310)
        w = 300 * abs(val) / 16
        left = zero - w
        d.rectangle((left, y, zero, y + 44), fill=RUST if 'Q3' in name else GREY)
        put(d, left + 12, y + 9, label, 22, WHITE, 'bold', zero - 4)

    d.line((zero, 780, zero + 6, 780), fill=TEAL, width=4)
    put(d, 634, 768, '前三季归母 +260.94 万元，贴着零线', 17, TEAL, 'body', 1008)
    put(d, 72, 806, 'Q3 归母、扣非为前三季减上半年推算；扣非 -15.46 亿元是前三季累计。', 17, DIM, 'body', 1008)

    d.rounded_rectangle((72, 846, 1008, 954), radius=12, fill=INK)
    put(d, 102, 862, '流水和收入同量级，利润在零线下方。', 25, '#f0c588', 'bold', 986)
    put(d, 102, 904, '四个数不同期、不同范围，不能相减，也不能互相替代。', 18, '#bdb3a1', 'body', 986)

    footer(d, 980, [
        '来源：昆仑万维 2026 三季报、半年报；每经、东方财富、新浪财经 10-29，紫金 10-30。',
        '流水年化仅作量级对照，不是收入预测；Q3 单季为推算值。',
    ])
    return im


def ramp():
    im, d = page('九个月，单月流水从 4,800 万到近 1 亿', 'AI 短剧平台业务 / 单位：万美元 / 一季度为「超 4,800 万」下限', '02', 1020)

    base_y, max_h, maxv = 720, 420, 11_000
    def y_of(v):
        return base_y - max_h * v / maxv

    for v, label in [(0, '0'), (5_000, '5,000'), (10_000, '10,000')]:
        gy = y_of(v)
        d.line((210, gy, 1000, gy), fill=LINE, width=1)
        tw = d.textlength(label, font=font(16, 'number'))
        put(d, 200 - tw, gy - 10, label, 16, DIM, 'number', 201)

    hdash(d, 210, 1000, y_of(10_000), fill=GREY)
    put(d, 916, y_of(10_000) + 10, '1 亿美元', 16, GREY, 'body', 1008)

    bars = [
        (4_800, '一季度', '4,800 万+', GREY),
        (6_500, '6 月底', '6,500 万+', GOLD),
        (10_000, '9 月', '近 1 亿美元', RUST),
    ]
    for i, (v, month, label, color) in enumerate(bars):
        bx = 210 + i * 270
        top = y_of(v)
        d.rectangle((bx, top, bx + 150, base_y), fill=color)
        tw = d.textlength(label, font=font(22, 'bold'))
        put(d, bx + 75 - tw / 2, top - 40, label, 22, color, 'bold', bx + 160)
        mw = d.textlength(month, font=font(20, 'bold'))
        put(d, bx + 75 - mw / 2, base_y + 16, month, 20, INK, 'bold', bx + 160)

    put(d, 388, 648, '+35%', 19, RUST, 'bold', 460)
    put(d, 658, 648, '+54%', 19, RUST, 'bold', 730)

    put(d, 72, 774, '一季度为下限口径，柱高按 4,800 万画；9 月为「近 1 亿」。', 17, DIM, 'body', 1008)

    d.rounded_rectangle((72, 806, 1008, 910), radius=12, fill=INK)
    put(d, 102, 822, '九个月翻了一倍，流水是真增长。', 25, '#f0c588', 'bold', 986)
    put(d, 102, 864, '但流水涨，不等于收入、毛利、净利同比例涨。', 18, '#bdb3a1', 'body', 986)

    footer(d, 936, [
        '来源：昆仑万维 2026 年一季报、半年报、三季报（AI 短剧平台业务单月流水）。',
        '单月流水为平台业务合计口径，非公司确认收入，也不是制作方分成。',
    ])
    return im


def waterfall():
    im, d = page('上半年每收 100 元，62 元花在销售上', '营收 → 毛利 → 扣掉销售费用 / 单位：亿元 / 2026 上半年', '03', 1080)

    base_y, maxv, max_h = 760, 55, 500
    def y_of(v):
        return base_y - max_h * v / maxv

    d.line((140, base_y, 1000, base_y), fill=INK, width=2)

    x1, x2, x3, x4, bw = 160, 380, 600, 820, 150
    d.rectangle((x1, y_of(53.59), x1 + bw, base_y), fill=INK)
    d.rectangle((x2, y_of(53.59), x2 + bw, y_of(35.15)), fill=GREY)
    d.rectangle((x3, y_of(35.15), x3 + bw, y_of(1.76)), fill=RUST)
    d.rectangle((x4, y_of(1.76), x4 + bw, base_y), fill=TEAL)

    hdash(d, x1 + bw, x2, y_of(53.59), fill=GREY)
    hdash(d, x2 + bw, x3, y_of(35.15), fill=GREY)
    hdash(d, x3 + bw, x4, y_of(1.76), fill=GREY)

    put(d, x1, y_of(53.59) - 44, '53.59', 30, INK, 'title', x1 + 150)
    put(d, x1 + 12, y_of(35.15) + 10, '毛利 35.15', 19, WHITE, 'bold', x1 + bw - 4)

    put(d, x2 + 12, y_of(53.59) + 26, '-18.44', 24, WHITE, 'bold', x2 + bw - 4)

    put(d, x3 + 12, y_of(35.15) + 30, '-33.39', 24, WHITE, 'bold', x3 + bw - 4)
    put(d, x3 + 12, y_of(35.15) + 70, '占毛利 95.0%', 18, '#f3eee4', 'bold', x3 + bw - 4)

    put(d, x4, y_of(1.76) - 40, '1.76', 28, TEAL, 'title', x4 + bw)

    for x, name in [(x1, '营收'), (x2, '营业成本'), (x3, '销售费用'), (x4, '剩余')]:
        put(d, x, base_y + 16, name, 20, INK, 'bold', x + bw)

    put(d, 72, 814, '毛利率 65.59%；销售费用率 62.31%；剩余 1.76 亿元=毛利 - 销售费用。', 19, INK, 'bold', 1008)

    d.rounded_rectangle((72, 858, 1008, 964), radius=12, fill=INK)
    put(d, 102, 874, '毛利减销售费用，只剩 1.76 亿元。', 25, '#f0c588', 'bold', 986)
    put(d, 102, 916, '管理费用、研发费用还没算；上半年扣非亏 4.58 亿元。', 18, '#bdb3a1', 'body', 986)

    footer(d, 988, [
        '来源：昆仑万维 2026 年半年报（营收 53.59 亿、营业成本 18.44 亿、销售费用 33.39 亿）。',
        '毛利、毛利率、销售费用率为本号按披露数直接相减、相除；未含管理、研发、财务费用。',
    ])
    return im


def cover():
    base.TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, '#bdb3a1', right=470)
    put(d, 33, 58, '三季报拆账 · 2026-10-31', 18, '#f0c588', 'bold', 480)
    put(d, 28, 92, '月流水', 28, '#efe6d6', 'bold', 470)
    put(d, 26, 126, '近 1 亿美元', 58, '#efe6d6', 'title', 480)
    put(d, 34, 214, '三季度亏 10.85 亿', 32, '#e0705a', 'bold', 480)
    put(d, 34, 260, '四个口径，四个数', 20, '#bdb3a1', 'bold', 480)
    put(d, 34, 296, '短剧的钱分四层', 18, '#8f8576', 'body', 480)

    d.line((494, 62, 494, 324), fill='#4a443c', width=1)
    put(d, 522, 62, '一份财报，四层账', 19, '#f0c588', 'bold', 880)

    rows = [
        ('流水', '1 亿美元/月', '09', '#b9853d'),
        ('收入', '89.37 亿', '前三季', '#efe6d6'),
        ('毛利率', '74.41%', 'Q3', '#efe6d6'),
        ('净利', '-10.85 亿', 'Q3', '#e0705a'),
    ]
    y = 112
    for name, value, period, color in rows:
        d.rectangle((522, y + 4, 526, y + 24), fill=color)
        put(d, 536, y, name, 17, '#bdb3a1', 'body', 626)
        put(d, 640, y - 2, value, 20, color, 'bold', 800)
        put(d, 812, y + 2, period, 13, '#8f8576', 'body', 880)
        y += 50

    put(d, 522, 318, '净利为 Q3 归母，前三季减上半年推算', 13, '#8f8576', 'body', 880)
    return im


def main():
    for maker, name in [(calibers, '055_图1_四个口径_1080.png'),
                        (ramp, '055_图2_流水爬坡_1080.png'),
                        (waterfall, '055_图3_毛利去哪了_1080.png')]:
        im = maker()
        base.validate_glyphs()
        base.save_png(im, OUT / name)
    im = cover()
    base.validate_glyphs()
    base.save_png(im, OUT / '封面_055_流水与亏损_900x383.png')
    print('done')


if __name__ == '__main__':
    main()
