#!/usr/bin/env python3
"""049《短剧今天没上热搜，百度短剧榜前 10 名却吃掉 61.6% 热度》配图与封面。纯本地 Pillow。"""
from pathlib import Path
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from _gen_charts_006 import f, HIRA, SONG, MONO

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = '#f3eee4', '#fffaf0', '#2c2925'
DIM, LINE, RUST, TEAL, GOLD = '#756d61', '#d4c9b8', '#ae422c', '#28695e', '#b9853d'
GREY = '#8f8576'
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


def concentration():
    im, d = page('前 10 名拿走 61.6% 的热度', '百度短剧榜 热剧榜 100 部 / 数据更新 2026-10-28 12:00', '01', 1000)

    x0, span, top, bot = 72, 936, 268, 338
    segs = [
        (0.195, RUST, '19.5%'),
        (0.421, GOLD, '42.1%'),
        (0.142, TEAL, '14.2%'),
        (0.242, GREY, '24.2%'),
    ]
    x = x0
    for ratio, color, label in segs:
        w = span * ratio
        d.rectangle((x, top, x + w, bot), fill=color)
        tw = d.textlength(label, font=font(26, 'bold'))
        put(d, x + (w - tw) / 2, top + 18, label, 26, WHITE, 'bold', x + w - 2)
        x += w

    legend = [
        (72, 360, RUST, '第 1 名', '910.8 万'),
        (560, 360, GOLD, '第 2-10 名', '1,969.4 万'),
        (72, 406, TEAL, '第 11-20 名', '664.5 万'),
        (560, 406, GREY, '第 21-100 名', '1,132.4 万'),
    ]
    for lx, ly, color, name, amount in legend:
        d.rectangle((lx, ly + 6, lx + 16, ly + 22), fill=color)
        put(d, lx + 28, ly, name, 23, INK, 'bold', lx + 250)
        put(d, lx + 250, ly, amount, 23, DIM, 'bold', lx + 460)

    cards = [
        (72, 486, 300, '榜首热度值', '910.8 万', '《离婚后我觉醒仙帝修仙》'),
        (390, 486, 300, '第二名热度值', '379.7 万', '《偏偏中意你》'),
        (708, 486, 300, '头部差距', '2.4 倍', '榜首 / 第二名'),
    ]
    for cx, cy, cw, label, value, note in cards:
        d.rounded_rectangle((cx, cy, cx + cw, cy + 156), radius=12, fill=WHITE)
        put(d, cx + 26, cy + 18, label, 20, DIM, 'bold', cx + cw - 12)
        put(d, cx + 22, cy + 50, value, 48, RUST if value.endswith('倍') else INK, 'title', cx + cw - 12)
        put(d, cx + 26, cy + 116, note, 18, DIM, 'body', cx + cw - 8)

    d.rounded_rectangle((72, 676, 1008, 782), radius=12, fill=INK)
    put(d, 102, 692, '前 10 名合计 2,880.2 万，占全榜 61.6%；前 20 名 75.8%。', 21, '#bdb3a1', right=986)
    put(d, 102, 730, '后 80 部只分到 24.2%。', 26, '#f0c588', 'bold', 986)

    put(d, 72, 818, '第 10 名 104.7 万，第 90 名 3.5 万，差近 30 倍。', 23, INK, 'bold', 1008)
    footer(d, 872, [
        '来源：百度短剧榜 热剧榜，2026-10-28 12:00 数据，本号 17:50 抓取。',
        '热度值为百度综合指数，非播放量、非分账；区间与占比为本号按原字段直接计算。',
    ])
    return im


def genre_structure():
    im, d = page('三类题材占 83 部，仙侠 2 部拿走第一', '按榜单自标题材 / 共 100 部', '02', 1220)

    rows = [
        ('现实情感', 37, RUST, ''),
        ('日常', 26, GOLD, ''),
        ('爱情', 20, TEAL, ''),
        ('权谋', 5, GREY, ''),
        ('军旅战争', 3, GREY, ''),
        ('仙侠', 2, RUST, '2 部里出了第 1 名'),
        ('言情', 2, GREY, ''),
        ('家庭伦理', 2, GREY, ''),
        ('其他', 3, GREY, '玄幻 / 悬疑推理 / 脑洞'),
    ]
    x_bar, max_w, step = 300, 520, 76
    y = 252
    for name, count, color, note in rows:
        put(d, 72, y, name, 25, INK, 'bold', 288)
        w = max_w * count / 37
        d.rectangle((x_bar, y + 4, x_bar + w, y + 40), fill=color)
        put(d, x_bar + w + 14, y, str(count), 26, INK, 'number', 900)
        if note:
            put(d, 660, y + 4, note, 19, RUST if name == '仙侠' else DIM, 'body', 1006)
        y += step

    d.rounded_rectangle((72, 946, 524, 1082), radius=12, fill=WHITE)
    put(d, 100, 962, '现实情感 + 日常 + 爱情', 20, DIM, 'bold', 500)
    put(d, 96, 994, '83 部', 44, INK, 'title', 240)
    put(d, 246, 1006, '= 83%', 26, RUST, 'bold', 500)

    d.rounded_rectangle((556, 946, 1008, 1082), radius=12, fill=INK)
    put(d, 584, 960, '仙侠：2 部', 20, '#bdb3a1', 'bold', 990)
    put(d, 580, 988, '19.5%', 40, '#f0c588', 'title', 800)
    put(d, 584, 1046, '全榜热度 / 其中 1 部是第 1 名', 17, '#bdb3a1', 'body', 1000)

    footer(d, 1110, [
        '来源：百度短剧榜 热剧榜 100 部（2026-10-28 12:00），题材为榜单自标字段。',
        '「其他」= 玄幻 1 + 悬疑推理 1 + 脑洞 1。份额为本号直接相加。',
    ])
    return im


def episodes():
    im, d = page('集数：中位数 65，80 集以上只有 22 部', '100 部 / 按榜单标注集数 / 纵轴为部数', '03', 1080)

    base, scale = 742, 330 / 47
    bars = [
        (300, 31, '60 集以下', '<60 集', GREY),
        (580, 47, '60-79 集', '60-79 集', RUST),
        (860, 22, '80 集以上', '80 集以上', TEAL),
    ]
    for cx, count, big, label, color in bars:
        h = count * scale
        d.rectangle((cx - 92, base - h, cx + 92, base), fill=color)
        put(d, cx - 30, base - h - 56, str(count), 40, INK, 'title', cx + 92)
        put(d, cx - 92, base + 18, label, 22, INK, 'bold', cx + 100)

    d.line((72, base, 1008, base), fill=INK, width=2)

    d.rounded_rectangle((72, 838, 1008, 936), radius=12, fill=WHITE)
    put(d, 100, 854, '中位数 65 集 / 平均 66.4 集 / 最长 141 集 / 最短 30 集', 21, INK, 'bold', 986)
    put(d, 100, 892, '141 集的《开局被退婚，公主竟能读我心声》是个例；30 集的是《失独母亲的曙光》。', 19, DIM, 'body', 990)

    d.rounded_rectangle((72, 960, 1008, 1014), radius=10, fill=INK)
    put(d, 100, 974, '80 集以上只占 22%，榜首 81 集就在中位数偏上一点。', 20, '#f0c588', 'bold', 986)

    footer(d, 1036, [
        '来源：百度短剧榜 热剧榜 100 部（2026-10-28 12:00），集数为榜单标注值。',
    ])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, '#bdb3a1', right=420)
    put(d, 33, 60, '百度短剧榜 100 部 · 10-28 12:00', 18, '#f0c588', 'bold', 470)
    put(d, 28, 96, '61.6%', 88, '#efe6d6', 'title', 470)
    put(d, 36, 200, '前 10 名占全榜热度', 24, '#bdb3a1', 'bold', 470)
    put(d, 36, 240, '2.4 倍', 34, '#e0705a', 'bold', 470)
    put(d, 186, 250, '第一名对第二名', 18, '#8f8576', 'body', 470)
    put(d, 36, 300, '后 80 部只分到 24.2%', 18, '#8f8576', 'body', 470)

    d.line((490, 62, 490, 324), fill='#4a443c', width=1)
    x0, span, top, bot = 528, 342, 148, 216
    segs = [(0.195, '#ae422c'), (0.421, '#b9853d'), (0.142, '#28695e'), (0.242, '#8f8576')]
    x = x0
    for ratio, color in segs:
        w = span * ratio
        d.rectangle((x, top, x + w, bot), fill=color)
        x += w
    put(d, x0, bot + 12, '第 1 名', 15, '#8f8576', 'body', x0 + 120)
    put(d, x0 + 86, bot + 12, '第 2-100 名', 15, '#8f8576', 'body', x0 + span + 4)
    put(d, 528, 100, '100 部的热度值怎么分', 18, '#bdb3a1', 'body', 880)
    put(d, 528, 262, '4,677 万热度值', 22, WHITE, 'bold', 880)
    put(d, 528, 300, '榜首一部占 19.5%', 18, '#8fc0b4', 'body', 880)
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
    for name, maker in [('049_图1_热度集中度_1080.png', concentration),
                        ('049_图2_题材结构_1080.png', genre_structure),
                        ('049_图3_集数分布_1080.png', episodes)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_049_61.6%与100部_900x383.png')
    print('done')
