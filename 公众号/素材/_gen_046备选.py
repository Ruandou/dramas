#!/usr/bin/env python3
"""046《9月重点微短剧备案 224 部》配图与封面。纯本地 Pillow。"""
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


def grow():
    im, d = page('备案量连涨，双核占比回落', '2026 年 7—9 月 / 重点微短剧规划备案', '01', 1140)
    base, top = 720, 250
    scale = (base - top) / 250

    for x, label, val in [(240, '7 月', 143), (540, '8 月', 207), (840, '9 月', 224)]:
        h = val * scale
        color = GOLD if val == 224 else RUST
        d.rounded_rectangle((x - 82, base - h, x + 82, base), radius=8, fill=color)
        put(d, x - d.textlength(str(val), font=font(48, 'number')) / 2, base - h - 62,
            str(val), 48, INK, 'number', x + 100)
        put(d, x - d.textlength(label, font=font(23, 'bold')) / 2, base + 16, label, 23, DIM, 'bold', x + 100)
    d.line((72, base, 1008, base), fill=INK, width=3)
    put(d, 72, 220, '9 月较 8 月 +17 部 / +8.2%', 22, TEAL, 'bold', 700)

    # stacked share bars
    y1 = 830
    put(d, 72, y1 - 44, '双核（都市 + 传奇）占当月备案', 22, DIM, 'bold', 700)
    for i, (label, core, other) in enumerate([('8 月', 62.8, 37.2), ('9 月', 54.9, 45.1)]):
        y = y1 + i * 74
        put(d, 72, y + 8, label, 23, INK, 'bold', 160)
        x0, x1 = 178, 1008
        split = x0 + (x1 - x0) * core / 100
        d.rounded_rectangle((x0, y, split, y + 42), radius=6, fill=RUST)
        d.rounded_rectangle((split, y, x1, y + 42), radius=6, fill='#e2d8c7')
        put(d, x0 + 16, y + 6, f'{core}%', 21, WHITE, 'number', split - 20)
        put(d, split + 16, y + 6, f'{other}%', 21, DIM, 'number', x1 - 10)

    footer(d, 1020, [
        '来源：总局 9 月公示经电影界 2026-10-18、剧短短 2026-10-11 转述。',
        '8 月分布见首都广电（光明网 2026-09-14 转载）；份额按 207 / 224 直接相除。',
        '备案为规划备案，不等于发行许可或上线。',
    ])
    return im


def slope():
    im, d = page('一个月，传奇少了 10.8 个百分点', '题材份额：8 月 → 9 月 / 按当月备案总数计算', '02', 1100)
    left, right = 300, 780
    top, bottom = 300, 900
    vmax = 40.0

    def yy(v):
        return bottom - (v - 0) / vmax * (bottom - top)

    for g in (10, 20, 30, 40):
        y = yy(g)
        d.line((left, y, right, y), fill='#ddd3c2', width=1)
        put(d, 82, y - 14, f'{g}%', 20, DIM, 'number', 150)
    d.line((left, top, left, bottom), fill=LINE, width=2)
    d.line((right, top, right, bottom), fill=LINE, width=2)
    put(d, left - 40, 262, '8 月', 24, DIM, 'bold', left + 30)
    put(d, right - 40, 262, '9 月', 24, DIM, 'bold', right + 30)

    series = [
        ('都市', 26.1, 29.0, RUST, 0),
        ('传奇', 36.7, 25.9, TEAL, 0),
        ('革命', 7.2, 9.8, GOLD, 0),
    ]
    for name, a, b, color, _ in series:
        d.line((left, yy(a), right, yy(b)), fill=color, width=5)
        d.ellipse((left - 9, yy(a) - 9, left + 9, yy(a) + 9), fill=color)
        d.ellipse((right - 9, yy(b) - 9, right + 9, yy(b) + 9), fill=color)
        put(d, left - 250, yy(a) - 18, f'{name} {a}%', 22, color, 'bold', left - 20)
        put(d, right + 22, yy(b) - 18, f'{b}%', 22, color, 'bold', right + 170)

    put(d, 72, 946, '都市 +2.9pp', 24, RUST, 'bold', 420)
    put(d, 400, 946, '传奇 -10.8pp', 24, TEAL, 'bold', 740)
    put(d, 770, 946, '革命 +2.6pp', 24, GOLD, 'bold', 1010)
    footer(d, 990, [
        '数据：总局 9 月公示（电影界 2026-10-18、剧短短 2026-10-11）；8 月分布见首都广电（光明网 2026-09-14 转载）。',
        '9 月仅公布前三名与「16 种」，第四名之后未公开，本图不展示。',
    ])
    return im


def accounts():
    im, d = page('三个数，三本账', '规划备案 / 发行许可 / 电视剧（网络剧）发行许可', '03', 1160)
    blocks = [
        ('224 部', '9 月重点微短剧规划备案', '开机前的登记；本号用它看供给结构。', RUST),
        ('159 部 · 5396 集', '4—6 月网络剧片发行许可', '微短剧单独一栏，占同期网络剧片集数 72.6%。', TEAL),
        ('125 部 · 1652 集', '7—9 月电视剧（网络剧）发行许可', '通告未列微短剧一栏，不能当微短剧过审数。', GOLD),
    ]
    y = 250
    for big, head, body, color in blocks:
        d.rounded_rectangle((72, y, 1008, y + 190), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 190), radius=4, fill=color)
        put(d, 108, y + 24, big, 40, color, 'title', 520)
        put(d, 108, y + 84, head, 26, INK, 'bold', 960)
        paragraph(d, 108, y + 126, body, width=850, size=21, color=DIM, leading=32)
        y += 206

    d.rounded_rectangle((72, y + 6, 1008, y + 104), radius=12, fill=INK)
    put(d, 104, y + 22, '时间窗不同、统计范围不同', 22, '#bdb3a1', right=980)
    put(d, 104, y + 58, '三个数不能直接相减', 30, '#f0c588', 'bold', 980)

    footer(d, y + 124, [
        'A 级：总局 Q2、Q3 发行许可通告（2026-07-13 / 2026-10-23）。',
        '9 月备案 224 部为 B 级；72.6% 由 5396 / 7436 相除得出。',
    ])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 48, 30, '一人短剧厂牌', 18, '#bdb3a1', right=600)
    put(d, 48, 88, '9 月重点微短剧备案', 21, '#f0c588', 'bold', 600)
    put(d, 48, 120, '224 部', 74, WHITE, 'title', 600)
    put(d, 48, 232, '都市回到第一', 28, '#8fc0b4', 'bold', 600)
    put(d, 48, 276, '传奇少了 10.8 个百分点', 19, '#d8cdbb', 'body', 600)
    d.line((48, 318, 560, 318), fill='#4a443c', width=1)
    put(d, 48, 332, '三个数，三本账', 16, '#8f8576', 'body', 600)

    # 右侧：8→9 月份额斜率
    x0, x1 = 636, 846
    put(d, x0, 74, '8 月', 15, '#8f8576', 'bold', x0 + 60)
    put(d, x1 - 34, 74, '9 月', 15, '#8f8576', 'bold', 900)
    d.line((x0, 96, x0, 300), fill='#4a443c', width=1)
    d.line((x1, 96, x1, 300), fill='#4a443c', width=1)
    d.line((x0, 150, x1, 122), fill='#ae422c', width=4)
    d.line((x0, 128, x1, 244), fill='#5f9e92', width=4)
    for x, y, c in [(x0, 150, '#ae422c'), (x1, 122, '#ae422c'), (x0, 128, '#5f9e92'), (x1, 244, '#5f9e92')]:
        d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=c)
    put(d, x1 + 10, 108, '都市', 15, '#d8cdbb', 'body', 900)
    put(d, x1 + 10, 236, '传奇', 15, '#d8cdbb', 'body', 900)
    put(d, 600, 300, '题材份额 8→9 月', 14, '#8f8576', 'body', 900)
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
    for name, maker in [('046备选_图1_备案与双核_1080.png', grow),
                        ('046备选_图2_题材份额_1080.png', slope),
                        ('046备选_图3_三本账_1080.png', accounts)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_046备选_224部_900x383.png')
    print('done')
