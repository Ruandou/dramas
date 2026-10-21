#!/usr/bin/env python3
"""032《PineDrama 下载破亿：日活只有 700 万》配图与封面。

结构：三个口径 → 三个该问的数。纯本地 Pillow，零扣费。
运行：/usr/local/bin/python3 _gen_032.py
"""
from pathlib import Path
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from _gen_charts_006 import f, HIRA, SONG, MONO

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = '#f3eee4', '#fffaf0', '#2c2925'
DIM, LINE, RUST, TEAL, GOLD = '#756d61', '#d4c9b8', '#ae422c', '#28695e', '#b9853d'
OLIVE, GREY = '#7a8b5e', '#a2988a'
FONTS = {'body': (HIRA, 0), 'bold': (HIRA, 2), 'title': (SONG, 1), 'number': (MONO, 1)}
GLYPHS, TEXT_BOXES = {}, []
TITLE = 'PineDrama 下载破亿：日活只有 700 万'
FIGURES = [
    ('032_图1_三个口径_1080.png', '三个口径，一条 7%'),
    ('032_图2_三个问题_1080.png', '问不到中位数，就不报价'),
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
    put(d, 72, 96, title, 46, INK, 'title', 1008)
    put(d, 72, 162, subtitle, 25, DIM, right=1008)
    d.line((72, 209, 1008, 209), fill=LINE, width=2)
    return im, d


def footer(d, y, lines):
    d.line((72, y, 1008, y), fill=LINE, width=2)
    for line in lines:
        y = paragraph(d, 72, y + 16, line, size=21, color=DIM, leading=30)
    return y


def chart_one():
    im, d = page('三个口径，一条 7%', '累计下载、月新增、日活，三个数不是一回事', '01', 1050)
    bars = [
        ('累计下载', '1 亿', 1.0, TEAL, '100%'),
        ('月新增下载', '1,700 万', 0.17, GOLD, '17%'),
        ('日活', '700 万', 0.07, RUST, '7%'),
    ]
    y = 270
    for label, value, ratio, color, pct in bars:
        put(d, 72, y, label, 24, INK, 'bold', 300)
        put(d, 72, y + 38, value, 28, color, 'bold', 300)
        width = max(10, int(540 * ratio))
        d.rounded_rectangle((330, y + 8, 330 + width, y + 52), radius=8, fill=color)
        put(d, 330 + width + 12, y + 14, pct, 22, color, 'bold', 1000)
        y += 120
    d.rounded_rectangle((72, 640, 1008, 780), radius=14, fill=WHITE)
    put(d, 100, 660, '700 万 ÷ 1 亿 = 7.0%', 28, RUST, 'bold', 980)
    put(d, 100, 706, '1,700 万 ÷ 700 万 = 2.4 倍', 24, INK, right=980)
    put(d, 100, 746, '1 亿 ÷ 1,700 万 ≈ 5.9 个月', 24, INK, right=980)
    d.rounded_rectangle((72, 800, 1008, 900), radius=14, fill=INK)
    put(d, 100, 820, '7% 不是留存率，是「累计装机」和「每天回来」的比值。', 22, WHITE, right=980)
    put(d, 100, 858, '平台规模是用户池，不是你的剧能拿到的量。', 22, '#f0c588', 'bold', right=980)
    footer(d, 930, ['来源：财新 2026-10-15（Sensor Tower 10-14 确认：下载超 1 亿、日活约 700 万）；腾讯新闻 2026-10-12（月新增下载超 1700 万）。'])
    return im


def chart_two():
    im, d = page('问不到中位数，就不报价', '出海承制或版权询价，先把三个数要过来', '02', 1060)
    questions = [
        ('01', '近 30 天同题材', '在播剧的单部中位播放是多少？', TEAL),
        ('02', '结算口径', '买断还是分账？分账按有效播放、充值还是广告？', GOLD),
        ('03', '冷启动', '新剧上线给多少测试流量？', OLIVE),
    ]
    y = 250
    for num, head, body, color in questions:
        d.rounded_rectangle((72, y, 1008, y + 190), radius=16, fill=WHITE)
        d.ellipse((100, y + 34, 164, y + 98), fill=color)
        center(d, 132, y + 44, num, 28, WHITE, 'number')
        put(d, 190, y + 30, head, 28, INK, 'bold', 980)
        paragraph(d, 190, y + 84, body, width=760, size=24, leading=36)
        y += 210
    d.rounded_rectangle((72, 900, 1008, 950), radius=12, fill='#f7e9e3')
    put(d, 100, 912, '只给头部案例、不给中位数，就按最低档做预算。', 21, RUST, 'bold', right=980)
    footer(d, 966, ['注：三个问题用于向平台/发行方核对，不代表任何平台的公开结算规则。'])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    center(d, 450, 62, 'PineDrama 下载破亿', 21, '#f0c588', 'bold', True)
    center(d, 450, 98, '1 亿', 54, WHITE, 'title', True)
    center(d, 450, 166, '日活只有 700 万', 40, WHITE, 'title', True)
    d.line((330, 232, 570, 232), fill='#766657', width=2)
    center(d, 450, 248, '除一下：7%', 24, '#8fc0b4', 'bold', True)
    center(d, 450, 292, '平台规模 ≠ 你的播放量', 19, '#bdb3a1', 'body', True)
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
    for name, maker in zip([x[0] for x in FIGURES], [chart_one, chart_two]):
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_032_7%_900x383.png')
    print('done')
