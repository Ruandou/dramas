#!/usr/bin/env python3
"""046《AI 剧 400 亿的市场，和你的万播 5 块钱》配图与封面。纯本地 Pillow。"""
from pathlib import Path
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from _gen_charts_006 import f, HIRA, SONG, MONO

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = '#f3eee4', '#fffaf0', '#2c2925'
DIM, LINE, RUST, TEAL, GOLD = '#756d61', '#d4c9b8', '#ae422c', '#28695e', '#b9853d'
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


def center(d, cx, y, text, size, color=INK, kind='bold', safe=False, width=351):
    w = d.textlength(text, font=font(size, kind))
    if safe:
        assert w <= width, (text, w, width)
    return put(d, cx - w / 2, y, text, size, color, kind, cx + w / 2 + 1)


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
    put(d, 72, 96, title, 46, INK, 'title', 1008)
    put(d, 72, 162, subtitle, 25, DIM, right=1008)
    d.line((72, 209, 1008, 209), fill=LINE, width=2)
    return im, d


def footer(d, y, lines):
    d.line((72, y, 1008, y), fill=LINE, width=2)
    for i, line in enumerate(lines):
        y = paragraph(d, 72, y + (16 if i == 0 else 8), line, size=21, color=DIM, leading=30)
    return y


def unit_price():
    im, d = page('万播从 30—100 元掉到 5—10 元', 'AI 剧漫剧行业监测 / 2025 下半年 → 2026 年', '01', 1100)
    x0, x1 = 300, 900
    vmax = 110

    def xx(v):
        return x0 + (v - 0) / vmax * (x1 - x0)

    for g in (0, 25, 50, 75, 100):
        x = xx(g)
        d.line((x, 268, x, 500), fill='#ddd3c2', width=1)
        put(d, x - 20, 508, str(g), 19, DIM, 'number', x + 40)

    for label, lo, hi, color, y in [('2025 下半年', 30, 100, RUST, 300), ('2026 年', 5, 10, TEAL, 410)]:
        put(d, 72, y + 8, label, 23, INK, 'bold', 280)
        d.rounded_rectangle((xx(lo), y, xx(hi), y + 46), radius=8, fill=color)
        put(d, xx(hi) + 14, y + 8, f'{lo}—{hi} 元', 22, color, 'bold', 1008)

    put(d, 72, 570, '同样播放量，收入少 80%—90%', 26, INK, 'bold', 700)

    cards = [
        ('100 万播放', '3,000—10,000 元', '500—1,000 元', RUST),
        ('5000 万播放', '15—50 万元', '2.5—5 万元', TEAL),
    ]
    y = 632
    for head, before, after, color in cards:
        d.rounded_rectangle((72, y, 1008, y + 160), radius=12, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 160), radius=4, fill=color)
        put(d, 104, y + 18, head, 22, DIM, 'bold', 400)
        put(d, 104, y + 58, '2025 下半年', 19, DIM, 'body', 300)
        put(d, 300, y + 50, before, 30, color, 'title', 640)
        put(d, 104, y + 108, '2026 年', 19, DIM, 'body', 300)
        put(d, 300, y + 100, after, 30, INK, 'title', 640)
        y += 176

    footer(d, 1022, [
        '数据：DataEye-ADX；30—100 元（2025 下半年）→ 5—10 元（2026 年）。',
        '行业区间值，不是平台结算单；不同平台、题材差异大。',
    ])
    return im


def three_numbers():
    im, d = page('三个数，三个来源', 'AI 剧漫剧市场 / 红果广告收入 / 单位：亿元', '02', 1100)
    x0, x1 = 250, 900
    vmax = 450

    def xx(v):
        return x0 + v / vmax * (x1 - x0)

    rows = [
        ('400 亿', 400, GOLD, 'AI 剧漫剧市场（全口径预测）', '机构预测'),
        ('240 亿', 240, TEAL, 'AI 漫剧市场（窄口径预测）', '机构预测'),
        ('200 亿', 200, RUST, '红果广告收入', '媒体口径·非审计'),
    ]
    y = 290
    for big, val, color, label, tag in rows:
        put(d, 72, y - 6, big, 30, color, 'title', 240)
        d.rounded_rectangle((x0, y, xx(val), y + 54), radius=8, fill=color)
        put(d, 72, y + 62, label, 21, DIM, 'body', 620)
        put(d, 850, y + 12, tag, 18, color, 'bold', 1000)
        y += 172

    d.rounded_rectangle((72, 820, 1008, 918), radius=12, fill=INK)
    put(d, 104, 836, '400 亿不是红果的收入', 21, '#bdb3a1', right=980)
    put(d, 104, 870, '一个是市场预测，一个是平台广告', 27, '#f0c588', 'bold', 980)

    footer(d, 968, [
        '数据：新浪财经 2026-10-15（市场）；钛媒体 2026-09-23（红果广告）。',
        '红果未公开财报；200 亿为媒体口径，400/240 亿为机构预测。',
    ])
    return im


def survival():
    im, d = page('22.19 万部里，1.3% 过线', '2026 上半年抖音端新增 AI 剧漫剧 / 每个点约 222 部', '03', 1180)
    cols, rows = 40, 25
    step, size = 24, 14
    left, top = 72, 240
    hi = {4, 9, 15, 22, 27, 31, 96, 142, 203, 287, 356, 431, 512}
    dark = {15, 96, 287, 431, 512}
    for i in range(cols * rows):
        cx = left + (i % cols) * step
        cy = top + (i // cols) * step
        if i in dark:
            color = RUST
        elif i in hi:
            color = GOLD
        else:
            color = '#e5dccb'
        d.rounded_rectangle((cx, cy, cx + size, cy + size), radius=3, fill=color)

    put(d, 72, 846, '1,000 个点 ≈ 22.19 万部', 21, DIM, 'body', 500)
    d.rounded_rectangle((72, 890, 92, 910), radius=3, fill=RUST)
    put(d, 104, 886, '破亿：1,055 部，0.48%（5 个点）', 21, RUST, 'bold', 760)
    d.rounded_rectangle((72, 934, 92, 954), radius=3, fill=GOLD)
    put(d, 104, 930, '过 5000 万播放：1.3%（13 个点，其中 5 个破亿）', 21, GOLD, 'bold', 800)
    put(d, 72, 986, '剩下 98.7%：半年内不回本', 27, INK, 'bold', 700)

    footer(d, 1046, [
        '数据：DataEye-ADX；2026 上半年抖音端新增 22.19 万部（新浪财经 2026-10-15）。',
        '5000 万播放为业内常用盈亏线；样本为行业区间，非全行业审计。',
    ])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 18, '#bdb3a1', right=500)
    put(d, 44, 82, 'AI 剧漫剧市场（预测）', 19, '#f0c588', 'bold', 430)
    put(d, 44, 112, '400 亿', 62, WHITE, 'title', 440)
    put(d, 44, 206, '红果广告收入（媒体口径）', 16, '#bdb3a1', 'body', 430)
    put(d, 44, 234, '200 亿', 38, '#8fc0b4', 'title', 440)
    put(d, 44, 300, '三本账，别混算', 17, '#8f8576', 'body', 430)

    d.line((500, 70, 500, 320), fill='#4a443c', width=1)
    put(d, 540, 82, '你的万播单价', 19, '#f0c588', 'bold', 880)
    put(d, 540, 116, '5—10 元', 54, WHITE, 'title', 880)
    put(d, 540, 196, '2025 下半年还是', 17, '#bdb3a1', 'body', 880)
    put(d, 540, 222, '30—100 元', 30, '#c9a07a', 'title', 880)
    put(d, 540, 286, '同样播放量，收入少 80%—90%', 16, '#d8cdbb', 'body', 880)
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
    assert size < 200 * 1024, (path, size)
    print(path.name, im.size, f'{size / 1024:.1f} KB')


if __name__ == '__main__':
    for name, maker in [('046_图2_万播单价_1080.png', unit_price),
                        ('046_图1_三个数_1080.png', three_numbers),
                        ('046_图3_回本漏斗_1080.png', survival)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_046_400亿与5块_900x383.png')
    print('done')
