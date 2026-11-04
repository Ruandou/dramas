#!/usr/bin/env python3
"""071《番茄小说 10 亿》配图与封面。纯本地 Pillow，零扣费。"""
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


def money_destination():
    im, d = page('10 亿元的去向', '番茄小说 2027 专项资源 / 2026-11-02 杭州创作者大会', '01', 940)

    put(d, 72, 238, '四项作者侧用途，制作侧零项', 23, INK, 'bold', 1008)

    d.rounded_rectangle((72, 278, 360, 610), radius=12, fill=INK)
    put(d, 96, 304, '专项资源', 20, '#c9c0b0', 'bold', 344)
    put(d, 92, 338, '10 亿元', 64, '#f6efe2', 'title', 344)
    put(d, 96, 426, '2027 年计划投入', 18, '#bdb3a1', 'body', 344)
    d.line((96, 462, 336, 462), fill='#4a443b', width=2)
    put(d, 96, 484, '不是现金补贴', 22, GOLD, 'bold', 344)
    put(d, 96, 518, '不是制作费', 22, GOLD, 'bold', 344)
    put(d, 96, 562, '收款方：作者与版权方', 17, '#bdb3a1', 'body', 344)

    rows = [
        ('征文激励', '延续千万级征文', '千万级', RUST),
        ('创新故事创作基金', '新题材、新设定、新表达', '未披露', GOLD),
        ('新人全周期奖励', '大师课 / 训练营 / 作品研讨', '未披露', TEAL),
        ('版权激励 + 开发资源', '推动向短剧、漫剧、有声延伸', '千万元级', GREY),
    ]
    for i, (name, note, amount, color) in enumerate(rows):
        y = 286 + i * 80
        d.rounded_rectangle((392, y, 1008, y + 64), radius=10, fill=WHITE)
        d.rounded_rectangle((392, y, 398, y + 64), radius=3, fill=color)
        put(d, 418, y + 9, name, 21, INK, 'bold', 980)
        put(d, 418, y + 38, note, 16, DIM, 'body', 900)
        put(d, 900, y + 18, amount, 17, color, 'bold', 996)

    dashed_rect(d, (72, 650, 1008, 772), RUST, 2)
    put(d, 100, 672, '制作方：不在用途清单', 24, RUST, 'bold', 986)
    paragraph(d, 100, 712, '拍摄费、后期费、演员费，不在 10 亿专项资源里。谈改编时，别把平台扶持当自己的制作预算。', 880, 18, DIM, 30)

    footer(d, 800, [
        '来源：新华网（2026-11-03）、科创板日报（2026-11-02）。10 亿为 2027 年「专项资源」，非现金补贴、非制作费。',
        '征文激励与版权激励的「千万级 / 千万元级」为报道原文表述；基金与新人奖励未披露金额，本图不估算。',
    ])
    return im


def supply_gate():
    im, d = page('供给更快，门槛没松', '番茄小说 IP 改编节奏与拒签 / 平台口径 2026-11', '02', 1000)

    put(d, 72, 238, '新增改编作品：每月 3000 到 7000', 23, INK, 'bold', 1008)

    d.rounded_rectangle((72, 278, 560, 700), radius=12, fill=WHITE)
    put(d, 96, 300, '平台新增改编作品 / 月', 19, DIM, 'bold', 540)

    put(d, 96, 348, '平均月增', 19, INK, 'bold', 300)
    d.rounded_rectangle((96, 380, 96 + 132, 422), radius=6, fill=GREY)
    put(d, 244, 388, '3000 部', 20, INK, 'bold', 540)

    put(d, 96, 462, '最近一个月', 19, INK, 'bold', 300)
    d.rounded_rectangle((96, 494, 96 + 308, 536), radius=6, fill=RUST)
    put(d, 420, 502, '超 7000 部', 20, RUST, 'bold', 540)

    put(d, 96, 588, '2.3x', 54, RUST, 'number', 260)
    put(d, 250, 600, '最近一个月', 18, DIM, 'body', 540)
    put(d, 250, 628, '除以平均月增', 18, DIM, 'body', 540)
    put(d, 96, 660, '仅腾讯新闻·新立场载明，不作稳定增速', 15, GREY, 'body', 540)

    d.rounded_rectangle((592, 278, 1008, 700), radius=12, fill=WHITE)
    put(d, 616, 300, '另外四个数', 19, DIM, 'bold', 990)

    stats = [
        ('3 万部', '年内进入影视化开发/授权链路', '不等于已上线或已分账'),
        ('2 亿元', '单月短漫剧授权总收入', '作者侧收入，不是单部价'),
        ('46 万本', '累计拒签低质作品', '门槛没松'),
        ('5 万部', '完成有声书录制', '音频改编更快'),
    ]
    for i, (num, label, note) in enumerate(stats):
        y = 336 + i * 88
        put(d, 616, y, num, 27, INK, 'bold', 990)
        put(d, 748, y + 2, label, 17, DIM, 'body', 990)
        put(d, 616, y + 36, note, 16, RUST if i == 2 else GREY, 'body', 990)

    d.rounded_rectangle((72, 730, 1008, 806), radius=10, fill='#efe6d6')
    put(d, 100, 748, '口径不同，不能相除', 20, RUST, 'bold', 986)
    put(d, 300, 752, '2 亿是短漫剧授权收入，7000 是全部新增改编作品。', 17, DIM, 'body', 986)

    footer(d, 834, [
        '来源：新华网（2026-11-03）、科创板日报（2026-11-02）、腾讯新闻·新立场（2026-11-02）。',
        '7000/3000 仅腾讯稿载明；3 万部为「进入开发/授权链路」；46 万本为累计拒签，未给起止时间。',
    ])
    return im


def cover_071():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 540)

    put(d, 36, 78, '番茄小说 · 2027 计划', 20, GOLD, 'bold', 540)
    put(d, 32, 108, '10 亿', 66, '#f6efe2', 'title', 540)
    put(d, 36, 194, '钱给作者', 36, GOLD, 'bold', 540)
    put(d, 36, 244, 'IP 月增 7000 部', 30, '#e07a5f', 'bold', 540)
    put(d, 36, 288, '钱没进制作端', 26, '#e8dfcf', 'bold', 540)
    put(d, 36, 330, '2026-11-02 杭州创作者大会', 18, '#bdb3a1', 'body', 540)

    d.line((560, 70, 560, 330), fill='#4a443b', width=2)

    put(d, 590, 76, '10 亿 → 作者侧', 19, '#c9c0b0', 'bold', 864)
    items = [
        ('征文激励', '千万级', RUST),
        ('创作基金', '未披露', GOLD),
        ('新人奖励', '未披露', TEAL),
        ('版权激励', '千万元级', GREY),
    ]
    for i, (name, amount, color) in enumerate(items):
        yy = 114 + i * 34
        d.rectangle((590, yy + 4, 598, yy + 20), fill=color)
        put(d, 610, yy, name, 17, '#e8dfcf', 'body', 864)
        put(d, 700, yy, amount, 15, '#bdb3a1', 'body', 864)

    dashed_rect(d, (590, 254, 864, 296), '#e07a5f', 2, 8, 6)
    put(d, 604, 264, '制作方：0 项', 18, '#e07a5f', 'bold', 860)

    put(d, 590, 312, '新增改编 / 月', 15, '#bdb3a1', 'body', 864)
    d.rounded_rectangle((700, 316, 760, 328), radius=3, fill=GREY)
    d.rounded_rectangle((700, 336, 840, 348), radius=3, fill=RUST)
    put(d, 768, 312, '3000', 14, '#e8dfcf', 'number', 864)
    put(d, 848, 332, '7000', 14, '#e07a5f', 'number', 896)

    im.save(OUT / '封面_071_番茄10亿_900x383.png')
    print('封面 071 OK', im.size)


if __name__ == '__main__':
    im = money_destination()
    im.save(OUT / '071_图1_10亿去向_1080.png')
    print('图1 OK', im.size)
    im = supply_gate()
    im.save(OUT / '071_图2_供给与门槛_1080.png')
    print('图2 OK', im.size)
    cover_071()
