from pathlib import Path
import json
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from _gen_charts_006 import f, HIRA, SONG, MONO

OUT = Path(__file__).resolve().parent
SAMPLES = OUT.parents[1] / 'samples'
PAPER = '#f3eee4'
WHITE = '#fffaf0'
INK = '#2c2925'
DIM = '#756d61'
LINE = '#d4c9b8'
RUST = '#ae422c'
TEAL = '#28695e'
BLUE = '#385a78'
FONTS = {'body': (HIRA, 0), 'bold': (HIRA, 2), 'title': (SONG, 1), 'number': (MONO, 1)}
GLYPHS = {}
TEXT_BOXES = []
TITLE = '厂牌实操01｜AI短剧接单先备5件'
DIGEST = '今天的厦门出海采访出现了承制案例，昨日一则招聘则把要求写到成片、修改和归档。本文拆出五件样片材料与三次确认：不承诺接单，先让已有作品可验收。'
FIGURES = [
    ('017_图1_两种业务付款依据_1080.png', '两种业务，先问清付款依据'),
    ('017_图2_五件交付物_1080.png', '从一条成片整理出五件交付物'),
    ('017_图3_三次确认_1080.png', '先确认故事，再确认形象，最后确认成片'),
]


def font(size, kind='body'):
    path, index = FONTS[kind]
    return f(path, size, index=index)


def put(d, x, y, text, size=28, color=INK, kind='body', right=1016):
    ff = font(size, kind)
    width = d.textlength(text, font=ff)
    assert x >= 0 and x + width <= right, (text, x, width, right)
    box = d.textbbox((x, y), text, font=ff, anchor='lt')
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
    im = Image.new('RGB', (1080, height), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle((72, 42, 83, 64), fill=RUST)
    put(d, 100, 42, '一人短剧厂牌 / 厂牌实操 01', 21, DIM, 'bold')
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


def arrow(d, points, color):
    d.line(points, fill=color, width=4)
    x, y = points[-1]
    d.polygon(((x - 8, y - 12), (x + 8, y - 12), (x, y)), fill=color)


def chart_one():
    im, d = page('同样是出海，钱按什么付？', '先确认业务结构，再谈价格 / 两类也可能混合', '01', 1220)
    d.rounded_rectangle((326, 244, 754, 311), radius=33, fill=INK)
    center(d, 540, 262, '一条 AI 短剧', 32, WHITE)
    arrow(d, [(540, 313), (540, 335), (292, 335), (292, 370)], BLUE)
    arrow(d, [(540, 335), (788, 335), (788, 370)], TEAL)
    cards = [
        (72, BLUE, '自有作品发行', '依据消费与变现表现',
         [('你提供', '作品的发行或运营权益'), ('钱从哪里来', '付费、广告或平台分成'), ('先问清楚', '分成口径、发行权、投流')]),
        (568, TEAL, '承制交付', '以固定制作费合作为例',
         [('你提供', '合同约定的制作服务'), ('钱按什么付', '制作合同与验收节点'), ('先问清楚', '范围、修改、付款条件')]),
    ]
    for x, color, title, sub, rows in cards:
        d.rounded_rectangle((x, 374, x + 440, 795), radius=18, fill=WHITE)
        d.rounded_rectangle((x, 374, x + 440, 467), radius=18, fill=color)
        put(d, x + 28, 393, title, 35, WHITE, 'bold', x + 416)
        put(d, x + 28, 437, sub, 21, WHITE, right=x + 416)
        y = 500
        for label, text in rows:
            put(d, x + 28, y, label, 22, color, 'bold', x + 416)
            put(d, x + 28, y + 39, text, 25, INK, right=x + 416)
            if y < 700:
                d.line((x + 28, y + 78, x + 412, y + 78), fill=LINE, width=1)
            y += 98
    put(d, 72, 841, '“承制”不自动等于包发行、包投流、包回款。', 32, RUST, 'bold')
    put(d, 72, 902, '制作费加分成：两套条件分别约定。', 28)
    put(d, 72, 949, '报道未披露合同金额和付款条件，不能拿来替自己报价。', 28)
    footer(d, 1062, ['依据：《海西晨报》2026-10-15 承制采访；分类为本号整理。',
                     '合作情况属企业受访自述，未取得合同或合作方确认。'])
    return im


def chart_two():
    im, d = page('把一条成片，整理成五件材料', '本号准备建议 / 不是企业原始清单，也不是平台门槛', '02', 1530)
    d.line((112, 274, 112, 1148), fill=LINE, width=3)
    rows = [
        ('完整样片', '看得完', '附题材、语种、画幅、时长和个人分工。', '完整叙事优先，高光混剪只作补充。'),
        ('一致性对照页', '接得上', '跨镜头对照脸、服装、道具、空间关系。', '截不同镜头并标编号，不重复裁同一张。'),
        ('可修改工程', '改得动', '检查素材路径、声音分轨及字幕可编辑性。', '复制工程改一句台词，再查音画与时长。'),
        ('素材授权台账', '查得到', '记录来源、许可用途、地域、期限与转交范围。', '没有依据就标“待核”，不要虚填已授权。'),
        ('报价验收确认单', '说得清', '列明规格、范围、修改、验收、付款和权利。', '暂无客户：先填能力范围，其余标待确认。'),
    ]
    for i, (title, verb, detail, action) in enumerate(rows, 1):
        y = 250 + (i - 1) * 191
        color = RUST if i == 5 else TEAL
        d.ellipse((76, y + 12, 148, y + 84), fill=color)
        center(d, 112, y + 34, str(i), 31, WHITE, 'number')
        put(d, 183, y + 8, title, 38, INK, 'title')
        d.rounded_rectangle((858, y + 6, 1008, y + 55), radius=24, outline=color, width=2)
        center(d, 933, y + 18, verb, 26, color)
        paragraph(d, 183, y + 69, detail, 817, 28, INK, 39)
        paragraph(d, 183, y + 118, action, 817, 25, DIM, 36)
        if i < 5:
            d.line((183, y + 166, 1008, y + 166), fill=LINE, width=1)
    d.rounded_rectangle((72, 1226, 1008, 1335), radius=12, fill=INK)
    put(d, 98, 1249, '先展示有权公开的样片，源文件按约定交付。', 31, WHITE, 'bold')
    put(d, 98, 1296, '可修改工程不等于免费交出全部工程、提示词与第三方素材。', 24, '#d4c9b8')
    footer(d, 1380, ['参考：华师就业网 2026-10-14 招聘公告；五件材料为本号方法建议。',
                     '岗位要求不等于外包招募；准备材料不构成接单或收益保证。'])
    return im


def chart_three():
    im, d = page('别留一句“修改到满意”', '三次确认 / 每次保留版本号与反馈记录', '03', 1360)
    d.line((120, 283, 120, 904), fill=TEAL, width=4)
    steps = [
        ('01', '先确认故事', '剧本、语种、画幅、交付范围', '方向未定，不急着批量生成。'),
        ('02', '再确认形象', '角色参考、代表镜头、整体画风', '人物没定，先别铺开后续镜头。'),
        ('03', '最后确认成片', '画面、声音、字幕、文件规格', '按已确认版本检查；新增需求另谈范围。'),
    ]
    for i, (num, title, items, warning) in enumerate(steps):
        y = 259 + i * 210
        d.rounded_rectangle((76, y + 10, 163, y + 76), radius=12, fill=TEAL)
        center(d, 120, y + 30, num, 28, WHITE, 'number')
        put(d, 202, y + 9, title, 39, INK, 'title')
        put(d, 202, y + 75, items, 28, INK)
        put(d, 202, y + 123, warning, 25, DIM)
        if i < 2:
            d.line((202, y + 178, 1008, y + 178), fill=LINE, width=1)
    d.rounded_rectangle((72, 905, 1008, 1116), radius=15, fill=WHITE)
    put(d, 96, 931, '一条能执行的反馈，长这样', 28, TEAL, 'bold')
    put(d, 96, 986, '00:18-00:21  /  角色名写错', 36, INK, 'bold')
    put(d, 96, 1043, '按已确认剧本更正字幕；保留修改前后版本。', 28, INK)
    put(d, 72, 1150, '换主角、改故事、加语种，不默认塞进“小修”。', 31, RUST, 'bold')
    footer(d, 1223, ['本图为本号组织建议，非平台强制流程；具体范围以双方约定为准。'])
    return im


def cover_a():
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    put(d, 744, 28, '实操 / 01', 18, '#bdb3a1', right=875)
    for i in range(5):
        x, y = 57 + i * 12, 123 - i * 8
        d.rounded_rectangle((x, y, x + 124, y + 170), radius=6, fill='#474038', outline='#79705f', width=2)
        d.line((x + 18, y + 48, x + 99, y + 48), fill='#a7987e', width=3)
        d.line((x + 18, y + 64, x + 86, y + 64), fill='#79705f', width=3)
    d.polygon(((95, 187), (144, 187), (155, 202), (248, 202), (230, 301), (87, 301)), fill='#b55b32')
    center(d, 450, 77, 'AI 短剧接单', 32, WHITE, safe=True)
    center(d, 450, 133, '先备 5 件', 72, '#f0c588', 'title', True)
    center(d, 450, 237, '让作品变成可验收的交付物', 23, WHITE, safe=True)
    d.line((319, 288, 581, 288), fill='#766657', width=2)
    center(d, 450, 307, '完整 · 稳定 · 可改 · 可查 · 可验', 18, '#bdb3a1', safe=True)
    for i, label in enumerate(['样片', '对照', '工程', '授权', '验收']):
        y = 99 + i * 42
        d.line((704, y + 8, 719, y + 21, 742, y - 3), fill='#cd9a5e', width=3)
        put(d, 755, y, label, 22, '#c3b69f', right=880)
    return im


def cover_b():
    im = Image.new('RGB', (900, 383), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, DIM, right=900)
    put(d, 744, 28, '实操 / 01', 18, DIM, right=875)
    for x in (28, 711):
        d.rounded_rectangle((x, 102, x + 162, 252), radius=7, fill=INK)
        for k in range(7):
            d.rectangle((x + 9 + k * 22, 109, x + 19 + k * 22, 115), fill=PAPER)
            d.rectangle((x + 9 + k * 22, 238, x + 19 + k * 22, 244), fill=PAPER)
        for k in range(3):
            d.rectangle((x + 13 + k * 48, 129, x + 51 + k * 48, 223), fill='#a9bbad' if k == 1 else '#b7aea0')
    center(d, 450, 81, 'AI 短剧 · 交付检查', 26, TEAL, safe=True)
    center(d, 450, 133, '成片能看', 61, INK, 'title', True)
    center(d, 450, 210, '还得能改', 61, RUST, 'title', True)
    center(d, 450, 308, '五件材料 / 三次确认', 24, TEAL, safe=True)
    for x in (40, 733):
        for i, length in enumerate((138, 108, 146)):
            d.rounded_rectangle((x, 280 + i * 15, x + length, 288 + i * 15), radius=3, fill=TEAL if i != 1 else '#b99262')
    return im


def cover_review(covers):
    im = Image.new('RGB', (1500, 1040), '#e5e2dc')
    d = ImageDraw.Draw(im)
    for index, cover in enumerate(covers):
        y = 35 + index * 500
        put(d, 28, y, ['A / 文件包：突出交付价值', 'B / 剪辑台：突出可修改能力'][index], 26, INK, 'bold', 1450)
        im.paste(cover, (28, y + 55))
        d.rectangle((286, y + 55, 669, y + 437), outline='#b48e60', width=1)
        crop = cover.crop((258, 0, 641, 383)).resize((142, 142), Image.Resampling.LANCZOS)
        for j, (bg, fg) in enumerate([('#ffffff', INK), ('#191919', '#f5efe4')]):
            x = 958 + j * 254
            d.rounded_rectangle((x, y + 55, x + 228, y + 437), radius=16, fill=bg)
            put(d, x + 18, y + 75, ['浅色分享卡', '深色分享卡'][j], 19, fg, right=x + 217)
            im.paste(crop, (x + 43, y + 129))
            put(d, x + 18, y + 296, 'AI短剧接单先备5件', 18, fg, right=x + 217)
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
    review = cover_review(covers)
    validate_glyphs()
    for im, (name, _) in zip(charts, FIGURES):
        save_png(im, OUT / name)
    cover_names = ['封面_017_A_先备5件_900x383.png', '封面_017_B_成片还得能改_900x383.png']
    for im, name in zip(covers, cover_names):
        save_png(im, OUT / name)
    save_png(review, OUT / '对照_017封面两方向.png')
    sheet = Image.new('RGB', (1212, 640), '#e5e2dc')
    for i, im in enumerate(charts):
        thumb = im.copy()
        thumb.thumbnail((380, 590), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (12 + i * 402, 12))
    save_png(sheet, SAMPLES / '017_正文配图手机宽预览.png')
    body = (OUT.parent / '文章' / '017_发布版.md').read_text()
    assert len(TITLE) <= 64 and len(DIGEST) <= 120
    for index, (name, caption) in enumerate(FIGURES, 1):
        assert f'【图 {index}：{caption}】' in body
    info = {
        'status': '本地待审，未上传、未发布',
        'title': TITLE,
        'title_alternatives': ['厂牌实操01｜AI短剧出海先问谁付钱', '厂牌实操01｜AI短剧样片怎样验收'],
        'digest': DIGEST,
        'tags': ['AI短剧', '短剧出海', '承制交付', '作品集', '验收清单'],
        'cover_recommended': cover_names[0],
        'covers': cover_names,
        'figures': [{'file': name, 'caption': caption} for name, caption in FIGURES],
        'sources': ['https://dzb.sunnews.cn/html/2026-10/15/content_842480.htm?div=-1', 'https://ccnu.91wllm.cn/campus/view/id/1006924'],
        'trend_api_used': False,
    }
    (OUT / '017_编辑信息.json').write_text(json.dumps(info, ensure_ascii=False, indent=2) + '\n')
    print('PASS: figure captions match body; title', len(TITLE), 'digest', len(DIGEST))
