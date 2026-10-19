#!/usr/bin/env python3
"""029《厂牌合规01｜快手 10 月治理公告》配图与封面。

版式与断言沿用 _gen_022.py：字形覆盖、文本量宽、画布边界、文本框不重叠、中央安全区。
运行：/usr/local/bin/python3 _gen_029.py
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
TITLE = '厂牌合规01｜快手 10 月下架二百余部微短剧：公告里的 6 类理由'
DIGEST = '快手 10 月治理公告：累计拦截、整改、下架违规微短剧（含动画微短剧）二百余部。公告给的 6 类理由逐条翻译成剧本写法，附发布前 6 条自查。'
FIGURES = [
    ('029_图1_六类理由_1080.png', '公告里的 6 类理由与对应的剧本写法'),
    ('029_图2_核三件事_1080.png', '一次治理公告，该核哪三件事'),
    ('029_图3_六条自查_1080.png', '发布前的 6 条自查'),
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
    put(d, 100, 42, '一人短剧厂牌 / 厂牌合规 01', 21, DIM, 'bold')
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
    im, d = page('6 类理由，逐条对到剧本', '快手安全中心 2026-10-12 公告 · 二百余部', '01', 1560)
    items = [
        (RUST, '① 片名低俗', '把身体部位、性暗示、猎奇关系塞进片名换点击。'),
        (RUST, '② 内容粗劣', '抠图式合成、口型对不上、情节靠字幕硬推。'),
        (GOLD, '③ 危害未成年人', '未成年角色的暴力、惊吓、性暗示情境。'),
        (GOLD, '④ 美化畸形婚恋', '控制、囚禁、报复式纠缠被写成值得羡慕的结局。'),
        (TEAL, '⑤ 宣扬极端暴力', '暴力被奖励；复仇爽剧最容易在这里踩线。'),
        (TEAL, '⑥ 换马甲', '下架后改名重发，平台明确「严厉打击」。'),
    ]
    y = 246
    for color, tag, text in items:
        d.rounded_rectangle((72, y, 1008, y + 150), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 80, y + 150), radius=4, fill=color)
        put(d, 104, y + 22, tag, 29, color, 'bold', 992)
        paragraph(d, 104, y + 72, text, width=876, size=24, color=INK, leading=34)
        y += 166
    d.rounded_rectangle((72, y + 12, 1008, y + 150), radius=14, fill=INK)
    put(d, 100, y + 34, '公告没给剧目清单，只给问题类型', 26, '#f0c588', 'bold')
    put(d, 100, y + 78, '所以这篇的重点不是「哪部被下架」，而是「这 6 类写在剧本里长什么样」。', 23, WHITE, right=980)
    footer(d, y + 200, ['来源：快手安全中心《关于违规微短剧的治理公告（2026年10月）》，2026-10-14 经流媒体网转载。'])
    return im


def chart_two():
    im, d = page('看到一个「下架 N 部」，先核三件事', '公告没写清的数字只能当热度', '02', 1180)
    items = [
        (TEAL, '统计口径', '是「前置拦截」还是「已下架」？两者不是一回事。'),
        (TEAL, '覆盖品类', '全品类巡检，还是只查某一类（比如 AI 剧专项）？'),
        (TEAL, '统计周期', '单次行动，还是几个月累计？'),
    ]
    y = 250
    for color, tag, text in items:
        d.rounded_rectangle((72, y, 1008, y + 130), radius=14, fill=WHITE)
        put(d, 100, y + 22, tag, 30, color, 'bold', 980)
        put(d, 100, y + 72, text, 24, INK, right=980)
        y += 146
    d.rounded_rectangle((72, y + 16, 1008, y + 200), radius=14, fill=RUST)
    put(d, 100, y + 40, '三个都没说清，就不要跨平台相加', 28, WHITE, 'bold')
    put(d, 100, y + 86, '不同平台的口径不一样，「二百余部」与「八千余部」可能统计的', 23, WHITE, right=980)
    put(d, 100, y + 124, '根本不是同一件事。', 23, WHITE, right=980)
    footer(d, y + 250, ['本图为本号整理的核查口径，非平台规则原文。'])
    return im


def chart_three():
    im, d = page('发布前，过这 6 问', '答不上来就先别发', '03', 1320)
    qs = [
        '片名能不能原样发给一个不认识的品牌方？',
        '成片里有没有生成废片、对不上口型的镜头？',
        '有未成年角色吗？他在剧里承担了什么功能？',
        '剧里的婚恋关系，你希望朋友遇到吗？',
        '暴力的结果，是被惩罚还是被奖励？',
        '这部剧（或它的前身）有没有被下架过？',
    ]
    y = 250
    for i, q in enumerate(qs, 1):
        d.rounded_rectangle((72, y, 1008, y + 112), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 152, y + 112), radius=14, fill=TEAL)
        w = d.textlength(str(i), font=font(40, 'number'))
        put(d, 112 - w / 2, y + 30, str(i), 40, WHITE, 'number')
        put(d, 178, y + 34, q, 26, INK, right=992)
        y += 128
    d.rounded_rectangle((72, y + 16, 1008, y + 150), radius=14, fill=INK)
    put(d, 100, y + 38, '6 问不保证过审', 27, '#f0c588', 'bold')
    put(d, 100, y + 82, '但能把公告点名的 6 类问题，挡在发布之前。', 24, WHITE, right=980)
    footer(d, y + 200, ['6 问为本号据公告 6 类理由整理的自查项，非平台审核标准。'])
    return im


def cover_a():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    put(d, 744, 28, '合规 01', 18, '#bdb3a1', right=875)
    for i, (w, color) in enumerate([(150, '#b55b32'), (104, '#28695e'), (58, '#b9853d')]):
        y = 104 + i * 44
        d.rounded_rectangle((40, y, 40 + w, y + 30), radius=8, fill=color)
    center(d, 450, 76, '快手 10 月治理公告', 24, '#f0c588', 'bold', True)
    center(d, 450, 122, '下架二百余部', 58, WHITE, 'title', True)
    d.line((306, 262, 594, 262), fill='#766657', width=2)
    center(d, 450, 282, '6 类理由 · 6 条自查', 21, '#bdb3a1', 'body', True)
    for i in range(3):
        d.rounded_rectangle((740, 300 + i * 18, 862 - i * 26, 310 + i * 18), radius=3, fill='#574e45')
    return im


def cover_b():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, DIM, right=900)
    put(d, 744, 28, '合规 01', 18, DIM, right=875)
    center(d, 450, 74, '公告原文 6 类问题', 24, TEAL, 'bold', True)
    center(d, 450, 118, '写进剧本', 54, INK, 'title', True)
    center(d, 450, 192, '长什么样', 54, RUST, 'title', True)
    center(d, 450, 298, '二百余部 · 附 6 条自查', 22, TEAL, 'bold', True)
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
        put(d, 28, y, ['A / 深色：强调「下架二百余部」', 'B / 浅色：强调「逐条对照」'][index], 26, INK, 'bold', 1450)
        im.paste(cover, (28, y + 55))
        d.rectangle((286, y + 55, 669, y + 437), outline='#b48e60', width=1)
        crop = cover.crop((258, 0, 641, 383)).resize((142, 142), Image.Resampling.LANCZOS)
        for j, (bg, fg) in enumerate([('#ffffff', INK), ('#191919', '#f5efe4')]):
            x = 958 + j * 254
            d.rounded_rectangle((x, y + 55, x + 228, y + 437), radius=16, fill=bg)
            put(d, x + 18, y + 75, ['浅色分享卡', '深色分享卡'][j], 19, fg, right=x + 217)
            im.paste(crop, (x + 43, y + 129))
            put(d, x + 18, y + 296, '快手 10 月治理公告', 18, fg, right=x + 217)
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
    cover_names = ['封面_029_A_下架二百余部_900x383.png', '封面_029_B_逐条对照_900x383.png']
    for im, name in zip(covers, cover_names):
        save_png(im, OUT / name)
    save_png(cover_review(covers), OUT / '对照_029封面两方向.png')
    sheet = Image.new('RGB', (1212, 640), '#e5e2dc')
    for i, im in enumerate(charts):
        thumb = im.copy()
        thumb.thumbnail((380, 590), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (12 + i * 402, 12))
    save_png(sheet, SAMPLES / '029_正文配图手机宽预览.png')
    body = (OUT.parent / '文章' / '029_发布版.md').read_text()
    assert len(TITLE) <= 64 and len(DIGEST) <= 120, (len(TITLE), len(DIGEST))
    for index, (name, caption) in enumerate(FIGURES, 1):
        assert f'【图 {index}：{caption}】' in body, (index, caption)
    print('PASS: figure captions match body; title', len(TITLE), 'digest', len(DIGEST))
