#!/usr/bin/env python3
"""019《厂牌盯数03｜人均 10 分钟这条线》配图与封面。

版式与断言沿用 _gen_017.py：字形覆盖、文本量宽、画布边界、文本框不重叠、中央安全区。
运行：/usr/local/bin/python3 _gen_019.py
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
TITLE = '厂牌盯数03｜人均 10 分钟这条线，拆成排集与剪辑动作'
DIGEST = '微信把人均看剧时长写成分档线：5 分钟档与 10 分钟档。按本号 90 秒一集换算，10 分钟等于人均看满 7 集。本号自算官方许可名单 159 部微短剧的集数结构，给出排集与剪辑的可执行清单。'
FIGURES = [
    ('019_图1_两条时长线_1080.png', '微信 Q4 两条时长线——5 分钟档与 10 分钟档'),
    ('019_图2_集数分布与换算_1080.png', '159 部官方许可微短剧的集数分布与 10 分钟换算'),
    ('019_图3_排集与剪辑清单_1080.png', '面向「人均 7 集」的排集与剪辑清单'),
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
    put(d, 100, 42, '一人短剧厂牌 / 厂牌盯数 03', 21, DIM, 'bold')
    put(d, 937, 42, number, 22, RUST, 'number')
    put(d, 72, 96, title, 49, INK, 'title')
    put(d, 72, 164, subtitle, 25, DIM)
    d.line((72, 211, 1008, 211), fill=LINE, width=2)
    return im, d


def footer(d, y, lines):
    d.line((72, y, 1008, y), fill=LINE, width=2)
    for line in lines:
        y = paragraph(d, 72, y + 16, line, size=21, color=DIM, leading=30)
    return y


def chart_one():
    im, d = page('人均看剧时长，就是分档线', '2026-10-16 生效 / 12-31 截止 · 本号已核官方文档', '01', 1180)
    cards = [
        (72, TEAL, '绿泡泡短剧联合发行', '按人均看剧时长分四档',
         [('≥10 分钟 + 优质新剧', '100%', '90% 现金 + 10% 广告金'),
          ('≥10 分钟（非优质）', '85%', '现金与广告金按平台规则配比'),
          ('<10 分钟', '50%', '不足门槛，档位直接砍半'),
          ('不参与联合发行', '65%', '不在联合发行机制内')]),
        (568, GOLD, '智能托管 / 流量主', '按人均看剧时长分两档',
         [('≥5 分钟', '70%', '60% 现金 + 10% 广告金'),
          ('<5 分钟', '60%', '不足 5 分钟即降档'),
          ('—', '', ''),
          ('—', '', '')]),
    ]
    for x, color, title, sub, rows in cards:
        filled = [r for r in rows if r[1]]
        d.rounded_rectangle((x, 246, x + 440, 830), radius=18, fill=WHITE)
        d.rounded_rectangle((x, 246, x + 440, 339), radius=18, fill=color)
        put(d, x + 28, 265, title, 33, WHITE, 'bold', x + 416)
        put(d, x + 28, 307, sub, 21, WHITE, right=x + 416)
        y = 372
        for i, (label, pct, note) in enumerate(filled):
            put(d, x + 28, y, label, 25, INK, 'bold', x + 416)
            put(d, x + 28, y + 34, note, 20, DIM, right=x + 416)
            pw = d.textlength(pct, font=font(40, 'number'))
            put(d, x + 412 - pw, y - 4, pct, 40, color, 'number')
            if i < len(filled) - 1:
                d.line((x + 28, y + 74, x + 412, y + 74), fill=LINE, width=1)
            y += 100
    put(d, 72, 872, '点开人数不定档位，人均停留时长定档位。', 32, RUST, 'bold')
    put(d, 72, 932, '同一部剧，人均 9 分钟与 11 分钟，落在两个档里；', 28)
    put(d, 72, 978, '这两个数之间的差距，是排集问题，不是投放问题。', 28)
    footer(d, 1058, ['依据：微信开放平台 2026 年 Q4「微短剧」小程序激励活动官方文档（本号 016 已逐档核对）；',
                     '智能托管两档另据流媒体网、聚短剧转述，两处表述一致。'])
    return im


def chart_two():
    im, d = page('10 分钟，等于人均看满 7 集', '本号自算：159 部官方许可微短剧 · 源为广电总局通告附件', '02', 1400)
    put(d, 72, 246, '官方许可名单的集数结构', 30, INK, 'bold')
    put(d, 72, 288, '2026 年 4—6 月拿到发行许可的 159 部微短剧 / 5396 集', 22, DIM)
    bars = [('<20 集', 28, 18, '#a2988a'), ('20–39 集', 91, 57, RUST),
            ('40–59 集', 5, 3, '#a2988a'), ('60–79 集', 23, 14, '#a2988a'),
            ('≥80 集', 12, 8, TEAL)]
    y = 342
    for label, count, pct, color in bars:
        put(d, 72, y + 4, label, 26, INK, 'bold', 240)
        w = int(420 * pct / 57)
        d.rounded_rectangle((252, y, 252 + max(w, 10), y + 34), radius=6, fill=color)
        put(d, 252 + max(w, 10) + 18, y + 4, f'{count} 部 · {pct}%', 24, color, 'bold', 1000)
        y += 62
    put(d, 72, y + 12, '集数均值 33.9 集/部，中位 24 集；最短 5 集，最长 100 集。', 26, INK)
    d.line((72, y + 66, 1008, y + 66), fill=LINE, width=2)
    put(d, 72, y + 92, '把 10 分钟换算成集数', 30, INK, 'bold')
    y2 = y + 146
    put(d, 100, y2, '单集时长', 24, DIM, 'bold', 560)
    put(d, 1008 - d.textlength('人均 10 分钟 = 看满几集', font=font(24, 'bold')) - 30, y2,
        '人均 10 分钟 = 看满几集', 24, DIM, 'bold')
    y2 += 40
    rows = [('60 秒', '10 集', DIM), ('90 秒（本号规格）', '6.7 集 → 取整 7 集', RUST),
            ('120 秒', '5 集', DIM)]
    for label, need, color in rows:
        d.rounded_rectangle((72, y2, 1008, y2 + 66), radius=10, fill=WHITE)
        put(d, 100, y2 + 17, label, 28, color, 'bold', 620)
        put(d, 1008 - d.textlength(need, font=font(30, 'bold')) - 30, y2 + 14, need, 30, color, 'bold')
        y2 += 82
    put(d, 72, y2 + 20, '按中位 24 集、90 秒一集算，全剧约 36 分钟；人均 10 分钟 ≈ 看完 28%。', 26, INK)
    put(d, 72, y2 + 66, '结论：爆点放在第 10 集之后，对这条件没有任何帮助。', 30, RUST, 'bold')
    footer(d, y2 + 152, ['集数的均值/中位/分档占比与换算均为本号自算，可复核；',
                         '源：国家广电总局 2026-07-13《2026 年 4 月至 6 月全国国产网络剧片发行许可情况通告》附件。'])
    return im


def chart_three():
    im, d = page('面向「人均 7 集」的清单', '目标：第 1 到第 7 集，留住多少人', '03', 1420)
    put(d, 72, 246, '排集（六条）', 30, INK, 'bold')
    d.line((72, 288, 1008, 288), fill=RUST, width=3)
    items = [
        '第 1 集 30 秒内出现具体冲突，不先讲世界观。',
        '每集结尾留一个未解问题，下一集前 60 秒内正面回答。',
        '第 4 集之前不放过渡集。',
        '每集最后 3 秒给下一集的具体悬念：谁要做什么。',
        '最强爆点必须落在第 7 集以内。',
        '集数预算反推：至少准备 7 个能独立成立的钩子位。',
    ]
    y = 314
    for i, text in enumerate(items, 1):
        d.rounded_rectangle((72, y + 6, 108, y + 40), radius=8, fill=RUST)
        w = d.textlength(str(i), font=font(24, 'number'))
        put(d, 90 - w / 2, y + 11, str(i), 24, WHITE, 'number')
        put(d, 130, y + 8, text, 28, INK, right=1008)
        y += 66
    y += 26
    put(d, 72, y, '剪辑（四条）', 30, INK, 'bold')
    d.line((72, y + 42, 1008, y + 42), fill=TEAL, width=3)
    y += 68
    cuts = [
        '前 3 秒给异常画面，不用片头 logo 或标题卡。',
        '按「删掉它剧情断不断」过一遍水词。',
        '把最强画面提前，不按剧本时间序。',
        '本集最后一镜与下集第一镜拼起来看一遍，不顺就补半句。',
    ]
    for i, text in enumerate(cuts, 1):
        d.rounded_rectangle((72, y + 6, 108, y + 40), radius=8, fill=TEAL)
        w = d.textlength(str(i), font=font(24, 'number'))
        put(d, 90 - w / 2, y + 11, str(i), 24, WHITE, 'number')
        put(d, 130, y + 8, text, 28, INK, right=1008)
        y += 66
    y += 40
    d.rounded_rectangle((72, y, 1008, y + 116), radius=12, fill=INK)
    put(d, 98, y + 24, '今天只做一件事：数一数第 1 到第 7 集里，', 30, WHITE, 'bold')
    put(d, 98, y + 70, '有几个「必须看下一集」的落点。少于 7 个，先补齐再谈投放。', 30, WHITE, 'bold')
    footer(d, y + 174, ['本图为本号整理的动作清单，非平台规则原文；门槛数据见图 1 与图 2。'])
    return im


def cover_a():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    put(d, 744, 28, '盯数 03', 18, '#bdb3a1', right=875)
    for i, (h, color) in enumerate([(196, '#b55b32'), (128, '#28695e')]):
        d.rounded_rectangle((40, 96 + i * 100, 40 + 150 - i * 40, 124 + i * 100), radius=8, fill=color)
    center(d, 450, 74, '微信 Q4 分档线', 26, '#f0c588', 'bold', True)
    center(d, 450, 122, '人均 10 分钟', 60, WHITE, 'title', True)
    center(d, 450, 206, '等于看满 7 集', 54, '#f0c588', 'title', True)
    d.line((306, 288, 594, 288), fill='#766657', width=2)
    center(d, 450, 306, '90 秒/集 · 159 部许可剧集数结构', 19, '#bdb3a1', 'body', True)
    for i in range(3):
        d.rounded_rectangle((740, 300 + i * 18, 862 - i * 26, 310 + i * 18), radius=3, fill='#574e45')
    return im


def cover_b():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, DIM, right=900)
    put(d, 744, 28, '盯数 03', 18, DIM, right=875)
    center(d, 450, 74, '人均看剧时长', 26, TEAL, 'bold', True)
    center(d, 450, 120, '5 分钟一档', 54, INK, 'title', True)
    center(d, 450, 194, '10 分钟一档', 54, RUST, 'title', True)
    center(d, 450, 300, '排集与剪辑的 10 个动作', 22, TEAL, 'bold', True)
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
        put(d, 28, y, ['A / 深色：强调换算「10 分钟＝7 集」', 'B / 浅色：强调两条档位线'][index], 26, INK, 'bold', 1450)
        im.paste(cover, (28, y + 55))
        d.rectangle((286, y + 55, 669, y + 437), outline='#b48e60', width=1)
        crop = cover.crop((258, 0, 641, 383)).resize((142, 142), Image.Resampling.LANCZOS)
        for j, (bg, fg) in enumerate([('#ffffff', INK), ('#191919', '#f5efe4')]):
            x = 958 + j * 254
            d.rounded_rectangle((x, y + 55, x + 228, y + 437), radius=16, fill=bg)
            put(d, x + 18, y + 75, ['浅色分享卡', '深色分享卡'][j], 19, fg, right=x + 217)
            im.paste(crop, (x + 43, y + 129))
            put(d, x + 18, y + 296, '人均 10 分钟这条线', 18, fg, right=x + 217)
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
    cover_names = ['封面_019_A_十倍换算_900x383.png', '封面_019_B_两条档位线_900x383.png']
    for im, name in zip(covers, cover_names):
        save_png(im, OUT / name)
    save_png(cover_review(covers), OUT / '对照_019封面两方向.png')
    sheet = Image.new('RGB', (1212, 640), '#e5e2dc')
    for i, im in enumerate(charts):
        thumb = im.copy()
        thumb.thumbnail((380, 590), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (12 + i * 402, 12))
    save_png(sheet, SAMPLES / '019_正文配图手机宽预览.png')
    body = (OUT.parent / '文章' / '019_发布版.md').read_text()
    assert len(TITLE) <= 64 and len(DIGEST) <= 120, (len(TITLE), len(DIGEST))
    for index, (name, caption) in enumerate(FIGURES, 1):
        assert f'【图 {index}：{caption}】' in body, (index, caption)
    print('PASS: figure captions match body; title', len(TITLE), 'digest', len(DIGEST))
