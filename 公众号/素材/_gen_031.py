#!/usr/bin/env python3
"""031《厂牌盯数04｜9 月立项备案 296 部》配图与封面。

版式与断言沿用 _gen_030.py。
运行：/usr/local/bin/python3 _gen_031.py
"""
from pathlib import Path
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from _gen_charts_006 import f, HIRA, SONG, MONO

OUT = Path(__file__).resolve().parent
SAMPLES = OUT.parents[1] / 'samples'
PAPER, WHITE, INK = '#f3eee4', '#fffaf0', '#2c2925'
DIM, LINE, RUST, TEAL, GOLD = '#756d61', '#d4c9b8', '#ae422c', '#28695e', '#b9853d'
FONTS = {'body': (HIRA, 0), 'bold': (HIRA, 2), 'title': (SONG, 1), 'number': (MONO, 1)}
GLYPHS, TEXT_BOXES = {}, []
TITLE = '厂牌盯数04｜9 月立项备案 296 部：「短剧集」只有 12 部'
DIGEST = '9 月电视剧（网络剧）备案 296 部：网络故事片 176、中剧 53、短剧集仅 12。这里的「短剧集」不是微短剧——两套备案口径不同，附三问定路径。'
FIGURES = [
    ('031_图1_296部结构_1080.png', '9 月备案的 296 部怎么拆'),
    ('031_图2_两套口径_1080.png', '两套备案口径'),
    ('031_图3_网络剧内部_1080.png', '网络剧 248 部的内部结构'),
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
    put(d, 100, 42, '一人短剧厂牌 / 厂牌盯数 04', 21, DIM, 'bold')
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


def chart_one():
    im, d = page('296 部怎么拆', '2026 年 9 月 · 电视剧（网络剧）备案公示', '01', 1300)
    rows = [
        (TEAL, '电视剧', 48, '16.2%'),
        (GOLD, '网络剧 · 网络故事片', 176, '59.5%'),
        (GOLD, '网络剧 · 中剧', 53, '17.9%'),
        (RUST, '网络剧 · 短剧集', 12, '4.1%'),
        (GOLD, '网络剧 · 季播剧', 6, '2%'),
        (GOLD, '网络剧 · 互动剧', 1, '0.3%'),
    ]
    y = 246
    for color, label, n, pct in rows:
        d.rounded_rectangle((72, y, 1008, y + 112), radius=12, fill=WHITE)
        d.rounded_rectangle((72, y, 80, y + 112), radius=4, fill=color)
        put(d, 104, y + 34, label, 28, INK, 'bold', 700)
        nw = d.textlength(f'{n} 部', font=font(30, 'bold'))
        put(d, 900 - nw, y + 30, f'{n} 部', 30, color, 'bold', 905)
        put(d, 934, y + 38, pct, 22, DIM, 'number', 1008)
        y += 128
    d.rounded_rectangle((72, y + 12, 1008, y + 120), radius=14, fill=INK)
    put(d, 100, y + 34, '题材：当代 57%、古代 29.8%、近代 12.2%、现代 1%', 24, WHITE, right=980)
    footer(d, y + 170, ['来源：广电总局办公厅《关于 2026 年 9 月全国拍摄制作电视剧（网络剧）备案公示的通知》。'])
    return im


def chart_two():
    im, d = page('两套备案，别混着读', '同一个月，两张不同的表', '02', 1180)
    cols = [
        (72, RUST, '微短剧', ['单集 < 20 分钟', '按投资/题材分一类、二类、三类', '分类实行备案公示 + 发行许可', '来源：《微短剧发展管理办法》']),
        (568, GOLD, '短剧集（剧集备案）', ['这份公示里的一个类别', '集数/时长阈值公示未给', '走电视剧（网络剧）备案', '9 月：12 部，占 4.1%']),
    ]
    for x, color, head, items in cols:
        d.rounded_rectangle((x, 246, x + 440, 800), radius=16, fill=WHITE)
        d.rounded_rectangle((x, 246, x + 440, 330), radius=16, fill=color)
        put(d, x + 26, 262, head, 27, WHITE, 'bold', x + 416)
        y = 352
        for it in items:
            paragraph(d, x + 26, y, '· ' + it, width=386, size=22, color=INK, leading=32)
            y += 74 if len(it) > 12 else 56
    d.rounded_rectangle((72, 828, 1008, 962), radius=14, fill=INK)
    put(d, 100, 850, '看到「短剧集 12 部」就推「微短剧只批了 12 部」', 24, '#f0c588', 'bold')
    put(d, 100, 892, '是拿错了表。两条线各走各的备案与许可。', 24, WHITE, right=980)
    footer(d, 1012, ['微短剧定义出自《微短剧发展管理办法》；短剧集的定义公示未给，本图不做推断。'])
    return im


def chart_three():
    im, d = page('网络剧 248 部的内部结构', '分母是 248，不是 296', '03', 1120)
    rows = [
        ('网络故事片', 176, 71, RUST),
        ('中剧', 53, 21, GOLD),
        ('短剧集', 12, 5, TEAL),
        ('季播剧 + 互动剧', 7, 3, '#a2988a'),
    ]
    y = 250
    for label, n, pct, color in rows:
        put(d, 72, y + 4, label, 26, INK, 'bold', 300)
        w = int(420 * pct / 71)
        d.rounded_rectangle((330, y, 330 + max(w, 10), y + 36), radius=6, fill=color)
        put(d, 330 + max(w, 10) + 18, y + 5, f'{n} 部 · {pct}%', 24, color, 'bold', 1000)
        y += 80
    d.rounded_rectangle((72, y + 24, 1008, y + 168), radius=14, fill=WHITE)
    put(d, 100, y + 46, '读法', 26, TEAL, 'bold')
    put(d, 100, y + 90, '这张表的大头是单本电影形态（网络故事片），不是短剧集。', 23, INK, right=980)
    put(d, 100, y + 128, '做微短剧的人，本来就不该在这张表里找自己。', 23, INK, right=980)
    footer(d, y + 216, ['占比以网络剧 248 部为分母自算，可复核。'])
    return im


def cover_a():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    put(d, 744, 28, '盯数 04', 18, '#bdb3a1', right=875)
    for i, (w, color) in enumerate([(150, '#b55b32'), (104, '#28695e'), (58, '#b9853d')]):
        y = 104 + i * 44
        d.rounded_rectangle((40, y, 40 + w, y + 30), radius=8, fill=color)
    center(d, 450, 76, '9 月立项备案 296 部', 22, '#f0c588', 'bold', True)
    center(d, 450, 122, '短剧集只有 12 部', 46, WHITE, 'title', True)
    d.line((306, 262, 594, 262), fill='#766657', width=2)
    center(d, 450, 282, '但它不是微短剧 · 两套口径', 20, '#bdb3a1', 'body', True)
    for i in range(3):
        d.rounded_rectangle((740, 300 + i * 18, 862 - i * 26, 310 + i * 18), radius=3, fill='#574e45')
    return im


def cover_b():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, DIM, right=900)
    put(d, 744, 28, '盯数 04', 18, DIM, right=875)
    center(d, 450, 74, '同一个月，两张表', 22, TEAL, 'bold', True)
    center(d, 450, 118, '短剧集 ≠ 微短剧', 44, INK, 'title', True)
    center(d, 450, 192, '别拿错表', 50, RUST, 'title', True)
    center(d, 450, 298, '296 部 · 短剧集占 4.1%', 21, TEAL, 'bold', True)
    for i, (width, color) in enumerate([(206, RUST), (150, TEAL), (98, GOLD)]):
        y = 112 + i * 62
        d.rounded_rectangle((44, y, 44 + width, y + 26), radius=6, fill=color)
    for i, width in enumerate((180, 132, 88)):
        y = 118 + i * 62
        d.rounded_rectangle((900 - 44 - width, y, 856, y + 22), radius=6, fill='#c2b7a6')
    return im


def cover_review(covers):
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (1500, 1040), '#e5e2dc')
    d = ImageDraw.Draw(im)
    for index, cover in enumerate(covers):
        y = 35 + index * 500
        put(d, 28, y, ['A / 深色：强调「只有 12 部」', 'B / 浅色：强调「两套口径」'][index], 26, INK, 'bold', 1450)
        im.paste(cover, (28, y + 55))
        d.rectangle((286, y + 55, 669, y + 437), outline='#b48e60', width=1)
        crop = cover.crop((258, 0, 641, 383)).resize((142, 142), Image.Resampling.LANCZOS)
        for j, (bg, fg) in enumerate([('#ffffff', INK), ('#191919', '#f5efe4')]):
            x = 958 + j * 254
            d.rounded_rectangle((x, y + 55, x + 228, y + 437), radius=16, fill=bg)
            put(d, x + 18, y + 75, ['浅色分享卡', '深色分享卡'][j], 19, fg, right=x + 217)
            im.paste(crop, (x + 43, y + 129))
            put(d, x + 18, y + 296, '短剧集 ≠ 微短剧', 18, fg, right=x + 217)
            put(d, x + 18, y + 330, '一人短剧厂牌', 16, fg, right=x + 217)
    return im


def validate_glyphs():
    for (path, index), chars in GLYPHS.items():
        ff = TTFont(path, fontNumber=index)
        cmap = ff.getBestCmap()
        missing = sorted(c for c in chars if ord(c) not in cmap)
        ff.close()
        assert not missing, (path, index, missing)
    print('PASS: font glyph coverage and', len(TEXT_BOXES), 'text width checks')


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
    cover_names = ['封面_031_A_只有12部_900x383.png', '封面_031_B_两套口径_900x383.png']
    for im, name in zip(covers, cover_names):
        save_png(im, OUT / name)
    save_png(cover_review(covers), OUT / '对照_031封面两方向.png')
    sheet = Image.new('RGB', (1212, 640), '#e5e2dc')
    for i, im in enumerate(charts):
        thumb = im.copy()
        thumb.thumbnail((380, 590), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (12 + i * 402, 12))
    save_png(sheet, SAMPLES / '031_正文配图手机宽预览.png')
    body = (OUT.parent / '文章' / '031_发布版.md').read_text()
    assert len(TITLE) <= 64 and len(DIGEST) <= 120, (len(TITLE), len(DIGEST))
    for index, (name, caption) in enumerate(FIGURES, 1):
        assert f'【图 {index}：{caption}】' in body, (index, caption)
    print('PASS: figure captions match body; title', len(TITLE), 'digest', len(DIGEST))
