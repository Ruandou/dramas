# -*- coding: utf-8 -*-
"""089《海外短剧 10 月榜》正文两图 + 封面。纯本地 Pillow，零扣费。"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from importlib import import_module

_c = import_module('_gen_charts_006')

OUT = HERE
PAPER, INK, DIM, LINE, BOX = _c.PAPER, _c.INK, _c.DIM, _c.LINE, _c.BOX
RUST, TEAL, GOLD = (174, 66, 44), (40, 105, 94), (185, 133, 61)
WHITE = (255, 250, 240)

SONG, HIRA, MONO = _c.SONG, _c.HIRA, _c.MONO
GLYPHS: dict = {}
BOXES: list = []
ISSUE = '089'
EDITION = '2026-11-09'
W = 1080


def font(size, kind='body'):
    path, index = {'body': (HIRA, 0), 'bold': (HIRA, 2),
                   'title': (SONG, 1), 'number': (MONO, 1)}[kind]
    return _c.f(path, size, index=index)


def put(d, x, y, text, size=28, color=INK, kind='body', right=None):
    ff = font(size, kind)
    width = d.textlength(text, font=ff)
    if right is not None:
        assert x + width <= right + 0.1, (text, x, width, right)
    box = d.textbbox((x, y), text, font=ff, anchor='lt')
    assert box[0] >= 0 and box[2] <= d._image.width and box[3] <= d._image.height, (text, box)
    for other, b in BOXES:
        if min(box[2], b[2]) > max(box[0], b[0]) and min(box[3], b[3]) > max(box[1], b[1]):
            raise AssertionError(f'文本重叠: {text!r} / {other!r}')
    BOXES.append((text, box))
    GLYPHS.setdefault((kind, size), set()).update(text)
    d.text((x, y), text, font=ff, fill=color, anchor='lt')
    return width


def put_right(d, x_right, y, text, size=28, color=INK, kind='body'):
    w = d.textlength(text, font=font(size, kind))
    return put(d, x_right - w, y, text, size, color, kind)


def head(d, title, sub):
    d.rectangle((72, 44, 83, 66), fill=RUST)
    put(d, 100, 44, f'一人短剧厂牌 / 行业观察 {ISSUE}', 21, DIM, 'bold')
    put_right(d, W - 72, 44, EDITION, 22, RUST, 'number')
    put(d, 72, 92, title, 46, INK, 'title')
    put(d, 72, 158, sub, 22, DIM)
    return 216


def dot_grid(d, x, y, n, color, dot=14, gap=4, cols=10):
    for i in range(100):
        cx = x + (i % cols) * (dot + gap)
        cy = y + (i // cols) * (dot + gap)
        if i < n:
            d.ellipse((cx, cy, cx + dot, cy + dot), fill=color)
        else:
            d.ellipse((cx, cy, cx + dot, cy + dot), outline=LINE, width=2)
    return cols * dot + (cols - 1) * gap


def save(im, name):
    dest = OUT / name
    im.quantize(colors=192, method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.NONE).save(dest, optimize=True)
    print(dest.name, im.size, f'{dest.stat().st_size / 1024:.1f} KB')


def check_glyphs():
    for (kind, size), chars in GLYPHS.items():
        path, index = {'body': (HIRA, 0), 'bold': (HIRA, 2),
                       'title': (SONG, 1), 'number': (MONO, 1)}[kind]
        ff = TTFont(path, fontNumber=index)
        cmap = ff.getBestCmap()
        missing = sorted(c for c in chars if ord(c) not in cmap)
        ff.close()
        assert not missing, (path, index, missing)


def chart1():
    BOXES.clear()
    im = Image.new('RGB', (W, 1000), PAPER)
    d = ImageDraw.Draw(im)
    y = head(d, '三张百强榜：总盘与尾部门槛', '2026 年 10 月榜 / 统计 10-01—10-31 / 尾部区间读成进榜门槛')

    rows = [
        ('海外短剧', '3.38', '亿', '总热值', '+5.87%', RUST, 85, '85 部在 150—500 万', '门槛 150 万热值'),
        ('海外 AI 剧', '88.05', '万组', '总素材量', '+20.42%', TEAL, 37, '37 部在 3,500—5,000 组', '门槛 3,500 组素材'),
        ('TikTok 热播', '88.44', '亿次', '播放增量', '+4.27%', GOLD, 79, '79 部在 5,900 万—1 亿', '门槛 5,900 万次'),
    ]
    for label, num, suffix, unit, delta, color, n, band, gate in rows:
        d.rounded_rectangle((72, y, W - 72, y + 228), radius=16, fill=BOX)
        put(d, 104, y + 22, label, 32, INK, 'bold')
        w = put(d, 104, y + 68, num, 40, INK, 'number')
        put(d, 104 + w + 8, y + 84, suffix, 22, INK)
        put(d, 104 + w + 8 + d.textlength(suffix, font=font(22)) + 10, y + 84, unit, 20, DIM)
        wd = put(d, 104, y + 122, delta, 24, color, 'number')
        put(d, 104 + wd + 8, y + 126, '环比', 20, DIM)
        put(d, 104, y + 160, gate, 30, color, 'bold')
        put(d, 104, y + 198, band, 20, DIM)
        gx = 680
        wn = put(d, gx, y + 24, f'{n}/100', 24, color, 'number')
        put(d, gx + wn + 8, y + 28, '部', 20, DIM)
        dot_grid(d, gx, y + 64, n, color)
        y += 248

    put(d, 72, 952, '数据：DataEye 研究院 2026 年 10 月海外短剧 / 海外 AI 剧 / TikTok 热播百强榜；门槛为榜单尾部分档下沿。', 19, DIM)
    check_glyphs()
    save(im, f'089_图1_三榜门槛_1080.png')


def arrow_row(d, y, label, v1, v2, color):
    x0, x1 = 470, 920
    put(d, 104, y - 14, label, 26, INK, 'bold')
    d.line((x0, y + 10, x1, y + 10), fill=LINE, width=2)
    scale = (x1 - x0) / 70.0
    p1, p2 = x0 + v1 * scale, x0 + v2 * scale
    d.line((p1, y + 10, p2, y + 10), fill=color, width=6)
    d.ellipse((p1 - 9, y + 1, p1 + 9, y + 19), fill=PAPER, outline=color, width=3)
    d.ellipse((p2 - 9, y + 1, p2 + 9, y + 19), fill=color, outline=color, width=3)
    if p2 - p1 < 90:
        mid = (p1 + p2) / 2
        label = f'{v1} → {v2}'
        wlab = d.textlength(label, font=font(22, 'body'))
        put(d, mid - wlab / 2, y - 36, label, 22, color)
    else:
        put(d, p1 - (8 if v1 < 10 else 14), y - 34, str(v1), 24, DIM, 'number')
        put_right(d, p2 + (8 if v2 < 10 else 16), y - 34, str(v2), 24, color, 'number')
    diff = v2 - v1
    sign = '+' if diff > 0 else ''
    put_right(d, W - 72, y - 8, f'{sign}{diff}', 28, color, 'number')


def chart2():
    BOXES.clear()
    im = Image.new('RGB', (W, 900), PAPER)
    d = ImageDraw.Draw(im)
    y = head(d, '席位换位：NetShort 加 9，DramaWave 少 13', '百强榜主投平台席位数 / 9 月空心 → 10 月实心')

    put(d, 72, 210, '真人短剧百强', 26, DIM, 'bold')
    d.line((72, 250, W - 72, 250), fill=RUST, width=3)
    arrow_row(d, 300, 'NetShort', 54, 63, RUST)
    put(d, 470, 336, '9 月 54 席 → 10 月 63 席，占比 63%', 20, DIM)

    put(d, 72, 400, 'AI 剧百强', 26, DIM, 'bold')
    d.line((72, 440, W - 72, 440), fill=TEAL, width=3)
    arrow_row(d, 490, 'NetShort', 53, 54, TEAL)
    arrow_row(d, 580, 'DramaWave', 33, 20, RUST)
    arrow_row(d, 670, 'FlickReels', 5, 18, TEAL)

    put(d, 72, 760, '空心＝9 月，实心＝10 月；刻度 0—70 席。', 20, DIM)
    put(d, 72, 800, '数据：DataEye 研究院 2026 年 10 月海外短剧 / 海外 AI 剧百强榜。', 19, DIM)
    check_glyphs()
    save(im, f'089_图2_席位换位_1080.png')


def cover():
    BOXES.clear()
    C_W, C_H = 900, 383
    im = Image.new('RGB', (C_W, C_H), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 26, '一人短剧厂牌 / 行业观察', 18, DIM, 'bold', C_W - 20)
    put_right(d, C_W - 33, 26, f'{ISSUE} / 10 月榜', 17, DIM, 'body')

    dot_grid(d, 42, 70, 63, RUST, dot=9, gap=3)
    wseat = put(d, 42, 224, '63/100', 20, RUST, 'number')
    put(d, 42 + wseat + 6, 228, '席', 18, RUST)
    put(d, 42, 252, 'NetShort', 19, DIM, 'number')

    def safe_center(cx, y, text, size, color=INK, kind='bold'):
        w = d.textlength(text, font=font(size, kind))
        assert w <= 351, (text, w)
        put(d, cx - w / 2, y, text, size, color, kind)

    safe_center(450, 76, '10 月海外短剧百强', 26, TEAL)
    safe_center(450, 120, '63 席归一家', 48, INK, 'title')
    safe_center(450, 198, '尾部门槛 150 万热值', 30, RUST)
    safe_center(450, 294, 'AI 剧 3,500 组素材', 19, DIM, 'body')
    safe_center(450, 322, 'TikTok 5,900 万播放增量', 19, DIM, 'body')

    put(d, 690, 90, 'AI 剧席位', 17, DIM, 'bold')
    for i, (name, v) in enumerate((('NetShort', 54), ('DramaWave', 20), ('FlickReels', 18))):
        y = 120 + i * 56
        put(d, 690, y, name, 18, INK, 'number')
        d.rounded_rectangle((690, y + 24, 690 + v * 2, y + 36), radius=4,
                            fill=TEAL if name != 'DramaWave' else RUST)
        put(d, 690 + v * 2 + 8, y + 20, str(v), 16, DIM, 'number')

    check_glyphs()
    save(im, f'封面_089_{EDITION.replace("-", "")}_900x383.png')


if __name__ == '__main__':
    {'chart1': chart1, 'chart2': chart2, 'cover': cover, 'all': lambda: (chart1(), chart2(), cover())}[
        sys.argv[1] if len(sys.argv) > 1 else 'all']()
