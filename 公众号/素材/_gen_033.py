#!/usr/bin/env python3
"""033《红果下线金币：收费没来，分账没提》配图与封面。

结构：公告时间线 → 8,321 亿分钟的三个口径。纯本地 Pillow，零扣费。
运行：/usr/local/bin/python3 _gen_033.py
"""
from pathlib import Path
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from _gen_charts_006 import f, HIRA, SONG, MONO

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = '#f3eee4', '#fffaf0', '#2c2925'
DIM, LINE, RUST, TEAL, GOLD = '#756d61', '#d4c9b8', '#ae422c', '#28695e', '#b9853d'
GREY = '#a2988a'
FONTS = {'body': (HIRA, 0), 'bold': (HIRA, 2), 'title': (SONG, 1), 'number': (MONO, 1)}
GLYPHS, TEXT_BOXES = {}, []
TITLE = '红果下线金币：收费没来，分账没提'


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


def timeline():
    im, d = page('公告给了两个节点，不是一刀切', '11 月 1 日新用户先停，12 月 31 日前全量停止', '01', 1040)
    d.line((140, 280, 140, 660), fill=LINE, width=3)
    nodes = [
        (280, '10-21', '公告发布', RUST, ['金币功能计划下线；未写原因', '已获得金币与现金收益不受影响']),
        (470, '11-01', '新激活用户先停', TEAL, ['不再有金币入口，看剧不领金币', '存量用户这一阶段不受影响']),
        (660, '12-31', '全量停止发放', GOLD, ['所有用户不再获得金币', '提现截止日「后续公布」']),
    ]
    for cy, date, head, color, lines in nodes:
        d.ellipse((127, cy - 13, 153, cy + 13), fill=color)
        put(d, 190, cy - 26, date, 26, color, 'number', 320)
        put(d, 330, cy - 22, head, 28, INK, 'bold', 980)
        for i, line in enumerate(lines):
            put(d, 190, cy + 24 + i * 38, line, 22, DIM if i else INK, right=980)
    d.rounded_rectangle((72, 780, 1008, 910), radius=14, fill=INK)
    put(d, 100, 802, '两个节点不是一回事：11-1 只卡新激活用户，12-31 前才全量。', 22, WHITE, right=980)
    put(d, 100, 842, '公告没提：收费、分账、提现截止日。', 22, '#f0c588', 'bold', right=980)
    put(d, 100, 878, '客服口径：内容免费，不会收费（媒体致电）。', 20, '#bdb3a1', right=980)
    footer(d, 928, ['来源：红果短剧公告 2026-10-21（IT 时代网转载）；凤凰网、白鹿视频客服回应 2026-10-21。'])
    return im


def numbers():
    im, d = page('8,321 亿分钟，反推不出日活', '一个月总时长、一个人均时长，除出来的是第三种口径', '02', 1060)
    put(d, 72, 248, '月总使用时长', 22, DIM, 'bold', 500)
    put(d, 72, 280, '8,321 亿分钟', 44, TEAL, 'bold', 700)
    put(d, 72, 344, 'QuestMobile 2026 Q3，7—8 月月均', 21, DIM, right=900)

    put(d, 72, 410, '人均单日使用时长', 22, DIM, 'bold', 500)
    put(d, 72, 442, '151 分钟', 44, GOLD, 'bold', 700)
    put(d, 72, 506, '按活跃用户摊；转引未写具体口径', 21, DIM, right=900)

    d.rounded_rectangle((72, 560, 1008, 690), radius=14, fill=INK)
    put(d, 100, 582, '832,100,000,000 ÷ 30.4 ÷ 151', 26, WHITE, 'number', 980)
    put(d, 100, 634, '≈ 181,000,000 人/日（本号反推，C 级）', 23, '#f0c588', 'bold', 980)

    cards = [
        ('DAU 1 亿', '2026-01 媒体口径', INK),
        ('MAU 3 亿', '2026-02 媒体口径', INK),
        ('反推 1.81 亿', '本号计算，C 级', RUST),
    ]
    for i, (head, sub, color) in enumerate(cards):
        x = 72 + i * 318
        d.rounded_rectangle((x, 720, x + 300, 832), radius=12, fill=WHITE)
        center(d, x + 150, 738, head, 30, color, 'bold')
        center(d, x + 150, 782, sub, 19, DIM, 'body')

    d.rounded_rectangle((72, 856, 1008, 922), radius=12, fill='#f7e9e3')
    put(d, 100, 868, '三个数对不上：日活涨了，或 151 分钟不是按日活摊的。', 20, RUST, 'bold', 980)
    put(d, 100, 894, '转引没写口径，别拿任何一个当报价分母。', 20, INK, right=980)

    footer(d, 938, ['来源：QuestMobile 2026 Q3 数据经 36 氪转引；公开 DAU/MAU 为 2026-01/02 媒体报道。'])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    center(d, 450, 62, '红果短剧', 20, '#f0c588', 'bold', True)
    center(d, 450, 92, '金币下线', 52, WHITE, 'title', True)
    center(d, 450, 164, '收费没来，分账没提', 34, WHITE, 'title', True)
    d.line((330, 232, 570, 232), fill='#766657', width=2)
    center(d, 450, 248, '11-1 新用户 / 12-31 全量', 21, '#8fc0b4', 'bold', True)
    center(d, 450, 292, '余额不受影响', 19, '#bdb3a1', 'body', True)
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
    for name, maker in [('033_图1_公告时间线_1080.png', timeline), ('033_图2_三个数_1080.png', numbers)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_033_收费没来_900x383.png')
    print('done')
