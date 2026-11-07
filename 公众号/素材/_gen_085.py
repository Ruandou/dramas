#!/usr/bin/env python3
"""085《AI 短剧很热，引力传媒收入不足 0.1%》配图与封面。纯本地 Pillow，零扣费。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def one_in_thousand():
    im, d = page('1000 个格子里，只有 1 格', '2025 年营收 82.83 亿元 / AI 短剧收入不足 0.1%', '01', 1000)

    cell, gap = 18, 4
    x0, y0 = 102, 250
    for i in range(1000):
        row, col = divmod(i, 40)
        x = x0 + col * (cell + gap)
        y = y0 + row * (cell + gap)
        fill = RUST if i == 500 else '#e4dbcb'
        d.rounded_rectangle((x, y, x + cell, y + cell), radius=2, fill=fill)

    put(d, 102, 214, '红格 = 0.1%；其余 999 格 = 2025 年营收的 99.9%', 17, DIM, 'body', 1000)

    d.rounded_rectangle((72, 840, 1008, 900), radius=10, fill=INK)
    put(d, 100, 856, '不足 0.1% → 不到 828.3 万元', 22, '#f0c588', 'bold', 986)
    put(d, 520, 860, '按 2025 年报营收 82.83 亿元换算（C）', 14, '#bdb3a1', 'body', 986)

    footer(d, 920, [
        '来源：引力传媒 2026-11-05 股票交易风险提示性公告；2025 年年度报告。',
        '1000 格为比例示意；828.3 万元为本号按 82.83 亿元 × 0.1% 换算，不是公司披露的绝对值。',
    ])
    return im


def contract_funnel():
    im, d = page('框架协议，不是收入', '看 AI 短剧业务，先拆合同质量', '02', 980)

    rows = [
        (900, RUST, '框架协议', '有具体项目/金额吗'),
        (780, GOLD, '订单', '还是意向书'),
        (660, TEAL, '验收', '标准/返工谁担'),
        (540, GREY, '收入', '按什么确认'),
        (420, INK, '回款', '账期/逾期'),
    ]
    y = 250
    for width, color, label, note in rows:
        x = (1080 - width) / 2
        d.rounded_rectangle((x, y, x + width, y + 80), radius=10, fill=color)
        put(d, x + 22, y + 12, label, 24, WHITE, 'bold', x + width - 10)
        put(d, x + 22, y + 50, note, 15, '#f6efe2', 'body', x + width - 10)
        y += 94

    d.rounded_rectangle((72, 760, 1008, 870), radius=12, fill=WHITE)
    put(d, 102, 778, '框架协议 ≠ 订单；订单 ≠ 收入；收入 ≠ 回款。', 23, INK, 'bold', 986)
    put(d, 102, 822, '每一步都要有金额、验收和付款条件，缺一步就不是可确认的收入。', 16, DIM, 'body', 986)

    footer(d, 900, [
        '来源：引力传媒 2026-11-05 股票交易风险提示性公告；2025 年报；2026 三季报。',
        '五道口为本号整理的合同质量检查顺序，不是公司披露的收入确认政策。',
    ])
    return im


def cover_085():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 530)

    put(d, 36, 78, '上市公司 · AI 短剧', 17, GOLD, 'bold', 530)
    put(d, 32, 108, 'AI 短剧很热', 36, '#f6efe2', 'title', 530)
    put(d, 32, 156, '收入不足 0.1%', 46, '#e07a5f', 'title', 530)
    put(d, 36, 226, '引力传媒 4 天 3 板后的风险提示', 17, '#e8dfcf', 'bold', 530)
    put(d, 36, 270, '2025 营收 82.83 亿元', 15, '#bdb3a1', 'body', 530)
    put(d, 36, 300, 'AI 短剧不到 828 万元', 15, '#bdb3a1', 'body', 530)
    put(d, 36, 342, '概念热，收入冷', 13, '#8f8576', 'body', 530)

    d.line((548, 70, 548, 330), fill='#4a443b', width=2)

    put(d, 580, 78, '2025 年营收', 15, GOLD, 'bold', 864)
    put(d, 580, 104, '82.83 亿元', 30, '#f6efe2', 'bold', 864)
    d.rounded_rectangle((580, 154, 842, 182), radius=4, fill=GREY)
    d.rounded_rectangle((838, 148, 842, 188), radius=2, fill=RUST)
    put(d, 580, 200, 'AI 短剧收入 < 0.1%', 16, '#e07a5f', 'bold', 864)
    d.line((840, 188, 840, 218), fill=RUST, width=2)
    put(d, 760, 230, '不到 828 万元', 13, '#bdb3a1', 'body', 864)

    put(d, 580, 300, '0.1% = 828.3 万元', 22, '#f6efe2', 'bold', 864)
    put(d, 580, 342, '本号按年报营收换算（C）', 12, '#8f8576', 'body', 864)

    im.save(OUT / '封面_085_引力传媒_900x383.png')
    print('封面 085 OK', im.size)


if __name__ == '__main__':
    im = one_in_thousand()
    im.save(OUT / '085_图1_差距_1080.png')
    print('图1 OK', im.size)
    im = contract_funnel()
    im.save(OUT / '085_图2_合同_1080.png')
    print('图2 OK', im.size)
    cover_085()
