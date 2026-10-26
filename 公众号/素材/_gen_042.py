#!/usr/bin/env python3
"""042《14 部入选：总局的口味写在题材里》配图与封面。纯本地 Pillow，零扣费。"""
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


def genres():
    im, d = page('14 部，五类题材', '2026 Q2 优秀网络视听节目推选 · 微短剧', '01', 1180)
    rows = [
        ('4', '非遗传承', '顾盼锦年 / 英歌，舞起！/ 戏比天大 / 阿桂的夏天', RUST),
        ('3', '国安法治', '安全距离 / 荆棘花开 / 国安行动·芯片疑云', TEAL),
        ('3', '家国历史', '姐姐的三条簪 / 朝花 / 一品布衣4：割据篇', GOLD),
        ('3', '现实生活', '小满人间 / 弄潮2：千禧红 / 冒姓琅琊3', RUST),
        ('1', '乡村振兴', '去桃花盛开的地方2', TEAL),
    ]
    y = 236
    for n, genre, titles, color in rows:
        d.rounded_rectangle((72, y, 1008, y + 128), radius=12, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 128), radius=4, fill=color)
        put(d, 104, y + 18, n, 44, color, 'number', 220)
        put(d, 178, y + 22, genre, 28, INK, 'bold', 380)
        put(d, 178, y + 70, titles, 19, DIM, 'body', 980)
        y += 144

    d.rounded_rectangle((72, y + 2, 1008, y + 92), radius=12, fill=INK)
    put(d, 100, y + 16, '14 部里 4 部是续作', 21, '#bdb3a1', right=980)
    put(d, 100, y + 48, '去桃花2 · 弄潮2 · 冒姓琅琊3 · 一品布衣4', 24, '#f0c588', 'bold', 980)

    footer(d, y + 112, [
        '来源：国家广电总局 2026 Q2 优秀网络视听节目推选结果；新华社稿，广西新闻网 10-26 转载。',
        '题材按稿件表述归类；一部剧可能跨两类，本图只取稿件给出的主类。',
    ])
    return im


def shifts():
    im, d = page('四个转向', '新华社稿里的四句话，正好是四道选题门', '02', 1060)
    blocks = [
        ('题材', '从「扎堆跟风」到「百花齐放」', '非遗、国安、历史、现实、乡村，五类都有位置。', RUST),
        ('态度', '从「快速收割」到「匠心打磨」', '长春实景、拒绝磨皮、易俗社做艺术指导。', TEAL),
        ('价值', '从「情绪快消」到「精神滋养」', '未成年人保护、左联历史、抗倭小切口。', GOLD),
        ('主体', '从「草根试水」到「多元共筑」', '主流媒体、专业机构、权威部门入场。', RUST),
    ]
    y = 236
    for label, head, detail, color in blocks:
        d.rounded_rectangle((72, y, 1008, y + 140), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 140), radius=4, fill=color)
        put(d, 104, y + 18, label, 22, color, 'bold', 220)
        put(d, 170, y + 12, head, 27, INK, 'bold', 980)
        paragraph(d, 170, y + 58, detail, width=790, size=21, color=DIM, leading=32)
        y += 156

    d.rounded_rectangle((72, y + 4, 1008, y + 92), radius=12, fill=SOFT)
    put(d, 100, y + 20, '「真实」正在从修辞变成制作标准', 25, RUST, 'bold', 980)
    put(d, 100, y + 56, '实景、原声、不过度修饰，都是能被看见的成本。', 20, DIM, 'body', 980)

    footer(d, y + 112, [
        '来源：新华社稿（2026-10-26，广西新闻网转载）；四句概括为稿件原意。',
        '制作细节为媒体转述，未见总局原文；本图只做归纳，不构成评奖标准。',
    ])
    return im


def actions():
    im, d = page('一人厂牌的三件事', '别抄名单，抄名单背后的成本结构', '03', 1040)
    blocks = [
        ('01', '选能核验的现实切口', '非遗、地方产业、法治科普，先找真实素材和顾问；用 3 集试水，不押 80 集。', RUST),
        ('02', '把「真实」写进拍摄清单', '至少一场实景、一位真实从业者顾问、原声保留、不磨皮；AI 做分镜，不做质感替身。', TEAL),
        ('03', '立项就按「可续」设计', '14 部里 4 部续作；续人物和世界观，不重复同一个反转，留三条可展开的线。', GOLD),
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
    put(d, 100, y + 18, '名单不等于流量，但能当选题清单用', 21, '#bdb3a1', right=980)
    put(d, 100, y + 50, '五类题材，就是五个可核验的入口', 26, '#f0c588', 'bold', 980)

    footer(d, y + 116, [
        '以上为执行建议，不是评选或申报标准；入选与分账、流量无直接关系。',
        '本号建议 · C 级；名单与题材来源见正文。',
    ])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    center(d, 450, 54, '总局这份名单', 22, '#f0c588', 'bold', True)
    center(d, 450, 90, '14 部微短剧入选', 42, WHITE, 'title', True)
    center(d, 450, 158, '非遗 4 · 国安 3 · 历史 3', 24, '#8fc0b4', 'bold', True)
    d.line((330, 210, 570, 210), fill='#766657', width=2)
    center(d, 450, 228, '口味写在题材里', 22, '#d8cdbb', 'body', True)
    center(d, 450, 284, '现实 3 · 乡村 1 · 4 部续作', 19, '#bdb3a1', 'body', True)
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
    for name, maker in [('042_图1_五类题材_1080.png', genres),
                        ('042_图2_四个转向_1080.png', shifts),
                        ('042_图3_三件事_1080.png', actions)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_042_14部入选_900x383.png')
    print('done')
