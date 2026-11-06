#!/usr/bin/env python3
"""077《中国微短剧何以全球“圈粉”》配图与封面。纯本地 Pillow，零扣费。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def market_split():
    im, d = page('180 亿是全球，海外只有 40 亿', '2025 年微短剧市场规模 / 人民日报 2026-11-04 第 15 版', '01', 980)

    put(d, 72, 246, '全球 180 亿美元', 22, INK, 'bold', 1008)
    x0, x1, y = 72, 1008, 280
    span = x1 - x0
    china_w = span * 140 / 180
    d.rectangle((x0, y, x0 + china_w, y + 52), fill=RUST)
    d.rectangle((x0 + china_w, y, x1, y + 52), fill=TEAL)
    put(d, x0 + 12, y + 14, '中国 140 亿美元', 20, WHITE, 'bold', x0 + china_w - 8)
    put(d, x0 + china_w + 12, y + 14, '海外 40', 20, WHITE, 'bold', x1 - 8)
    put(d, 72, 344, '中国占 77.78%', 18, DIM, 'body', 400)
    put(d, 760, 344, '海外约 40 亿美元', 18, DIM, 'body', 1008)

    put(d, 72, 402, '海外 40 亿美元里，谁在赚？', 22, INK, 'bold', 1008)
    y = 438
    w36 = span * 0.9
    d.rectangle((x0, y, x0 + w36, y + 52), fill=GOLD)
    d.rectangle((x0 + w36, y, x1, y + 52), fill=GREY)
    put(d, x0 + 12, y + 14, '中国企业约 36 亿美元（90%）', 20, WHITE, 'bold', x0 + w36 - 8)
    put(d, x0 + w36 + 24, y + 14, '4', 20, WHITE, 'bold', x1 - 4)
    put(d, 72, 502, '非中国企业约 4 亿美元（10%）', 18, DIM, 'body', 600)

    cards = [
        (72, '全球', '180 亿美元', '2025 年'),
        (390, '中国', '140 亿美元', '占 77.78%'),
        (708, '海外', '40 亿美元', '全球减中国'),
    ]
    y = 552
    for cx, label, value, note in cards:
        d.rounded_rectangle((cx, y, cx + 300, y + 150), radius=12, fill=WHITE)
        put(d, cx + 22, y + 16, label, 18, DIM, 'bold', cx + 288)
        put(d, cx + 22, y + 48, value, 38, RUST if label == '海外' else INK, 'bold', cx + 288)
        put(d, cx + 22, y + 108, note, 16, DIM, 'body', cx + 288)

    d.rounded_rectangle((72, 744, 1008, 850), radius=12, fill=INK)
    put(d, 102, 762, '海外 40 亿 → 中国企业约 36 亿 → 非中国企业约 4 亿', 21, '#f0c588', 'bold', 986)
    put(d, 102, 804, '按报告口径粗算；不是海外应用收入 23.29 亿美元。', 17, '#bdb3a1', 'body', 986)

    footer(d, 884, [
        '来源：人民日报 2026-11-04 第 15 版整版及同版评论。',
        '180/140/77.78%/90% 为报告口径；40/36/4 为本号复算（C）。',
    ])
    return im


def shoot_cadence():
    im, d = page('8 天，36 集，108 分钟', '《贝家花园的秘密》/ 人民日报 2026-11-04；集数取北京日报上线稿', '02', 960)

    x0, y0, cell, gap = 72, 252, 62, 8
    colors = [RUST, TEAL, GOLD]
    for i in range(36):
        row, col = divmod(i, 6)
        x = x0 + col * (cell + gap)
        y = y0 + row * (cell + gap)
        d.rounded_rectangle((x, y, x + cell, y + cell), radius=6, fill=colors[row % 3])
        put(d, x + cell / 2 - 8, y + cell / 2 - 10, str(i + 1), 15, WHITE, 'number', x + cell - 2)

    put(d, 540, 258, '36 集', 34, INK, 'bold', 1008)
    put(d, 540, 304, '× 3 分钟', 24, DIM, 'body', 1008)
    put(d, 540, 350, '= 108 分钟', 40, RUST, 'bold', 1008)
    put(d, 540, 420, '8 天拍完', 28, INK, 'bold', 1008)
    put(d, 540, 466, '日均 13.5 分钟', 22, TEAL, 'bold', 1008)
    put(d, 540, 502, '日均 4.5 集', 22, TEAL, 'bold', 1008)

    put(d, 72, 690, '8 天拍摄节奏', 20, INK, 'bold', 1008)
    for i in range(8):
        x = 72 + i * 117
        d.rounded_rectangle((x, 722, x + 105, 784), radius=8, fill=TEAL if i % 2 == 0 else RUST)
        put(d, x + 38, 740, f'D{i + 1}', 18, WHITE, 'bold', x + 100)

    put(d, 72, 806, '按 36 集 × 3 分钟复算；8 天为演员文森特·马蒂尔口径，集数取北京日报上线稿。', 18, DIM, 'body', 1008)

    footer(d, 840, [
        '来源：人民日报 2026-11-04；北京日报 2025-09-26（36 集×3 分钟）。',
        '108 分钟、13.5 分钟/天、4.5 集/天为本号复算（C），不是片方公布的制作周期表。',
    ])
    return im


def cover_077():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 540)

    put(d, 36, 74, '人民日报整版 · 短剧出海', 18, GOLD, 'bold', 540)
    put(d, 32, 106, '中国微短剧', 26, '#e8dfcf', 'bold', 540)
    put(d, 32, 142, '何以全球“圈粉”', 40, '#f6efe2', 'title', 540)
    put(d, 36, 210, '海外 40 亿美元', 26, '#e07a5f', 'bold', 540)
    put(d, 36, 250, '约九成是中国企业', 18, '#bdb3a1', 'body', 540)
    put(d, 36, 292, '8 天拍 36 集 / 108 分钟', 16, '#bdb3a1', 'body', 540)
    put(d, 36, 330, '先做一集本地化试播', 14, '#bdb3a1', 'body', 540)

    d.line((520, 70, 520, 330), fill='#4a443b', width=2)

    put(d, 560, 70, '2025 全球盘子', 15, GOLD, 'bold', 864)
    rows = [
        ('全球 180', 180, 260, GREY),
        ('中国 140', 140, 202, RUST),
        ('海外 40', 40, 58, TEAL),
    ]
    y = 104
    for label, value, width, color in rows:
        put(d, 560, y, label, 13, '#c9c0b0', 'body', 700)
        d.rectangle((560, y + 22, 560 + width, y + 38), fill=color)
        put(d, 560 + width + 8, y + 20, str(value), 13, '#f6efe2', 'bold', 864)
        y += 62

    put(d, 560, 300, '按报告口径粗算', 12, '#8f8576', 'body', 864)

    im.save(OUT / '封面_077_短剧出海_900x383.png')
    print('封面 077 OK', im.size)


if __name__ == '__main__':
    im = market_split()
    im.save(OUT / '077_图1_市场_1080.png')
    print('图1 OK', im.size)
    im = shoot_cadence()
    im.save(OUT / '077_图2_产能_1080.png')
    print('图2 OK', im.size)
    cover_077()
