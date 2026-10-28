#!/usr/bin/env python3
"""050《75 岁大爷刷 AI 短剧刷到脑梗，银发用户已有 4,653 万》配图与封面。纯本地 Pillow。"""
from pathlib import Path
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from _gen_charts_006 import f, HIRA, SONG, MONO

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = '#f3eee4', '#fffaf0', '#2c2925'
DIM, LINE, RUST, TEAL, GOLD = '#756d61', '#d4c9b8', '#ae422c', '#28695e', '#b9853d'
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
    put(d, 72, 96, title, 44, INK, 'title', 1008)
    put(d, 72, 158, subtitle, 24, DIM, right=1008)
    d.line((72, 204, 1008, 204), fill=LINE, width=2)
    return im, d


def footer(d, y, lines):
    d.line((72, y, 1008, y), fill=LINE, width=2)
    for i, line in enumerate(lines):
        y = paragraph(d, 72, y + (16 if i == 0 else 8), line, size=20, color=DIM, leading=29)
    return y


def waffle():
    im, d = page('银发用户 4,653 万，小程序 31.2% 超 51 岁', 'QuestMobile 2026-02 / 短剧 App 与微信小程序', '01', 1150)

    put(d, 72, 246, '小程序短剧用户里，51 岁以上占 31.2%', 24, DIM, 'bold')
    put(d, 72, 284, '每格 1%', 18, DIM)
    cell, gap = 42, 8
    x0, y0 = 72, 324
    for i in range(100):
        r, c = divmod(i, 10)
        x = x0 + c * (cell + gap)
        y = y0 + r * (cell + gap)
        if i < 31:
            d.rectangle((x, y, x + cell, y + cell), fill=TEAL)
        else:
            d.rectangle((x, y, x + cell, y + cell), outline=LINE, width=2)
    put(d, 72, 832, '31 / 100 格：51 岁以上', 22, TEAL, 'bold')

    panel_x = 620
    d.line((588, 246, 588, 892), fill=LINE, width=2)

    put(d, panel_x, 250, '短剧 App 50 岁以上月活', 21, DIM, 'bold', 1000)
    put(d, panel_x - 6, 282, '4,653', 72, RUST, 'title', 1000)
    ux = panel_x - 6 + d.textlength('4,653', font=font(72, 'title')) + 12
    put(d, ux, 330, '万', 26, INK, 'bold', 1000)

    put(d, panel_x, 400, '短剧 App 整体月活', 21, DIM, 'bold', 1000)
    put(d, panel_x, 432, '3.35 亿', 44, INK, 'title', 1000)

    put(d, panel_x, 506, '小程序短剧用户 51 岁以上', 21, DIM, 'bold', 1000)
    put(d, panel_x, 538, '31.2%', 44, TEAL, 'title', 1000)

    put(d, panel_x, 612, '人均单日视听时长', 21, DIM, 'bold', 1000)
    put(d, panel_x, 644, '约 2 小时', 44, INK, 'title', 1000)
    put(d, panel_x, 704, '2026 上半年 / CSM 全媒体数据', 17, DIM, right=1000)

    d.rounded_rectangle((72, 906, 1008, 986), radius=12, fill=INK)
    put(d, 102, 922, '银发不是边角用户：小程序里 31.2% 是 51 岁以上，接近三分之一。', 22, '#f0c588', 'bold', 990)
    put(d, 102, 956, '数据月份不同（2 月 / 上半年），不能直接相乘。', 18, '#bdb3a1', right=990)

    footer(d, 1008, [
        '来源：QuestMobile 2026 短剧行业洞察报告（2026-02 数据，经钛媒体 2026-04-08 报道）；CSM 全媒体数据（经视听网）。',
        '本号整理；银发人群口径为 50 岁以上，小程序口径为 51 岁以上，两者不可混用。',
    ])
    return im


def actions_matrix():
    im, d = page('10 月的三个动作，都没碰连刷结构', '红果短剧 2026-10 公告 / 本号对照', '02', 1030)

    col_x = [430, 560, 690, 850]
    heads = ['激励', '提醒', '供给', '连刷结构']
    for x, h in zip(col_x, heads):
        put(d, x, 240, h, 20, DIM, 'bold', 1008 if x < 800 else 1008)

    rows = [
        ('10-21', '金币分阶段下线', [1, 0, 0, 0], '看越久给越多 → 退坡'),
        ('10-23', '休息 / 睡眠提醒', [0, 1, 0, 0], '连续观剧触发，逐步覆盖'),
        ('10-27', '处置 20,426 部', [0, 0, 1, 0], '低质 / 同质化，内容侧'),
    ]
    y = 290
    for stamp, name, marks, note in rows:
        d.line((72, y - 18, 1008, y - 18), fill=LINE, width=2)
        put(d, 72, y, stamp, 21, GOLD, 'number', 300)
        put(d, 72, y + 34, name, 26, INK, 'bold', 420)
        put(d, 72, y + 72, note, 17, DIM, right=420)
        for x, m in zip(col_x, marks):
            cy = y + 40
            if m:
                d.ellipse((x - 12, cy - 12, x + 12, cy + 12), fill=TEAL)
            else:
                d.ellipse((x - 12, cy - 12, x + 12, cy + 12), outline=LINE, width=2)
        y += 150

    d.line((72, y - 18, 1008, y - 18), fill=RUST, width=2)
    put(d, 72, y, '缺口', 21, RUST, 'bold', 300)
    put(d, 72, y + 34, '没人动连刷结构', 26, RUST, 'bold', 420)
    put(d, 72, y + 72, '一集接一集，没有自然终点', 17, DIM, right=420)
    for x in col_x[:3]:
        d.ellipse((x - 12, y + 28, x + 12, y + 52), outline=LINE, width=2)
    d.ellipse((col_x[3] - 12, y + 28, col_x[3] + 12, y + 52), outline=RUST, width=3)
    put(d, col_x[3] - 4, y + 56, '空', 19, RUST, 'bold', 1008)

    d.rounded_rectangle((72, 862, 1008, 938), radius=12, fill=INK)
    put(d, 102, 878, '金币管激励，提醒管时长，治理管供给。', 21, '#bdb3a1', right=990)
    put(d, 102, 908, '三个动作都在外围，播放结构本身没人碰。', 24, '#f0c588', 'bold', 990)

    footer(d, 962, [
        '来源：红果短剧 2026-10-21、10-23、10-27 公告（A 级）；「连刷结构」一行为本号判断（C 级）。',
    ])
    return im


def episode_bars():
    im, d = page('65 集是中间值，最长 141 集', '百度短剧榜 2026-10-28 12:00 / 100 部 / 本号统计', '03', 980)

    bins = [('30—40', 5), ('41—60', 34), ('61—80', 43), ('81—100', 15), ('101—141', 3)]
    base_y, top_y = 700, 300
    max_v = 45
    bar_w, gap = 120, 55
    x = 100
    for label, v in bins:
        h = (v / max_v) * (base_y - top_y)
        d.rectangle((x, base_y - h, x + bar_w, base_y), fill=TEAL if label == '61—80' else DIM)
        put(d, x, base_y - h - 40, str(v), 26, INK, 'number', x + bar_w)
        put(d, x, base_y + 14, label, 19, DIM, 'number', x + bar_w + 40)
        x += bar_w + gap

    d.line((100, base_y, 1008, base_y), fill=INK, width=2)

    median_x = 100 + 2 * (bar_w + gap) + bar_w * (5 / 20)
    d.line((median_x, 268, median_x, base_y), fill=RUST, width=2)
    put(d, median_x + 10, 250, '中位 65 集', 22, RUST, 'bold', 1008)
    put(d, 100, 236, '100 部里，43 部落在 61—80 集', 21, DIM, 'bold')

    d.rounded_rectangle((72, 790, 1008, 866), radius=12, fill=WHITE)
    put(d, 104, 806, '80 集以上 22 部，最长 141 集；65 集 × 1—2 分钟 ≈ 65—130 分钟。', 20, INK, 'bold', 990)
    put(d, 104, 838, '等于一部电影，但切成 65 次「下一集」；单集时长为本号估算（C 级）。', 18, DIM, right=990)

    footer(d, 890, [
        '来源：百度短剧榜 2026-10-28 12:00 快照，本号按榜单标注集数统计（A 级）；单集 1—2 分钟为行业常见区间，未在榜单披露（C 级）。',
    ])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 17, '#bdb3a1', right=400)
    put(d, 33, 54, '健康杭州 10-28 病例', 17, '#f0c588', 'bold', 400)

    big = font(104, 'title')
    box = d.textbbox((30, 92), '75', font=big, anchor='lt')
    put(d, 30, 92, '75', 104, '#efe6d6', 'title', 300)
    xiao = font(36, 'title')
    xbox = d.textbbox((0, 0), '岁', font=xiao, anchor='lt')
    put(d, box[2] + 8, box[3] - (xbox[3] - xbox[1]), '岁', 36, '#efe6d6', 'title', 300)
    put(d, 33, 214, '刷 AI 短剧', 34, '#8fc0b4', 'bold', 400)
    put(d, 33, 262, '刷到脑梗', 46, WHITE, 'title', 420)
    put(d, 33, 322, '硬扛 14 小时才就医', 20, '#e0705a', 'bold', 440)

    d.line((450, 40, 450, 344), fill='#4a443c', width=1)

    put(d, 486, 48, '静脉溶栓黄金窗口', 18, '#8f8576', 'bold', 880)
    d.rectangle((486, 78, 486 + 4.5 / 16 * 330, 112), fill='#8fc0b4')
    put(d, 486 + 4.5 / 16 * 330 + 12, 80, '4.5 小时', 22, '#8fc0b4', 'bold', 880)

    put(d, 486, 132, '这次送医', 18, '#8f8576', 'bold', 880)
    d.rectangle((486, 162, 486 + 14 / 16 * 330, 196), fill='#d0553c')
    put(d, 486 + 14 / 16 * 330 + 12, 164, '14 小时', 22, '#e0705a', 'bold', 880)

    put(d, 486, 228, '短剧 App 50 岁以上月活', 17, '#8f8576', 'bold', 880)
    put(d, 482, 254, '4,653', 52, WHITE, 'title', 880)
    ux = 482 + d.textlength('4,653', font=font(52, 'title')) + 8
    put(d, ux, 254 + 52 - 22, '万', 22, '#bdb3a1', 'bold', 880)
    put(d, 486, 330, '小程序用户 51+ 占 31.2%', 17, '#8fc0b4', 'bold', 880)
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
    for name, maker in [('050_图1_银发用户_1080.png', waffle),
                        ('050_图2_三个动作_1080.png', actions_matrix),
                        ('050_图3_集数分布_1080.png', episode_bars)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_050_75岁与4653万_900x383.png')
    print('done')
