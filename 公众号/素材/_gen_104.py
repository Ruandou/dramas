# -*- coding: utf-8 -*-
"""104 纳逗Pro封面。仅用本地Pillow生成900×383封面，零扣费。"""
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
}
OUT = HERE / '封面_104_20261115_900x383.png'
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
    assert not OUT.exists(), f'禁止覆盖既有封面：{OUT}'
    TEXT_BOXES.clear()
    GLYPHS.clear()
    im = Image.new('RGB', (WIDTH, HEIGHT), PAPER)
    d = ImageDraw.Draw(im)

    put(d, 33, 24, '一人短剧厂牌', 18, DIM, 'bold')
    label = '104 / 文档核验'
    put(d, WIDTH - 33 - d.textlength(label, font=font(17)), 24, label, 17, DIM)
    d.line((33, 53, WIDTH - 33, 53), fill=LINE, width=1)

    # 四行核心文字全部留在居中383px方形裁切范围。
    d.rounded_rectangle((240, 66, 660, 359), radius=18, fill=(238, 232, 218))
    d.rectangle((433, 66, 467, 71), fill=RUST)
    centered(d, 89, '纳逗Pro', 44, INK, 'title')
    d.line((340, 148, 560, 148), fill=LINE, width=1)
    centered(d, 173, '上传视频', 40, INK, 'bold')
    centered(d, 231, '成本另记', 48, RUST, 'bold')
    centered(d, 310, '文档算例', 20, DIM)

    check_glyphs()
    im.quantize(colors=192, method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.NONE).save(OUT, optimize=True)
    with Image.open(OUT) as saved:
        assert saved.size == (WIDTH, HEIGHT), saved.size
        saved.verify()
    assert len(TEXT_BOXES) == 6, TEXT_BOXES
    print(f'{OUT}\n900×383; {OUT.stat().st_size / 1024:.1f} KB')
    print('PASS: 字形、画布越界、文本重叠、核心文字方形裁切及PNG重读校验')


if __name__ == '__main__':
    cover()
