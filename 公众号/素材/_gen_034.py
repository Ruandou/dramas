#!/usr/bin/env python3
"""034《一天 1,795 部：49 万部微短剧，平均数不是你的观众》配图与封面。

结构：上新速度 → 上线/许可/备案三个池子 → 平台尺子。纯本地 Pillow，零扣费。
运行：/usr/local/bin/python3 _gen_034.py
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


def speed():
    im, d = page('一天 1,795 部，摊下来是什么', '49 万部 ÷ 273 天；2025 年按 365 天摊是 90 部/天', '01', 1040)
    put(d, 72, 240, '2026 年 1—9 月，平均每天上线', 22, DIM, 'bold', 500)
    put(d, 72, 270, '1,795 部', 74, TEAL, 'bold', 620)
    big_w = d.textlength('1,795 部', font=font(74, 'bold'))
    put(d, 72 + big_w + 14, 318, '/ 天', 30, TEAL, 'bold', 700)
    put(d, 72, 372, '49 万部是 9 个月累计，不是市场规模的替代数', 21, DIM, right=1008)

    put(d, 72, 424, '2026 年 1—9 月', 20, DIM, 'bold', 500)
    put(d, 72, 450, '1,795 部/天', 26, TEAL, 'bold', 500)
    d.rounded_rectangle((72, 486, 832, 530), radius=8, fill=TEAL)

    put(d, 72, 552, '2025 年全年', 20, DIM, 'bold', 500)
    put(d, 72, 578, '90 部/天', 26, GOLD, 'bold', 500)
    d.rounded_rectangle((72, 614, 110, 658), radius=8, fill=GOLD)
    put(d, 132, 616, '按天摊，2026 是 2025 的 19.9 倍', 22, RUST, 'bold', 760)

    d.line((72, 700, 1008, 700), fill=LINE, width=2)
    put(d, 72, 718, '一天上新的量，一个人连看要多久', 22, DIM, 'bold', 600)
    put(d, 72, 756, '60 分钟/部 → 1,795 小时/天 → 75 天', 26, INK, 'bold', 900)
    put(d, 72, 798, '80 分钟/部 → 2,393 小时/天 → 100 天', 26, INK, 'bold', 900)
    put(d, 760, 758, '本号估算 · C 级', 19, RUST, right=1008)

    d.rounded_rectangle((72, 846, 1008, 900), radius=12, fill=INK)
    put(d, 100, 858, '供给的增长速度，已经快于注意力的增长速度。', 23, '#f0c588', 'bold', 980)
    footer(d, 918, ['来源：2026-10-20《中国—东盟微短剧国际传播发展报告》媒体转述。',
                    '49 万部、3.3 万部、13 倍来自转述；除数为本号计算；60/80 分钟每部为估算，不是平台数据。'])
    return im


def pools():
    im, d = page('上线、许可、备案，不是一个池子', '同一批供给，三个口径，三个量级', '02', 1040)
    put(d, 72, 236, '同一组数，三个倍数', 22, DIM, 'bold', 500)
    cards = [
        ('13 倍', '官方通稿', '口径未说明', RUST),
        ('14.8 倍', '49 万 ÷ 3.3 万', '9 个月对 12 个月', TEAL),
        ('19.9 倍', '1,795 ÷ 90', '按天摊', GOLD),
    ]
    for i, (big, mid, small, color) in enumerate(cards):
        x = 72 + i * 318
        d.rounded_rectangle((x, 266, x + 300, 376), radius=12, fill=WHITE)
        center(d, x + 150, 278, big, 36, color, 'bold')
        center(d, x + 150, 326, mid, 18, INK, 'body')
        center(d, x + 150, 352, small, 17, DIM, 'body')

    put(d, 72, 400, '三个池子，各归各的', 22, DIM, 'bold', 500)
    rows = [
        ('上线播出', '49 万部（2026 1—9 月）', '各平台上线，含三类', '能说明上新速度', TEAL),
        ('发行许可', '159 部 · 5,396 集（2026 Q2）', '只覆盖一类、二类', '季度口径，不含三类', GOLD),
        ('备案公示', '296 部（2026 年 9 月）', '电视剧、网络剧', '不含微短剧', RUST),
    ]
    for i, (name, big, cover, verdict, color) in enumerate(rows):
        y = 432 + i * 126
        d.rounded_rectangle((72, y, 1008, y + 108), radius=12, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 108), radius=4, fill=color)
        put(d, 104, y + 12, name, 26, INK, 'bold', 300)
        put(d, 104, y + 50, big, 27, color, 'bold', 600)
        put(d, 600, y + 16, cover, 19, DIM, 'body', 860)
        put(d, 600, y + 54, verdict, 21, color, 'bold', 980)

    d.rounded_rectangle((72, 822, 1008, 900), radius=12, fill='#f7e9e3')
    put(d, 100, 834, '49 万部说明的是上新速度，不是市场规模，', 21, RUST, 'bold', 980)
    put(d, 100, 866, '也不是合规数量。', 21, RUST, 'bold', 980)
    footer(d, 918, ['来源：广电总局《微短剧发展管理办法》第十七条（2026-07-31）；',
                    '发行许可通报 2026-07-13：159 部、5,396 集（2026 Q2）；',
                    '9 月备案公示 296 部为电视剧/网络剧口径；报告数字为媒体转述。'])
    return im


def rulers():
    im, d = page('平台给钱，从「上架」转向「看完」', '三家尺子不一样，量的都不是「你上了多少部」', '03', 1060)
    blocks = [
        ('快手', '10—11 月「好剧、系列剧激励」', RUST, [
            '时长达标 +15%　完播率达标 +15%',
            '第二季 60 天内上线 +20%；可叠加',
            '封顶 50%，单剧最高 20 万元',
        ], '媒体转述 · B 级'),
        ('微信', 'Q4 联合发行', TEAL, [
            '人均看剧 ≥10 分钟：75% 现金 + 10% 广告金',
            '不到 10 分钟：50% 现金',
            '优质新剧：90% 现金 + 10% 广告金',
        ], '官方文档 · A 级'),
        ('红果', '金币退场', GOLD, [
            '11-01 起，新激活用户停发金币',
            '12-31 前，全量用户停止发放',
            '已有金币与现金余额不受影响',
        ], '官方公告 · A 级'),
    ]
    y = 236
    for name, head, color, lines, level in blocks:
        h = 172 if name != '红果' else 160
        d.rounded_rectangle((72, y, 1008, y + h), radius=12, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + h), radius=4, fill=color)
        put(d, 104, y + 14, name, 28, color, 'bold', 240)
        put(d, 190, y + 22, head, 21, INK, 'bold', 780)
        put(d, 800, y + 22, level, 18, DIM, right=980)
        for i, line in enumerate(lines):
            put(d, 104, y + 62 + i * 36, line, 21, INK if i == 0 else DIM, 'body', 980)
        y += h + 20

    d.rounded_rectangle((72, y + 8, 1008, y + 92), radius=12, fill=INK)
    put(d, 100, y + 22, '该记的三个数', 20, '#bdb3a1', right=980)
    put(d, 100, y + 52, '有效播放时长 · 完播率 · 推荐占比', 28, '#f0c588', 'bold', 980)
    footer(d, y + 110, ['来源：快手激励经新浪财经 2026-09-30、财富号 2026-10-10 转述；',
                        '微信 Q4 文档经本号 027 逐字读取；红果公告 2026-10-21。'])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    center(d, 450, 62, '49 万部微短剧', 20, '#f0c588', 'bold', True)
    center(d, 450, 92, '一天 1,795 部', 52, WHITE, 'title', True)
    center(d, 450, 164, '平均数不是你的观众', 33, WHITE, 'title', True)
    d.line((330, 232, 570, 232), fill='#766657', width=2)
    center(d, 450, 248, '13 倍 / 14.8 倍 / 19.9 倍', 21, '#8fc0b4', 'bold', True)
    center(d, 450, 292, '同一组数，三个口径', 19, '#bdb3a1', 'body', True)
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
    for name, maker in [('034_图1_一天1795部_1080.png', speed),
                        ('034_图2_三个口径_1080.png', pools),
                        ('034_图3_平台的尺子_1080.png', rulers)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_034_一天1795_900x383.png')
    print('done')
