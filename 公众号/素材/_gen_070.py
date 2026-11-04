#!/usr/bin/env python3
"""070《Visa 赞助竖屏短剧》配图与封面。纯本地 Pillow，零扣费。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def arrow_down(d, x, y0, y1, color=GREY, w=2):
    d.line((x, y0, x, y1 - 8), fill=color, width=w)
    d.polygon([(x - 6, y1 - 10), (x + 6, y1 - 10), (x, y1)], fill=color)


def money_flow():
    im, d = page('一部竖屏剧，三方出钱', 'Daddy Yankee × aTwist × Visa / 2026-11-03 / Variety + PRODU', '01', 1140)

    put(d, 72, 238, '出钱的三方', 23, INK, 'bold', 1008)

    cards = [
        ('艺人', 'Daddy Yankee', '专辑《La Postal》10-30', '内容与粉丝', RUST),
        ('品牌', 'Visa', 'ProMove campaign', '拉美与加勒比营销', GOLD),
        ('平台', 'aTwist', '2026-09-03 上线', '制作与分发', TEAL),
    ]
    cw, gap = 296, 24
    for i, (kind, name, line1, line2, color) in enumerate(cards):
        cx = 72 + i * (cw + gap)
        d.rounded_rectangle((cx, 278, cx + cw, 448), radius=12, fill=WHITE)
        d.rounded_rectangle((cx, 278, cx + cw, 284), radius=3, fill=color)
        put(d, cx + 20, 300, kind, 19, color, 'bold', cx + cw - 14)
        put(d, cx + 20, 332, name, 27, INK, 'title', cx + cw - 14)
        put(d, cx + 20, 384, line1, 17, DIM, 'body', cx + cw - 14)
        put(d, cx + 20, 412, line2, 17, DIM, 'body', cx + cw - 14)
        arrow_down(d, cx + cw // 2, 452, 492, color, 2)

    d.line((220, 492, 860, 492), fill=LINE, width=2)
    arrow_down(d, 540, 492, 520, INK, 3)

    d.rounded_rectangle((72, 524, 1008, 624), radius=12, fill=INK)
    put(d, 100, 542, '制作：200% Media', 23, '#f0c588', 'bold', 986)
    put(d, 100, 580, '波多黎各实拍 · 原创编舞 Karina Ortiz · 本地舞者、演员、创作团队', 18, '#bdb3a1', 'body', 986)

    put(d, 72, 652, '两个窗口：免费触达 + 付费独家', 23, INK, 'bold', 1008)

    windows = [
        (72, 'YouTube', '免费', 'Daddy Yankee 官方频道', '负责触达粉丝盘', RUST),
        (560, 'aTwist', 'freemium', '部分集广告免费 / 整季金币或订阅', '独家幕后 + 专访', TEAL),
    ]
    for cx, name, mode, line1, line2, color in windows:
        d.rounded_rectangle((cx, 692, cx + 448, 852), radius=12, fill=WHITE)
        put(d, cx + 22, 710, name, 24, INK, 'bold', cx + 430)
        put(d, cx + 22, 750, mode, 20, color, 'bold', cx + 430)
        put(d, cx + 22, 790, line1, 17, DIM, 'body', cx + 430)
        put(d, cx + 22, 818, line2, 17, DIM, 'body', cx + 430)

    d.rounded_rectangle((72, 882, 1008, 962), radius=12, fill='#efe6d6')
    put(d, 100, 900, '未披露：集数、单集时长、制作预算、授权金、分成比例', 20, RUST, 'bold', 986)
    put(d, 100, 934, '报道只给合作结构，不能据此推算利润。', 17, DIM, 'body', 986)

    footer(d, 984, [
        '来源：Variety（2026-11-02）、PRODU（2026-11-02）；aTwist 与 Visa 的角色按两篇报道的直接引语整理。',
        'aTwist 市场与 freemium 模式为平台口径转述；集数与时长未披露，本图不做推测。',
    ])
    return im


def launch_timeline():
    im, d = page('从专辑到剧集，只隔 4 天', '《La Postal: Written in the Dance》上线节点 / 2026-09—11', '02', 940)

    put(d, 72, 238, '三个节点，一部剧', 24, INK, 'bold', 1008)

    y = 390
    d.line((120, y, 960, y), fill=LINE, width=3)
    nodes = [
        (200, '09-03', 'aTwist 上线', '竖屏平台，创始团队来自好莱坞大厂', TEAL),
        (540, '10-30', '专辑《La Postal》', 'Daddy Yankee 新专辑发行，剧集用专辑做配乐', GOLD),
        (880, '11-03', '剧集上线', 'YouTube + aTwist 双端独家，首批墨西哥、西班牙', RUST),
    ]
    for x, date, title, body, color in nodes:
        d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=color)
        put(d, x - 48, y - 100, date, 34, color, 'number', x + 90)
        put(d, x - 88, y + 34, title, 22, INK, 'bold', x + 120)
        paragraph(d, x - 88, y + 74, body, 240, 17, DIM, 27)

    d.rounded_rectangle((72, 620, 1008, 724), radius=12, fill=WHITE)
    put(d, 100, 638, '首批市场：墨西哥、西班牙（英语 / 西语）', 21, INK, 'bold', 986)
    put(d, 100, 676, '其他国际市场待定；aTwist App 目前可用：澳、加、印、爱、新西兰、菲、英、美。', 17, DIM, 'body', 986)

    d.rounded_rectangle((72, 752, 1008, 826), radius=12, fill=INK)
    put(d, 100, 770, '专辑 10-30，剧集 11-03：中间只隔 4 天。', 23, '#f0c588', 'bold', 986)
    put(d, 100, 802, '这不是长周期自制剧，是跟着专辑发行日历走的影音物料。', 17, '#bdb3a1', 'body', 986)

    footer(d, 848, [
        '来源：Variety（2026-11-02）、PRODU（2026-11-02）；节点日期按两篇报道。',
        '4 天为本号按 10-30 至 11-03 的日期差复算；集数、单集时长未披露。',
    ])
    return im


def cover_070():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 860)

    put(d, 36, 78, '品牌预算 · 2026-11-03', 20, GOLD, 'bold', 540)
    put(d, 32, 112, 'Visa', 66, '#f6efe2', 'title', 540)
    put(d, 36, 196, '赞助了一部竖屏短剧', 34, GOLD, 'bold', 540)
    put(d, 36, 248, '品牌钱，不只买广告', 28, '#e07a5f', 'bold', 540)
    put(d, 36, 312, 'Daddy Yankee × aTwist', 20, '#bdb3a1', 'body', 540)

    d.line((560, 70, 560, 330), fill='#4a443b', width=2)

    put(d, 590, 86, '三方出钱', 19, '#c9c0b0', 'bold', 864)
    items = [
        ('艺人', '专辑《La Postal》', RUST),
        ('品牌', 'Visa ProMove', GOLD),
        ('平台', 'aTwist', TEAL),
    ]
    for i, (name, value, color) in enumerate(items):
        yy = 136 + i * 64
        d.rounded_rectangle((590, yy, 598, yy + 40), radius=2, fill=color)
        put(d, 612, yy - 2, name, 18, '#bdb3a1', 'body', 860)
        put(d, 612, yy + 20, value, 21, '#f0e8d8', 'bold', 864)

    put(d, 590, 330, 'YouTube 免费 + aTwist 付费', 17, '#e07a5f', 'body', 864)

    im.save(OUT / '封面_070_Visa短剧_900x383.png')
    print('封面 070 OK', im.size)


if __name__ == '__main__':
    im = money_flow()
    im.save(OUT / '070_图1_三方出钱_1080.png')
    print('图1 OK', im.size)
    im = launch_timeline()
    im.save(OUT / '070_图2_上线节点_1080.png')
    print('图2 OK', im.size)
    cover_070()
