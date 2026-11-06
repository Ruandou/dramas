#!/usr/bin/env python3
"""076《印度现代汽车 6 集短剧，只发 Instagram》配图与封面。纯本地 Pillow，零扣费。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def runtime_compare():
    im, d = page('15 分钟，是 30 秒 TVC 的 30 倍', '《Diwali Chori Ho Gayi!》6 集 / ET BrandEquity·afaqs 2026-11-03—04', '01', 940)

    put(d, 72, 246, '六集成片：单集 1—3 分钟，合计约 15 分钟', 23, INK, 'bold', 1008)

    minutes = [2, 3, 2, 3, 2, 3]
    gap = 6
    span = 936 - gap * (len(minutes) - 1)
    x = 72
    for i, m in enumerate(minutes):
        w = span * m / sum(minutes)
        d.rounded_rectangle((x, 292, x + w, 382), radius=8, fill=[RUST, TEAL, GOLD][i % 3])
        put(d, x + w / 2 - 6, 322, str(i + 1), 24, WHITE, 'number', x + w - 4)
        x += w + gap

    put(d, 72, 406, '900 秒', 44, INK, 'bold', 300)
    put(d, 72, 462, '一条 30 秒 TVC 只有 30 秒', 19, DIM, 'body', 1008)

    d.rectangle((72, 512, 103, 534), fill=RUST)
    put(d, 116, 510, '30 秒 TVC', 18, RUST, 'bold', 400)
    put(d, 300, 510, '不到 6 集时长的 1/30', 17, DIM, 'body', 700)

    put(d, 72, 580, '30×', 84, RUST, 'bold', 500)
    put(d, 300, 604, '15 分钟 ÷ 30 秒', 26, INK, 'bold', 700)
    put(d, 300, 646, '换 60 秒版本，是 15×', 20, DIM, 'body', 700)

    put(d, 72, 740, '品牌买的不是贴片曝光，是能装下人物和冲突的叙事时长；制作费之外还要算媒体投放。', 18, INK, 'body', 1008)

    footer(d, 820, [
        '来源：ET BrandEquity 2026-11-03；afaqs 2026-11-04。',
        '30×/15× 为本号按 900 秒与 30/60 秒换算；单集时长区间与 15 分钟为品牌方口径。',
    ])
    return im


def compare_card():
    im, d = page('品牌定制 vs 平台供片', '同样拍短剧，买家、钱和交付不是一套', '02', 1000)

    put(d, 72, 246, '逐项对照', 22, INK, 'bold', 1008)

    d.rectangle((200, 286, 588, 322), fill=RUST)
    d.rectangle((620, 286, 1008, 322), fill=TEAL)
    put(d, 216, 292, '品牌定制', 20, WHITE, 'bold', 580)
    put(d, 636, 292, '平台供片', 20, WHITE, 'bold', 1000)

    rows = [
        ('买家', '品牌市场部', '短剧 App 或平台'),
        ('钱从哪来', '社媒、话题片预算', '内容采购或分账池'),
        ('交付', '6 集，单集 1—3 分钟，合计约 15 分钟', '通常 60—90 秒一集，几十集起'),
        ('分发', '品牌自有社媒（Instagram、Shorts）', '平台 App 内'),
        ('回款', '项目制，按合同节点', '买断或分账，周期长'),
        ('复购', '看 15 天数据，可能没有下一单', '看数据续订，可能季播'),
    ]
    y = 340
    for i, (label, a, b) in enumerate(rows):
        put(d, 72, y + 4, label, 18, DIM, 'bold', 190)
        paragraph(d, 200, y, a, width=380, size=17, color=INK, leading=25)
        paragraph(d, 620, y, b, width=380, size=17, color=INK, leading=25)
        if i < len(rows) - 1:
            d.line((72, y + 84, 1008, y + 84), fill=LINE, width=1)
        y += 92

    put(d, 72, 900, '本号按公开事实整理，不是品牌或平台披露的合同条款。', 17, RUST, 'body', 1008)
    return im


def cover_076():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 540)

    put(d, 36, 74, 'Hyundai India × TTT', 20, GOLD, 'bold', 540)
    put(d, 32, 104, '15 分钟', 56, '#f6efe2', 'title', 540)
    put(d, 36, 176, '6 集品牌短剧', 28, '#e8dfcf', 'bold', 540)
    put(d, 36, 216, '只发 Instagram', 28, '#e07a5f', 'bold', 540)
    put(d, 36, 280, '社媒预算 / 15 天复盘', 18, '#bdb3a1', 'body', 540)
    put(d, 36, 330, '不是平台供片', 16, '#bdb3a1', 'body', 540)

    d.line((560, 70, 560, 330), fill='#4a443b', width=2)

    put(d, 590, 76, '对比 30 秒 TVC', 16, '#c9c0b0', 'bold', 864)
    put(d, 590, 154, '30×', 72, RUST, 'bold', 864)
    put(d, 590, 250, '6 集 = 约 900 秒', 16, '#bdb3a1', 'body', 864)
    d.rectangle((590, 284, 614, 306), fill=RUST)
    put(d, 624, 282, '30 秒 TVC', 15, '#bdb3a1', 'body', 864)

    im.save(OUT / '封面_076_现代汽车短剧_900x383.png')
    print('封面 076 OK', im.size)


if __name__ == '__main__':
    im = runtime_compare()
    im.save(OUT / '076_图1_时长_1080.png')
    print('图1 OK', im.size)
    im = compare_card()
    im.save(OUT / '076_图2_对照_1080.png')
    print('图2 OK', im.size)
    cover_076()
