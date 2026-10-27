#!/usr/bin/env python3
"""044《即梦上线短剧工作室：流水线收进一个平台》配图与封面。纯本地 Pillow。"""
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


def pipeline():
    im, d = page('五步，收进一个平台', '即梦「短剧工作室」/ 2026-10-26 上线', '01', 1100)
    steps = [
        ('01', '剧本整理', '文档/表格', RUST),
        ('02', '角色与场景', '图片工具 + 本地文件夹', TEAL),
        ('03', '分镜生成', '文档 + 提示词表', GOLD),
        ('04', '视频制作', '视频模型/第三方', RUST),
        ('05', '后期调整', '剪辑软件', TEAL),
    ]
    y = 238
    for num, name, old, color in steps:
        d.rounded_rectangle((72, y, 1008, y + 118), radius=12, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 118), radius=4, fill=color)
        put(d, 104, y + 26, num, 24, color, 'number', 180)
        put(d, 170, y + 16, name, 28, INK, 'bold', 500)
        put(d, 170, y + 64, '过去：' + old, 20, DIM, 'body', 980)
        put(d, 780, y + 40, '现在：平台内', 21, color, 'bold', 1000)
        y += 134

    d.rounded_rectangle((72, y + 2, 1008, y + 92), radius=12, fill=INK)
    put(d, 100, y + 16, '省下来的不是软件钱', 21, '#bdb3a1', right=980)
    put(d, 100, y + 48, '是切换和返工的时间', 30, '#f0c588', 'bold', 980)

    footer(d, y + 112, [
        '来源：新浪科技 2026-10-26；即梦产品页功能描述。功能范围以官方为准。',
        '「过去」列为本号对常见单人工作流的归纳，不是平台官方对比。',
    ])
    return im


def changes():
    im, d = page('三个变化，先看清', '工具合并之后，流程和资产都要重排', '02', 1080)
    blocks = [
        ('01', '角色与场景变成资产库', '一致性从「每次贴参考图」变成「复用平台资产」；前提是你先把 L01 整理干净。', RUST),
        ('02', '分镜到视频，返工变短', '同一平台改镜头，不用重导分镜表；默认值也更容易把节奏带跑，仍要自己盯。', TEAL),
        ('03', '旧工作流要迁移', '小云雀保留独立入口，但两套资产结构不同；先确认原项目能不能完整导出。', GOLD),
    ]
    y = 238
    for num, head, body, color in blocks:
        d.rounded_rectangle((72, y, 1008, y + 176), radius=14, fill=WHITE)
        d.rounded_rectangle((72, y, 82, y + 176), radius=4, fill=color)
        put(d, 104, y + 18, num, 22, color, 'number', 200)
        put(d, 150, y + 14, head, 27, INK, 'bold', 980)
        paragraph(d, 150, y + 62, body, width=820, size=21, color=DIM, leading=33)
        y += 192

    d.rounded_rectangle((72, y + 2, 1008, y + 96), radius=12, fill=SOFT)
    put(d, 100, y + 16, '工具会换，资产不能丢', 22, RUST, 'bold', 980)
    put(d, 100, y + 54, '先盘点能导出什么，再决定迁不迁。', 20, DIM, 'body', 980)

    footer(d, y + 116, [
        '来源：新浪科技 2026-10-26；澎湃新闻 2026-10-24。功能整合细节官方未逐项说明。',
        '「资产结构不同」为本号判断；迁移前以自己账号的实际导出结果为准。',
    ])
    return im


def actions():
    im, d = page('一人厂牌的三件事', '先盘资产，再用一集做对照', '03', 1020)
    blocks = [
        ('01', '先盘资产，再换工具', '角色卡、场景基准图、提示词版本、配音音色按项目归档，确认能导出、能迁移。', RUST),
        ('02', '用一集做对照', '同剧本旧流程一版、新工作室一版；只比角色一致性、返工时长、单集成本。', TEAL),
        ('03', '别把流程绑死', '平台整合是趋势，账号/额度/商用条款都可能变；关键资产留本地副本。', GOLD),
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
    put(d, 100, y + 18, '工具效率不等于内容质量', 21, '#bdb3a1', right=980)
    put(d, 100, y + 50, '一致性和完播，仍要逐集验证', 26, '#f0c588', 'bold', 980)

    footer(d, y + 116, [
        '以上为执行建议，不是平台规则；定价、额度与商用条款以官方为准。',
        '本号建议 · C 级；来源见正文。',
    ])
    return im


def cover():
    global TEXT_BOXES
    TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    center(d, 450, 54, '即梦上线「短剧工作室」', 22, '#f0c588', 'bold', True)
    center(d, 450, 92, '流水线收进一个平台', 38, WHITE, 'title', True)
    center(d, 450, 158, '剧本 → 分镜 → 视频 → 后期', 22, '#8fc0b4', 'bold', True)
    d.line((300, 210, 600, 210), fill='#766657', width=2)
    center(d, 450, 228, '省下的是切换和返工的时间', 20, '#d8cdbb', 'body', True)
    center(d, 450, 284, '一人厂牌，先盘资产再换工具', 19, '#bdb3a1', 'body', True)
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
    for name, maker in [('044_图1_五步流水线_1080.png', pipeline),
                        ('044_图2_三个变化_1080.png', changes),
                        ('044_图3_三件事_1080.png', actions)]:
        im = maker()
        validate_glyphs()
        save_png(im, OUT / name)
    im = cover()
    validate_glyphs()
    save_png(im, OUT / '封面_044_即梦工作室_900x383.png')
    print('done')
