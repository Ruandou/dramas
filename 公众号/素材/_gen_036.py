#!/usr/bin/env python3
"""036《双11 短剧招商：一人厂牌能接哪一档》配图与封面。

结构：三档钱 → 三道门 → 三个动作。纯本地 Pillow，零扣费。
运行：/usr/local/bin/python3 _gen_036.py
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
    put(d, 72, 96, title, 46, INK, 'title', 1008)
    put(d, 72, 162, subtitle, 25, DIM, right=1008)
    d.line((72, 209, 1008, 209), fill=LINE, width=2)
    return im, d


def footer(d, y, lines):
    d.line((72, y, 1008, y), fill=LINE, width=2)
    for i, line in enumerate(lines):
        y = paragraph(d, 72, y + (16 if i == 0 else 8), line, size=21, color=DIM, leading=30)
    return y


def money():
    im, d = page('三档钱，三种门槛', '上限是平台写的，门槛是要自己过的', '01', 1150)
    cards = [
        ('30 万', 'AI 短剧 · 单部最高激励', '热剧保底 5,000 元/部；激励可叠加；榜单保底最高 5,000 元', RUST),
        ('150 万 + 150 万', '真人短剧 · 精品独家', '制作保底最高 150 万；播放分成最高 150 万；榜单保底最高 5 万', TEAL),
        ('300 万', '机构 · 单月收入封顶', '三证 + 淘宝企业账号认证 + 绑定支付宝；可叠加其他激励', GOLD),
    ]
    y = 238
    for big, head, desc, color in cards:
        h = 196
        d.rounded_rectangle((72, y, 1008, y + h), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + h), radius=4, fill=color)
        put(d, 104, y + 18, big, 50, color, 'bold', 560)
        put(d, 104, y + 92, head, 22, INK, 'bold', 560)
        put(d, 104, y + 128, desc, 19, DIM, 'body', 980)
        y += h + 18

    d.rounded_rectangle((72, y + 6, 1008, y + 96), radius=12, fill=INK)
    put(d, 100, y + 20, '最高值是上限，不是报价单', 21, '#bdb3a1', right=980)
    put(d, 100, y + 52, '保底是下限 · 分成是上限 · 到手看条件', 28, '#f0c588', 'bold', 980)

    footer(d, y + 116, [
        '来源：DataEye 短剧观察 2026-10-22（经广电时评转载）；流媒体网 2026-10-17—10-23 周报。',
        '淘宝官方细则未公开；「热剧」定义、三证具体所指均未说明。最高值不等于平均到手。',
        '本图只做口径整理，不构成招商承诺。',
    ])
    return im


def gates():
    im, d = page('三道门与四个切口', '资质、产能、内容方向；先过门，再谈钱', '02', 1080)
    rows = [
        ('01', '资质', '机构入驻要「三证」+ 淘宝企业账号 + 绑定支付宝；个人与一人公司能否直接进，公开信息没写。', RUST),
        ('02', '产能', '单集 ≥40 秒；每月 ≥2 部全集短剧；30 天内删除比例 <20%。这是按月供片的节奏，不是做一部试试。', TEAL),
        ('03', '内容方向', '以商品为起点、以真实为核心、以交易为落点；纯故事不够，要能挂商品、能进店。', GOLD),
    ]
    y = 238
    for num, head, body, color in rows:
        d.rounded_rectangle((72, y, 1008, y + 176), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 176), radius=4, fill=color)
        put(d, 104, y + 18, num, 22, color, 'number', 200)
        put(d, 150, y + 14, head, 30, INK, 'bold', 980)
        paragraph(d, 150, y + 64, body, width=820, size=22, color=DIM, leading=34)
        y += 192

    d.rounded_rectangle((72, y + 2, 1008, y + 136), radius=12, fill=SOFT)
    put(d, 100, y + 16, '四个切口（媒体报道口径）', 20, RUST, 'bold', 980)
    put(d, 100, y + 50, '文旅 · 非遗 · 助农 · 国货', 30, INK, 'bold', 980)
    put(d, 100, y + 96, '不是平台官方文件，但方向和招商描述一致。', 19, DIM, 'body', 980)

    footer(d, y + 156, [
        '来源：DataEye 短剧观察 2026-10-22；流媒体网 2026-10-23 周报。',
        '内容门槛来自报道转述；报名入口与审核标准以淘宝官方为准。',
    ])
    return im


def actions():
    im, d = page('一人厂牌的三件事', '先做能谈的样片，再谈能签的报价', '03', 1060)
    blocks = [
        ('01', '先做一部商品原生样片', '10—20 集、单集 40 秒以上，选一个本地产业带或国货品牌，把商品写进剧情，不是贴片。', RUST),
        ('02', '报价拆三段：制作费 / 保底 / 分成', '问清达标条件、保底覆盖几部、分成按什么口径结算；把「最高」换成「达到什么条件给多少」。', TEAL),
        ('03', '资质路径提前定', '自己办个体户或公司，还是挂靠有资质机构；挂靠合同写清署名、分成、素材归属。', GOLD),
    ]
    y = 238
    for num, head, body, color in blocks:
        d.rounded_rectangle((72, y, 1008, y + 178), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 178), radius=4, fill=color)
        put(d, 104, y + 18, num, 22, color, 'number', 200)
        put(d, 150, y + 14, head, 28, INK, 'bold', 980)
        paragraph(d, 150, y + 62, body, width=820, size=22, color=DIM, leading=34)
        y += 194

    d.rounded_rectangle((72, y + 2, 1008, y + 96), radius=12, fill=INK)
    put(d, 100, y + 18, '只有一部剧的产能，先别冲真人档', 21, '#bdb3a1', right=980)
    put(d, 100, y + 50, 'AI 档试错成本更低，也接近一人产能', 26, '#f0c588', 'bold', 980)

    footer(d, y + 116, [
        '以上为执行建议，不是平台规则；资质、报名与结算以淘宝官方为准。',
        '本号建议 · C 级；数据来源见正文。',
    ])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    center(d, 450, 54, '双 11 短剧招商', 22, '#f0c588', 'bold', True)
    center(d, 450, 92, '一人厂牌能接哪一档', 38, WHITE, 'title', True)
    center(d, 450, 160, '30 万 / 150 万 / 300 万', 26, '#8fc0b4', 'bold', True)
    d.line((330, 214, 570, 214), fill='#766657', width=2)
    center(d, 450, 232, '先看门槛，再看上限', 22, '#d8cdbb', 'body', True)
    center(d, 450, 288, '三档钱，三种门槛', 19, '#bdb3a1', 'body', True)
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
    for name, maker in [('036_图1_三档钱_1080.png', money),
                        ('036_图2_三道门_1080.png', gates),
                        ('036_图3_三件事_1080.png', actions)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_036_双11短剧_900x383.png')
    print('done')
