#!/usr/bin/env python3
"""037《一半算力造霸总？先把这笔账算完》配图与封面。

结构：两个分母 → 440 亿元这道账 → 三个数与两个指标。纯本地 Pillow，零扣费。
运行：/usr/local/bin/python3 _gen_037.py
"""
from pathlib import Path
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from _gen_charts_006 import f, HIRA, SONG, MONO

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = '#f3eee4', '#fffaf0', '#2c2925'
DIM, LINE, RUST, TEAL, GOLD = '#756d61', '#d4c9b8', '#ae422c', '#28695e', '#b9853d'
SOFT = '#f7e9e3'
FONTS = {'body': (HIRA, 0), 'bold': (HIRA, 2), 'title': (SONG, 1), 'number': (MONO, 1)}
GLYPHS, TEXT_BOXES = {}, []


def font(size, kind='body'):
    path, index = FONTS[kind]
    return f(path, size, index=index)


def put(d, x, y, text, size=28, color=INK, kind='body', right=1016):
    ff = font(size, kind)
    width = d.textlength(text, font=ff)
    assert x >= 0 and x + width <= right + 0.1, (text, x, width, right)
    box = d.textbbox((x, y), text, font=ff, anchor='lt')
    assert box[0] >= 0 and box[2] <= d._image.width and box[3] <= d._image.height, (text, box)
    for other, b in TEXT_BOXES:
        if min(box[2], b[2]) > max(box[0], b[0]) and min(box[3], b[3]) > max(box[1], b[1]):
            raise AssertionError(f'文本重叠: {text!r} / {other!r}')
    TEXT_BOXES.append((text, box))
    GLYPHS.setdefault(FONTS[kind], set()).update(text)
    d.text((x, y), text, font=ff, fill=color, anchor='lt')
    return box[3]


def center(d, cx, y, text, size, color=INK, kind='bold', safe=False):
    width = d.textlength(text, font=font(size, kind))
    if safe:
        assert width <= 351, (text, width)
    return put(d, cx - width / 2, y, text, size, color, kind, cx + width / 2 + 1)


def paragraph(d, x, y, text, width=936, size=27, color=INK, leading=43, kind='body'):
    lines, current = [], ''
    for char in text:
        if d.textlength(current + char, font=font(size, kind)) > width:
            lines.append(current)
            current = char
        else:
            current += char
    if current:
        lines.append(current)
    for line in lines:
        put(d, x, y, line, size, color, kind, x + width + 1)
        y += leading
    return y


def page(title, subtitle, number, height):
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (1080, height), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle((72, 42, 83, 64), fill=RUST)
    put(d, 100, 42, '一人短剧厂牌', 21, DIM, 'bold')
    put(d, 949, 42, number, 22, RUST, 'number')
    put(d, 72, 96, title, 44, INK, 'title', 1008)
    put(d, 72, 160, subtitle, 25, DIM, right=1008)
    d.line((72, 207, 1008, 207), fill=LINE, width=2)
    return im, d


def footer(d, y, lines):
    d.line((72, y, 1008, y), fill=LINE, width=2)
    for i, line in enumerate(lines):
        y = paragraph(d, 72, y + (16 if i == 0 else 8), line, size=21, color=DIM, leading=30)
    return y


def denominators():
    im, d = page('55% 和 10%，分母不一样', '两个数字可以同时成立，也可以同时不成立', '01', 1150)
    # 55% 面板
    d.rounded_rectangle((72, 236, 1008, 596), radius=14, fill=WHITE)
    put(d, 104, 256, '55%', 58, RUST, 'bold', 400)
    put(d, 300, 268, '全国 AI Token 消耗份额', 28, INK, 'bold', 980)
    put(d, 300, 306, '分子：AI 短剧 + 视频生成', 21, DIM, 'body', 980)
    bars = [('AI 短剧与视频生成', '55%', 0.55, RUST), ('电商与营销', '24%', 0.24, TEAL), ('软件开发', '15%', 0.15, GOLD)]
    y = 356
    for label, pct, ratio, color in bars:
        put(d, 104, y + 2, label, 20, DIM, 'body', 420)
        d.rounded_rectangle((430, y + 6, 430 + 480 * ratio, y + 34), radius=5, fill=color)
        put(d, 430 + 480 * ratio + 12, y + 2, pct, 22, color, 'bold', 980)
        y += 62
    put(d, 104, 545, '其余约 6% 为其他场景（100 - 55 - 24 - 15）。数据期：2026-06-03。', 19, DIM, 'body', 980)

    # 10% 面板
    d.rounded_rectangle((72, 616, 1008, 906), radius=14, fill=WHITE)
    put(d, 104, 636, '10%', 58, TEAL, 'bold', 400)
    put(d, 300, 648, '字节一家公司的总算力用途', 28, INK, 'bold', 980)
    put(d, 300, 686, '分子：视频生成模型的训练 + 推理', 21, DIM, 'body', 980)
    put(d, 104, 750, '分母是「字节的总算力」，不是「全国 Token」；', 23, INK, 'body', 980)
    put(d, 104, 786, '分子是「视频生成模型」，不是「短剧 + 视频生成」。', 23, INK, 'body', 980)
    put(d, 104, 838, '回应时间：2026-10-19。', 19, DIM, 'body', 980)

    d.rounded_rectangle((72, 926, 1008, 1006), radius=12, fill=INK)
    put(d, 100, 940, '分母不同 · 单位不同 · 范围不同', 22, '#bdb3a1', right=980)
    put(d, 100, 970, '两个数字不互斥，不能放在同一个句子里比较', 25, '#f0c588', 'bold', 980)

    footer(d, 1026, [
        '来源：中文在线《投资者关系活动记录表》2026-06-03；豆包公关负责人刘星 2026-10-19 微博回应（媒体转述）。',
        '55% 原文是 Token 份额，媒体标题写成「算力」；10% 是字节单家公司的算力用途。',
    ])
    return im


def cost_math():
    im, d = page('22 万部 × 20 万元 = 440 亿元', '上半年，仅抖音一个平台的 AI 短剧算力成本', '02', 1120)
    # 算式
    d.rounded_rectangle((72, 236, 1008, 436), radius=14, fill=WHITE)
    put(d, 100, 268, '22 万部', 40, RUST, 'bold', 340)
    put(d, 318, 278, '×', 34, DIM, 'body', 380)
    put(d, 372, 268, '20 万元', 40, TEAL, 'bold', 640)
    put(d, 618, 278, '=', 34, DIM, 'body', 680)
    put(d, 672, 268, '440 亿元', 40, INK, 'bold', 980)
    put(d, 100, 348, '「22 万部」和「20 万元」来自媒体转述，原文只写「另有数据显示」，未点名机构。', 19, DIM, 'body', 980)
    put(d, 100, 386, '计算：220,000 × 200,000 = 44,000,000,000 元。', 19, DIM, 'body', 980)

    # 对比条
    put(d, 72, 474, '和另一组数对照', 24, INK, 'bold', 700)
    rows = [
        ('上半年算力成本（仅抖音 AI 短剧）', '440 亿元', 440, RUST),
        ('全年 AI 剧漫剧市场规模（DataEye 预估）', '400 亿元+', 400, TEAL),
    ]
    y = 520
    for label, value, amount, color in rows:
        put(d, 72, y, label, 20, DIM, 'body', 1008)
        d.rounded_rectangle((72, y + 38, 72 + 780 * amount / 500, y + 78), radius=6, fill=color)
        put(d, 72 + 780 * amount / 500 + 12, y + 40, value, 24, color, 'bold', 1008)
        y += 112

    d.rounded_rectangle((72, 756, 1008, 892), radius=12, fill=SOFT)
    put(d, 100, 772, '成本和收入不是一个口径，不能直接相减；', 22, INK, 'body', 980)
    put(d, 100, 808, '但成本不可能长期高于收入。', 26, RUST, 'bold', 980)
    put(d, 100, 850, '所以 20 万元不可能是 22 万部的平均值。', 21, DIM, 'body', 980)

    footer(d, 912, [
        '来源：界面新闻 2026-10-15（22 万部、20 万元）；DataEye 2026 年预估经 36 氪 2026-08-04 转述。',
        '440 亿元为本号按两个公开数字相乘所得，不是官方统计；两组数的口径差异见正文。',
    ])
    return im


def three_numbers():
    im, d = page('三个数，两个指标', '用自己的账单，替代行业平均数', '03', 1180)
    inputs = [
        ('01', '成片分钟数', '最终交付多少分钟', RUST),
        ('02', '生成次数', '一共提交多少次生成，含废片', TEAL),
        ('03', '算力 / Token 账单', '这一部实际花了多少钱', GOLD),
    ]
    y = 236
    for num, head, body, color in inputs:
        d.rounded_rectangle((72, y, 1008, y + 128), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 128), radius=4, fill=color)
        put(d, 104, y + 16, num, 21, color, 'number', 200)
        put(d, 150, y + 12, head, 28, INK, 'bold', 980)
        put(d, 150, y + 62, body, 21, DIM, 'body', 980)
        y += 144

    y += 12
    put(d, 72, y, '算两个指标', 25, INK, 'bold', 700)
    y += 48
    formulas = [
        ('元 / 成片分钟', '账单 ÷ 成片分钟', RUST),
        ('抽卡倍率', '生成次数 ÷ 成片镜头数', TEAL),
    ]
    for label, formula, color in formulas:
        d.rounded_rectangle((72, y, 1008, y + 108), radius=14, fill=SOFT)
        put(d, 100, y + 18, label, 24, color, 'bold', 980)
        put(d, 100, y + 60, formula, 27, INK, 'body', 980)
        y += 124

    d.rounded_rectangle((72, y + 4, 1008, y + 92), radius=12, fill=INK)
    put(d, 100, y + 20, '还没有账单的，先做一部 1 分钟样片', 22, '#bdb3a1', right=980)
    put(d, 100, y + 52, '把三个数记全，比争论 55% 有用', 25, '#f0c588', 'bold', 980)

    footer(d, y + 112, [
        '指标定义与算法为本号建议（C 级），不是平台或机构标准。',
        '行业数字的来源与口径见正文；不要用行业平均数替代自己的账单。',
    ])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    center(d, 450, 54, '一半算力造霸总？', 22, '#f0c588', 'bold', True)
    center(d, 450, 92, '55% 和 10% 没对齐', 36, WHITE, 'title', True)
    center(d, 450, 158, '22 万部 × 20 万元 = 440 亿元', 23, '#8fc0b4', 'bold', True)
    d.line((300, 212, 600, 212), fill='#766657', width=2)
    center(d, 450, 230, '先把这笔账算完', 22, '#d8cdbb', 'body', True)
    center(d, 450, 286, '分母不同，结论就不同', 19, '#bdb3a1', 'body', True)
    return im


def validate_glyphs():
    for (path, index), chars in GLYPHS.items():
        ff = TTFont(path, fontNumber=index)
        cmap = ff.getBestCmap()
        missing = sorted(c for c in chars if ord(c) not in cmap)
        ff.close()
        assert not missing, (path, index, missing)
    print('PASS: font glyph coverage and', len(TEXT_BOXES), 'text box checks')


def save_png(im, path):
    im.quantize(colors=192, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(path, optimize=True)
    size = path.stat().st_size
    assert size < 220 * 1024, (path, size)
    print(path.name, im.size, f'{size / 1024:.1f} KB')


if __name__ == '__main__':
    for name, maker in [('037_图1_两个分母_1080.png', denominators),
                        ('037_图2_440亿_1080.png', cost_math),
                        ('037_图3_三个数_1080.png', three_numbers)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_037_算力账_900x383.png')
    print('done')
