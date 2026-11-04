#!/usr/bin/env python3
"""069《红果超豆包，短剧三条货架》配图与封面。纯本地 Pillow，零扣费。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def bar_row(d, y, label, value, maxv, color, unit='', note='', h=38, x0=300, x1=1000, shown=None):
    put(d, 72, y + 2, label, 21, INK, 'bold', x0 - 12)
    w = (x1 - x0) * value / maxv
    d.rounded_rectangle((x0, y, x0 + w, y + h), radius=5, fill=color)
    txt = shown or f'{value:g}{unit}'
    tw = d.textlength(txt, font=font(21, 'bold'))
    if w > tw + 24:
        put(d, x0 + w - tw - 14, y + 7, txt, 21, WHITE, 'bold', x0 + w - 8)
    else:
        put(d, x0 + w + 12, y + 7, txt, 21, color, 'bold', x1 + 8)
    if note:
        put(d, x0 + 12, y + 9, note, 17, WHITE, 'body', x0 + w - 8)


def duration_bars():
    im, d = page('短剧同比多出 133.29 亿小时', '2026-09 移动互联网细分行业总使用时长净增量 / 同比 / QuestMobile', '01', 1040)

    put(d, 72, 238, '净增长：短剧第一，短视频第二', 24, INK, 'bold', 1008)
    rows = [
        ('短剧视频', 133.29, RUST),
        ('短视频', 57.17, TEAL),
        ('AIGC', 9.78, GOLD),
    ]
    y = 288
    for label, v, color in rows:
        bar_row(d, y, label, v, 140, color, ' 亿小时')
        y += 72

    d.line((72, 520, 1008, 520), fill=LINE, width=2)
    put(d, 72, 548, '净减少：在线视频跌得最多', 24, INK, 'bold', 1008)
    neg = [
        ('在线视频', 13.80),
        ('综合资讯', 13.07),
        ('搜索引擎', 9.84),
    ]
    y = 598
    for label, v in neg:
        bar_row(d, y, label, v, 20, GREY, ' 亿小时', shown=f'{v:.2f} 亿小时')
        y += 72

    d.rounded_rectangle((72, 820, 1008, 906), radius=12, fill=INK)
    put(d, 100, 838, '短剧视频净增 ≈ 在线视频净减的 9.7 倍', 25, '#f0c588', 'bold', 986)
    put(d, 100, 876, '净增量 = 2026-09 月总使用时长 - 2025-09 月总使用时长；TOP2 贡献率 111.5%', 18, '#bdb3a1', 'body', 986)

    footer(d, 928, [
        '来源：QuestMobile《2026 中国移动互联网秋季大报告》（2026-11-03）图表「细分行业总使用时长净增量」。',
        '9.7 倍为本号按 133.29 ÷ 13.80 复算，算术对照，不是结算数据。',
    ])
    return im


def shelf_cards():
    im, d = page('三条货架：红果、绿泡泡、漫剧', '2026-09 月活 / QuestMobile 秋季报告 / 单位：万', '02', 1120)

    put(d, 72, 238, '主货架：三种入口，不是一条线', 24, INK, 'bold', 1008)

    cards = [
        ('红果免费短剧', 'App', '42,969', '+81.8%', RUST),
        ('绿泡泡短剧', '微信小程序', '15,635', '+12,495.6%', TEAL),
        ('红果免费漫剧', 'App', '7,883', '+26,870.2%', GOLD),
    ]
    cw, gap = 296, 24
    for i, (name, kind, value, growth, color) in enumerate(cards):
        cx = 72 + i * (cw + gap)
        d.rounded_rectangle((cx, 282, cx + cw, 486), radius=12, fill=WHITE)
        d.rounded_rectangle((cx, 282, cx + 6, 486), radius=3, fill=color)
        put(d, cx + 22, 302, name, 22, INK, 'bold', cx + cw - 14)
        put(d, cx + 22, 342, kind, 17, DIM, 'body', cx + cw - 14)
        put(d, cx + 22, 382, value, 36, color, 'number', cx + cw - 14)
        put(d, cx + 22, 434, '万 MAU', 16, DIM, 'body', cx + cw - 14)
        put(d, cx + 22, 458, growth, 16, color, 'bold', cx + cw - 14)

    put(d, 72, 512, '第二梯队：河马跌四成，喜番翻倍', 24, INK, 'bold', 1008)
    rows = [
        ('河马剧场', 3080, '-40.3%', RUST),
        ('火龙漫剧', 1113, '', GOLD),
        ('喜番免费短剧', 834, '+123.9%', TEAL),
        ('繁花剧场', 340, '-2.4%', GREY),
        ('星芽免费短剧', 45, '-76.8%', GREY),
    ]
    x0, x1, maxv = 320, 760, 3200
    y = 554
    for label, v, growth, color in rows:
        put(d, 72, y + 2, label, 20, INK, 'bold', x0 - 12)
        w = (x1 - x0) * v / maxv
        d.rounded_rectangle((x0, y, x0 + w, y + 34), radius=5, fill=color)
        put(d, x1 + 12, y + 4, f'{v:,} 万', 19, INK, 'bold', 1000)
        if growth:
            put(d, x1 + 112, y + 6, growth, 17, color, 'bold', 1008)
        y += 56

    d.rounded_rectangle((72, 846, 1008, 938), radius=12, fill=INK)
    put(d, 100, 862, '重合度：红果 88.5% 来自抖音，漫剧 85.1%，喜番 75.8% 来自快手', 20, '#f0c588', 'bold', 986)
    put(d, 100, 900, '三条货架的入口不同，MAU 不能直接相加，报价也不能互相套用。', 18, '#bdb3a1', 'body', 986)

    footer(d, 958, [
        '来源：QuestMobile《2026 中国移动互联网秋季大报告》（2026-11-03）「短剧视频各类应用月活 TOP10」及重合用户图。',
        '绿泡泡 2026-09 底上线、漫剧 2025-11 上线（北京日报口径），增速为低基数；红果去重总用户 4.30 亿与 App MAU 42,969 万口径不同。',
    ])
    return im


def cover_069():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 860)

    put(d, 36, 78, 'QuestMobile · 2026-09', 20, GOLD, 'bold', 540)
    put(d, 32, 112, '4.30 亿', 62, '#f6efe2', 'title', 540)
    put(d, 36, 194, '红果超过豆包', 36, GOLD, 'bold', 540)
    put(d, 36, 246, '短剧拆成三条货架', 30, '#f6efe2', 'bold', 540)
    put(d, 36, 308, '红果短剧 · 绿泡泡 · 漫剧', 20, '#e07a5f', 'body', 540)

    d.line((560, 70, 560, 330), fill='#4a443b', width=2)

    put(d, 590, 86, '2026-09 月活', 18, '#c9c0b0', 'bold', 864)
    items = [
        ('红果短剧', '4.2969 亿', GOLD),
        ('绿泡泡短剧', '1.5635 亿', TEAL),
        ('红果漫剧', '7,883 万', RUST),
    ]
    for i, (name, value, color) in enumerate(items):
        yy = 136 + i * 62
        d.rounded_rectangle((590, yy, 598, yy + 40), radius=2, fill=color)
        put(d, 612, yy - 2, name, 18, '#bdb3a1', 'body', 860)
        put(d, 612, yy + 20, value, 23, '#f0e8d8', 'bold', 860)

    put(d, 590, 330, '别用一条货架的价，谈三条', 17, '#e07a5f', 'body', 864)

    im.save(OUT / '封面_069_三条货架_900x383.png')
    print('封面 069 OK', im.size)


if __name__ == '__main__':
    im = duration_bars()
    im.save(OUT / '069_图1_时长净增_1080.png')
    print('图1 OK', im.size)
    im = shelf_cards()
    im.save(OUT / '069_图2_三条货架_1080.png')
    print('图2 OK', im.size)
    cover_069()
