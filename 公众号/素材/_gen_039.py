#!/usr/bin/env python3
"""039《红果 10 月取消系列系数，第二部起不再翻倍》配图与封面。

结构：拆剧金额前后对照 → 三个数字的日期。纯本地 Pillow，零扣费。
运行：cd 公众号/素材 && python3 _gen_039.py
"""
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


def series_split():
    im, d = page('一部 360 分钟，拆成 3 部', '每部 120 分钟、热度都过 7000 万，单部按 20 万算', '01', 1120)
    panels = [
        (236, '9 月 22 日之前', [(20, TEAL), (40, RUST), (40, RUST)], '合计 100 万', RUST),
        (560, '10 月起', [(20, TEAL), (20, TEAL), (20, TEAL)], '合计 60 万', TEAL),
    ]
    for top, label, rows, total, color in panels:
        d.rounded_rectangle((72, top, 1008, top + 304), radius=14, fill=WHITE)
        put(d, 104, top + 18, label, 24, DIM, 'bold', 600)
        y = top + 60
        for i, (value, bar_color) in enumerate(rows):
            put(d, 104, y + 8, f'第 {i + 1} 部', 22, INK, 'body', 290)
            width = value * 7.5
            d.rounded_rectangle((300, y + 8, 300 + width, y + 42), radius=6, fill=bar_color)
            put(d, 300 + width + 16, y + 10, f'{value} 万', 24, bar_color, 'bold', 900)
            y += 60
        put(d, 104, top + 252, total, 32, color, 'bold', 600)
        put(d, 420, top + 258, '系数乘在活动金额上' if top == 236 else '三部各拿一份，不再翻倍', 20, DIM, 'body', 980)

    d.rounded_rectangle((72, 884, 1008, 980), radius=12, fill=INK)
    put(d, 100, 900, '上限之间的差', 22, '#bdb3a1', right=600)
    put(d, 100, 932, '少 40 万', 30, '#f0c588', 'bold', 600)
    put(d, 360, 940, '热度低一档，金额也低，差额跟着缩', 21, '#bdb3a1', right=980)

    footer(d, 1000, [
        '依据：红果 2.0（09-22 更新）；流媒体网 07-29（第二部 2 倍、系列最多 3 部）。',
        '20 万为单部上限；100 万与 60 万为本号按上限粗算（C 级），不是结算承诺。',
    ])
    return im


def three_dates():
    im, d = page('三个数字，三个日期', '并排写进「十月转向」，容易读成同一次改动', '02', 1040)
    axis_y = 402
    d.line((140, axis_y, 940, axis_y), fill=LINE, width=3)

    nodes = [
        (200, '2026-05-11', '真人剧 IAP 分成\n70%→80%', DIM),
        (470, '2026-07-29', '热度 5000 以上\n单部最高 20 万', DIM),
        (740, '2026-09-22', '红果 2.0：取消\n系列剧规模系数', RUST),
    ]
    for x, date, body, color in nodes:
        d.ellipse((x - 11, axis_y - 11, x + 11, axis_y + 11), fill=color)
        put(d, x - 78, 330, date, 24, color, 'number', x + 78)
        lines = body.split('\n')
        for i, line in enumerate(lines):
            put(d, x - 100, axis_y + 34 + i * 32, line, 20, INK if color == DIM else RUST, 'body', x + 100)

    d.line((770, axis_y, 916, axis_y), fill=TEAL, width=3)
    d.polygon([(916, axis_y - 9), (936, axis_y), (916, axis_y + 9)], fill=TEAL)
    put(d, 790, axis_y - 42, '10 月起执行', 21, TEAL, 'bold', 990)

    d.rounded_rectangle((72, 560, 1008, 760), radius=14, fill=WHITE)
    put(d, 104, 584, '只有 9 月 22 日那条，是这次改的', 27, INK, 'bold', 980)
    put(d, 104, 630, '80% 在 5 月，20 万在 7 月。两个数字都真，日期不在 10 月。', 21, DIM, 'body', 980)
    put(d, 104, 676, '红果这轮只删掉一个乘法：第二部起，不再翻倍。', 24, RUST, 'bold', 980)

    d.rounded_rectangle((72, 784, 1008, 872), radius=12, fill=INK)
    put(d, 100, 798, '三件事并排，只有一件发生在 9 月 22 日', 22, '#bdb3a1', right=980)
    put(d, 100, 830, '另两个数字早已生效，不是十月新政', 25, '#f0c588', 'bold', 980)

    footer(d, 892, [
        '依据：新京报 05-11、IT之家 05-12（真人剧 70%→80%）；流媒体网 07-29（最高 20 万）；澎湃 09-23（取消系数）。',
        '横轴为发布顺序，不是等比例时间轴；红果未公开可访问的活动原文页。',
    ])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    center(d, 450, 56, '红果 AI 剧活动 2.0', 22, '#f0c588', 'bold', True)
    center(d, 450, 96, '只动了一条系数', 44, WHITE, 'title', True)
    center(d, 450, 160, '第二部起，不再翻倍', 27, '#8fc0b4', 'bold', True)
    d.line((300, 212, 600, 212), fill='#766657', width=2)
    center(d, 450, 230, '360 分钟拆 3 部：100 万 → 60 万', 21, '#d8cdbb', 'body', True)
    center(d, 450, 288, '9.22 更新 · 10 月起执行', 19, '#bdb3a1', 'body', True)
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
    for name, maker in [('039_图1_拆三部_1080.png', series_split),
                        ('039_图2_三个日期_1080.png', three_dates)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_039_红果系数_900x383.png')
    print('done')
