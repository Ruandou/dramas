#!/usr/bin/env python3
"""073《人民日报谈短剧出海》配图与封面。纯本地 Pillow，零扣费。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def growth_gap():
    im, d = page('下载涨得比收入快', '2025 海外短剧应用 / 人民日报评论引用行业报告 / 2026-11-04', '01', 1000)

    put(d, 72, 238, '两个总量，两个增速', 23, INK, 'bold', 1008)

    d.rounded_rectangle((72, 278, 540, 620), radius=12, fill=WHITE)
    put(d, 96, 300, '总下载', 20, RUST, 'bold', 520)
    put(d, 96, 330, '亿次', 16, DIM, 'body', 520)
    put(d, 96, 372, '2024', 18, DIM, 'body', 300)
    d.rounded_rectangle((96, 404, 96 + 103, 446), radius=6, fill=GREY)
    put(d, 212, 412, '3.26', 20, INK, 'bold', 520)
    put(d, 96, 478, '2025', 18, DIM, 'body', 300)
    d.rounded_rectangle((96, 510, 96 + 380, 552), radius=6, fill=RUST)
    put(d, 96, 570, '+268%', 32, RUST, 'number', 520)

    d.rounded_rectangle((568, 278, 1008, 620), radius=12, fill=WHITE)
    put(d, 592, 300, '总收入', 20, TEAL, 'bold', 990)
    put(d, 592, 330, '亿美元', 16, DIM, 'body', 990)
    put(d, 592, 372, '2024', 18, DIM, 'body', 800)
    d.rounded_rectangle((592, 404, 592 + 163, 446), radius=6, fill=GREY)
    put(d, 768, 412, '10.0', 20, INK, 'bold', 990)
    put(d, 592, 478, '2025', 18, DIM, 'body', 800)
    d.rounded_rectangle((592, 510, 592 + 380, 552), radius=6, fill=TEAL)
    put(d, 592, 570, '+133%', 32, TEAL, 'number', 990)

    d.rounded_rectangle((72, 660, 1008, 780), radius=10, fill=INK)
    put(d, 100, 678, '单次下载收入', 20, '#c9c0b0', 'bold', 986)
    put(d, 100, 708, '$3.07', 30, '#bdb3a1', 'number', 300)
    put(d, 240, 714, '→', 24, '#bdb3a1', 'body', 300)
    put(d, 282, 706, '$1.94', 34, '#f6efe2', 'number', 400)
    put(d, 420, 712, '约 -37%', 26, '#e07a5f', 'bold', 600)
    put(d, 600, 686, '2024 为按增速倒推（C）', 17, '#bdb3a1', 'body', 986)
    put(d, 600, 716, '不是 ARPU，只能看趋势', 17, '#bdb3a1', 'body', 986)
    put(d, 600, 746, '下载≠付费用户，收入≠全部由下载带来', 15, '#8f8576', 'body', 986)

    footer(d, 808, [
        '来源：人民日报 2026-11-04 第 15 版评论（作者杨乘虎）引用《2025海外短剧行业报告》。',
        '2024 下载/收入与单次下载收入为本号按同比增速（下载 +268%、收入 +133%）倒推；增速四舍五入会放大误差。',
    ])
    return im


def three_stages():
    im, d = page('出海的三个阶段', '人民日报评论归纳 / 成本与壁垒为本号整理 / 2026-11-04', '02', 940)

    put(d, 72, 238, '同一部剧，三种做法，三种成本', 23, INK, 'bold', 1008)

    y = 400
    d.line((100, y, 980, y), fill=LINE, width=3)
    nodes = [
        (190, '译制试水', '字幕 / 配音，直接搬运', '成本最低\n差异化最低', RUST),
        (540, '平台化原创', '本土演员、本地语境', '成本更高\n壁垒更高', GOLD),
        (890, 'AI 介入', '压缩译制周期，AI 漫剧', '成本下降\n变成入场券', TEAL),
    ]
    for x, name, body, note, color in nodes:
        d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=color)
        put(d, x - 90, y - 110, name, 26, color, 'bold', x + 130)
        paragraph(d, x - 90, y + 34, body, 220, 17, DIM, 27)
        yy = y + 104
        for line in note.split('\n'):
            put(d, x - 90, yy, line, 18, INK, 'bold', x + 130)
            yy += 30

    d.rounded_rectangle((72, 700, 1008, 800), radius=10, fill='#efe6d6')
    put(d, 100, 718, '评论案例：东北风情 + 南洋华人，红果首月 30 亿次播放', 19, RUST, 'bold', 986)
    put(d, 100, 752, '红果是国内平台，这个数字不是海外成绩；宋锦非遗《顾盼锦年》在加拿大推广，评论未给播放与收入。', 16, DIM, 'body', 986)

    footer(d, 828, [
        '来源：人民日报 2026-11-04 第 15 版评论（作者杨乘虎）；三阶段为评论归纳。',
        '成本与壁垒判断为本号解读（C），不是报告结论；未给各阶段的市场份额、收入或制作成本。',
    ])
    return im


def cover_073():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 540)

    put(d, 36, 78, '短剧出海 · 2025 全年', 20, GOLD, 'bold', 540)
    put(d, 32, 106, '11.99 亿次', 52, '#f6efe2', 'title', 540)
    put(d, 36, 176, '下载', 22, '#bdb3a1', 'body', 540)
    put(d, 36, 208, '23.29 亿美元', 38, GOLD, 'bold', 540)
    put(d, 36, 258, '收入', 22, '#bdb3a1', 'body', 540)
    put(d, 36, 296, '下载 +268%，收入 +133%', 25, '#e07a5f', 'bold', 540)
    put(d, 36, 334, '人民日报评论引用行业报告', 17, '#bdb3a1', 'body', 540)

    d.line((560, 70, 560, 330), fill='#4a443b', width=2)

    put(d, 590, 76, '单次下载收入', 18, '#c9c0b0', 'bold', 864)
    put(d, 590, 108, '$3.07', 32, '#bdb3a1', 'number', 720)
    put(d, 700, 114, '→', 26, '#bdb3a1', 'body', 760)
    put(d, 744, 104, '$1.94', 38, '#f6efe2', 'number', 864)
    put(d, 590, 160, '约 -37%', 22, '#e07a5f', 'bold', 864)

    put(d, 590, 210, '下载', 16, '#bdb3a1', 'body', 660)
    d.rounded_rectangle((650, 214, 650 + 54, 226), radius=3, fill=GREY)
    put(d, 718, 210, '3.26 亿', 15, '#e8dfcf', 'bold', 864)
    d.rounded_rectangle((650, 244, 650 + 140, 256), radius=3, fill=RUST)
    put(d, 792, 240, '11.99 亿', 15, '#e07a5f', 'bold', 864)

    put(d, 590, 300, '红果 30 亿次是国内案例', 15, '#bdb3a1', 'body', 864)
    put(d, 590, 326, '不是海外成绩', 15, '#e07a5f', 'body', 864)

    im.save(OUT / '封面_073_短剧出海_900x383.png')
    print('封面 073 OK', im.size)


if __name__ == '__main__':
    im = growth_gap()
    im.save(OUT / '073_图1_增速差_1080.png')
    print('图1 OK', im.size)
    im = three_stages()
    im.save(OUT / '073_图2_三阶段_1080.png')
    print('图2 OK', im.size)
    cover_073()
