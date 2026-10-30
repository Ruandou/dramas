#!/usr/bin/env python3
"""054《3 亿播放，2 万还是 4 万美元：TikTok 出海单价要重算》配图与封面。纯本地 Pillow。"""
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def unit_price():
    im, d = page('同一笔 3 亿播放，两个单价', '四笔公开说法，折成每万次播放 / 单位：人民币', '01', 1000)

    x0, maxw, maxv = 300, 660, 100
    rows = [
        (98, '早期合作', '1 亿播放 / 14 万美元', RUST),
        (17, '后来合作', '5 亿播放 / 12 万美元', GOLD),
        (9.3, '2026-10 说法一', '3 亿播放 / 约 4 万美元', TEAL),
        (4.7, '2026-10 说法二', '3 亿播放 / 2 万美元截图', GREY),
    ]

    band_a = x0 + maxw * 5 / maxv
    band_b = x0 + maxw * 10 / maxv
    d.rectangle((band_a, 268, band_b, 668), fill='#e8e1d4')
    put(d, 380, 246, '国内 AI 漫剧 2026：5—10 元/万播（DataEye）', 17, TEAL, 'bold', 1000)

    for i in range(5):
        gx = x0 + maxw * i / 4
        d.line((gx, 268, gx, 668), fill=LINE, width=1)
        label = f'{int(maxv * i / 4)}'
        tw = d.textlength(label, font=font(16, 'number'))
        put(d, gx - tw / 2, 676, label, 16, DIM, 'number', gx + tw / 2 + 1)

    for i, (val, name, detail, color) in enumerate(rows):
        y = 300 + i * 96
        put(d, 72, y + 2, name, 21, INK, 'bold', 292)
        put(d, 72, y + 28, detail, 17, DIM, 'body', 294)
        w = maxw * val / maxv
        d.rectangle((x0, y, x0 + w, y + 56), fill=color)
        text = f'{val:g} 元'
        tw = d.textlength(text, font=font(25, 'bold'))
        if w > tw + 32:
            put(d, x0 + w - tw - 14, y + 12, text, 25, WHITE, 'bold', x0 + w - 6)
        else:
            put(d, x0 + w + 14, y + 12, text, 25, color, 'bold', x0 + w + 130)

    d.rounded_rectangle((72, 726, 1008, 830), radius=12, fill=INK)
    put(d, 102, 742, '3 亿档折 4.7—9.3 元，和国内 5—10 元基本接上。', 25, '#f0c588', 'bold', 986)
    put(d, 102, 786, '四笔账主体、时间、剧都不同，不能相加，也不能取平均。', 18, '#bdb3a1', 'body', 986)

    footer(d, 866, [
        '来源：剧短短 10-27（2 万美元截图、万播 30 美元→几美元）；钛媒体、第一财经 10-28（黄浩南）。',
        '汇率为 1 美元≈7 元粗算；2 万美元与 4 万美元不属同一部剧，仅并列展示。',
    ])
    return im


def supply():
    im, d = page('三个月，上新量差 200 倍以上', 'TikTok 短剧月上新量 / 对数刻度 / 黄浩南转述合作方数据', '02', 1030)

    def y_of(v):
        return 700 - 400 * (math.log10(v) - 2) / 4

    for v, label in [(100, '100'), (1_000, '1 千'), (10_000, '1 万'), (100_000, '10 万'), (1_000_000, '100 万')]:
        gy = y_of(v)
        d.line((150, gy, 990, gy), fill=LINE, width=1)
        tw = d.textlength(label, font=font(17, 'body'))
        put(d, 140 - tw, gy - 11, label, 17, DIM, 'body', 141)

    bars = [
        (1_000, '6 月', '<1,000', GREY),
        (5_000, '7 月', '<5,000', GREY),
        (100_000, '8 月', '10 万', GOLD),
        (200_000, '9 月', '约 20 万', RUST),
    ]
    for i, (v, month, label, color) in enumerate(bars):
        bx = 190 + i * 210
        top = y_of(v)
        d.rectangle((bx, top, bx + 140, 700), fill=color)
        tw = d.textlength(label, font=font(26, 'bold'))
        put(d, bx + 70 - tw / 2, top - 44, label, 26, color, 'bold', bx + 150)
        mw = d.textlength(month, font=font(21, 'bold'))
        put(d, bx + 70 - mw / 2, 714, month, 21, INK, 'bold', bx + 150)

    put(d, 72, 764, '6 月、7 月为「不足」口径，按上限画；数据为黄浩南转述 TikTok 合作方，非平台公告。', 17, DIM, 'body', 1008)

    d.rounded_rectangle((72, 806, 1008, 900), radius=12, fill=INK)
    put(d, 102, 820, '播放量不会跟着涨 200 倍。', 26, '#f0c588', 'bold', 986)
    put(d, 102, 862, '进来的人多了，系数再降，单部到手只能往下走。', 19, '#bdb3a1', 'body', 986)

    footer(d, 936, [
        '来源：钛媒体 2026-10-28 黄浩南访谈（6—9 月上新量）；剧短短 10-27（万播单价）。',
        '纵轴为对数刻度，柱高按数量级比较，不按线性比例。',
    ])
    return im


def cost():
    im, d = page('成本降了 60%，单价掉了一个数量级', '同一部 80 分钟 AI 漫剧 / 2026-10 公开访谈口径', '03', 1090)

    d.rounded_rectangle((72, 250, 510, 580), radius=12, fill=WHITE)
    put(d, 96, 270, '单部成本 · 80 分钟', 19, DIM, 'bold', 496)
    bx, bw = 176, 280
    d.rectangle((bx, 326, bx + bw, 370), fill='#c9bba6')
    put(d, 96, 336, '原来', 19, INK, 'bold', 168)
    put(d, bx + bw - 82, 336, '10 万元', 19, WHITE, 'bold', bx + bw - 6)
    d.rectangle((bx, 400, bx + bw * 0.4, 444), fill=TEAL)
    put(d, 96, 410, '现在', 19, INK, 'bold', 168)
    put(d, bx + bw * 0.4 + 14, 410, '4 万元', 19, TEAL, 'bold', 480)
    put(d, 96, 480, '-60% 成本', 30, RUST, 'title', 480)
    put(d, 96, 532, '1,000 元/分钟 → 400 元/分钟', 17, DIM, 'body', 490)

    d.rounded_rectangle((546, 250, 1008, 580), radius=12, fill=WHITE)
    put(d, 570, 270, '3 亿播放分成', 19, DIM, 'bold', 992)
    put(d, 570, 310, '旧模型', 18, DIM, 'body', 700)
    put(d, 570, 336, '90 万美元', 40, GREY, 'title', 900)
    put(d, 570, 386, '按 30 美元/万播，本号算术', 15, DIM, 'body', 900)
    put(d, 570, 424, '现在', 18, DIM, 'body', 700)
    put(d, 570, 448, '2—4 万美元', 40, RUST, 'title', 980)
    put(d, 570, 512, '差 22—45 倍', 24, GOLD, 'bold', 900)

    d.rounded_rectangle((72, 610, 1008, 810), radius=12, fill=WHITE)
    put(d, 96, 628, '钱花在哪：Token 占比从 20%—30% 升到 50%', 20, DIM, 'bold', 986)
    sx, sy, sh, sw = 96, 674, 62, 888
    segs = [(0.50, RUST, 'Token 50%'), (0.20, GOLD, '人工 20%'), (0.15, TEAL, '剧本 15%'), (0.15, GREY, '其他 15%')]
    cx = sx
    for ratio, color, label in segs:
        w = sw * ratio
        d.rectangle((cx, sy, cx + w, sy + sh), fill=color)
        tw = d.textlength(label, font=font(18, 'bold'))
        put(d, cx + (w - tw) / 2, sy + 20, label, 18, WHITE, 'bold', cx + w - 2)
        cx += w
    put(d, 96, 754, '原文口径：人工约 20%、剧本 10%—20%；堆叠图按剧本、其他各 15% 绘制。', 15, DIM, 'body', 990)
    put(d, 96, 780, 'Token 占比上升，意味着算力价格对成本的影响更大。', 15, DIM, 'body', 990)

    d.rounded_rectangle((72, 838, 1008, 930), radius=12, fill=INK)
    put(d, 102, 852, '降本 60%，补不上 22—45 倍的单价下跌。', 25, '#f0c588', 'bold', 986)
    put(d, 102, 894, '90 万美元是旧行情下的本号算术，不是平台结算。', 17, '#bdb3a1', 'body', 986)

    footer(d, 966, [
        '来源：钛媒体、第一财经 2026-10-28 黄浩南访谈（成本、Token 占比、分成）；剧短短 10-27（万播 30 美元旧行情）。',
        '成本与分成均为访谈口径，样本与统计方式未披露。',
    ])
    return im


def cover():
    base.TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, '#bdb3a1', right=440)
    put(d, 33, 58, '出海单价 · 2026-10-31', 18, '#f0c588', 'bold', 460)
    put(d, 28, 92, '3 亿播放', 82, '#efe6d6', 'title', 460)
    put(d, 34, 194, '2 万还是 4 万美元？', 26, '#e0705a', 'bold', 470)
    put(d, 34, 238, '万播单价跌到 5—9 元', 22, '#bdb3a1', 'bold', 470)
    put(d, 34, 290, '国内 5—10 元，出海不再溢价', 17, '#8f8576', 'body', 480)

    d.line((490, 62, 490, 324), fill='#4a443c', width=1)
    put(d, 520, 66, '四笔公开说法', 20, '#f0c588', 'bold', 880)
    rows = [
        ('1 亿播放', '14 万美元', '98 元', RUST),
        ('5 亿播放', '12 万美元', '17 元', GOLD),
        ('3 亿播放', '4 万美元', '9.3 元', TEAL),
        ('3 亿播放', '2 万美元', '4.7 元', GREY),
    ]
    y = 120
    for name, usd, rmb, color in rows:
        put(d, 520, y, name, 17, '#bdb3a1', 'body', 645)
        put(d, 650, y - 2, usd, 19, color, 'bold', 780)
        put(d, 790, y - 2, rmb, 19, '#efe6d6', 'bold', 880)
        y += 50
    put(d, 520, 306, '2 万美元为网传截图，未披露主体', 14, '#8f8576', 'body', 880)
    return im


def main():
    for maker, name in [(unit_price, '054_图1_单价_1080.png'),
                        (supply, '054_图2_上新量_1080.png'),
                        (cost, '054_图3_成本_1080.png')]:
        im = maker()
        base.validate_glyphs()
        base.save_png(im, OUT / name)
    im = cover()
    base.validate_glyphs()
    base.save_png(im, OUT / '封面_054_3亿播放_900x383.png')
    print('done')


if __name__ == '__main__':
    main()
