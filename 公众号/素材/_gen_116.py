# -*- coding: utf-8 -*-
"""116 封面：109 分钟的 AI 漫剧番外，进 200 余城影院，预约放映。"""
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
CREAM = '#F6EFE2'
SCREEN = '#2A2621'
SCREEN_MUTED = '#C9BFAE'

COVER_NAME = '封面_116_20261120_900x383.png'


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
    c.text(27, 22, '一人短剧厂牌', 17, INK, True)
    c.text(760, 24, '116 / 观察', 15, MUTED)
    d.line((27, 56, 873, 56), fill=LINE, width=1)

    # 左：片名与事件
    c.text(27, 84, '《万妖图录传》', 22, INK, True)
    c.text(27, 118, '之《云州异客》', 22, INK, True)
    c.text(27, 160, 'AI漫剧 · 光宇出品', 14, MUTED)
    c.text(27, 184, '改编自番茄小说同名作品', 13, MUTED)
    c.text(27, 224, '11-20 起 影院开场', 16, TEAL, True)
    c.text(27, 250, '200 余座城市', 16, TEAL, True)
    c.text(27, 280, '预约放映 · 反向组场', 13, MUTED)
    c.text(27, 350, '数据截至 2026-11-20', 11, MUTED)

    # 中：银幕，109 分钟
    d.rectangle((262, 70, 628, 350), fill=SCREEN)
    d.rectangle((262, 70, 628, 76), fill=TEAL)
    c.text(278, 92, '中影院线 · 特别篇', 13, SCREEN_MUTED)
    c.text(278, 118, '109', 96, CREAM, True, critical=True)
    c.text(490, 122, '分钟', 28, CREAM, True)
    d.line((278, 252, 612, 252), fill='#5A5248', width=1)
    c.text(278, 264, '独立番外故事线', 16, CREAM)
    c.text(278, 292, '不是已更内容的剪辑版', 14, SCREEN_MUTED)
    c.text(278, 318, '赛博修仙 · 姜月初新篇', 14, SCREEN_MUTED)

    # 右：预约放映票根
    d.rectangle((652, 70, 880, 350), outline=LINE, width=1)
    c.text(668, 82, '预约放映', 15, TEAL, True)
    for y in range(112, 132, 6):
        d.line((668, y, 862, y), fill=LINE, width=1)
    c.text(668, 142, '11-20 起', 20, INK, True)
    c.text(668, 174, '全国 200+ 城', 15, MUTED)
    c.text(668, 200, '票价 30 / 35 元', 18, RUST, True)
    c.text(668, 232, '中影电影通 / 京东电影', 12, MUTED)
    for y in range(258, 278, 6):
        d.line((668, y, 862, y), fill=LINE, width=1)
    c.text(668, 290, '没公开', 12, MUTED)
    c.text(668, 310, '结束日期 · 场次', 13, INK)
    c.text(668, 330, '票房 · 分账', 13, INK)

    c.finish(out / COVER_NAME)


if __name__ == '__main__':
    cover(HERE)