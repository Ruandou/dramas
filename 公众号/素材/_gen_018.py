from pathlib import Path
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from _gen_charts_006 import f, HIRA, SONG, MONO

OUT = Path(__file__).resolve().parent
SAMPLES = OUT.parents[1] / 'samples'
PAPER, WHITE, INK = '#f3eee4', '#fffaf0', '#2c2925'
DIM, LINE, RUST, TEAL = '#756d61', '#d4c9b8', '#ae422c', '#28695e'
FONTS = {'body': (HIRA, 0), 'bold': (HIRA, 2), 'title': (SONG, 1), 'number': (MONO, 1)}
GLYPHS, BOXES = {}, []
FIGURES = [
    ('018_图1_两条赛道材料量_1080.png', '郑州征集两条赛道，材料量不是一回事'),
    ('018_图2_三个交稿阶段_1080.png', '十月梗概与两条最终交稿时间线'),
    ('018_图3_报名材料准备_1080.png', '从已有故事到可核对的报名材料'),
]
COVERS = ['封面_018_A_先投剧本还是成片_900x383.png', '封面_018_B_十月梗概阶段_900x383.png', '封面_018_C_先选赛道再制作_900x383.png']


def font(size, kind='body'):
    path, index = FONTS[kind]
    return f(path, size, index=index)


def put(d, x, y, text, size=28, color=INK, kind='body', right=1008):
    ff = font(size, kind)
    width = d.textlength(text, font=ff)
    assert x >= 0 and x + width <= right + 0.1, (text, x, width, right)
    box = d.textbbox((x, y), text, font=ff, anchor='lt')
    assert box[0] >= 0 and box[2] <= d._image.width and box[3] <= d._image.height, (text, box)
    for other, b in BOXES:
        overlap = min(box[2], b[2]) > max(box[0], b[0]) and min(box[3], b[3]) > max(box[1], b[1])
        assert not overlap, (text, other, box, b)
    BOXES.append((text, box))
    GLYPHS.setdefault(FONTS[kind], set()).update(text)
    d.text((x, y), text, font=ff, fill=color, anchor='lt')


def center(d, x, y, text, size, color=INK, kind='bold', safe=False):
    w = d.textlength(text, font=font(size, kind))
    if safe:
        assert w <= 351, (text, w)
    put(d, x - w / 2, y, text, size, color, kind, x + w / 2 + 1)


def canvas(w, h, bg=PAPER):
    BOXES.clear()
    im = Image.new('RGB', (w, h), bg)
    return im, ImageDraw.Draw(im)


def page(title, sub, number, h):
    im, d = canvas(1080, h)
    d.rectangle((72, 42, 83, 64), fill=RUST)
    put(d, 101, 42, '一人短剧厂牌 / 厂牌机会 01', 21, DIM, 'bold')
    put(d, 952, 42, number, 22, RUST, 'number')
    put(d, 72, 98, title, 45, INK, 'title')
    put(d, 72, 166, sub, 25, DIM)
    d.line((72, 216, 1008, 216), fill=LINE, width=2)
    return im, d


def footer(d, y, lines):
    d.line((72, y, 1008, y), fill=LINE, width=2)
    for i, line in enumerate(lines):
        put(d, 72, y + 19 + i * 32, line, 21, DIM)


def chart_one():
    im, d = page('先投剧本，还是交整部成片？', '两条参评路径 / 奖金不是投稿补贴', '01', 1390)
    for x, color, title, prize in [(72, TEAL, '剧本赛道', '一等奖 1 名 / 1 万元'), (568, RUST, '成片赛道', '一等奖 1 名 / 3 万元')]:
        d.rounded_rectangle((x, 256, x + 440, 927), radius=16, fill=WHITE)
        d.rounded_rectangle((x, 256, x + 440, 353), radius=16, fill=color)
        put(d, x + 27, 277, title, 38, WHITE, 'bold', x + 414)
        put(d, x + 27, 377, prize, 25, color, 'bold', x + 414)
    put(d, 99, 441, '20,000', 60, TEAL, 'number', 486)
    put(d, 99, 514, '字起 / 完整剧本', 28, right=486)
    d.line((99, 568, 485, 568), fill=LINE, width=2)
    put(d, 99, 602, '5,000', 60, TEAL, 'number', 486)
    put(d, 99, 676, '字起 / 大纲与人物小传合计', 24, right=486)
    d.line((99, 733, 485, 733), fill=LINE, width=2)
    put(d, 99, 771, '另附故事梗概', 30, INK, 'bold', 486)
    put(d, 99, 827, '3000 字以内，不是写满', 25, DIM, right=486)
    put(d, 595, 441, '20', 74, RUST, 'number')
    put(d, 715, 474, '集起', 35, RUST, 'bold')
    put(d, 595, 551, '每集 30 秒至 20 分钟', 29)
    d.line((595, 614, 981, 614), fill=LINE, width=2)
    put(d, 595, 650, '不是一条样片', 36, INK, 'title')
    put(d, 595, 718, '完整剧情 + 商都主题', 27)
    put(d, 595, 771, '全套版权授权材料', 27)
    put(d, 595, 838, 'AI 占比未见数值门槛', 25, DIM)
    put(d, 72, 980, '本号工作量示例，不是官方总时长要求', 29, TEAL, 'bold')
    d.rounded_rectangle((72, 1031, 1008, 1131), radius=10, fill=INK)
    center(d, 540, 1062, '20 集 × 90 秒 = 30 分钟成片', 39, WHITE)
    put(d, 72, 1168, '不要按奖金倒推必能回本的预算，也不要按下限凑片。', 29, RUST, 'bold')
    footer(d, 1259, ['来源：正观新闻 2026-10-14 活动说明；详细条件未取得完整附件核验。', '资料核查截至 2026-10-15。实际投稿请核对完整方案及报名要求。'])
    return im


def chart_two():
    im, d = page('梗概阶段，不等于最终交稿', '全部为 2026 年 / 不要把活动结束日当成投稿截止日', '02', 1380)
    d.rounded_rectangle((72, 261, 1008, 533), radius=18, fill=INK)
    put(d, 102, 291, '10 月', 60, '#f0c588', 'bold')
    put(d, 339, 313, '故事梗概征集阶段', 38, WHITE, 'title')
    put(d, 102, 400, '交什么：故事梗概、人物小传、创作思路', 32, WHITE)
    put(d, 102, 466, '具体哪天截止、是否必经，公开说明未写清。', 27, '#d4c9b8')
    d.line((540, 534, 540, 586), fill=DIM, width=3)
    d.line((292, 586, 788, 586), fill=DIM, width=3)
    for x, date, label, color in [(72, '11.30', '剧本征集截止', TEAL), (568, '12.31', '成片征集截止', RUST)]:
        cx = x + 220
        d.line((cx, 586, cx, 631), fill=color, width=3)
        d.polygon(((cx - 8, 619), (cx + 8, 619), (cx, 635)), fill=color)
        d.rounded_rectangle((x, 655, x + 440, 858), radius=15, fill=WHITE)
        center(d, cx, 690, date, 67, color, 'number')
        center(d, cx, 791, label, 33, color)
    put(d, 72, 916, '先向活动方确认，再安排后续投入', 35, INK, 'title')
    for i, line in enumerate(['十月阶段是否必经？准确截止到哪一天、几点？', '提交后是否要等确认，才能继续交最终作品？', '已有完整剧本或成片，能不能直接报名？']):
        y = 981 + i * 63
        d.ellipse((75, y + 7, 86, y + 18), fill=TEAL)
        put(d, 105, y, line, 29)
    put(d, 72, 1190, '活动延续至 2027 年 2 月，不等于届时仍可交作品。', 28, RUST, 'bold')
    footer(d, 1250, ['来源：正观新闻 2026-10-14；下方三问为本号整理，未替活动方作答。', '资料核查截至 2026-10-15。不要自行补成 10 月 31 日 23:59。'])
    return im


def chart_three():
    im, d = page('先整理项目，再启动长篇制作', '本号准备方法 / 不是活动原始报名模板', '03', 1440)
    rows = [
        ('项目判断', '选赛道，列出现有与缺失材料。', '商都文化元素必须影响人物行动，不只是换背景。'),
        ('三个文本', '梗概 / 人物小传 / 创作思路', '梗概写到结局；最终剧本另按赛道要求准备。'),
        ('AI 创作说明', '环节 / 工具 / 人的判断 / 保留记录', '如实区分已经完成与计划使用，不虚填工具。'),
        ('版权材料', '查改编、音乐、字体、声音与素材许可。', '注明使用范围；没有依据就标“待核”。'),
        ('提交与回执', '从活动原文核对入口，下载实际表格。', '查格式、命名、大小、接收方和报名回执。'),
    ]
    d.line((111, 275, 111, 1090), fill=LINE, width=3)
    for i, (title, line1, line2) in enumerate(rows):
        y = 262 + i * 178
        d.ellipse((76, y + 7, 148, y + 79), fill=TEAL)
        center(d, 112, y + 28, str(i + 1), 32, WHITE, 'number')
        put(d, 183, y + 5, title, 36, INK, 'title')
        put(d, 183, y + 66, line1, 28)
        put(d, 183, y + 117, line2, 25, DIM)
        if i < 4:
            d.line((183, y + 156, 1008, y + 156), fill=LINE, width=1)
    d.rounded_rectangle((72, 1180, 1008, 1290), radius=12, fill=INK)
    put(d, 101, 1203, '投入前问清：授权用途与期限、商业开发、费用。', 30, WHITE, 'bold')
    put(d, 101, 1254, '报道未写费用，不等于免费；入库不等于获得订单。', 25, '#d4c9b8')
    footer(d, 1325, ['参考：正观新闻 2026-10-14 材料说明；本号未完成实际投稿测试。', '完整授权文件尚未取得，不替活动方保证授权范围。'])
    return im


def cover_a():
    im, d = canvas(900, 383)
    put(d, 30, 24, '一人短剧厂牌', 18, DIM, right=870)
    put(d, 756, 24, '机会 / 01', 18, DIM, right=878)
    for i in range(3):
        x, y = 43 + i * 12, 103 - i * 9
        d.polygon(((x, y), (x + 127, y), (x + 148, y + 23), (x + 148, y + 170), (x, y + 170)), fill=WHITE, outline='#aeaa91')
        for k in range(5):
            d.line((x + 22, y + 44 + k * 21, x + 115, y + 44 + k * 21), fill='#93a998', width=3)
    d.rounded_rectangle((690, 95, 867, 275), radius=6, fill=INK)
    for i in range(7):
        for y in (105, 258):
            d.rectangle((700 + i * 23, y, 711 + i * 23, y + 8), fill=PAPER)
    for i in range(3):
        d.rectangle((704 + i * 50, 135, 745 + i * 50, 236), fill=['#809684', '#c89a68', '#9ba993'][i])
    center(d, 450, 71, '郑州 · AI 微短剧征集', 25, TEAL, safe=True)
    center(d, 450, 124, '先投剧本', 66, INK, 'title', True)
    center(d, 450, 205, '还是成片', 66, RUST, 'title', True)
    d.line((304, 291, 596, 291), fill=LINE, width=2)
    center(d, 450, 313, '十月梗概 / 两条参评路径', 24, TEAL, safe=True)
    for x in range(0, 900, 36):
        h = 14 if x % 72 == 0 else 9
        d.rectangle((x, 383 - h, x + 28, 383), fill='#c9bda7')
    return im


def cover_b():
    im, d = canvas(900, 383, INK)
    put(d, 30, 24, '一人短剧厂牌', 18, '#c8bba5', right=870)
    put(d, 756, 24, '机会 / 01', 18, '#c8bba5', right=878)
    for x in (42, 706):
        d.rounded_rectangle((x, 106, x + 150, 292), radius=12, fill='#474038')
        d.rectangle((x, 132, x + 150, 156), fill=RUST)
        for i in range(3):
            for j in range(4):
                d.rectangle((x + 17 + j * 32, 176 + i * 31, x + 34 + j * 32, 190 + i * 31), fill='#8b7961')
    center(d, 450, 72, '郑州 AI 微短剧征集', 27, '#cfb999', safe=True)
    center(d, 450, 126, '先核十月', 63, WHITE, 'title', True)
    center(d, 450, 207, '梗概阶段', 63, '#f0c588', 'title', True)
    center(d, 450, 313, '先确认是否必经，再安排交稿', 23, '#cfb999', safe=True)
    return im


def cover_c():
    im, d = canvas(900, 383, TEAL)
    put(d, 30, 24, '一人短剧厂牌', 18, '#d4d5bc', right=870)
    put(d, 756, 24, '机会 / 01', 18, '#d4d5bc', right=878)
    for x in (64, 724):
        d.line((x, 300, x + 85, 94), fill='#769c81', width=8)
        d.polygon(((x + 66, 105), (x + 108, 103), (x + 93, 68)), fill='#769c81')
    center(d, 450, 72, '郑州征集 / 不是制作补贴', 25, '#d4d5bc', safe=True)
    center(d, 450, 125, '先选赛道', 66, WHITE, 'title', True)
    center(d, 450, 207, '再做整部', 66, '#f0c588', 'title', True)
    center(d, 450, 313, '看材料与排期，不只看奖金', 23, '#d4d5bc', safe=True)
    return im


def review(covers):
    im, d = canvas(1500, 1530, '#e5e2dc')
    for i, cover in enumerate(covers):
        y = 25 + i * 500
        put(d, 28, y, ['A / 手稿与胶片：突出两条路径', 'B / 日历：突出当前报名阶段', 'C / 路标：突出投入前的选择'][i], 25, right=1450)
        im.paste(cover, (28, y + 52))
        d.rectangle((286, y + 52, 669, y + 434), outline='#b48e60', width=1)
        crop = cover.crop((258, 0, 641, 383)).resize((142, 142), Image.Resampling.LANCZOS)
        for j, (bg, fg) in enumerate([('#ffffff', INK), ('#191919', WHITE)]):
            x = 958 + j * 254
            d.rounded_rectangle((x, y + 52, x + 228, y + 434), radius=16, fill=bg)
            put(d, x + 18, y + 73, ['浅色分享卡', '深色分享卡'][j], 19, fg, right=x + 215)
            im.paste(crop, (x + 43, y + 123))
            put(d, x + 18, y + 293, '郑州AI短剧征集', 19, fg, right=x + 215)
            put(d, x + 18, y + 329, '一人短剧厂牌', 16, fg, right=x + 215)
    return im


def save(im, path):
    im.quantize(colors=192, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(path, optimize=True)
    if path.parent == OUT:
        assert path.stat().st_size < 200 * 1024, (path.name, path.stat().st_size)
    print(path.name, im.size, path.stat().st_size)


if __name__ == '__main__':
    charts = [chart_one(), chart_two(), chart_three()]
    covers = [cover_a(), cover_b(), cover_c()]
    proof = review(covers)
    for (path, index), chars in GLYPHS.items():
        tt = TTFont(path, fontNumber=index)
        missing = sorted(c for c in chars if ord(c) not in tt.getBestCmap())
        tt.close()
        assert not missing, (path, missing)
    for im, (name, _) in zip(charts, FIGURES):
        save(im, OUT / name)
    for im, name in zip(covers, COVERS):
        save(im, OUT / name)
    save(proof, SAMPLES / '018_封面三方向与分享卡对照.png')
    sheet, _ = canvas(1212, 550, '#e5e2dc')
    for i, im in enumerate(charts):
        thumb = im.copy()
        thumb.thumbnail((380, 530), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (12 + i * 402, 10))
    save(sheet, SAMPLES / '018_正文配图手机宽预览.png')
    body = (OUT.parent / '文章' / '018_发布版.md').read_text()
    for i, (_, caption) in enumerate(FIGURES, 1):
        assert f'【图 {i}：{caption}】' in body
    print('PASS: glyph coverage, bounds, non-overlap, safe crops, file sizes, captions')
