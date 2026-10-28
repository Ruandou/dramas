#!/usr/bin/env python3
"""047《红果否认 400 亿，腾讯短剧周活 8968 万》配图与封面。纯本地 Pillow。"""
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


def timeline():
    im, d = page('24 小时，两条声明', '2026-10-26 → 10-27 / 北京时间', '01', 1150)
    rail = 246
    d.line((rail, 256, rail, 936), fill='#d9a24a', width=3)

    cards = [
        ('10-26 18:50', 'QuestMobile / 界面新闻',
         '绿泡泡短剧 8 月 MAU 1.43 亿',
         '10 月首周 WAU 8,968 万，环比 +44.1%', TEAL),
        ('10-27 21:09', '红果短剧官方声明',
         '「400 亿」「420—450 亿」不实',
         '「机构数据」「行业数据」「专家预计」都不是官方信息', RUST),
        ('10-27 21:23', '抖音集团副总裁李亮',
         '「腾讯短剧增速远超抖音和红果」',
         '「没有哪家公司能稳居市场第一」', GOLD),
    ]
    y = 256
    for time_s, who, main, sub, color in cards:
        d.ellipse((rail - 9, y + 26, rail + 9, y + 44), fill=color)
        d.rounded_rectangle((296, y, 1008, y + 196), radius=12, fill=WHITE)
        d.rounded_rectangle((296, y, 307, y + 196), radius=5, fill=color)
        put(d, 330, y + 18, time_s, 23, color, 'number', 700)
        put(d, 330, y + 54, who, 22, DIM, 'bold', 980)
        put(d, 330, y + 96, main, 27, INK, 'bold', 980)
        put(d, 330, y + 146, sub, 19, DIM, 'body', 980)
        y += 228

    d.rounded_rectangle((72, 950, 1008, 1030), radius=12, fill=INK)
    put(d, 102, 964, '一个否认收入，一个承认对手更快。', 20, '#bdb3a1', right=980)
    put(d, 102, 996, '短剧没有分出胜负，账先别算死。', 25, '#f0c588', 'bold', 980)
    footer(d, 1046, [
        '时间：界面新闻 2026-10-26；红果官方微博、李亮发文 2026-10-27。',
        'QuestMobile 为第三方估算；红果声明与李亮表态为公开口径。',
    ])
    return im


def three_numbers():
    im, d = page('绿泡泡短剧的三个数', 'QuestMobile / DataEye 口径 / 腾讯未官方披露用户数', '02', 1080)
    d.rounded_rectangle((72, 256, 620, 720), radius=14, fill=WHITE)
    put(d, 108, 286, '10 月首周周活', 22, DIM, 'bold', 580)
    put(d, 104, 330, '8,968 万', 78, TEAL, 'title', 600)
    put(d, 108, 446, 'WAU / 2026-10-01—07', 20, DIM, 'number', 580)
    put(d, 108, 490, '较 9 月首周', 22, DIM, 'body', 400)
    put(d, 108, 524, '+44.1%', 52, RUST, 'title', 500)
    d.line((108, 612, 584, 612), fill=LINE, width=2)
    put(d, 108, 632, '从 7 月更名起，周活约三个月逼近 9,000 万。', 21, INK, 'body', 590)

    d.rounded_rectangle((648, 256, 1008, 462), radius=14, fill=WHITE)
    put(d, 680, 276, '8 月月活', 21, DIM, 'bold', 980)
    put(d, 676, 312, '1.43 亿', 52, GOLD, 'title', 980)
    put(d, 680, 386, 'MAU / 2026-08', 19, DIM, 'number', 980)
    put(d, 680, 420, '月活，不是周活', 19, RUST, 'bold', 980)

    d.rounded_rectangle((648, 490, 1008, 720), radius=14, fill=WHITE)
    put(d, 680, 510, '10 月首周投放素材', 21, DIM, 'bold', 980)
    put(d, 676, 546, '4.3 万组', 48, RUST, 'title', 980)
    put(d, 680, 618, '日均较节前一周 +57%', 20, INK, 'body', 980)
    put(d, 680, 664, 'DataEye 监测', 19, DIM, 'body', 980)

    d.rounded_rectangle((72, 752, 1008, 842), radius=12, fill=INK)
    put(d, 102, 768, 'MAU 与 WAU 是两把尺子。', 20, '#bdb3a1', right=980)
    put(d, 102, 800, '可以看趋势，不能直接排名。', 26, '#f0c588', 'bold', 980)
    footer(d, 870, [
        '数据：界面新闻 2026-10-26 引 QuestMobile；DataEye 监测（经媒体转述）。',
        '1.43 亿为 2026 年 8 月 MAU；8,968 万为 10 月 1—7 日 WAU，较 9 月首周 +44.1%。',
    ])
    return im


def denominators():
    im, d = page('三个分母，不能直接排名', 'DAU / MAU / WAU：同一块布，三把尺子', '03', 1060)
    rows = [
        ('红果 DAU', '1.68 亿', '2026-07 / QuestMobile', '日活 / 第三方估算', RUST),
        ('绿泡泡 MAU', '1.43 亿', '2026-08 / QuestMobile', '月活 / 第三方估算', GOLD),
        ('绿泡泡 WAU', '8,968 万', '2026-10 首周 / QuestMobile', '周活 / 环比 +44.1%', TEAL),
    ]
    y = 270
    for label, value, meta, note, color in rows:
        d.rounded_rectangle((72, y, 1008, y + 156), radius=12, fill=WHITE)
        d.rounded_rectangle((72, y, 84, y + 156), radius=5, fill=color)
        put(d, 112, y + 20, label, 23, color, 'bold', 420)
        put(d, 112, y + 60, value, 54, INK, 'title', 460)
        put(d, 500, y + 28, meta, 20, DIM, 'body', 980)
        put(d, 500, y + 78, note, 20, DIM, 'body', 980)
        y += 176

    d.rounded_rectangle((72, 816, 1008, 906), radius=12, fill=INK)
    put(d, 102, 832, '把不同分母放一起排名，等于把三把尺子焊成一把。', 20, '#bdb3a1', right=980)
    put(d, 102, 864, '正确用法：同平台 + 同指标 + 同时间窗。', 25, '#f0c588', 'bold', 980)
    footer(d, 926, [
        '另：短剧微信小程序总用户 5.08 亿（2026-05，QuestMobile）是整个大盘，不是绿泡泡单产品。',
        '数据：界面新闻 2026-10-26；QuestMobile 2026-07/08；本号仅做口径提醒，不做排名。',
    ])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 26, '一人短剧厂牌', 18, '#bdb3a1', right=500)
    put(d, 33, 78, '红果', 20, '#f0c588', 'bold', 420)
    put(d, 33, 112, '400 亿', 72, '#efe6d6', 'title', 430)
    put(d, 33, 204, '年化收入传闻', 18, '#bdb3a1', 'body', 430)
    put(d, 33, 236, '官方：不实', 30, '#e0705a', 'bold', 430)

    # 红色删除线：把“400 亿”划掉，表达官方否认。
    d.line((36, 160, 300, 160), fill='#d0553c', width=7)
    d.line((36, 171, 278, 171), fill='#d0553c', width=4)

    d.line((470, 66, 470, 320), fill='#4a443c', width=1)
    put(d, 510, 78, '腾讯短剧', 20, '#8fc0b4', 'bold', 880)
    put(d, 510, 112, '8,968 万', 62, WHITE, 'title', 880)
    put(d, 510, 194, '10 月首周周活', 18, '#bdb3a1', 'body', 880)
    put(d, 510, 224, '+44.1%', 42, '#8fc0b4', 'title', 880)
    put(d, 510, 286, '环比 9 月首周', 17, '#d8cdbb', 'body', 880)

    # 右侧上升箭头，画出增速方向，不画柱状图避免暗示绝对规模。
    d.line((760, 250, 760, 150, 820, 120), fill='#6fbfa8', width=5)
    d.polygon([(820, 120), (796, 128), (814, 144)], fill='#6fbfa8')
    put(d, 33, 330, '同一天，两本账', 17, '#8f8576', 'body', 430)
    put(d, 510, 330, '10-27 21:09 / 21:23', 16, '#8f8576', 'number', 880)
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
    for name, maker in [('047_图1_24小时_1080.png', timeline),
                        ('047_图2_三个数_1080.png', three_numbers),
                        ('047_图3_三个分母_1080.png', denominators)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_047_400亿与8968万_900x383.png')
    print('done')
