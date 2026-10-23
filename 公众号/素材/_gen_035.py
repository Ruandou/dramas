#!/usr/bin/env python3
"""035《红果热播榜前十，5 部 AI 剧带季数》配图与封面。

结构：三榜并排 → 前十明细 → 三个动作。纯本地 Pillow，零扣费。
运行：/usr/local/bin/python3 _gen_035.py
"""
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


def boards():
    im, d = page('三个榜单，同一个方向', '口径不同，不能直接换算；方向一致：带季数的剧在头部更密', '01', 1040)
    cards = [
        ('5/10', '热播榜 · 10-21', '前十里 6 席是 AI 剧，5 部带季数', '湖南日报 · B 级', RUST),
        ('9/10', '新剧榜 · 10-21', '榜首第 14 季 9,014 万热度；前三都是多季', '腾讯新闻整理 · C 级', TEAL),
        ('5/10', '热播榜 · 10-23', '全榜 100 部里 24 部带季数', '短剧工程 · B 级', GOLD),
    ]
    y = 238
    for big, label, desc, src, color in cards:
        d.rounded_rectangle((72, y, 1008, y + 172), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 172), radius=4, fill=color)
        put(d, 104, y + 22, big, 62, color, 'bold', 360)
        put(d, 104, y + 112, label, 21, INK, 'bold', 420)
        put(d, 380, y + 26, desc, 24, INK, 'bold', 980)
        put(d, 380, y + 70, '口径：' + src, 20, DIM, 'body', 980)
        put(d, 380, y + 110, '别把三行的数字互相加减', 20, DIM, 'body', 980)
        y += 186

    d.rounded_rectangle((72, y + 4, 1008, y + 92), radius=12, fill=INK)
    put(d, 100, y + 18, '前十占一半，全榜只占四分之一', 21, '#bdb3a1', right=980)
    put(d, 100, y + 50, '头部浓度 2.1 倍', 32, '#f0c588', 'bold', 980)

    footer(d, y + 112, [
        '来源：湖南日报·新湖南 2026-10-21；腾讯新闻 2026-10-21（自媒体）；',
        '短剧工程 2026-10-23 红果短剧热播榜 TOP100。三榜口径不同，不能换算。',
        '统计口径：只按标题「第 N 季」或数字结尾计数，不含同名衍生。',
    ])
    return im


def top10():
    im, d = page('10 月 23 日热播榜前十', '带季数的 5 部，用锈红底色标出', '02', 1240)
    rows = [
        ('1', '大唐憨婿之我姐姐是太子妃第四季', '古风权谋', '6,981', True),
        ('2', '王妈在顾家当保姆后全家只会搞笑了', '都市日常', '6,828', False),
        ('3', '和离后我带女儿横扫魔域', '玄幻仙侠', '6,781', False),
        ('4', '聚宝仙盆之杂灵根才是真BOSS第十四季', '玄幻仙侠', '6,695', True),
        ('5', '谁让这个文盲修仙的第五季', '玄幻仙侠', '6,468', True),
        ('6', '觉醒伪神：神明弃我我自为神7', '都市玄幻', '6,462', True),
        ('7', '枝头春意闹', '古风爱情', '6,401', False),
        ('8', '持械入宋：第九季', '古风权谋', '6,239', True),
        ('9', '反向拿捏：和闺蜜穿七零带着婆婆一起离', '年代爱情', '6,230', False),
        ('10', '婆婆装瘫七年，我高调离婚！', '家庭伦理', '6,162', False),
    ]
    put(d, 84, 232, '名次', 19, DIM, 'bold', 150)
    put(d, 160, 232, '剧名', 19, DIM, 'bold', 700)
    put(d, 760, 232, '题材', 19, DIM, 'bold', 900)
    put(d, 920, 232, '热播指数', 19, DIM, 'bold', 1010)
    y = 266
    for rank, name, genre, idx, season in rows:
        d.rounded_rectangle((72, y, 1008, y + 62), radius=8, fill=SOFT if season else WHITE)
        if season:
            d.rounded_rectangle((72, y, 78, y + 62), radius=3, fill=RUST)
        put(d, 92, y + 16, rank, 24, RUST if season else DIM, 'number', 150)
        put(d, 160, y + 17, name, 20, INK if season else DIM, 'bold' if season else 'body', 755)
        put(d, 760, y + 19, genre, 18, DIM, 'body', 910)
        put(d, 920, y + 17, idx, 21, RUST if season else DIM, 'number', 1008)
        y += 72

    d.rounded_rectangle((72, y + 10, 1008, y + 92), radius=12, fill=INK)
    put(d, 100, y + 24, '前十 5 部带季数 = 50%', 22, '#f0c588', 'bold', 980)
    put(d, 100, y + 56, '全榜 24/100 = 24%，头部浓度 2.1 倍', 22, '#bdb3a1', right=980)

    footer(d, y + 112, [
        '来源：短剧工程 2026-10-23 红果短剧热播榜 TOP100（第三方整理）。',
        '热播指数为播放量、完播率、搜索量、互动量综合计算，不等于播放量。',
        '上架日期取自榜单页；本号只做统计，不对单剧质量作评价。',
    ])
    return im


def actions():
    im, d = page('一人厂牌的三件事', '把「季」当成生产单位，而不是营销噱头', '03', 1040)
    blocks = [
        ('01', '立项就按「季」设计', '一句话世界观 + 三条可展开的人物线 + 季末钩子；可续的壳，是第一季拍完还能开机的前提。', RUST),
        ('02', '续订线，开机前写死', '首周完播率、追更或复看比例、7 日热度排名；达标做第二季，不达标就换题。', TEAL),
        ('03', '把 AI 资产做成库', '角色形象、场景基准图、提示词版本、配音音色按项目归档；续作只换冲突，不重造底。', GOLD),
    ]
    y = 238
    for num, head, body, color in blocks:
        d.rounded_rectangle((72, y, 1008, y + 168), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 168), radius=4, fill=color)
        put(d, 104, y + 18, num, 22, color, 'number', 200)
        put(d, 150, y + 16, head, 30, INK, 'bold', 980)
        paragraph(d, 150, y + 66, body, width=820, size=22, color=DIM, leading=34)
        y += 184

    d.rounded_rectangle((72, y + 4, 1008, y + 150), radius=12, fill=SOFT)
    put(d, 100, y + 18, '选题偏好（媒体观察，B 级）', 20, RUST, 'bold', 980)
    put(d, 100, y + 52, '历史穿越 · 玄幻修真 · 萌宝治愈', 26, INK, 'bold', 980)
    put(d, 100, y + 92, '规则清晰、结局可预期；霸总虐恋「已基本排不上号」。', 21, DIM, 'body', 980)
    put(d, 100, y + 120, '不是平台口径，但方向和榜单一致。', 19, DIM, 'body', 980)

    footer(d, y + 170, [
        '来源：湖南日报·新湖南 2026-10-21；短剧工程 2026-10-23 榜单。',
        '续订线三个指标为本号管理建议，不是平台标准；续作成本下降幅度需按项目实测。',
    ])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    center(d, 450, 56, '红果热播榜前十', 22, '#f0c588', 'bold', True)
    center(d, 450, 92, '5 部 AI 剧带季数', 44, WHITE, 'title', True)
    center(d, 450, 166, '第 14 季 · 第 9 季 · 第 5 季', 24, '#8fc0b4', 'bold', True)
    d.line((330, 220, 570, 220), fill='#766657', width=2)
    center(d, 450, 238, '继续押新本，还是做能续的壳？', 21, '#d8cdbb', 'body', True)
    center(d, 450, 292, '三个动作，开机前定好', 19, '#bdb3a1', 'body', True)
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
    for name, maker in [('035_图1_三个榜单_1080.png', boards),
                        ('035_图2_前十带季数_1080.png', top10),
                        ('035_图3_三件事_1080.png', actions)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_035_前十带季数_900x383.png')
    print('done')
