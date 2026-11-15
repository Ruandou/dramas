# -*- coding: utf-8 -*-
"""103 百度一镜封面。仅生成 900×383 封面，纯本地 Pillow，零扣费。"""
from __future__ import annotations

from importlib import import_module
from pathlib import Path
import sys

from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_c = import_module('_gen_charts_006')

WIDTH, HEIGHT = 900, 383
SAFE_LEFT, SAFE_RIGHT = (WIDTH - HEIGHT) / 2, (WIDTH + HEIGHT) / 2
PAPER, INK, DIM, LINE = _c.PAPER, _c.INK, _c.DIM, _c.LINE
RUST = (174, 66, 44)
FONT_SPECS = {
    'body': (_c.HIRA, 0),
    'bold': (_c.HIRA, 2),
    'title': (_c.SONG, 1),
    'number': (_c.MONO, 1),
}
OUT = HERE / '封面_103_20261114_900x383.png'
GLYPHS: dict[tuple[str, int], set[str]] = {}
TEXT_BOXES: list[tuple[str, tuple[int, int, int, int]]] = []


def font(size: int, kind: str = 'body'):
    path, index = FONT_SPECS[kind]
    return _c.f(path, size, index=index)


def put(draw, x, y, text, size, color=INK, kind='body', critical=False):
    ff = font(size, kind)
    box = draw.textbbox((x, y), text, font=ff, anchor='lt')
    assert 0 <= box[0] < box[2] <= WIDTH, (text, box)
    assert 0 <= box[1] < box[3] <= HEIGHT, (text, box)
    if critical:
        assert SAFE_LEFT <= box[0] and box[2] <= SAFE_RIGHT, (text, box, '方形裁切越界')
    for other, previous in TEXT_BOXES:
        overlap = min(box[2], previous[2]) > max(box[0], previous[0]) and min(box[3], previous[3]) > max(box[1], previous[1])
        assert not overlap, (text, other, '文本重叠')
    TEXT_BOXES.append((text, box))
    GLYPHS.setdefault((kind, size), set()).update(text)
    draw.text((x, y), text, font=ff, fill=color, anchor='lt')


def centered(draw, y, text, size, color=INK, kind='body', critical=True):
    text_width = draw.textlength(text, font=font(size, kind))
    put(draw, (WIDTH - text_width) / 2, y, text, size, color, kind, critical)


def check_glyphs():
    for (kind, size), chars in GLYPHS.items():
        path, index = FONT_SPECS[kind]
        ff = TTFont(path, fontNumber=index)
        cmap = ff.getBestCmap()
        missing = sorted(char for char in chars if ord(char) not in cmap)
        ff.close()
        assert not missing, (path, index, size, missing)


def cover():
    TEXT_BOXES.clear()
    GLYPHS.clear()
    im = Image.new('RGB', (WIDTH, HEIGHT), PAPER)
    d = ImageDraw.Draw(im)

    put(d, 33, 24, '一人短剧厂牌', 18, DIM, 'bold')
    label = '103 / 快讯'
    put(d, WIDTH - 33 - d.textlength(label, font=font(17)), 24, label, 17, DIM)
    d.line((33, 53, WIDTH - 33, 53), fill=LINE, width=1)

    # 所有核心信息均位于居中 383px 方形裁切范围内。
    d.rounded_rectangle((240, 66, 660, 359), radius=18, fill=(238, 232, 218))
    d.rectangle((433, 66, 467, 71), fill=RUST)
    centered(d, 85, '百度一镜', 43, INK, 'title')

    number, unit = '0.7', '元/秒'
    nw = d.textlength(number, font=font(76, 'number'))
    uw = d.textlength(unit, font=font(32, 'bold'))
    start = (WIDTH - nw - 13 - uw) / 2
    put(d, start, 143, number, 76, RUST, 'number', critical=True)
    put(d, start + nw + 13, 174, unit, 32, RUST, 'bold', critical=True)

    d.line((337, 230, 563, 230), fill=LINE, width=1)
    centered(d, 251, '5秒镜头怎么算', 29, INK, 'bold')
    centered(d, 296, '按刊例估算', 20, DIM)
    centered(d, 331, 'ERNIE-Wizshot-ME', 15, DIM, 'number')

    check_glyphs()
    im.quantize(colors=192, method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.NONE).save(OUT, optimize=True)
    with Image.open(OUT) as saved:
        assert saved.size == (WIDTH, HEIGHT), saved.size
        saved.verify()
    assert len(TEXT_BOXES) == 8, TEXT_BOXES
    print(f'{OUT}\n900×383; {OUT.stat().st_size / 1024:.1f} KB')
    print('PASS: 字形、画布越界、文本重叠、核心信息方形裁切及PNG重读校验')


if __name__ == '__main__':
    cover()
