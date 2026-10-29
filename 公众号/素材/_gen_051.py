#!/usr/bin/env python3
"""051《减亏 74.63%，营收又降 17.64%》配图与封面。纯本地 Pillow。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def three_numbers():
    im, d = base.page('三个数：营收降、亏损缩、毛利升', '中文在线 2026 年三季报 / 2026-10-26 披露', '01', 940)
    cards = [
        (72, 260, 292, '前三季营收', '8.33 亿', '-17.64%', '去年 10.11 亿'),
        (394, 260, 292, '归母净利润', '-1.32 亿', '减亏 74.63%', '去年亏 5.20 亿'),
        (716, 260, 292, '毛利', '3.89 亿', '毛利率 46.7%', '去年 3.50 亿 / 34.6%'),
    ]
    for cx, cy, cw, label, value, delta, note in cards:
        d.rounded_rectangle((cx, cy, cx + cw, cy + 250), radius=12, fill=WHITE)
        base.put(d, cx + 24, cy + 20, label, 21, DIM, 'bold', cx + cw - 12)
        base.put(d, cx + 20, cy + 58, value, 52, RUST if value.startswith('-') else INK, 'title', cx + cw - 12)
        base.put(d, cx + 24, cy + 136, delta, 22, TEAL if delta.startswith('减亏') or delta.startswith('毛利') else RUST, 'bold', cx + cw - 12)
        base.put(d, cx + 24, cy + 200, note, 19, DIM, 'body', cx + cw - 10)

    d.rounded_rectangle((72, 552, 1008, 664), radius=12, fill=INK)
    base.put(d, 102, 572, '收入少 1.78 亿，成本少 2.18 亿，销售费用少 2.76 亿。', 22, '#bdb3a1', right=986)
    base.put(d, 102, 612, '毛利反升 0.39 亿。', 28, '#f0c588', 'bold', 986)

    base.put(d, 72, 706, '单季营收：Q1 3.10 亿 → Q2 2.68 亿 → Q3 2.55 亿。', 23, INK, 'bold', 1008)
    base.footer(d, 762, [
        '来源：中文在线 2026 年三季报，经北京日报 10-26、新浪财经 10-27 等四家交叉一致。',
        '去年同期与毛利为本号按同比倒推计算；毛利率 = (营收 - 营业成本) ÷ 营收。',
    ])
    return im


def gross_vs_sales():
    im, d = base.page('毛利 3.89 亿，投流 3.84 亿', '毛利与销售费用，2025 与 2026 前三季对照（亿元）', '02', 980)
    x0, span, unit = 300, 620, 620 / 6.8
    groups = [
        (250, '2025 前三季', [(3.50, GOLD), (6.60, RUST)], '毛利 - 投流 = -3.10', RUST),
        (470, '2026 前三季', [(3.89, GOLD), (3.84, TEAL)], '毛利 - 投流 = +0.05', TEAL),
    ]
    for gy, name, bars, gap, gap_color in groups:
        base.put(d, 72, gy, name, 24, INK, 'bold', 280)
        for i, (val, color) in enumerate(bars):
            by = gy + 42 + i * 62
            w = span * (val / 6.8)
            d.rectangle((x0, by, x0 + w, by + 44), fill=color)
            base.put(d, x0 + w + 16, by + 8, f'{val:.2f}', 24, INK, 'bold', 1008)
        base.put(d, 72, gy + 168, gap, 22, gap_color, 'bold', 1008)

    d.rounded_rectangle((72, 690, 1008, 800), radius=12, fill=INK)
    base.put(d, 102, 708, '2025：毛利不够付投流，缺口 3.10 亿。', 23, '#bdb3a1', right=986)
    base.put(d, 102, 748, '2026：毛利刚好盖住投流，剩 0.05 亿。', 26, '#f0c588', 'bold', 986)

    base.put(d, 72, 824, '销售费用率 65.3% → 46.1%；毛利率 34.6% → 46.7%。', 23, INK, 'bold', 1008)
    base.footer(d, 872, [
        '毛利 = 营业收入 - 营业成本；2025 同期由同比增速倒推。',
        '销售费用含投流推广；公司未单列投流，本图不把销售费用等同于投流。',
    ])
    return im


def quarterly():
    im, d = base.page('三个季度，一条向下的线', '单季营业收入（亿元）/ 2026 年 Q1—Q3', '03', 1020)

    d.rounded_rectangle((72, 240, 1008, 356), radius=12, fill=WHITE)
    base.put(d, 100, 258, 'Q3 单季亏 0.89 亿，上半年合计亏 0.43 亿。', 24, INK, 'bold', 990)
    base.put(d, 100, 304, '一个季度，亏掉前两个季度的 2.1 倍。', 22, RUST, 'bold', 990)

    bars = [(240, 3.10, 'Q1', '—'), (470, 2.68, 'Q2', '环比 -13.5%'), (700, 2.55, 'Q3', '环比 -4.9%')]
    baseline, unit = 700, 95
    for bx, val, label, mom in bars:
        h = val * unit
        d.rectangle((bx, baseline - h, bx + 140, baseline), fill=INK if label != 'Q3' else RUST)
        base.put(d, bx + 20, baseline - h - 52, f'{val:.2f}', 40, INK, 'title', bx + 150)
        base.put(d, bx + 40, baseline + 16, label, 24, INK, 'bold', bx + 150)
        base.put(d, bx + 10, baseline + 56, mom, 19, DIM, 'body', bx + 190)
    d.line((180, baseline, 900, baseline), fill=LINE, width=2)

    base.put(d, 72, 836, 'Q3 同比 -43.95%，比前三季整体的 -17.64% 陡得多。', 23, INK, 'bold', 1008)
    base.footer(d, 892, [
        '来源：中文在线 2026 年三季报；环比与倍数为本号直接计算。',
        '上半年亏损 = 前三季亏损 1.32 亿 - Q3 亏损 0.89 亿。',
    ])
    return im


def cover():
    base.TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    base.put(d, 33, 24, '一人短剧厂牌', 18, '#bdb3a1', right=420)
    base.put(d, 33, 60, '中文在线 2026 三季报 · 10-26', 18, '#f0c588', 'bold', 470)
    base.put(d, 28, 92, '74.63%', 76, '#efe6d6', 'title', 470)
    base.put(d, 36, 190, '减亏幅度', 22, '#bdb3a1', 'bold', 470)
    base.put(d, 36, 228, '营收 -17.64%', 30, '#e0705a', 'bold', 470)
    base.put(d, 36, 276, '少亏 3.88 亿，毛利只多 0.39 亿', 19, '#8f8576', 'body', 470)

    d.line((490, 62, 490, 330), fill='#4a443c', width=1)
    base.put(d, 528, 96, '钱从哪省的', 18, '#bdb3a1', 'body', 880)
    rows = [
        ('营业成本', '-2.18 亿', '#b9853d'),
        ('销售费用', '-2.76 亿', '#28695e'),
        ('营业收入', '-1.78 亿', '#ae422c'),
    ]
    y = 140
    for name, val, color in rows:
        d.rectangle((528, y + 6, 540, y + 24), fill=color)
        base.put(d, 552, y, name, 19, '#efe6d6', 'body', 700)
        base.put(d, 700, y, val, 19, color, 'bold', 880)
        y += 40
    base.put(d, 528, 276, '毛利 3.89 亿 / 投流 3.84 亿', 19, '#8fc0b4', 'body', 880)
    base.put(d, 528, 308, '两个数几乎相等', 22, '#efe6d6', 'bold', 880)
    return im


def main():
    outputs = [
        (three_numbers(), '051_图1_三个数_1080.png'),
        (gross_vs_sales(), '051_图2_毛利与投流_1080.png'),
        (quarterly(), '051_图3_单季营收_1080.png'),
    ]
    for im, name in outputs:
        im.save(OUT / name, optimize=True)
        base.validate_glyphs()
        print(name, im.size, f'{(OUT / name).stat().st_size / 1024:.1f} KB')
    cv = cover()
    cv.save(OUT / '封面_051_减亏74.63%_900x383.png', optimize=True)
    base.validate_glyphs()
    print('封面_051_减亏74.63%_900x383.png', cv.size)
    print('done')


if __name__ == '__main__':
    main()
