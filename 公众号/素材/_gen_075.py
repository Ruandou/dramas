#!/usr/bin/env python3
"""075《NBCUniversal 投 8000 万：印度短剧要开美国》配图与封面。纯本地 Pillow，零扣费。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def deal_card():
    im, d = page('8000 万美元，换的是下一站', 'EloElo / Story TV C 轮 / Variety·TechCrunch 2026-11-03', '01', 940)

    put(d, 72, 248, '本轮 C 轮融资', 22, DIM, 'bold', 500)
    put(d, 64, 280, '$80M', 104, RUST, 'number', 520)
    put(d, 72, 408, 'Hornbill Capital 与 NBCUniversal 联合领投', 19, DIM, 'body', 520)

    put(d, 560, 250, '累计融资', 20, DIM, 'body', 1008)
    put(d, 560, 280, '$1.3 亿', 46, INK, 'bold', 1008)
    put(d, 800, 250, '估值', 20, DIM, 'body', 1008)
    put(d, 800, 282, '$5 亿', 46, INK, 'bold', 1008)

    put(d, 560, 376, '本轮占比（本号按 5 亿估值换算）', 19, DIM, 'body', 1008)
    put(d, 560, 410, '投后约 16%', 34, TEAL, 'bold', 800)
    put(d, 800, 420, '投前约 13.8%', 24, DIM, 'bold', 1008)
    put(d, 560, 466, '原文未说明投前/投后，两个数都列', 17, GREY, 'body', 1008)

    d.line((72, 552, 1008, 552), fill=LINE, width=2)
    put(d, 72, 580, '钱的三个去向（分配比例未披露）', 23, INK, 'bold', 1008)

    chips = [
        ('本地语原创', '六种语言，5,000+ 部在架'),
        ('海外开服', 'NBCU 点名含美国市场'),
        ('Dolphin AI', '内部创作套件，计划对外'),
    ]
    for i, (name, note) in enumerate(chips):
        cx = 72 + i * 312
        d.rounded_rectangle((cx, 630, cx + 288, 748), radius=10, fill=WHITE)
        d.rounded_rectangle((cx, 630, cx + 288, 636), radius=3, fill=[RUST, TEAL, GOLD][i])
        put(d, cx + 20, 652, name, 22, INK, 'bold', cx + 270)
        put(d, cx + 20, 694, note, 16, DIM, 'body', cx + 270)

    put(d, 72, 770, '8000 万不是制作补贴，平台没有公布单部预算、买断价或分账比例。', 19, RUST, 'bold', 1008)

    footer(d, 826, [
        '来源：Variety 2026-11-03 21:00 PT；TechCrunch 2026-11-03 20:45 PST。',
        '占比为本号按 80/500 与 80/(500+80) 复算，原文只给估值 5 亿美元。',
    ])
    return im


def price_gap():
    im, d = page('北美单次下载内购是亚洲的 8.6 倍', '2026 上半年海外短剧 App / 投中网 2026-11-04 / 单次下载口径', '02', 940)

    put(d, 72, 250, '单次下载带来的 App 内购', 23, INK, 'bold', 1008)

    maxw = 660
    rows = [
        ('北美', 4.3, RUST, 300),
        ('亚洲', 0.5, TEAL, 396),
    ]
    for name, val, color, y in rows:
        put(d, 72, y, name, 24, INK, 'bold', 200)
        w = maxw * val / 4.3
        d.rectangle((240, y + 4, 240 + w, y + 34), fill=color)
        put(d, 240 + w + 14, y + 2, f'${val:.1f}', 26, color, 'number', 1008)

    put(d, 72, 486, '4.3 ÷ 0.5 = 8.6', 44, RUST, 'bold', 700)
    put(d, 72, 546, '同样的下载量，北美市场的单次内购更高。', 22, INK, 'body', 1008)

    d.rounded_rectangle((72, 604, 1008, 748), radius=10, fill='#efe6d6')
    put(d, 100, 622, '口径提醒', 21, RUST, 'bold', 986)
    put(d, 100, 658, '分母是下载，不是用户；这不是 Story TV 的 ARPU，', 18, DIM, 'body', 986)
    put(d, 100, 690, '也不是亚洲全部市场的平均值。只能说明区域单次收入差距。', 18, DIM, 'body', 986)

    footer(d, 790, [
        '来源：投中网《AI短剧，真的赚钱吗？》2026-11-04（新浪科技转载）。',
        '原文：2026 上半年海外短剧 App 内购 12.7 亿美元，北美 4.3 美元/下载、亚洲 0.5 美元/下载。',
    ])
    return im


def cover_075():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 540)

    put(d, 36, 74, 'NBCUniversal 投 8000 万美元', 20, GOLD, 'bold', 540)
    put(d, 32, 104, '印度短剧', 52, '#f6efe2', 'title', 540)
    put(d, 32, 166, '进军美国', 52, '#f6efe2', 'title', 540)
    put(d, 36, 244, '5,000+ 部、六语、每 3 小时一部', 17, '#bdb3a1', 'body', 540)
    put(d, 36, 316, '8000 万不是制作补贴', 15, '#e07a5f', 'body', 540)

    d.line((560, 70, 560, 330), fill='#4a443b', width=2)

    put(d, 590, 76, '为什么先开美国', 17, '#c9c0b0', 'bold', 864)
    put(d, 590, 108, '北美', 15, '#bdb3a1', 'body', 700)
    d.rectangle((640, 112, 860, 134), fill=RUST)
    put(d, 795, 115, '$4.3', 16, '#f6efe2', 'number', 858)
    put(d, 590, 158, '亚洲', 15, '#bdb3a1', 'body', 700)
    d.rectangle((640, 162, 666, 184), fill=TEAL)
    put(d, 676, 162, '$0.5', 16, TEAL, 'number', 864)
    put(d, 590, 220, '8.6×', 54, RUST, 'bold', 864)
    put(d, 590, 280, '单次下载内购差', 15, '#bdb3a1', 'body', 864)
    put(d, 590, 306, '投中网 11-04 / 不是 ARPU', 13, '#bdb3a1', 'body', 864)

    im.save(OUT / '封面_075_StoryTV_进军美国_900x383.png')
    print('封面 075 OK', im.size)


if __name__ == '__main__':
    im = deal_card()
    im.save(OUT / '075_图1_融资_1080.png')
    print('图1 OK', im.size)
    im = price_gap()
    im.save(OUT / '075_图2_单价_1080.png')
    print('图2 OK', im.size)
    cover_075()
