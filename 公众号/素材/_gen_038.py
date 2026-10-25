#!/usr/bin/env python3
"""038《微信短剧 90% 现金，卡在人均 10 分钟》配图与封面。

结构：90% 的三层意思 → 人均 10 分钟两种难度 → 三条激励三条路。纯本地 Pillow，零扣费。
运行：cd 公众号/素材 && python3 _gen_038.py
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


def split_ratio():
    im, d = page('90% 现金，是「达标后的上限」', '把「最高 100% 收入激励」拆开看', '01', 1040)
    d.rounded_rectangle((72, 236, 1008, 420), radius=14, fill=WHITE)
    put(d, 100, 258, '最高', 24, DIM, 'body', 300)
    put(d, 100, 292, '100%', 56, RUST, 'bold', 300)
    put(d, 292, 306, '=', 30, DIM, 'body', 330)
    put(d, 336, 300, '90% 现金', 38, TEAL, 'bold', 520)
    put(d, 540, 306, '+', 30, DIM, 'body', 570)
    put(d, 578, 300, '10% 广告金', 38, GOLD, 'bold', 980)
    put(d, 100, 378, '「最高」＝达标剧目里的上限，不是所有接入剧都按 90% 结算。', 20, DIM, 'body', 980)

    cards = [
        ('01', '人均', '看剧的人平均看了多久；不是单集时长，也不是全剧总时长。', RUST),
        ('02', '最高', '只有人均播放时长 ≥10 分钟的剧，才进入这个档位。', TEAL),
        ('03', '广告金', '配赠的投放额度，能用来买量，不等于到账的现金。', GOLD),
    ]
    y = 452
    for num, head, body, color in cards:
        d.rounded_rectangle((72, y, 1008, y + 108), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 108), radius=4, fill=color)
        put(d, 104, y + 16, num, 21, color, 'number', 200)
        put(d, 150, y + 10, head, 28, INK, 'bold', 400)
        put(d, 300, y + 16, body, 20, DIM, 'body', 980)
        y += 126

    d.rounded_rectangle((72, 832, 1008, 920), radius=12, fill=INK)
    put(d, 100, 846, '90% 分账 ≠ 90% 现金到账', 22, '#bdb3a1', right=980)
    put(d, 100, 878, '现金 90% + 广告金 10%，基数与条件看协议', 25, '#f0c588', 'bold', 980)

    footer(d, 940, [
        '依据：微信开放平台 2026 年第四季度微短剧小程序激励活动（2026-09-23 发布，媒体转述）。',
        '「优质新剧」的认定标准与结算口径未公开，本图只拆比例构成。',
    ])
    return im


def two_difficulties():
    im, d = page('60 分钟和 10 分钟', '同一道门槛，两种难度', '02', 1100)
    d.rounded_rectangle((72, 236, 1008, 540), radius=14, fill=WHITE)
    put(d, 104, 258, '情况 A：20 集 × 3 分钟 = 60 分钟', 26, INK, 'bold', 980)
    d.rounded_rectangle((104, 320, 980, 364), radius=22, fill=LINE)
    d.rounded_rectangle((104, 320, 250, 364), radius=22, fill=RUST)
    put(d, 264, 326, '人均 10 分钟 ≈ 1/6', 21, RUST, 'bold', 980)
    put(d, 104, 384, '总时长够长，但大多数人看不到第 4 集。', 21, DIM, 'body', 980)
    put(d, 104, 430, '达标看的是留人，不是片长。', 25, TEAL, 'bold', 980)
    put(d, 104, 478, '用总播放时长 ÷ 观看人数，才是人均。', 20, DIM, 'body', 980)

    d.rounded_rectangle((72, 560, 1008, 860), radius=14, fill=WHITE)
    put(d, 104, 582, '情况 B：10 集 × 1 分钟 = 10 分钟', 26, INK, 'bold', 980)
    d.rounded_rectangle((104, 644, 980, 688), radius=22, fill=TEAL)
    put(d, 104, 704, '人均 10 分钟 ＝ 全部看完，一集不落', 21, TEAL, 'bold', 980)
    put(d, 104, 746, '总时长刚好够，但完播率要求接近 100%。', 21, DIM, 'body', 980)
    put(d, 104, 792, '同一个门槛，难度完全不同。', 25, RUST, 'bold', 980)

    d.rounded_rectangle((72, 884, 1008, 972), radius=12, fill=INK)
    put(d, 100, 898, '用户点开看 40 秒就走', 22, '#bdb3a1', right=980)
    put(d, 100, 930, '总时长再长，人均也上不去', 25, '#f0c588', 'bold', 980)

    footer(d, 992, [
        '10 分钟为微信 Q4 联合发行激励的人均播放时长门槛；换算为本号举例（C 级）。',
        '人均播放时长的统计周期与去重口径未公开。',
    ])
    return im


def three_paths():
    im, d = page('三条钱，三条路', 'Q4 窗口 10.16—12.31，今天还剩 67 天', '03', 1080)
    cards = [
        ('01', '联合发行', '最高 100%', '人均播放时长 ≥10 分钟：90% 现金 + 10% 广告金配赠。', RUST),
        ('02', 'IAA', '最高 70% 现金', '小程序主营短剧、使用官方播放器，按看剧时长结算。', TEAL),
        ('03', '小说改编', '额外 5% + 5%', '公众号小说改编并优先发行，承制方与作者各 5%，上不封顶。', GOLD),
    ]
    y = 236
    for num, head, value, body, color in cards:
        d.rounded_rectangle((72, y, 1008, y + 170), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 170), radius=4, fill=color)
        put(d, 104, y + 18, num, 21, color, 'number', 200)
        put(d, 150, y + 14, head, 27, INK, 'bold', 420)
        put(d, 150, y + 54, value, 30, color, 'bold', 980)
        put(d, 150, y + 104, body, 20, DIM, 'body', 980)
        y += 186

    d.rounded_rectangle((72, 816, 1008, 904), radius=12, fill=INK)
    put(d, 100, 830, '前两条是两种发行模式，能否叠加公告未写明', 22, '#bdb3a1', right=980)
    put(d, 100, 862, '先看走哪条路，再谈比例', 25, '#f0c588', 'bold', 980)

    footer(d, 924, [
        '依据：微信开放平台 Q4 激励 2026-09-23；电影界、剧短短 2026-10-16；新浪财经 2026-10-19。',
        'IAA 70% 与小说改编 5%+5% 为媒体转述口径，以平台通知为准。',
    ])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    center(d, 450, 56, '微信短剧 Q4 激励', 22, '#f0c588', 'bold', True)
    center(d, 450, 96, '90% 现金', 44, WHITE, 'title', True)
    center(d, 450, 160, '卡在人均 10 分钟', 27, '#8fc0b4', 'bold', True)
    d.line((300, 212, 600, 212), fill='#766657', width=2)
    center(d, 450, 230, '10.16—12.31 · 剩 67 天', 21, '#d8cdbb', 'body', True)
    center(d, 450, 288, '不是单集，是人均播放时长', 19, '#bdb3a1', 'body', True)
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
    for name, maker in [('038_图1_90分成_1080.png', split_ratio),
                        ('038_图2_人均10分钟_1080.png', two_difficulties),
                        ('038_图3_三条钱_1080.png', three_paths)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_038_微信激励_900x383.png')
    print('done')
