#!/usr/bin/env python3
"""062《雄安千部漫剧》配图与封面。纯本地 Pillow。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def plan_vs_order():
    im, d = page('1000 部是计划量，不是订单', '雄安「千部精品 AI 短剧计划」/ 2026-10-30 / 三家媒体', '01', 1060)

    cards = [
        (72, 246, 288, '计划目标', '1000 部', '报道口径，不是签约数', RUST),
        (396, 246, 288, '园区主体', '30 余家', '已聚，官方口径', INK),
        (720, 246, 288, '已公布细则', '0 项', '采购价 / 分账 / 门槛 / 资格', RUST),
    ]
    for cx, cy, cw, label, value, note, color in cards:
        d.rounded_rectangle((cx, cy, cx + cw, cy + 190), radius=12, fill=WHITE)
        put(d, cx + 24, cy + 20, label, 19, DIM, 'bold', cx + cw - 16)
        put(d, cx + 20, cy + 54, value, 48, color, 'title', cx + cw - 14)
        paragraph(d, cx + 24, cy + 128, note, width=248, size=17, color=DIM, leading=24)

    put(d, 72, 476, '四项未公布', 26, INK, 'bold', 500)
    put(d, 72, 512, '决定能不能接、接了赚不赚', 17, DIM, 'body', 700)

    unknowns = [
        ('单部采购价', '多少钱一部'),
        ('分账比例', '怎么分'),
        ('报名门槛', '谁能报'),
        ('外地团队', '能不能参与'),
    ]
    for i, (name, note) in enumerate(unknowns):
        cx = 72 + (i % 2) * 456
        cy = 554 + (i // 2) * 82
        d.rounded_rectangle((cx, cy, cx + 432, cy + 66), radius=10, fill=WHITE)
        put(d, cx + 16, cy + 16, '×', 30, RUST, 'bold', cx + 52)
        put(d, cx + 52, cy + 10, name, 24, INK, 'bold', cx + 280)
        put(d, cx + 258, cy + 18, note, 18, DIM, 'body', cx + 424)

    d.rounded_rectangle((72, 746, 1008, 828), radius=12, fill=WHITE)
    put(d, 100, 760, '同向背景', 20, DIM, 'bold', 400)
    put(d, 100, 790, '10-27 雄安 × 腾讯 AIGC 漫剧基地；10-26 河北 OPC 工作举措。', 19, INK, 'body', 986)

    d.rounded_rectangle((72, 852, 1008, 952), radius=12, fill=INK)
    put(d, 100, 866, '计划量不是已签约订单', 30, '#f0c588', 'bold', 986)
    put(d, 100, 914, '先盯河北国控文化传媒、雄安新区官网；细则出来再判断。', 18, '#bdb3a1', 'body', 986)

    footer(d, 976, [
        '来源：中国新闻网、21 世纪经济报道、纵览新闻（2026-10-30）。',
        '背景：雄安新区官网（2026-10-27、10-29）；四项细则均未公布。',
    ])
    return im


def cover_062():
    base.TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, '#bdb3a1', right=440)
    put(d, 33, 60, '雄安 · 2026-10-30', 18, '#f0c588', 'bold', 480)
    put(d, 28, 92, '1000 部', 96, '#efe6d6', 'title', 480)
    put(d, 36, 208, '是计划量，不是订单', 28, '#e0705a', 'bold', 480)
    put(d, 36, 252, '30 余家园区主体', 20, '#bdb3a1', 'body', 480)
    put(d, 36, 286, '四项细则未公布', 20, '#8fc0b4', 'bold', 480)

    d.line((500, 62, 500, 324), fill='#4a443c', width=1)
    items = ['单部采购价', '分账比例', '报名门槛', '外地团队资格']
    for i, t in enumerate(items):
        y = 84 + i * 56
        put(d, 540, y, '×', 26, '#e0705a', 'bold', 566)
        put(d, 576, y, t, 24, '#efe6d6', 'bold', 880)
    put(d, 540, 318, '等细则，再判断', 16, '#8f8576', 'body', 880)
    return im


if __name__ == '__main__':
    jobs = [
        ('062_图1_计划量_1080.png', plan_vs_order),
        ('封面_062_1000部不是订单_900x383.png', cover_062),
    ]
    for name, maker in jobs:
        im = maker()
        base.validate_glyphs()
        base.save_png(im, OUT / name)
    print('done')
