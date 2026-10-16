#!/usr/bin/env python3
"""022《厂牌实操02｜出图之前》配图与封面。

版式与断言沿用 _gen_021.py：字形覆盖、文本量宽、画布边界、文本框不重叠、中央安全区。
运行：/usr/local/bin/python3 _gen_022.py
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
TITLE = '厂牌实操02｜出图之前：用一页纸把视觉定死'
DIGEST = '第 ③ 阶段按张计费：参考图 ¥0.72/张，改一次主意就重出一批图。本篇给可抄的一页纸字段、三类图的依赖顺序，以及四条踩过的禁令。'
FIGURES = [
    ('022_图1_三类图顺序_1080.png', '三类图的依赖顺序与门控'),
    ('022_图2_一页纸字段_1080.png', '一页纸的字段（角色 / 道具 / 场景）'),
    ('022_图3_四条白花钱的坑_1080.png', '四条会白花钱的坑'),
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
    put(d, 100, 42, '一人短剧厂牌 / 厂牌实操 02', 21, DIM, 'bold')
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
    im, d = page('三类图有先后：道具 → 角色 ∥ 场景', '顺序错了，就是重出一批图', '01', 1340)
    d.rounded_rectangle((72, 246, 1008, 372), radius=16, fill=TEAL)
    put(d, 100, 268, '先出：道具图', 32, WHITE, 'bold', 980)
    put(d, 100, 314, '装备 / 信物 / 器械，会被反复拍到的东西', 23, '#d8e7e3', right=980)
    put(d, 72, 390, '↓  道具出完，且传上对象存储拿到永久地址（硬门控）', 26, INK, 'bold', 1008)
    for i, (x, label, note, color) in enumerate([
        (72, '后出：角色图', '握着道具 → 引用同一张道具参考图', GOLD),
        (568, '后出：场景图', '摆着道具 → 引用同一张道具参考图', GOLD)]):
        d.rounded_rectangle((x, 448, x + 440, 610), radius=16, fill=WHITE)
        put(d, x + 26, 470, label, 30, color, 'bold', x + 416)
        paragraph(d, x + 26, 516, note, width=390, size=23, color=INK, leading=34)
    d.rounded_rectangle((266, 632, 814, 700), radius=14, fill=WHITE)
    put(d, 290, 648, '角色与场景可并行', 26, TEAL, 'bold', 790)
    put(d, 72, 736, '先出角色图会怎样', 28, INK, 'bold')
    d.line((72, 776, 1008, 776), fill=RUST, width=3)
    y = 800
    for text in ['角色手上的东西，和后来的道具参考图不是一件；',
                 '要么改角色图（重扣费），要么让后面每一集都别扭。']:
        put(d, 96, y, text, 26, INK, right=1008)
        y += 54
    footer(d, y + 60, ['本图为执行顺序说明，非平台规则；成本口径见正文。',
                       '门控内容：道具未出完 / 未拿到永久地址，角色与场景不开工。'])
    return im


def chart_two():
    im, d = page('一页纸的字段', '写完能一句话复述，才算定死', '02', 1320)
    cols = [
        (72, TEAL, '角色', ['身份与年龄', '外形锚点（脸/发/特征）', '服装与材质', '年代与地域', '随身物件 → 道具 ID']),
        (568, GOLD, '道具', ['名称与用途', '尺寸与材质', '新旧与磨损', '出现在谁身上', '→ 角色 / 场景引用']),
    ]
    for x, color, head, items in cols:
        d.rounded_rectangle((x, 246, x + 440, 700), radius=16, fill=WHITE)
        d.rounded_rectangle((x, 246, x + 440, 330), radius=16, fill=color)
        put(d, x + 26, 262, head, 32, WHITE, 'bold', x + 416)
        y = 352
        for it in items:
            put(d, x + 26, y, '· ' + it, 25, INK, right=x + 416)
            y += 62
    d.rounded_rectangle((72, 726, 1008, 1046), radius=16, fill=WHITE)
    d.rounded_rectangle((72, 726, 1008, 810), radius=16, fill=RUST)
    put(d, 100, 742, '场景', 32, WHITE, 'bold', 980)
    y = 832
    for it in ['空间结构（几进几出、门窗朝向）', '光源与时段（晨 / 午 / 夜、室内外）',
               '季节与天气', '固定陈设 → 道具 ID', '基准图之外的状态（打烊、雨后）另出变体']:
        put(d, 100, y, '· ' + it, 25, INK, right=980)
        y += 42
    footer(d, 1082, ['字段为本号工作法整理；重点是「可复述」，不是字段数量。'])
    return im


def chart_three():
    im, d = page('四条会白花钱的坑', '都踩过，写进规则才消停', '03', 1280)
    items = [
        (RUST, '禁人脸', '场景图、道具图里不出现人脸——人脸由视频生成阶段单独加。'),
        (RUST, '自然锚点', '道具要绑在具体物理位置：握在手里 / 挂在腰上 / 摆在桌面上。'),
        (GOLD, '简体中文', '指令里写 Simplified Chinese，只写 Chinese 可能出繁体。'),
        (GOLD, '文字拼全', '画面里要出现的字，必须在指令里完整拼出来。'),
    ]
    y = 246
    for color, tag, text in items:
        d.rounded_rectangle((72, y, 1008, y + 108), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 80, y + 108), radius=4, fill=color)
        put(d, 104, y + 20, tag, 28, color, 'bold', 980)
        put(d, 104, y + 62, text, 23, INK, right=980)
        y += 124
    d.rounded_rectangle((72, y + 16, 1008, y + 250), radius=14, fill=INK)
    put(d, 100, y + 40, '还有一层：给脸上叠网格', 28, '#f0c588', 'bold')
    put(d, 100, y + 86, '照片级写实人脸会被视频接口按「疑似真人」拒收 → 面部叠三角网格后再提交。', 23, WHITE, right=980)
    put(d, 100, y + 126, '两条边界：网格版只喂给视频生成（换装/受伤仍传原图）；', 23, WHITE, right=980)
    put(d, 100, y + 166, '背影、剪影不需要网格，但豁免原因要登记，否则下游当缺口重做。', 23, WHITE, right=980)
    footer(d, y + 300, ['四条禁令来自本号事故复盘；网格方案为等白名单期间的工程手段。'])
    return im


def cover_a():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    put(d, 744, 28, '实操 02', 18, '#bdb3a1', right=875)
    for i, (w, color) in enumerate([(150, '#b55b32'), (104, '#28695e'), (58, '#b9853d')]):
        y = 104 + i * 44
        d.rounded_rectangle((40, y, 40 + w, y + 30), radius=8, fill=color)
    center(d, 450, 76, '出图之前', 26, '#f0c588', 'bold', True)
    center(d, 450, 122, '先写一页纸', 56, WHITE, 'title', True)
    d.line((306, 262, 594, 262), fill='#766657', width=2)
    center(d, 450, 282, '三类图 · 五类字段 · 四条禁令', 20, '#bdb3a1', 'body', True)
    for i in range(3):
        d.rounded_rectangle((740, 300 + i * 18, 862 - i * 26, 310 + i * 18), radius=3, fill='#574e45')
    return im


def cover_b():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, DIM, right=900)
    put(d, 744, 28, '实操 02', 18, DIM, right=875)
    center(d, 450, 74, '第 ③ 阶段 · 视觉设计', 24, TEAL, 'bold', True)
    center(d, 450, 118, '一页纸定死', 54, INK, 'title', True)
    center(d, 450, 192, '再开图', 54, RUST, 'title', True)
    center(d, 450, 298, '道具 → 角色 ∥ 场景', 22, TEAL, 'bold', True)
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
        put(d, 28, y, ['A / 深色：强调「先写一页纸」', 'B / 浅色：强调「一页纸定死再开图」'][index], 26, INK, 'bold', 1450)
        im.paste(cover, (28, y + 55))
        d.rectangle((286, y + 55, 669, y + 437), outline='#b48e60', width=1)
        crop = cover.crop((258, 0, 641, 383)).resize((142, 142), Image.Resampling.LANCZOS)
        for j, (bg, fg) in enumerate([('#ffffff', INK), ('#191919', '#f5efe4')]):
            x = 958 + j * 254
            d.rounded_rectangle((x, y + 55, x + 228, y + 437), radius=16, fill=bg)
            put(d, x + 18, y + 75, ['浅色分享卡', '深色分享卡'][j], 19, fg, right=x + 217)
            im.paste(crop, (x + 43, y + 129))
            put(d, x + 18, y + 296, '出图之前：一页纸', 18, fg, right=x + 217)
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
    cover_names = ['封面_022_A_先写一页纸_900x383.png', '封面_022_B_一页纸定死_900x383.png']
    for im, name in zip(covers, cover_names):
        save_png(im, OUT / name)
    save_png(cover_review(covers), OUT / '对照_022封面两方向.png')
    sheet = Image.new('RGB', (1212, 640), '#e5e2dc')
    for i, im in enumerate(charts):
        thumb = im.copy()
        thumb.thumbnail((380, 590), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (12 + i * 402, 12))
    save_png(sheet, SAMPLES / '022_正文配图手机宽预览.png')
    body = (OUT.parent / '文章' / '022_发布版.md').read_text()
    assert len(TITLE) <= 64 and len(DIGEST) <= 120, (len(TITLE), len(DIGEST))
    for index, (name, caption) in enumerate(FIGURES, 1):
        assert f'【图 {index}：{caption}】' in body, (index, caption)
    print('PASS: figure captions match body; title', len(TITLE), 'digest', len(DIGEST))
