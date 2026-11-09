#!/usr/bin/env python3
"""086《AI 微短剧《辛弃疾》上星：2 集 72 分钟》配图与封面。纯本地 Pillow，零扣费。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def broadcast_spec():
    im, d = page('一部剧，两集，72 分钟', 'AI 微短剧《辛弃疾》/ 山东卫视 2026-11-07', '01', 1000)

    put(d, 72, 236, '2', 92, RUST, 'title', 360)
    put(d, 140, 268, '集', 34, INK, 'bold', 360)
    put(d, 210, 236, '×', 46, DIM, 'body', 360)
    put(d, 262, 236, '36', 92, INK, 'title', 470)
    put(d, 356, 268, '分钟', 34, INK, 'bold', 470)
    put(d, 470, 300, '合计 72 分钟', 22, DIM, 'body', 620)

    rows = [
        ('首播', '11 月 7—8 日 22:25', '山东卫视'),
        ('网络', '优酷同步', '与电视端同步'),
        ('重播', '11 月 14—15 日 8:05', '山东卫视'),
        ('画幅', '横屏', '不是竖屏拼接'),
    ]
    y = 390
    for label, value, note in rows:
        d.rounded_rectangle((72, y, 1008, y + 96), radius=10, fill=WHITE)
        put(d, 100, y + 16, label, 17, RUST, 'bold', 170)
        put(d, 190, y + 12, value, 24, INK, 'bold', 700)
        put(d, 190, y + 54, note, 16, DIM, 'body', 960)
        y += 106

    d.rounded_rectangle((72, 826, 1008, 888), radius=10, fill=INK)
    put(d, 100, 842, '竖屏 90 秒 × N 集 ≠ 电视 36 分钟 × 2 集', 21, '#f0c588', 'bold', 986)

    footer(d, 912, [
        '来源：山东卫视 2026-11-06 17:51 官方发布（齐鲁网）。',
        '规格数字出自官方稿；72 分钟为本号按 2×36 分钟相加。',
    ])
    return im


def project_structure():
    im, d = page('项目制，不是征稿', '谁在《辛弃疾》这个项目里', '02', 1020)

    chain = [
        ('指导', '山东省广播电视局', TEAL),
        ('联合摄制', '中共济南市委宣传部', TEAL),
        ('出品', '山影集团 + 山东卫视', RUST),
        ('制作', '万物润泽 + 闪电文化', GOLD),
        ('支持', '济南市大数据局 / AI 办 / 城投资本', GREY),
    ]
    y = 240
    for label, value, color in chain:
        d.rounded_rectangle((72, y, 1008, y + 88), radius=10, fill=WHITE)
        d.rectangle((72, y, 84, y + 88), fill=color)
        put(d, 104, y + 14, label, 16, color if color != GREY else DIM, 'bold', 250)
        put(d, 104, y + 42, value, 22, INK, 'bold', 1000)
        y += 100

    put(d, 72, 760, '独立制作方能站的位置', 18, DIM, 'bold', 1008)

    actions = [
        ('备电视版', '36 分钟/集、横屏、2 集'),
        ('找项目入口', '文旅项目 / 宣传部联合摄制'),
        ('拆版权', '首播、网络、重播、窗口期'),
    ]
    x = 72
    for title, desc in actions:
        d.rounded_rectangle((x, 796, x + 300, 906), radius=10, fill=INK)
        put(d, x + 18, 812, title, 20, '#f0c588', 'bold', x + 286)
        put(d, x + 18, 852, desc, 14, '#bdb3a1', 'body', x + 286)
        x += 312

    footer(d, 930, [
        '来源：山东卫视 2026-11-06 17:51 官方发布（齐鲁网）。',
        '三方支持单位为官方稿所列；制作方为万物润泽（山东）影视传媒、闪电（山东）文化科技。',
    ])
    return im


def cover_086():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 520)

    put(d, 36, 76, '电视端 · AI 微短剧', 16, GOLD, 'bold', 520)
    put(d, 32, 104, '《辛弃疾》上星', 40, '#f6efe2', 'title', 520)
    put(d, 32, 154, '2 集 72 分钟', 40, '#e07a5f', 'title', 520)
    put(d, 36, 216, '今晚 22:25 山东卫视 / 优酷同步', 16, '#e8dfcf', 'bold', 540)
    put(d, 36, 252, '36 分钟一集，横屏，台网同播', 15, '#bdb3a1', 'body', 540)
    put(d, 36, 288, '重播 11-14—15 8:05', 14, '#bdb3a1', 'body', 540)
    put(d, 36, 342, '不是竖屏拼接', 13, '#8f8576', 'body', 540)

    d.line((560, 70, 560, 330), fill='#4a443b', width=2)

    # TV frame
    d.rounded_rectangle((590, 70, 864, 208), radius=8, outline='#8f8576', width=2)
    d.rectangle((606, 86, 848, 184), fill='#1f1c18')
    put(d, 622, 100, '辛弃疾', 24, '#f6efe2', 'bold', 838)
    put(d, 622, 138, 'AI 微短剧 / 山东卫视', 13, '#bdb3a1', 'body', 838)

    # two nights, 36 min each
    for i, day in enumerate(('11-07', '11-08')):
        y = 228 + i * 34
        put(d, 590, y - 4, day, 13, '#e8dfcf', 'body', 640)
        d.rectangle((642, y, 806, y + 10), fill=GREY)
        d.rectangle((642, y, 648, y + 10), fill=RUST)
        put(d, 816, y - 4, '22:25', 13, '#e8dfcf', 'body', 864)
    put(d, 590, 300, '每集 36 分钟，两晚播完', 14, '#bdb3a1', 'body', 864)
    put(d, 590, 330, '优酷同步', 15, GOLD, 'bold', 864)

    im.save(OUT / '封面_086_辛弃疾_900x383.png')
    print('封面 086 OK', im.size)


if __name__ == '__main__':
    im = broadcast_spec()
    im.save(OUT / '086_图1_规格_1080.png')
    print('图1 OK', im.size)
    im = project_structure()
    im.save(OUT / '086_图2_结构_1080.png')
    print('图2 OK', im.size)
    cover_086()
