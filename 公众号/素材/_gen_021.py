#!/usr/bin/env python3
"""021《7 阶段流水线全拆解》配图与封面。

版式与断言沿用 _gen_019.py：字形覆盖、文本量宽、画布边界、文本框不重叠、中央安全区。
运行：/usr/local/bin/python3 _gen_021.py
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
TITLE = '7 阶段流水线全拆解：从 86 集大纲到成片'
DIGEST = '七个阶段七个岗位，只有视觉设计与视频生成两段真花钱。剧本轨零扣费可连续跑，制作轨扣费可停在设计稿。附仓库实测规模与六道闸门两道审核。'
FIGURES = [
    ('021_图1_七阶段与两轨道_1080.png', '七个阶段与两条轨道'),
    ('021_图2_跨集穿帮复盘_1080.png', '一次跨集穿帮的复盘'),
    ('021_图3_六道闸门与两道审核_1080.png', '六道闸门与两道审核'),
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
    put(d, 100, 42, '一人短剧厂牌 / 流水线拆解', 21, DIM, 'bold')
    put(d, 949, 42, number, 22, RUST, 'number')
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
    im, d = page('七个阶段，两条轨道', '只有 ③ 视觉设计、⑥ 视频生成 两段真扣费', '01', 1240)
    tracks = [
        (72, TEAL, '剧本轨｜零扣费 · 可连续跑', [
            ('① 故事架构', '大纲师 · 86 集大纲'),
            ('② 制片登记', '制片登记 · ID 系统与资产骨架'),
            ('④ 分集编剧', '编剧 · 逐集剧本 + 分镜脚本'),
        ]),
        (560, RUST, '制作轨｜扣费 · 可停在设计稿', [
            ('③ 视觉设计', '道具师 → 角色师 / 场景师 · 参考图'),
            ('⑤ 分镜构建', '分镜构建师 · shots / segments 配置'),
            ('⑥ 视频生成', '引擎执行 · 分集成片 mp4'),
        ]),
    ]
    for x, color, head, rows in tracks:
        d.rounded_rectangle((x, 246, x + 448, 640), radius=16, fill=WHITE)
        d.rounded_rectangle((x, 246, x + 448, 330), radius=16, fill=color)
        put(d, x + 26, 264, head, 26, WHITE, 'bold', x + 424)
        y = 348
        for i, (name, note) in enumerate(rows):
            put(d, x + 26, y, name, 30, INK, 'bold', x + 424)
            put(d, x + 26, y + 38, note, 21, DIM, right=x + 424)
            if i < len(rows) - 1:
                d.line((x + 26, y + 82, x + 422, y + 82), fill=LINE, width=1)
            y += 96
    d.rounded_rectangle((72, 668, 1008, 782), radius=16, fill=INK)
    put(d, 100, 690, '⑦ 审查发布', 30, WHITE, 'bold')
    put(d, 100, 730, '总导演 · 标题 / 封面 / 简介合规确认 · 不额外扣费', 22, '#bdb3a1', right=980)
    d.rounded_rectangle((72, 812, 1008, 956), radius=14, fill=WHITE)
    put(d, 100, 834, '两轨唯一的交接点：一个状态标记', 27, INK, 'bold')
    put(d, 100, 878, '某一集剧本经审核定稿 → 标成「可制作」→ 制作轨才认它。', 24)
    put(d, 100, 916, '剧本轨继续往前走下一集，不等制作轨出片。', 24)
    footer(d, 1004, ['因此本号现状是：剧本轨攒下 1364 集，制作轨只出成片 129 条。',
                     '阶段与岗位为本号工作法，非任何平台或官方的标准流程。'])
    return im


def chart_two():
    im, d = page('一次跨集穿帮的复盘', '同一个路人，被两集剧本各自命名', '02', 1240)
    steps = [
        (DIM, '第 ④ 阶段', '两集剧本各写到一个没登记过的路人，没走占位符，各自现编了一个 ID。'),
        (DIM, '第 ② 阶段', '两个新 ID 各自登记，没人发现它们其实是同一个角色。'),
        (RUST, '第 ③ 阶段', '按两个 ID 出了两张脸，两张图，两次扣费。'),
        (RUST, '跨集播出', '同一个路人换了张脸，观众看得出来，穿帮。'),
    ]
    y = 246
    for color, tag, text in steps:
        d.rounded_rectangle((72, y, 1008, y + 128), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 80, y + 128), radius=4, fill=color)
        put(d, 104, y + 20, tag, 24, color, 'bold', 980)
        paragraph(d, 104, y + 58, text, width=880, size=24, leading=34)
        y += 152
    d.rounded_rectangle((72, y, 1008, y + 156), radius=14, fill=TEAL)
    put(d, 100, y + 22, '现在的规矩', 26, WHITE, 'bold')
    put(d, 100, y + 66, '未登记的角色一律用占位符 [待补：描述]，不能自编 ID；', 24, WHITE, right=980)
    put(d, 100, y + 104, '交回第 ② 阶段补登记、第 ③ 阶段补一张图。', 24, WHITE, right=980)
    footer(d, y + 204, ['同类两条：参考图里不许画人脸（人脸由视频生成阶段加）；',
                        '场景底图里不许放情节道具（放了会被固化进底图，换一集还穿着）。'])
    return im


def chart_three():
    im, d = page('每一步都有一道闸门', '六道阶段门 + 两道审核 · 只有「过」与「打回」', '03', 1380)
    gates = [
        (TEAL, 'G1', '大纲完整性校验', '① 故事架构 之后'),
        (GOLD, 'R1', '大纲审核（低于分数线不放行）', '① 之后 · 人工审'),
        (TEAL, 'G2', '制片体系与 ID 骨架就绪', '② 制片登记 之后'),
        (TEAL, 'G3', '道具 / 角色 / 场景资产就绪', '③ 视觉设计 之后'),
        (TEAL, 'G4', '分集剧本合规性', '④ 分集编剧 之后'),
        (GOLD, 'R2', '单集审核（提的问题改干净才放行）', '④ 之后 · 人工审'),
        (TEAL, 'G5', '提交配置合规校验', '⑤ 分镜构建 之后'),
        (TEAL, 'G6', '标题 / 封面 / 简介合规', '⑦ 发布之前'),
    ]
    y = 246
    for color, tag, text, pos in gates:
        d.rounded_rectangle((72, y, 1008, y + 84), radius=12, fill=WHITE)
        d.rounded_rectangle((88, y + 16, 166, y + 68), radius=10, fill=color)
        w = d.textlength(tag, font=font(28, 'number'))
        put(d, 127 - w / 2, y + 24, tag, 28, WHITE, 'number')
        put(d, 190, y + 18, text, 28, INK, 'bold', 996)
        put(d, 190, y + 54, pos, 20, DIM, right=996)
        y += 100
    d.rounded_rectangle((72, y + 10, 1008, y + 178), radius=14, fill=INK)
    put(d, 100, y + 34, '最贵的一道：时长红线', 27, '#f0c588', 'bold')
    put(d, 100, y + 78, '单集时长不达标 → 整集重写，禁止给镜头偷偷加秒凑数。', 24, WHITE, right=980)
    put(d, 100, y + 116, '第 ⑥ 阶段按秒计费，剧本多加 3 秒，视频就真拍满 3 秒。', 24, WHITE, right=980)
    footer(d, y + 226, ['门控编号与顺序为本号工作法整理；分数线的具体阈值随项目规格定义。'])
    return im


def cover_a():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    put(d, 744, 28, '流水线拆解', 18, '#bdb3a1', right=875)
    for i, (w, color) in enumerate([(150, '#b55b32'), (104, '#28695e'), (58, '#b9853d')]):
        y = 100 + i * 46
        d.rounded_rectangle((40, y, 40 + w, y + 32), radius=8, fill=color)
        d.rounded_rectangle((740, y, 740 + w - 20, y + 32), radius=8, fill='#574e45')
    center(d, 450, 74, '七个阶段', 26, '#f0c588', 'bold', True)
    center(d, 450, 122, '只有两步', 58, WHITE, 'title', True)
    center(d, 450, 198, '花钱', 58, WHITE, 'title', True)
    d.line((306, 284, 594, 284), fill='#766657', width=2)
    center(d, 450, 302, '86 集大纲 → 成片', 20, '#bdb3a1', 'body', True)
    return im


def cover_b():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, DIM, right=900)
    put(d, 744, 28, '流水线拆解', 18, DIM, right=875)
    center(d, 450, 74, '86 集大纲', 26, TEAL, 'bold', True)
    center(d, 450, 120, '到成片', 58, INK, 'title', True)
    center(d, 450, 196, '七个岗位', 50, RUST, 'title', True)
    center(d, 450, 298, '两条轨道 · 六道闸门', 22, TEAL, 'bold', True)
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
        put(d, 28, y, ['A / 深色：强调「只有两步花钱」', 'B / 浅色：强调「从大纲到成片」'][index], 26, INK, 'bold', 1450)
        im.paste(cover, (28, y + 55))
        d.rectangle((286, y + 55, 669, y + 437), outline='#b48e60', width=1)
        crop = cover.crop((258, 0, 641, 383)).resize((142, 142), Image.Resampling.LANCZOS)
        for j, (bg, fg) in enumerate([('#ffffff', INK), ('#191919', '#f5efe4')]):
            x = 958 + j * 254
            d.rounded_rectangle((x, y + 55, x + 228, y + 437), radius=16, fill=bg)
            put(d, x + 18, y + 75, ['浅色分享卡', '深色分享卡'][j], 19, fg, right=x + 217)
            im.paste(crop, (x + 43, y + 129))
            put(d, x + 18, y + 296, '7 阶段流水线全拆解', 18, fg, right=x + 217)
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
    cover_names = ['封面_021_A_只有两步花钱_900x383.png', '封面_021_B_从大纲到成片_900x383.png']
    for im, name in zip(covers, cover_names):
        save_png(im, OUT / name)
    save_png(cover_review(covers), OUT / '对照_021封面两方向.png')
    sheet = Image.new('RGB', (1212, 640), '#e5e2dc')
    for i, im in enumerate(charts):
        thumb = im.copy()
        thumb.thumbnail((380, 590), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (12 + i * 402, 12))
    save_png(sheet, SAMPLES / '021_正文配图手机宽预览.png')
    body = (OUT.parent / '文章' / '021_发布版.md').read_text()
    assert len(TITLE) <= 64 and len(DIGEST) <= 120, (len(TITLE), len(DIGEST))
    for index, (name, caption) in enumerate(FIGURES, 1):
        assert f'【图 {index}：{caption}】' in body, (index, caption)
    print('PASS: figure captions match body; title', len(TITLE), 'digest', len(DIGEST))
