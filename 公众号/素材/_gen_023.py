#!/usr/bin/env python3
"""023《为什么有的文章有「内容由AI生成」》配图与封面。

版式与断言沿用 _gen_022.py：字形覆盖、文本量宽、画布边界、文本框不重叠、封面中央安全区。
运行：python3 _gen_023.py
"""
from pathlib import Path
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from _gen_charts_006 import f, HIRA, SONG, MONO

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = '#f3eee4', '#fffaf0', '#2c2925'
DIM, LINE, RUST, TEAL, GOLD = '#756d61', '#d4c9b8', '#ae422c', '#28695e', '#b9853d'
FONTS = {'body': (HIRA, 0), 'bold': (HIRA, 2), 'title': (SONG, 1), 'number': (MONO, 1)}
GLYPHS, TEXT_BOXES = {}, []
HEAD = '一人短剧厂牌 / AI 标识'


def font(size, kind='body'):
    path, index = FONTS[kind]
    return f(path, size, index=index)


def put(d, x, y, text, size=28, color=INK, kind='body', right=1008):
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
    put(d, 100, 42, HEAD, 21, DIM, 'bold')
    put(d, 949, 42, number, 22, RUST, 'number')
    put(d, 72, 96, title, 44, INK, 'title')
    put(d, 72, 160, subtitle, 25, DIM)
    d.line((72, 207, 1008, 207), fill=LINE, width=2)
    return im, d


def footer(d, y, lines):
    d.line((72, y, 1008, y), fill=LINE, width=2)
    for line in lines:
        y = paragraph(d, 72, y + 16, line, size=21, color=DIM, leading=30)
    return y


def figure_one():
    """后台弹窗：原文 + 7 个单选。"""
    im, d = page('后台那个弹窗：两段原文，7 个单选', '默认「未添加」——不点开就看不见', '01', 1170)
    d.rounded_rectangle((72, 240, 1008, 985), radius=16, fill=WHITE)
    d.rounded_rectangle((72, 240, 1008, 322), radius=16, fill=INK)
    put(d, 104, 258, '创作来源', 32, WHITE, 'title', 980)
    y = 350
    put(d, 104, y, '原文', 21, RUST, 'bold')
    y = paragraph(d, 104, y + 34,
                  '根据《人工智能生成合成内容标识办法》要求，用户发布的内容为AI生成合成的，'
                  '发布时需主动进行声明。', width=872, size=25, color=INK, leading=38)
    put(d, 104, y + 12, '原文', 21, RUST, 'bold')
    y = paragraph(d, 104, y + 46,
                  '根据中央网信办《关于加强"自媒体"管理的通知》，发布内容涉及国内外时事、'
                  '公共政策、社会事件等信息时，需完成创作来源标注。如未规范标注，可能会被限制传播。',
                  width=872, size=25, color=INK, leading=38)
    put(d, 104, y + 22, '声明类型（单选）', 24, INK, 'bold')
    y += 62
    options = ['内容由AI生成', '素材来源官方媒体·网络新闻', '内容剧情演绎，仅供娱乐',
               '个人观点，仅供参考', '健康医疗分享，仅供参考', '投资观点，仅供参考', '无需声明']
    for i, opt in enumerate(options):
        x = 104 if i % 2 == 0 else 560
        row = y + (i // 2) * 62
        color = RUST if i == 0 else DIM
        d.ellipse((x, row + 4, x + 24, row + 28), outline=color, width=3)
        if i == 0:
            d.ellipse((x + 7, row + 11, x + 17, row + 21), fill=RUST)
        put(d, x + 38, row + 2, opt, 25, INK if i == 0 else DIM, 'bold' if i == 0 else 'body', x + 430)
    footer(d, 1009, [
        'B 级：2026-10-17 本号公众号后台实测；弹窗文字为原文照抄，界面为示意重绘，非截图。',
        '单选意味着：一篇文章只能挂一个声明类型。',
    ])
    return im


def figure_two():
    """两条路径对照。"""
    im, d = page('两条路径：作者声明，和平台提示', '一个是你选的，一个是平台加的', '02', 1240)
    for x, color, head, lines in [
        (72, TEAL, '作者声明', ['依据：办法第十条', '谁做：发布内容的人', '读者看到：作者从 7 项里选的那一行']),
        (568, GOLD, '平台提示', ['依据：办法第六条', '谁做：传播平台', '读者看到：生成合成 / 可能 / 疑似 三档']),
    ]:
        d.rounded_rectangle((x, 240, x + 440, 640), radius=16, fill=WHITE)
        d.rounded_rectangle((x, 240, x + 440, 322), radius=16, fill=color)
        put(d, x + 26, 256, head, 32, WHITE, 'title', x + 416)
        y = 352
        for line in lines:
            y = paragraph(d, x + 26, y, line, width=386, size=24, color=INK, leading=36) + 22
    d.rounded_rectangle((72, 672, 1008, 1000), radius=16, fill=INK)
    put(d, 104, 700, '两边都是弱信号', 30, '#f0c588', 'title', 980)
    y = 756
    for line in ['没标那行字 ≠ 这不是 AI 做的——平台被法规要求用「可能」「疑似」这种措辞，因为判不准；',
                 '标了那行字 ≠ 平台判定过——那是作者自己勾的，一份自述。',
                 '所以：看到标签，读作「作者说自己用了 AI」，而不是「平台查实了」。']:
        y = paragraph(d, 104, y, line, width=872, size=25, color=WHITE, leading=38) + 14
    footer(d, 1024, ['依据：《人工智能生成合成内容标识办法》第十条（用户主动声明）、第六条（平台核验与提示）。'])
    return im


def figure_three():
    """四件事速记。"""
    im, d = page('一句话记住四件事', '下次再看到那行字，不用猜', '03', 1180)
    items = [
        (RUST, '那行字是作者勾的', '后台「创作来源」默认「未添加」，7 个单选里第一个就是它。'),
        (RUST, '平台另有三种话术', '生成合成 / 可能为生成合成 / 疑似生成合成（办法第六条）。'),
        (GOLD, '时事·公共政策类是另一条线', '要标创作来源。平台原文：如未规范标注，可能会被限制传播。'),
        (TEAL, '「标了 AI 就限流」没有官方说法', '微信侧我没查到；知乎官方说外显标识不影响流量（跨平台参照）。'),
    ]
    y = 240
    for color, tag, text in items:
        d.rounded_rectangle((72, y, 1008, y + 132), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 80, y + 132), radius=4, fill=color)
        put(d, 104, y + 24, tag, 29, color, 'bold', 980)
        paragraph(d, 104, y + 72, text, width=872, size=23, color=INK, leading=32)
        y += 152
    footer(d, y + 24, [
        '四条的证据等级见正文：第 1、2 条 A 级（法规原文）+ B 级（后台实测），第 3 条 B 级（平台界面原文），',
        '第 4 条「微信无官方说法」是「没查到」，不等于「不影响」。',
    ])
    return im


def cover_a():
    """封面 A：浅底。"""
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, DIM, right=900)
    put(d, 744, 28, 'AI 标识', 18, DIM, right=875)
    center(d, 450, 74, '那行字是谁加的', 24, TEAL, 'bold', True)
    center(d, 450, 112, '「内容由AI生成」', 38, INK, 'title', True)
    center(d, 450, 172, '作者自己勾的', 48, RUST, 'title', True)
    center(d, 450, 296, '后台一个默认关着的开关 · 7 个选项', 20, DIM, 'body', True)
    for i, (width, color) in enumerate([(200, RUST), (146, TEAL), (96, GOLD)]):
        y = 110 + i * 62
        d.rounded_rectangle((44, y, 44 + width, y + 26), radius=6, fill=color)
    for i, width in enumerate((176, 128, 86)):
        d.rounded_rectangle((856 - width, 116 + i * 62, 856, 138 + i * 62), radius=6, fill='#c2b7a6')
    return im


def cover_b():
    """封面 B：深底。"""
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    put(d, 744, 28, 'AI 标识', 18, '#bdb3a1', right=875)
    center(d, 450, 74, '17 篇在架文章', 24, '#f0c588', 'bold', True)
    center(d, 450, 114, '3 篇带着这行字', 46, WHITE, 'title', True)
    d.line((300, 196, 600, 196), fill='#766657', width=2)
    center(d, 450, 218, '「内容由AI生成」', 32, '#f0c588', 'title', True)
    center(d, 450, 284, '后台一个单选钮 · 字段值 1', 19, '#bdb3a1', 'body', True)
    for i, (width, color) in enumerate([(180, '#b55b32'), (124, '#28695e'), (74, '#b9853d')]):
        y = 112 + i * 60
        d.rounded_rectangle((44, y, 44 + width, y + 26), radius=6, fill=color)
    for i, width in enumerate((160, 112, 78)):
        d.rounded_rectangle((856 - width, 118 + i * 60, 856, 140 + i * 60), radius=6, fill='#574e45')
    return im


def check_glyphs():
    for (path, index), chars in GLYPHS.items():
        ff = TTFont(path, fontNumber=index)
        cmap = ff.getBestCmap()
        missing = sorted(c for c in chars if ord(c) not in cmap)
        ff.close()
        assert not missing, (path, index, missing)


def save(im, name, tag):
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / name
    im.quantize(colors=192, method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.NONE).save(dest, optimize=True)
    print(f'{name} {im.size} {dest.stat().st_size / 1024:.1f} KB  [{tag}]')


if __name__ == '__main__':
    for fn, name, tag in [
        (figure_one, '023_图1_后台创作来源弹窗_1080.png', 'fig1'),
        (figure_two, '023_图2_两条路径_1080.png', 'fig2'),
        (figure_three, '023_图3_四件事速记_1080.png', 'fig3'),
    ]:
        im = fn()
        check_glyphs()
        save(im, name, tag)
    for fn, name, tag in [
        (cover_a, '封面_023_A_作者自己勾的_900x383.png', 'coverA'),
        (cover_b, '封面_023_B_17篇3篇_900x383.png', 'coverB'),
    ]:
        im = fn()
        check_glyphs()
        save(im, name, tag)
    print(f'PASS: 字形覆盖、量宽、边界、不重叠；{len(TEXT_BOXES)} 个文本框（末页）')
