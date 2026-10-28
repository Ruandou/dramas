#!/usr/bin/env python3
"""048《红果处置 2 万部：换皮、同脸、撞脸，红线在哪》配图与封面。纯本地 Pillow。"""
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
    put(d, 72, 96, title, 46, INK, 'title', 1008)
    put(d, 72, 162, subtitle, 25, DIM, right=1008)
    d.line((72, 209, 1008, 209), fill=LINE, width=2)
    return im, d


def footer(d, y, lines):
    d.line((72, y, 1008, y), fill=LINE, width=2)
    for i, line in enumerate(lines):
        y = paragraph(d, 72, y + (16 if i == 0 else 8), line, size=21, color=DIM, leading=30)
    return y


def notice_numbers():
    im, d = page('20,426 部，公告写了什么', '红果短剧 2026-10-27 治理公告 / 微短剧', '01', 1100)

    d.rounded_rectangle((72, 256, 620, 590), radius=14, fill=WHITE)
    put(d, 106, 282, '截至 10-27 累计处置', 22, DIM, 'bold', 590)
    put(d, 100, 322, '20,426', 86, RUST, 'title', 590)
    unit_x = 100 + d.textlength('20,426', font=font(86, 'title')) + 14
    put(d, unit_x, 374, '部', 30, INK, 'bold', 590)
    d.line((106, 486, 584, 486), fill=LINE, width=2)
    put(d, 106, 506, '公告口径；未披露从哪天起算', 21, DIM, 'body', 590)
    put(d, 106, 544, '也不能推出「都是 AI 剧」', 21, RUST, 'bold', 590)

    d.rounded_rectangle((648, 256, 1008, 590), radius=14, fill=WHITE)
    put(d, 680, 276, '公告点了四类问题', 21, DIM, 'bold', 980)
    rows = ['过度情绪渲染', '刻意渲染矛盾', '剧情同质化 · 换皮', '人物同质化 · 同脸/撞脸']
    y = 316
    for i, text in enumerate(rows, 1):
        put(d, 680, y, f'0{i}', 18, GOLD, 'number', 980)
        put(d, 716, y - 4, text, 24, INK, 'bold', 990)
        y += 62

    d.rounded_rectangle((72, 620, 1008, 744), radius=12, fill=WHITE)
    put(d, 104, 636, '公告举例点名 6 部，剧名打码，原文带「等」', 21, DIM, 'bold', 980)
    put(d, 104, 678, '《别*女》《败*惹》《八*富》', 26, INK, 'title', 980)
    put(d, 104, 714, '《离*摊》《一*起》《泼*家》', 26, INK, 'title', 980)

    d.rounded_rectangle((72, 774, 1008, 908), radius=12, fill=INK)
    put(d, 102, 790, '公告没写：统计区间 / 判定阈值 / 处置手段', 23, '#e0705a', 'bold', 980)
    put(d, 102, 832, '「处置」不等于「下架」。', 25, '#f0c588', 'bold', 980)
    put(d, 102, 870, '把它当成一次平台表态，不是一份可复算的账。', 20, '#bdb3a1', right=980)

    footer(d, 934, [
        '来源：红果短剧 2026-10-27 公告，经财联社、凤凰网、南方都市报、九派新闻转述。',
        '本号整理；公告未给统计区间与判定阈值，正文已标注。',
    ])
    return im


def timeline():
    im, d = page('4 月、7 月、10 月：治理范围在扩大', '三次公告，三个口径 / 不能直接相除', '02', 1150)
    rail = 246
    d.line((rail, 256, rail, 946), fill='#d9a24a', width=3)

    cards = [
        ('04-06', 'AI 短剧素材违规',
         '下架漫剧 1,718 部',
         '专项核查 1.5 万部，处置 670 部，曝光四类案例', RUST),
        ('07-23', 'AI 剧角色规范',
         '主要角色要「清晰区分度」',
         '版权红线：不得用他人独创角色与素材；公告没给百分比阈值', GOLD),
        ('10-27', '低质与同质化',
         '累计处置 20,426 部',
         '从素材违规扩到剧情同质化、人物同质化', TEAL),
    ]
    y = 256
    for stamp, who, main, sub, color in cards:
        d.ellipse((rail - 9, y + 26, rail + 9, y + 44), fill=color)
        d.rounded_rectangle((296, y, 1008, y + 206), radius=12, fill=WHITE)
        d.rounded_rectangle((296, y, 307, y + 206), radius=5, fill=color)
        put(d, 330, y + 18, stamp, 23, color, 'number', 700)
        put(d, 330, y + 54, who, 22, DIM, 'bold', 980)
        put(d, 330, y + 94, main, 30, INK, 'bold', 980)
        put(d, 330, y + 146, sub, 19, DIM, 'body', 985)
        y += 238

    d.rounded_rectangle((72, 970, 1008, 1050), radius=12, fill=INK)
    put(d, 102, 986, '1,718 是漫剧/素材违规，20,426 是微短剧/剧情与人物同质化。', 19, '#bdb3a1', right=990)
    put(d, 102, 1016, '口径不同，不能相除。', 25, '#f0c588', 'bold', 980)
    footer(d, 1066, [
        '来源：红果短剧 2026-04-06、07-23、10-27 公告（经财联社、新京报、凤凰网等转述）。',
    ])
    return im


def coin_exit():
    im, d = page('同一个月，金币要下线了', '2026-10-21 公告 / 分阶段执行', '03', 1080)

    d.rounded_rectangle((72, 256, 1008, 316), radius=10, fill='#d9a24a')
    put(d, 104, 274, '10-21 公告：金币功能分阶段下线', 22, INK, 'bold', 980)

    steps = [
        ('11-01', '新激活用户', '不再获得金币功能及相关入口',
         '此前已在使用金币的用户，这一阶段不受影响', RUST),
        ('12-31 前', '所有用户', '全面下线、停止发放金币',
         '存量金币与现金权益不受影响，留出兑换提现时间', TEAL),
    ]
    y = 350
    for stamp, who, what, note, color in steps:
        d.rounded_rectangle((72, y, 1008, y + 150), radius=12, fill=WHITE)
        d.rounded_rectangle((72, y, 84, y + 150), radius=5, fill=color)
        put(d, 112, y + 22, stamp, 30, color, 'title', 400)
        put(d, 112, y + 76, who, 22, DIM, 'bold', 400)
        put(d, 440, y + 34, what, 27, INK, 'bold', 990)
        put(d, 440, y + 90, note, 20, DIM, 'body', 990)
        y += 170

    d.rounded_rectangle((72, 704, 1008, 806), radius=12, fill=WHITE)
    put(d, 104, 720, '10-23 同时上线防沉迷：休息提醒 / 睡眠提醒', 22, GOLD, 'bold', 980)
    put(d, 104, 762, '连续观剧到一定时长触发；深夜打开可能刷到提醒。逐步覆盖，尚未全量。', 20, DIM, 'body', 990)

    d.rounded_rectangle((72, 836, 1008, 936), radius=12, fill=INK)
    put(d, 102, 852, '补贴退坡 + 时长刹车，考核重心转向内容留存。', 20, '#bdb3a1', right=990)
    put(d, 102, 890, '这是推断，不是公告原话。', 24, '#f0c588', 'bold', 980)

    footer(d, 962, [
        '来源：红果短剧 2026-10-21 公告（北京日报、新浪财经转述）；2026-10-23 防沉迷机制（界面新闻）。',
        '「考核重心转向内容留存」为本号推断（C 级），不构成平台口径。',
    ])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 26, '一人短剧厂牌', 18, '#bdb3a1', right=500)
    put(d, 33, 74, '红果 10-27 公告', 20, '#f0c588', 'bold', 430)
    put(d, 30, 108, '20,426', 78, '#efe6d6', 'title', 470)
    put(d, 36, 206, '部 微短剧被处置', 26, '#bdb3a1', 'bold', 470)
    put(d, 36, 258, '公告没给判定阈值', 25, '#e0705a', 'bold', 470)
    put(d, 36, 300, '65% 是网上传的', 18, '#8f8576', 'body', 470)

    d.line((490, 62, 490, 324), fill='#4a443c', width=1)
    put(d, 530, 68, '三类同质化', 20, '#8fc0b4', 'bold', 880)
    items = ['换皮', '同脸', '撞脸']
    y = 112
    for text in items:
        put(d, 530, y, text, 52, WHITE, 'title', 880)
        d.line((536, y + 44, 700, y + 44), fill='#d0553c', width=6)
        y += 76
    put(d, 530, 338, '剧情 / 人物素材', 17, '#8f8576', 'body', 880)
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
    for name, maker in [('048_图1_公告数字_1080.png', notice_numbers),
                        ('048_图2_治理时间线_1080.png', timeline),
                        ('048_图3_金币退坡_1080.png', coin_exit)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_048_2万部与三条线_900x383.png')
    print('done')
