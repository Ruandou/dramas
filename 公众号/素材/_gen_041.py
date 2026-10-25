#!/usr/bin/env python3
"""041《短剧的钱：上海看片单，江西看执照》配图与封面。

结构：两张倒排表 → 两种钱的方向。纯本地 Pillow，零扣费。
运行：cd 公众号/素材 && python3 _gen_041.py
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


def schedule():
    im, d = page('两张倒排表', '今天同时准备，截止日差 19 天', '01', 1200)

    panels = [
        (236, 360, '江西 · AI+OPC 大赛', '报名免费，不看注册地', TEAL, [
            ('10-30', '报名截止', RUST),
            ('11-05', '初评前', INK),
            ('11-25', '决赛前', INK),
            ('赛后 2 个月', '在江西注册 OPC 才能领奖', GOLD),
        ]),
        (620, 280, '上海 · 专项经费', '主体须在沪', RUST, [
            ('10-21', '指南发布', INK),
            ('11-18', '线上受理截止', RUST),
            ('11-19—20', '纸质材料现场递交', INK),
        ]),
    ]
    for top, height, label, note, accent, rows in panels:
        d.rounded_rectangle((72, top, 1008, top + height), radius=14, fill=WHITE)
        d.rectangle((72, top, 78, top + height), fill=accent)
        put(d, 104, top + 18, label, 24, accent, 'bold', 640)
        put(d, 660, top + 22, note, 20, DIM, 'body', 980)
        y = top + 72
        for date, event, color in rows:
            put(d, 104, y + 4, date, 22, color, 'number' if date[0].isdigit() else 'bold', 286)
            put(d, 300, y, event, 25, INK if color != GOLD else GOLD, 'body', 980)
            d.line((104, y + 46, 976, y + 46), fill=LINE, width=1)
            y += 66

    d.rounded_rectangle((72, 928, 1008, 1036), radius=12, fill=INK)
    put(d, 100, 944, '今天 10-26', 22, '#bdb3a1', right=600)
    put(d, 100, 978, '江西 4 天 · 上海 23 天', 30, '#f0c588', 'bold', 600)
    put(d, 560, 952, '上海纸质材料只有 11-19—20 两天', 20, '#d8cdbb', right=980)
    put(d, 560, 986, '现场递交，不收快递、邮寄', 20, '#d8cdbb', right=980)

    footer(d, 1056, [
        '依据：上海市文旅局 10-21 申报指南；江西大赛公告（流媒体网 10-15）、凤凰网江西 10-23。',
        '「4 天／23 天」按 2026-10-26 起算；赛后注册时限按决赛 11-25 推算（C 级）。',
    ])
    return im


def directions():
    im, d = page('两种钱的方向', '同一句「最高」，说的是两件相反的事', '02', 1000)

    lanes = [
        (72, 528, '上海', RUST, '先有片，后给钱', [
            ('已完成片单', '2025-10-16—2026-10-15'),
            ('评审 + 专项审计', '主体须在上海'),
            ('最高 300 万', '精品类，评审决定'),
        ]),
        (552, 1008, '江西', TEAL, '奖金换注册', [
            ('5 万奖金', '16 个名额，42 万总池'),
            ('赛后 2 个月内', '把公司注册到江西'),
            ('江西 OPC', '注册后才可领取'),
        ]),
    ]
    for left, right, label, accent, subtitle, steps in lanes:
        d.rounded_rectangle((left, 236, right, 720), radius=14, fill=WHITE)
        put(d, left + 28, 254, label, 30, accent, 'bold', right - 20)
        put(d, left + 28, 298, subtitle, 24, INK, 'bold', right - 20)
        y = 360
        for i, (main, note) in enumerate(steps):
            d.rounded_rectangle((left + 24, y, right - 24, y + 86), radius=10,
                                fill=PAPER if i < 2 else accent)
            color = WHITE if i == 2 else INK
            put(d, left + 44, y + 12, main, 24, color, 'bold', right - 36)
            put(d, left + 44, y + 50, note, 19, WHITE if i == 2 else DIM, 'body', right - 36)
            if i < 2:
                d.line((left + 60, y + 92, left + 60, y + 104), fill=LINE, width=3)
                d.polygon([(left + 54, y + 100), (left + 66, y + 100), (left + 60, y + 110)], fill=accent)
            y += 112

    d.rounded_rectangle((72, 752, 1008, 880), radius=12, fill=INK)
    put(d, 100, 768, '上海补过去，江西买未来', 28, '#f0c588', 'bold', 980)
    put(d, 100, 816, '一个看你已经交了什么，一个看你把公司放在哪', 22, '#d8cdbb', right=980)
    put(d, 100, 850, '两笔钱都不是「拍到就能拿」', 20, '#bdb3a1', right=980)

    footer(d, 900, [
        '依据：上海市文旅局 10-21 指南；江西大赛公告（流媒体网 10-15）；凤凰网江西 10-23。',
        '42 万为本号按两赛道 1+2+5 个名额加总（C 级），不含可能另设的组织类奖项。',
    ])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 26, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    center(d, 450, 52, '2026 地方微短剧资金', 21, '#f0c588', 'bold', True)
    center(d, 450, 88, '上海看片单', 42, WHITE, 'title', True)
    center(d, 450, 140, '江西看执照', 42, '#8fc0b4', 'title', True)
    d.line((300, 200, 600, 200), fill='#766657', width=2)
    center(d, 450, 216, '两笔短剧的钱，方向相反', 22, '#d8cdbb', 'body', True)
    center(d, 450, 254, '300 万补旧片 · 5 万买注册', 20, '#f0c588', 'body', True)
    center(d, 450, 312, '10.26', 18, '#bdb3a1', 'body', True)
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
    for name, maker in [('041_图1_两张倒排_1080.png', schedule),
                        ('041_图2_两种方向_1080.png', directions)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_041_上海江西_900x383.png')
    print('done')
