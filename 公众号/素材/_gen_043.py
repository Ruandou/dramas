#!/usr/bin/env python3
"""043《出海 60 亿美元：AI 剧已经占六成》配图与封面。纯本地 Pillow，零扣费。"""
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


def market():
    im, d = page('海外，三个数', '2026 年中国以外市场 / 报告 2026-10-20', '01', 1000)
    put(d, 72, 236, '海外市场规模（2026 年预测）', 22, DIM, 'bold', 700)
    put(d, 72, 268, '60 亿美元', 64, TEAL, 'bold', 620)
    w = d.textlength('60 亿美元', font=font(64, 'bold'))
    put(d, 72 + w + 16, 296, '同比 +67%', 30, RUST, 'bold', 900)

    cards = [
        ('10 / 10', '下载量前 10', '均为中国背景平台', RUST),
        ('9 / 10', '内购收入前 10', '前 9 席为中国背景', GOLD),
    ]
    y = 400
    for big, head, sub, color in cards:
        d.rounded_rectangle((72, y, 1008, y + 132), radius=12, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 132), radius=4, fill=color)
        put(d, 104, y + 24, big, 46, color, 'number', 420)
        put(d, 360, y + 30, head, 26, INK, 'bold', 760)
        put(d, 360, y + 74, sub, 21, DIM, 'body', 980)
        y += 148

    d.rounded_rectangle((72, y + 4, 1008, y + 96), radius=12, fill=INK)
    put(d, 100, y + 18, '市场在涨，渠道也在中国人手里', 21, '#bdb3a1', right=980)
    put(d, 100, y + 50, '先选平台，再谈内容', 30, '#f0c588', 'bold', 980)

    footer(d, y + 116, [
        '来源：国家广电总局《中国—东盟微短剧国际传播发展报告》2026-10-20；北京日报等转述。',
        '60 亿美元为 2026 年预测值，不是已实现收入；「中国背景」按平台归属判断。',
    ])
    return im


def structure():
    im, d = page('结构在变：本土剧翻倍，AI 剧过半', '2026 年 5 月 vs 9 月 / 出海微短剧', '02', 1000)
    rows = [
        ('本土剧', '5%', '11%', '5 月 → 9 月，翻了一倍多', RUST),
        ('译制剧', '95%', '89%', '仍是绝对主力', TEAL),
        ('AI 剧', '—', '>60%', '截至 9 月底，占出海短剧六成以上', GOLD),
    ]
    y = 236
    for name, before, after, note, color in rows:
        d.rounded_rectangle((72, y, 1008, y + 164), radius=12, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 164), radius=4, fill=color)
        put(d, 104, y + 22, name, 27, INK, 'bold', 320)
        put(d, 340, y + 18, before, 34, DIM, 'number', 500)
        put(d, 470, y + 24, '→', 26, DIM, 'body', 520)
        put(d, 540, y + 18, after, 34, color, 'number', 700)
        put(d, 104, y + 100, note, 21, DIM, 'body', 980)
        y += 180

    d.rounded_rectangle((72, y + 2, 1008, y + 96), radius=12, fill=SOFT)
    put(d, 100, y + 16, '出海主力产能，是 AI 生成加译制', 22, RUST, 'bold', 980)
    put(d, 100, y + 54, '不是海外实拍，也不是先搭多语种团队。', 20, DIM, 'body', 980)

    footer(d, y + 116, [
        '来源：同报告，北京日报 2026-10-20 转述；AI 剧占比口径（部数/时长/收入）报告未说明。',
        '5 月与 9 月为两个时点，不能代表全年；译制剧与本土剧按上线内容统计。',
    ])
    return im


def actions():
    im, d = page('一人厂牌的三件事', '用 AI 产能接出海的活', '03', 1020)
    blocks = [
        ('01', '先做 AI 剧，别先搭海外剧组', '六成以上占比说明平台已经在收；先解决选题和完播，不是签证和场地。', RUST),
        ('02', '先译制，再本土化', '译制仍占 89%；总台多语种平台把 AI 译制压到 300—500 元/部（B 级），先跑一部。', TEAL),
        ('03', '先选平台，再谈内容', '下载前 10、内购前 9 都是中国背景；签前问清分账口径、结算周期、是否独家。', GOLD),
    ]
    y = 236
    for num, head, body, color in blocks:
        d.rounded_rectangle((72, y, 1008, y + 178), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 178), radius=4, fill=color)
        put(d, 104, y + 18, num, 22, color, 'number', 200)
        put(d, 150, y + 14, head, 28, INK, 'bold', 980)
        paragraph(d, 150, y + 62, body, width=820, size=22, color=DIM, leading=34)
        y += 194

    d.rounded_rectangle((72, y + 2, 1008, y + 96), radius=12, fill=INK)
    put(d, 100, y + 18, '渠道集中，谈判筹码在平台那边', 21, '#bdb3a1', right=980)
    put(d, 100, y + 50, '合同要比内容看得更细', 26, '#f0c588', 'bold', 980)

    footer(d, y + 116, [
        '以上为执行建议，不是平台规则；译制价格为媒体转述，随语种/时长波动。',
        '本号建议 · C 级；数据来源见正文。',
    ])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    center(d, 450, 54, '海外短剧市场', 22, '#f0c588', 'bold', True)
    center(d, 450, 92, '60 亿美元：AI 剧六成', 36, WHITE, 'title', True)
    center(d, 450, 158, '下载前 10：10/10 中国背景', 22, '#8fc0b4', 'bold', True)
    d.line((330, 210, 570, 210), fill='#766657', width=2)
    center(d, 450, 228, '先平台，再内容', 22, '#d8cdbb', 'body', True)
    center(d, 450, 284, '先译制，再本土化', 19, '#bdb3a1', 'body', True)
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
    for name, maker in [('043_图1_海外三个数_1080.png', market),
                        ('043_图2_结构变化_1080.png', structure),
                        ('043_图3_三件事_1080.png', actions)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_043_出海60亿_900x383.png')
    print('done')
