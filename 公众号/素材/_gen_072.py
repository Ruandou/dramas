#!/usr/bin/env python3
"""072《Runway 可灵 4.0 折扣》配图与封面。纯本地 Pillow，零扣费。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def dashed_rect(d, box, color=LINE, width=2, dash=10, gap=8):
    x0, y0, x1, y1 = box
    for x in range(x0, x1, dash + gap):
        d.line((x, y0, min(x + dash, x1), y0), fill=color, width=width)
        d.line((x, y1, min(x + dash, x1), y1), fill=color, width=width)
    for y in range(y0, y1, dash + gap):
        d.line((x0, y, x0, min(y + dash, y1)), fill=color, width=width)
        d.line((x1, y, x1, min(y + dash, y1)), fill=color, width=width)


def two_pools():
    im, d = page('两个通道，两套价', 'Runway × Kling 4.0 / 2026-11-03 / 官方定价页 + Dev 文档', '01', 1000)

    d.rounded_rectangle((72, 238, 540, 700), radius=12, fill=WHITE)
    put(d, 96, 260, '消费端', 21, RUST, 'bold', 520)
    put(d, 96, 292, 'Standard / Pro / Max', 18, DIM, 'body', 520)
    put(d, 96, 342, '5 秒 1080p', 22, INK, 'bold', 520)
    put(d, 96, 386, '118', 34, GREY, 'number', 300)
    put(d, 186, 390, '→', 28, GREY, 'body', 300)
    put(d, 226, 372, '89', 54, INK, 'number', 360)
    put(d, 330, 396, 'credits', 20, DIM, 'body', 520)
    d.line((96, 452, 516, 452), fill=LINE, width=2)
    put(d, 96, 474, '少收 25%，截止 11-30', 20, RUST, 'bold', 520)
    paragraph(d, 96, 514, '积分来自订阅套餐，和 Dev API 不互通；其它时长与分辨率未公开。', 420, 18, DIM, 29)

    d.rounded_rectangle((568, 238, 1008, 700), radius=12, fill=WHITE)
    put(d, 592, 260, 'Dev API', 21, TEAL, 'bold', 990)
    put(d, 592, 292, 'kling_4', 18, DIM, 'body', 990)

    rows = [
        ('720p 无输入', '15.7', '12.56', 344),
        ('1080p 无输入', '23.5', '18.8', 410),
        ('720p 带输入', '9.4', '7.52', 476),
        ('1080p 带输入', '14.1', '11.28', 542),
    ]
    put(d, 592, 326, 'credits / 秒', 16, GREY, 'body', 990)
    for name, before, after, y in rows:
        put(d, 592, y, name, 18, DIM, 'body', 760)
        put(d, 780, y, before, 20, GREY, 'number', 850)
        put(d, 850, y, '→', 18, GREY, 'body', 880)
        put(d, 884, y, after, 22, INK, 'bold', 990)
    put(d, 592, 606, '八折，截止 11-30 UTC；1 credit = $0.01', 18, TEAL, 'bold', 990)
    paragraph(d, 592, 640, '计费先按原价向上取整，再八折，再向上取整。', 390, 17, DIM, 27)

    d.rounded_rectangle((72, 740, 1008, 820), radius=10, fill=INK)
    put(d, 100, 756, '5 秒 720p、无输入：64 credits（$0.64）', 23, '#f0c588', 'bold', 986)
    put(d, 100, 790, '这是折扣价；12-01 UTC 起按原价 79 credits（$0.79）。', 17, '#bdb3a1', 'body', 986)

    footer(d, 848, [
        '来源：runway.com/pricing（抓取 2026-11-03）、dev.runway.com/pricing、docs.dev.runwayml.com/guides/pricing/。',
        'App 与 API 积分不互通；App 积分按订阅套餐计，不能按 $0.01 折算。美元金额为本号按官方取整规则复算。',
    ])
    return im


def reference_billing():
    im, d = page('参考视频的双计账单', '5 秒 720p 输出 / 输入越长，第二笔越大 / 2026-11-03', '02', 940)

    put(d, 72, 238, '输出收一遍，输入与输出较长者再收一遍', 23, INK, 'bold', 1008)

    bars = [
        ('无参考', 64, '$0.64', RUST),
        ('带 5 秒参考', 76, '$0.76', GOLD),
        ('带 30 秒参考', 264, '$2.64', INK),
    ]
    max_w = 560
    for i, (name, credits, usd, color) in enumerate(bars):
        y = 310 + i * 120
        put(d, 72, y + 24, name, 21, INK, 'bold', 270)
        w = max_w * credits / 300
        d.rounded_rectangle((280, y, 280 + w, y + 62), radius=8, fill=color)
        put(d, 292 + w, y + 6, f'{credits} credits', 22, color, 'bold', 1000)
        put(d, 292 + w, y + 38, usd, 17, DIM, 'body', 1000)

    d.rounded_rectangle((72, 700, 1008, 800), radius=10, fill='#efe6d6')
    put(d, 100, 718, '1080p 更贵：5 秒输出带 30 秒参考 = 396 credits（$3.96）', 20, RUST, 'bold', 986)
    put(d, 100, 754, '参考剪到和输出等长，再提交；输入合计上限 30 秒，每个片段最多计 30 秒。', 17, DIM, 'body', 986)

    footer(d, 828, [
        '来源：docs.dev.runwayml.com/guides/pricing/（抓取 2026-11-03）；kling_4 折扣价 7.52（720p）/ 11.28（1080p）credits/秒。',
        '计费规则：输出时长 + 输入与输出中较长者；先按原价取整、再八折、再取整。金额为本号复算。',
    ])
    return im


def cover_072():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 540)

    put(d, 36, 78, '可灵 4.0 · Runway', 20, GOLD, 'bold', 540)
    put(d, 32, 108, '八折', 66, '#f6efe2', 'title', 540)
    put(d, 36, 194, '单镜 $0.64 起', 36, GOLD, 'bold', 540)
    put(d, 36, 244, '11-30 截止', 32, '#e07a5f', 'bold', 540)
    put(d, 36, 292, '不是可灵官方降价', 24, '#e8dfcf', 'bold', 540)
    put(d, 36, 332, 'App 与 Dev API 是两个积分池', 17, '#bdb3a1', 'body', 540)

    d.line((560, 70, 560, 330), fill='#4a443b', width=2)

    put(d, 590, 76, '两个通道', 19, '#c9c0b0', 'bold', 864)
    put(d, 590, 110, 'App', 18, '#bdb3a1', 'body', 700)
    put(d, 650, 108, '118 → 89', 21, '#e8dfcf', 'bold', 864)
    put(d, 590, 142, 'credits / 5s 1080p', 15, '#bdb3a1', 'body', 864)

    put(d, 590, 182, 'Dev API', 18, '#bdb3a1', 'body', 700)
    put(d, 690, 180, '64 credits', 21, '#e8dfcf', 'bold', 864)
    put(d, 590, 214, '5s 720p 无输入 = $0.64', 15, '#bdb3a1', 'body', 864)

    dashed_rect(d, (590, 252, 864, 294), '#e07a5f', 2, 8, 6)
    put(d, 604, 262, '12-01 恢复原价', 18, '#e07a5f', 'bold', 860)

    put(d, 590, 312, '带 30s 参考：5s 镜头 264 credits', 15, '#e8dfcf', 'body', 864)
    put(d, 590, 336, '参考越长，第二笔越大', 15, '#e07a5f', 'body', 864)

    im.save(OUT / '封面_072_Runway八折_900x383.png')
    print('封面 072 OK', im.size)


if __name__ == '__main__':
    im = two_pools()
    im.save(OUT / '072_图1_两个通道_1080.png')
    print('图1 OK', im.size)
    im = reference_billing()
    im.save(OUT / '072_图2_参考计费_1080.png')
    print('图2 OK', im.size)
    cover_072()
