# -*- coding: utf-8 -*-
"""114 封面：宝安微短剧播映资助，3000万播放单部10万，11月23日截止。"""
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

COVER_NAME = '封面_114_20261120_900x383.png'


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
    d.rectangle((0, 0, 9, 383), fill=TEAL)
    c.text(27, 24, '一人短剧厂牌', 17, INK, True)
    c.text(758, 26, '114 / 申报', 15, MUTED)
    d.line((27, 58, 873, 58), fill=LINE, width=1)

    c.text(29, 94, '宝安', 26, INK, True)
    c.text(29, 134, '播映资助', 40, INK, True)
    c.text(29, 208, '对象：影视企业', 18, MUTED)
    c.text(29, 244, '入口：亲清平台', 18, MUTED)
    c.text(29, 306, '11月23日截止', 20, TEAL, True)

    c.text(300, 96, '3000万次', 44, RUST, True, critical=True)
    c.text(300, 158, '单一账号 · 同一作品', 16, MUTED)
    c.text(300, 190, '单部资助 10 万', 26, INK, True)
    c.text(300, 232, '每家企业年上限 100 万', 17, MUTED)
    c.text(300, 270, '「微短剧+」入选 20 万', 18, TEAL, True)
    c.text(300, 302, '每家企业年上限 200 万', 15, MUTED)

    d.line((672, 96, 672, 330), fill=LINE, width=1)
    c.text(692, 98, '别混成', 16, MUTED)
    c.text(692, 130, '市第二批', 20, INK, True)
    c.text(692, 160, '11-13 已截止', 17, RUST, True)
    c.text(692, 210, '截止无整点', 17, TEAL, True)
    c.text(692, 250, '指南未公开', 17, MUTED)
    c.text(692, 290, '两条不默认叠加', 15, MUTED)

    c.finish(out / COVER_NAME)


if __name__ == '__main__':
    cover(HERE)
