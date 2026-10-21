#!/usr/bin/env python3
"""030《9 月 1 日新规：剧名、封面、正片分三条管》配图与封面。

结构：提交字段↔法条条款 → 三处各卡什么 → 十分钟对账。纯本地 Pillow，零扣费。
运行：/usr/local/bin/python3 _gen_030.py
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
TITLE = '9 月 1 日新规：剧名、封面、正片分三条管'
DIGEST = '一部剧提审要填六个字段，法条把它拆成五条管。剧名、封面、正片各卡什么，文末一张十分钟对账表。'
FIGURES = [
    ('030_图1_六个字段对条款_1080.png', '六个提交字段，对上五条法条'),
    ('030_图2_三处各卡什么_1080.png', '三个位置，三套标准'),
    ('030_图3_十分钟对账_1080.png', '十分钟，对四个地方'),
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
    im, d = page('字段与条款，怎么对上', '微信「剧目提审」接口字段 ×《微短剧发展管理办法》', '01', 1120)
    d.rounded_rectangle((72, 238, 1008, 902), radius=16, fill=WHITE)
    heads = [(100, '提交字段（平台）'), (440, '对应条款'), (730, '卡什么')]
    for x, label in heads:
        put(d, x, 262, label, 21, DIM, 'bold')
    d.line((88, 300, 992, 300), fill=LINE, width=2)
    rows = [
        ('剧名', 'name', '第二十六条', '用语规范', TEAL),
        ('简介', 'description', '第二十八条', '不承诺正片没有的', GOLD),
        ('剧目海报', 'cover_material_id', '第二十八条', '与内容相适配', RUST),
        ('推广海报', 'promotion_poster_material_id', '第二十八条', '同上，单独过', RUST),
        ('剧集', 'media_id_list', '第二十五 / 二十七 / 三十四条', '内容·标注·AI 标识', OLIVE),
        ('资质', 'qualification_type', '第二十七条', '片头编号要对得上', TEAL),
    ]
    y = 322
    for i, (cn, code, clause, what, color) in enumerate(rows):
        if i % 2 == 0:
            d.rounded_rectangle((88, y - 8, 992, y + 84), radius=8, fill='#faf5ea')
        put(d, 100, y, cn, 21, INK, 'bold', 420)
        put(d, 100, y + 32, code, 15, DIM, right=420)
        put(d, 440, y + 10, clause, 19, color, 'bold', 720)
        put(d, 730, y + 10, what, 19, DIM, right=990)
        y += 92
    d.rounded_rectangle((72, 926, 1008, 976), radius=12, fill=INK)
    put(d, 100, 942, '字段按「提交位置」切，条款按「内容性质」切；一张表叠一张表，才是全部。', 21, WHITE, right=980)
    footer(d, 1020, ['注：字段名与必填项取自微信开放文档「短剧媒资管理 · 剧目提审」；图中只列与内容审核相关的字段，另有制作方等主体字段未列。'])
    return im


def chart_two():
    im, d = page('三个位置，三套标准', '同一部剧，剧名、封面、正片分别被什么卡住', '02', 1000)
    cards = [
        ('剧名', '第二十六条 + 平台创作建议', [
            '用语规范',
            '封面字 = 正片名',
            '不过小、不截断',
        ], TEAL),
        ('封面', '第二十八条 + 平台审片标准', [
            '与正片相适配',
            '无热播/爆款/强推',
            '不擦边、五官完整',
        ], RUST),
        ('正片', '第二十五 / 二十七 / 三十四条', [
            '11 类禁止内容',
            '片头四样 + 署名',
            'AI 剧每集标识',
        ], OLIVE),
    ]
    for i, (name, src, items, color) in enumerate(cards):
        x = 72 + i * 318
        d.rounded_rectangle((x, 238, x + 300, 716), radius=16, fill=WHITE)
        d.rectangle((x, 238, x + 300, 250), fill=color)
        center(d, x + 150, 280, name, 40, color, 'title')
        for j, line in enumerate(src.split(' + ')):
            center(d, x + 150, 340 + j * 30, line, 17, DIM, 'body')
        d.line((x + 26, 406, x + 274, 406), fill=LINE, width=2)
        for j, item in enumerate(items):
            d.rectangle((x + 26, 444 + j * 88, x + 34, 452 + j * 88), fill=color)
            paragraph(d, x + 50, 432 + j * 88, item, width=228, size=21, leading=30)
    d.rounded_rectangle((72, 742, 1008, 916), radius=14, fill='#f7e9e3')
    put(d, 100, 764, '最常见的误判：内容没问题，卡在封面字；封面没问题，卡在片头编号。', 23, INK, right=980)
    put(d, 100, 808, '三处不是同一标准换三个地方用，是三套东西。', 23, RUST, 'bold', right=980)
    put(d, 100, 852, '封面暗示的，正片得有；正片没有的，封面不能承诺。', 21, DIM, right=980)
    footer(d, 946, ['注：平台侧具体要求来自媒体对抖音两份文档的转述（B 级），只作自查线索。'])
    return im


def chart_three():
    im, d = page('十分钟，对四个地方', '发布前对账：五个名字、一张封面、一次片头、一遍简介', '03', 1200)
    names = ['备案名', '后台 name', '封面字', '标题', '片头字幕']
    d.rounded_rectangle((72, 238, 1008, 430), radius=16, fill=WHITE)
    put(d, 100, 258, '第一处 · 五个名字写成同一个', 24, INK, 'bold')
    step = 168
    for i, name in enumerate(names):
        cx = 100 + 44 + i * step
        d.rounded_rectangle((cx - 74, 316, cx + 74, 374), radius=10, fill='#faf5ea', outline=LINE, width=2)
        center(d, cx, 330, name, 19, TEAL, 'bold')
        if i < 4:
            center(d, cx + 84, 330, '=', 22, RUST, 'bold')
    put(d, 100, 392, '标点、空格、繁简都算不同；对不上就先改，不要指望审核替你对。', 19, DIM, right=980)

    steps = [
        ('1', '封面缩到手机列表大小', '看剧名还能不能读全；读不全就重做。', RUST),
        ('2', '抽首集前 15 秒', '剧名、许可证号、批准文件编号、节目编号，四样都在？', GOLD),
        ('3', 'AI 剧再抽一集', '每集明显位置有没有提示标识。', OLIVE),
        ('4', '简介逐句对正片', '删掉找不到对应镜头的句子。', TEAL),
    ]
    y = 456
    for num, head, body, color in steps:
        d.rounded_rectangle((72, y, 1008, y + 132), radius=14, fill=WHITE)
        d.ellipse((100, y + 38, 156, y + 94), fill=color)
        center(d, 128, y + 47, num, 28, WHITE, 'number')
        put(d, 180, y + 32, head, 24, INK, 'bold', 980)
        put(d, 180, y + 80, body, 20, DIM, right=980)
        y += 148
    d.rounded_rectangle((72, 1058, 1008, 1110), radius=12, fill=INK)
    put(d, 100, 1072, '这四步挡的是「内容没错、包装出错」；正片里的红线，只能逐集审。', 21, WHITE, right=980)
    footer(d, 1136, ['对账依据：《微短剧发展管理办法》第二十六、二十七、二十八、三十四条；微信剧目提审字段。'])
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
    center(d, 450, 74, '9 月 1 日新规', 22, '#f0c588', 'bold', True)
    center(d, 450, 116, '三个位置', 44, WHITE, 'title', True)
    center(d, 450, 174, '三套标准', 44, WHITE, 'title', True)
    d.line((306, 252, 594, 252), fill='#766657', width=2)
    center(d, 450, 268, '剧名 · 封面 · 正片', 20, '#bdb3a1', 'body', True)
    center(d, 450, 304, '各卡什么，不一样', 20, '#8fc0b4', 'bold', True)
    return im


def cover_b():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), PAPER)
    d = ImageDraw.Draw(im)
    d.text((42, 92), '5', font=font(100, 'number'), fill='#e7ddcc', anchor='lt')
    d.rectangle((38, 28, 44, 50), fill=RUST)
    put(d, 64, 28, '一人短剧厂牌', 19, DIM, right=900)
    center(d, 450, 74, '五个名字', 21, TEAL, 'bold', True)
    center(d, 450, 110, '要写成同一个', 50, INK, 'title', True)
    center(d, 450, 190, '备案名 / 后台 / 封面字 / 标题 / 片头', 19, DIM, 'body', True)
    d.line((300, 250, 600, 250), fill=LINE, width=2)
    center(d, 450, 266, '少一个对不上，就可能被退回', 19, RUST, 'bold', True)
    center(d, 450, 308, '9 月 1 日新规：剧名、封面、正片分三条管', 16, DIM, 'body')
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
    outputs = []
    for name, maker in zip([x[0] for x in FIGURES], [chart_one, chart_two, chart_three]):
        im = maker()
        validate_glyphs()
        path = OUT / name
        save_png(im, path)
        outputs.append(path)
    for name, maker in (('封面_030_A_三个位置_900x383.png', cover_a), ('封面_030_B_五个名字_900x383.png', cover_b)):
        im = maker()
        validate_glyphs()
        path = OUT / name
        save_png(im, path)
        outputs.append(path)
    print('done', len(outputs))
