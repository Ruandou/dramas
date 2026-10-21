#!/usr/bin/env python3
"""031 重做版《9 月备案 296 部：短剧集 12 部，连降三个月》配图与封面。

结构：部数/集数三个分母 → 三个月反向 → 集数区间。纯本地 Pillow，零扣费。
运行：/usr/local/bin/python3 _gen_031_v2.py
"""
from pathlib import Path
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from _gen_charts_006 import f, HIRA, SONG, MONO

OUT = Path(__file__).resolve().parent
SAMPLES = OUT.parents[1] / 'samples'
PAPER, WHITE, INK = '#f3eee4', '#fffaf0', '#2c2925'
DIM, LINE, RUST, TEAL, GOLD = '#756d61', '#d4c9b8', '#ae422c', '#28695e', '#b9853d'
OLIVE, GREY = '#7a8b5e', '#a2988a'
FONTS = {'body': (HIRA, 0), 'bold': (HIRA, 2), 'title': (SONG, 1), 'number': (MONO, 1)}
GLYPHS, TEXT_BOXES = {}, []
TITLE = '9 月备案 296 部：短剧集 12 部，连降三个月'
DIGEST = '9 月电视剧（网络剧）备案 296 部、3,067 集。逐行复算：短剧集 12 部 141 集，连降三个月；总量涨的是网络故事片和中剧。两套备案口径别混。'
FIGURES = [
    ('031v2_图1_三个分母_1080.png', '同一个 296，三个分母'),
    ('031v2_图2_三个月反向_1080.png', '三个月，总量与短剧集走反方向'),
    ('031v2_图3_集数区间_1080.png', '集数不能反推类别'),
]


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
    put(d, 72, 96, title, 46, INK, 'title')
    put(d, 72, 162, subtitle, 25, DIM)
    d.line((72, 209, 1008, 209), fill=LINE, width=2)
    return im, d


def footer(d, y, lines):
    d.line((72, y, 1008, y), fill=LINE, width=2)
    for line in lines:
        y = paragraph(d, 72, y + 16, line, size=21, color=DIM, leading=30)
    return y


def vline(d, x, y0, y1, color=LINE):
    y = y0
    while y < y1:
        d.line((x, y, x, min(y + 8, y1)), fill=color, width=2)
        y += 15


def chart_one():
    im, d = page('同一个 296，三个分母', '部数、网络剧部数、集数，同一批项目三种读法', '01', 1200)
    d.rounded_rectangle((72, 238, 1008, 628), radius=16, fill=WHITE)
    put(d, 100, 262, '网络故事片 176 部', 28, GOLD, 'bold')
    put(d, 780, 268, '9 月最大类别', 20, DIM, right=980)
    for i, (label, value, pct) in enumerate((
        ('占全部备案 296 部', '59.5', 59.5),
        ('占网络剧 248 部', '71.0', 71.0),
        ('占全部集数 3,067 集', '6.9', 6.9),
    )):
        y = 330 + i * 84
        put(d, 100, y + 4, label, 22, INK, right=356)
        bar = max(6, int(460 * pct / 75))
        d.rounded_rectangle((370, y, 370 + bar, y + 28), radius=6, fill=GOLD)
        put(d, 960 - d.textlength(f'{value}%', font=font(26, 'bold')), y - 2,
            f'{value}%', 26, GOLD, 'bold', 965)
    put(d, 100, 572, '换分母，网络故事片可以从 6.9% 变成 71.0%。', 21, DIM, right=980)

    d.rounded_rectangle((72, 648, 1008, 996), radius=16, fill=WHITE)
    put(d, 100, 668, '其余五类，三个分母各是多少', 22, INK, 'bold')
    for cx, label in ((500, '占 296 部'), (700, '占网络剧 248 部'), (900, '占 3,067 集')):
        center(d, cx, 712, label, 18, DIM, 'bold')
    rows = [
        ('中剧', '17.9', '21.4', '38.6', OLIVE, False),
        ('短剧集', '4.1', '4.8', '4.6', RUST, True),
        ('季播剧', '2.0', '2.4', '2.6', GREY, False),
        ('互动剧', '0.3', '0.4', '1.0', GREY, False),
        ('电视剧 · 常规剧集', '16.2', None, '46.3', TEAL, False),
    ]
    y = 752
    for label, v1, v2, v3, color, highlight in rows:
        if highlight:
            d.rounded_rectangle((88, y - 6, 992, y + 38), radius=8, fill='#f7e9e3')
        put(d, 100, y, label, 22, RUST if highlight else INK, 'bold', 330)
        for cx, value in ((500, v1), (700, v2), (900, v3)):
            if value is None:
                center(d, cx, y, '不适用', 18, DIM, 'body')
            else:
                center(d, cx, y - 2, f'{value}%', 22, color, 'bold')
        y += 50
    d.rounded_rectangle((72, 1016, 1008, 1106), radius=14, fill=INK)
    put(d, 100, 1038, '三个分母下，短剧集都没超过 5%；网络故事片却能读出 71.0%。', 23, WHITE, right=980)
    put(d, 100, 1074, '占比不是属性，是分数——先看分母。', 23, '#f0c588', 'bold', right=980)
    footer(d, 1136, ['来源：广电总局 2026 年 9 月备案公示附件（296 行）· 占比为本地逐行复算，分母写在列头。'])
    return im


def chart_two():
    im, d = page('三个月，总量与短剧集走反向', '2026 年 7–9 月 · 同口径备案公示', '02', 1180)
    d.rounded_rectangle((72, 238, 1008, 596), radius=16, fill=WHITE)
    put(d, 100, 258, '备案总量（部）', 24, INK, 'bold')
    put(d, 760, 262, '三个月 +88', 22, RUST, 'bold', right=980)
    xs = (240, 570, 900)
    totals = (208, 254, 296)
    ys = [530 - int((v - 190) / 120 * 200) for v in totals]
    d.line(list(zip(xs, ys)), fill=TEAL, width=5, joint='curve')
    for x, y, v in zip(xs, ys, totals):
        d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=WHITE, outline=TEAL, width=4)
        center(d, x, y - 54, str(v), 32, TEAL, 'bold')
    for x, month in zip(xs, ('7 月', '8 月', '9 月')):
        center(d, x, 548, month, 22, DIM)
    center(d, 405, 474, '+46', 20, RUST, 'bold')
    center(d, 735, 399, '+42', 20, RUST, 'bold')

    d.rounded_rectangle((72, 616, 1008, 930), radius=16, fill=WHITE)
    put(d, 100, 636, '短剧集（部）', 24, RUST, 'bold')
    put(d, 760, 640, '三个月 -6', 22, RUST, 'bold', right=980)
    for x, v in zip(xs, (18, 14, 12)):
        h = int(v / 20 * 150)
        top = 860 - h
        d.rounded_rectangle((x - 55, top, x + 55, 860), radius=8, fill=RUST)
        center(d, x, top - 44, str(v), 30, RUST, 'bold')
    for x, month in zip(xs, ('7 月', '8 月', '9 月')):
        center(d, x, 872, month, 22, DIM)
    center(d, 405, 790, '-4', 20, RUST, 'bold')
    center(d, 735, 806, '-2', 20, RUST, 'bold')

    d.rounded_rectangle((72, 950, 1008, 1070), radius=14, fill=INK)
    put(d, 100, 970, '同期：网络故事片 104→143→176（+72）', 22, WHITE, right=980)
    put(d, 100, 1006, '中剧 33→38→53（+20）；短剧集 18→14→12（-6）', 22, '#f0c588', 'bold', right=980)
    footer(d, 1110, ['来源：广电总局 7 月（2026-07-27）、8 月（2026-08-31）、9 月（2026-09-29）备案公示通知，数据为通稿原数。'])
    return im


def chart_three():
    im, d = page('集数不能反推类别', '2026 年 9 月备案附件 · 各类别集数区间', '03', 1140)
    x0, span = 300, 680

    def px(v):
        return x0 + v / 42 * span

    for value in (12, 24):
        vline(d, px(value), 248, 870)
        center(d, px(value), 220, f'{value} 集', 20, RUST, 'bold')
    rows = [
        ('网络故事片', 1, 3, 1.2, GOLD, '1-3 集，均值 1.2', False),
        ('季播剧', 4, 24, 13.3, GREY, '4-24 集', False),
        ('短剧集', 6, 16, 12, RUST, '6-16 集', True),
        ('中剧', 12, 30, 22.4, OLIVE, '12-30 集', False),
        ('电视剧 · 常规剧集', 18, 40, 29.6, TEAL, '18-40 集', False),
        ('互动剧', 30, 30, 30, GREY, '30 集', False),
    ]
    y = 286
    for label, lo, hi, marker, color, caption, highlight in rows:
        put(d, 72, y + 6, label, 24, RUST if highlight else INK, 'bold', 290)
        put(d, 72, y + 42, caption, 19, DIM, right=290)
        if lo == hi:
            mx = px(marker)
            d.ellipse((mx - 9, y + 20, mx + 9, y + 38), fill=color)
        else:
            left, right = px(lo), px(hi)
            d.rounded_rectangle((left, y + 16, right, y + 42), radius=7, fill=color)
            if right - left >= 30:
                mx = px(marker)
                d.ellipse((mx - 7, y + 22, mx + 7, y + 36), fill=WHITE, outline=color, width=3)
        y += 104
    d.rounded_rectangle((72, 925, 1008, 1060), radius=14, fill=WHITE)
    put(d, 100, 945, '12 集：短剧集、中剧、季播剧都有。', 23, INK, right=980)
    put(d, 100, 983, '24 集：中剧 32 部、常规剧集 15 部、季播剧 1 部。', 23, INK, right=980)
    put(d, 100, 1021, '类别看「备注」列，不看集数。', 23, RUST, 'bold', right=980)
    footer(d, 1085, ['复算：附件「集数」列按「备注」分组取最小/最大/均值；短剧集圆点为中位数 12。'])
    return im


def cover_a():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    for i, (w, color) in enumerate([(150, '#b55b32'), (104, '#28695e'), (58, '#b9853d')]):
        y = 104 + i * 44
        d.rounded_rectangle((40, y, 40 + w, y + 30), radius=8, fill=color)
    center(d, 450, 74, '9 月备案 296 部', 22, '#f0c588', 'bold', True)
    center(d, 450, 116, '短剧集 12 部', 44, WHITE, 'title', True)
    center(d, 450, 174, '连降三个月', 44, WHITE, 'title', True)
    d.line((306, 252, 594, 252), fill='#766657', width=2)
    center(d, 450, 268, '总量 208→254→296', 20, '#bdb3a1', 'body', True)
    center(d, 450, 304, '但它不是微短剧', 20, '#8fc0b4', 'bold', True)
    return im


def cover_b():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), PAPER)
    d = ImageDraw.Draw(im)
    d.text((42, 92), '296', font=font(100, 'number'), fill='#e7ddcc', anchor='lt')
    d.rectangle((38, 28, 44, 50), fill=RUST)
    put(d, 64, 28, '一人短剧厂牌', 19, DIM, right=900)
    center(d, 450, 74, '同一批 296 部备案', 21, TEAL, 'bold', True)
    center(d, 450, 110, '4.1%', 84, RUST, 'number', True)
    center(d, 450, 206, '是短剧集的部数占比', 22, INK, 'body', True)
    center(d, 450, 258, '按集数算，是 4.6%', 22, DIM, 'body', True)
    d.line((330, 306, 570, 306), fill=LINE, width=2)
    center(d, 450, 322, '两个分母，两个答案', 19, TEAL, 'bold', True)
    return im


def cover_review(covers):
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (1500, 1040), '#e5e2dc')
    d = ImageDraw.Draw(im)
    labels = ['A / 深色：12 部 · 连降三个月', 'B / 浅色：4.1% 这个占比']
    share = [('短剧集 12 部', '一人短剧厂牌'), ('短剧集占 4.1%', '一人短剧厂牌')]
    for index, cover in enumerate(covers):
        y = 35 + index * 500
        put(d, 28, y, labels[index], 26, INK, 'bold', 1450)
        im.paste(cover, (28, y + 55))
        d.rectangle((286, y + 55, 669, y + 437), outline='#b48e60', width=1)
        crop = cover.crop((258, 0, 641, 383)).resize((142, 142), Image.Resampling.LANCZOS)
        for j, (bg, fg) in enumerate([('#ffffff', INK), ('#191919', '#f5efe4')]):
            x = 958 + j * 254
            d.rounded_rectangle((x, y + 55, x + 228, y + 437), radius=16, fill=bg)
            put(d, x + 18, y + 75, ['浅色分享卡', '深色分享卡'][j], 19, fg, right=x + 217)
            im.paste(crop, (x + 43, y + 129))
            put(d, x + 18, y + 296, share[index][0], 18, fg, right=x + 217)
            put(d, x + 18, y + 330, share[index][1], 16, fg, right=x + 217)
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
    if path.parent == OUT and not path.name.startswith('对照'):
        assert size < 200 * 1024, (path, size)
    print(path.name, im.size, f'{size / 1024:.1f} KB')


if __name__ == '__main__':
    charts = [chart_one(), chart_two(), chart_three()]
    covers = [cover_a(), cover_b()]
    validate_glyphs()
    for im, (name, _) in zip(charts, FIGURES):
        save_png(im, OUT / name)
    cover_names = ['封面_031v2_A_连降三月_900x383.png', '封面_031v2_B_占比4.1_900x383.png']
    for im, name in zip(covers, cover_names):
        save_png(im, OUT / name)
    save_png(cover_review(covers), OUT / '对照_031v2封面两方向.png')
    sheet = Image.new('RGB', (1212, 640), '#e5e2dc')
    for i, im in enumerate(charts):
        thumb = im.copy()
        thumb.thumbnail((380, 590), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (12 + i * 402, 12))
    save_png(sheet, SAMPLES / '031v2_正文配图手机宽预览.png')
    body = (OUT.parent / '文章' / '031_发布版.md').read_text()
    assert len(TITLE) <= 64 and len(DIGEST) <= 120, (len(TITLE), len(DIGEST))
    for index, (name, caption) in enumerate(FIGURES, 1):
        assert f'【图 {index}：{caption}】' in body, (index, caption)
    print('PASS: figure captions match body; title', len(TITLE), 'digest', len(DIGEST))
