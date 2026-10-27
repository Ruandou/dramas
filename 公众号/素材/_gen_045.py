#!/usr/bin/env python3
"""045《横店之夜：15% 预算，要花在剧本上》配图与封面。纯本地 Pillow。"""
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


def budget():
    im, d = page('至少 15%，给剧本和后期', '横店微短剧之夜 / 行业自律倡议 / 2026-10-25', '01', 1040)
    put(d, 72, 240, '15%', 110, RUST, 'title', 500)
    put(d, 72, 394, '这条线：剧本 + 后期', 30, INK, 'bold', 900)

    cards = [
        ('剧本', '开发 · 修改 · 围读', RUST),
        ('后期', '剪辑 · 调色 · 声音', TEAL),
    ]
    y = 480
    for name, detail, color in cards:
        d.rounded_rectangle((72, y, 1008, y + 120), radius=12, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 120), radius=4, fill=color)
        put(d, 104, y + 22, name, 30, color, 'bold', 300)
        put(d, 300, y + 34, detail, 24, INK, 'body', 980)
        y += 136

    d.rounded_rectangle((72, y + 6, 1008, y + 100), radius=12, fill=INK)
    put(d, 100, y + 18, '这是自律倡议，不是强制规则', 21, '#bdb3a1', right=980)
    put(d, 100, y + 52, '但它给了你一条可对照的投入线', 26, '#f0c588', 'bold', 980)

    footer(d, y + 120, [
        '来源：新浪娱乐 2026-10-27；浙江在线 2026-10-26。倡议原文未公开。',
        '「至少 15%」为现场行业自律倡议，不是主管部门规定，无强制约束力。',
    ])
    return im


def signals():
    im, d = page('三个信号，比奖项本身重要', '奖项扩容 / 真人表演 / 两个盘子', '02', 1080)
    blocks = [
        ('01', '奖项扩容到全链条', '演员、编剧、导演、制片、作品；横屏竖屏都算，首次单设出海与 AI 创新奖。', RUST),
        ('02', '真人表演被反复强调', '获奖演员谈 AI 冲击，认为真人表演的魅力不可替代——和总局 Q2 名单同向。', TEAL),
        ('03', '报告给了两个盘子', '2024 全球市场超 500 亿元、中国占 60%+；2025 Q1 海外下载超 2.7 亿人次、收入超 24 亿元。', GOLD),
    ]
    y = 238
    for num, head, body, color in blocks:
        d.rounded_rectangle((72, y, 1008, y + 180), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 180), radius=4, fill=color)
        put(d, 104, y + 18, num, 22, color, 'number', 200)
        put(d, 150, y + 14, head, 27, INK, 'bold', 980)
        paragraph(d, 150, y + 64, body, width=820, size=21, color=DIM, leading=33)
        y += 196

    d.rounded_rectangle((72, y + 2, 1008, y + 96), radius=12, fill=SOFT)
    put(d, 100, y + 16, '奖给谁，就是在告诉制作方做什么', 21, RUST, 'bold', 980)
    put(d, 100, y + 52, '出海、AI、真人表演，今年都被点名。', 19, DIM, 'body', 980)

    footer(d, y + 116, [
        '来源：新浪娱乐 2026-10-27；报告数字为现场发布、媒体转述，原文未公开。',
        '「500 亿元 / 60% / 2.7 亿人次 / 24 亿元」口径未说明，引用时请连同来源。',
    ])
    return im


def actions():
    im, d = page('一人厂牌的三件事', '15% 是检查线，不是装饰', '03', 1020)
    blocks = [
        ('01', '按 15% 检查预算表', '剧本开发+修改、后期剪辑+调色+声音，加起来不到 15%，先减集数、减场景。', RUST),
        ('02', '把剧本当资产', '活动联动剧本征集，获奖剧本可对接制作资源；不一定要自己拍，先让剧本被看见。', TEAL),
        ('03', 'AI 用在流程，真人留在情绪戏', '分镜、预演、译制交给 AI；眼神、停顿、哭戏，仍要真人。', GOLD),
    ]
    y = 236
    for num, head, body, color in blocks:
        d.rounded_rectangle((72, y, 1008, y + 178), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 178), radius=4, fill=color)
        put(d, 104, y + 18, num, 22, color, 'number', 200)
        put(d, 150, y + 14, head, 27, INK, 'bold', 980)
        paragraph(d, 150, y + 62, body, width=820, size=22, color=DIM, leading=34)
        y += 194

    d.rounded_rectangle((72, y + 2, 1008, y + 96), radius=12, fill=INK)
    put(d, 100, y + 18, '工具负责效率，表演负责相信', 21, '#bdb3a1', right=980)
    put(d, 100, y + 50, '这是今年两次名单的共同取向', 26, '#f0c588', 'bold', 980)

    footer(d, y + 116, [
        '以上为执行建议，不是行业规则；15% 与自律公约均为倡议。',
        '本号建议 · C 级；来源见正文。',
    ])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    center(d, 450, 54, '横店微短剧之夜', 22, '#f0c588', 'bold', True)
    center(d, 450, 90, '15% 预算给剧本', 42, WHITE, 'title', True)
    center(d, 450, 158, '自律倡议，不是强制规则', 22, '#8fc0b4', 'bold', True)
    d.line((330, 210, 570, 210), fill='#766657', width=2)
    center(d, 450, 228, '奖项第一次给了 AI 和出海', 19, '#d8cdbb', 'body', True)
    center(d, 450, 284, '一人厂牌先查自己的预算表', 19, '#bdb3a1', 'body', True)
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
    for name, maker in [('045_图1_15预算_1080.png', budget),
                        ('045_图2_三个信号_1080.png', signals),
                        ('045_图3_三件事_1080.png', actions)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_045_15预算_900x383.png')
    print('done')
