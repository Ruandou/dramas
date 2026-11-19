# -*- coding: utf-8 -*-
"""112 封面：快手分账加码，乡村/悬疑1.1倍、体育1.2倍。"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONT_PATH = '/System/Library/Fonts/Hiragino Sans GB.ttc'
PAPER = '#FAF6EE'
INK = '#2C2925'
MUTED = '#756D61'
LINE = '#D4C9B8'
RUST = '#AE422C'
TEAL = '#28695E'

COVER_NAME = '封面_112_20261119_900x383.png'


@lru_cache(None)
def font(size, bold=False):
    return ImageFont.truetype(FONT_PATH, size, index=2 if bold else 0)


class Canvas:
    def __init__(self, w, h):
        self.im = Image.new('RGB', (w, h), PAPER)
        self.d = ImageDraw.Draw(self.im)
        self.w, self.h = w, h
        self.boxes = []
        self.chars = {0: set(), 2: set()}
        self.critical = []

    def text(self, x, y, text, size, fill=INK, bold=False, center=None, region=None, critical=False):
        face = font(size, bold)
        if center is not None:
            x = center - self.d.textlength(text, font=face) / 2
        box = self.d.textbbox((x, y), text, font=face, anchor='lt')
        region = region or (0, 0, self.w, self.h)
        assert region[0] <= box[0] < box[2] <= region[2], ('横向越界', text, box, region)
        assert region[1] <= box[1] < box[3] <= region[3], ('纵向越界', text, box, region)
        for prev_text, prev in self.boxes:
            overlap = min(box[2], prev[2]) > max(box[0], prev[0]) and min(box[3], prev[3]) > max(box[1], prev[1])
            assert not overlap, ('文字重叠', text, prev_text, box, prev)
        if critical:
            left = (self.w - self.h) / 2
            assert left + 8 <= box[0] and box[2] <= left + self.h - 8, ('方形裁切丢字', text, box)
            self.critical.append((text, box))
        self.boxes.append((text, box))
        self.chars[2 if bold else 0].update(text)
        self.d.text((x, y), text, font=face, fill=fill, anchor='lt')
        return box

    def finish(self, path):
        for idx, chars in self.chars.items():
            face = TTFont(FONT_PATH, fontNumber=idx)
            cmap = face.getBestCmap()
            missing = sorted(c for c in chars if ord(c) not in cmap)
            face.close()
            assert not missing, ('字体缺字', idx, missing)
        with path.open('xb') as out:
            self.im.save(out, format='PNG', optimize=True)
        with Image.open(path) as saved:
            assert saved.size == (self.w, self.h)
            saved.verify()
        print(f'PASS {path.name} | {self.w}x{self.h} | {len(self.boxes)} boxes | {path.stat().st_size:,} bytes')
        if self.critical:
            print('CENTER CROP PASS:', '; '.join(t for t, _ in self.critical))


def cover(out):
    c = Canvas(900, 383)
    d = c.d
    d.rectangle((0, 0, 9, 383), fill=RUST)
    c.text(27, 24, '一人短剧厂牌', 17, INK, True)
    c.text(760, 26, '112 / 分账', 15, MUTED)
    d.line((27, 58, 873, 58), fill=LINE, width=1)

    c.text(29, 94, '快手分账', 30, INK, True)
    c.text(29, 136, '加码', 44, RUST, True)
    c.text(29, 208, '全片 ≥80 分钟', 19, MUTED)
    c.text(29, 240, 'AIGC 仿真人剧', 19, MUTED)
    c.text(29, 300, '至 12-31', 20, TEAL, True)

    c.text(300, 96, '乡村 / 悬疑 1.1 倍', 30, INK, True, critical=True)
    c.text(300, 146, '体育 1.2 倍', 30, INK, True, critical=True)
    c.text(300, 196, '系列剧 1.2 倍', 26, INK, True, critical=True)
    c.text(300, 250, '老剧时长/完播 1.15 倍', 21, MUTED, critical=True)
    c.text(300, 308, '保底 1 万 / 2 万，额外补贴', 20, TEAL, True, critical=True)

    d.line((672, 96, 672, 330), fill=LINE, width=1)
    c.text(692, 98, '窗口', 17, MUTED)
    c.text(692, 132, '12-31', 26, RUST, True)
    c.text(692, 176, '条件', 17, MUTED)
    c.text(692, 210, '全网首发', 18, INK, True)
    c.text(692, 240, '永久非独家', 18, INK, True)
    c.text(692, 270, '分销授权', 18, INK, True)

    c.finish(out / COVER_NAME)


if __name__ == '__main__':
    cover(HERE)
