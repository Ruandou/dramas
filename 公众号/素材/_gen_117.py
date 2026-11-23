# -*- coding: utf-8 -*-
"""117 封面：红果短剧「时间管理」与「时间锁」，锁的开关在用户手里。"""
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

COVER_NAME = '封面_117_20261121_900x383.png'


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
    c.text(758, 24, '117 / 产品', 15, MUTED)
    d.line((27, 56, 873, 56), fill=LINE, width=1)

    # 左：产品与三个可调项
    c.text(27, 80, '红果短剧', 28, INK, True)
    c.text(27, 118, '时间管理', 22, INK, True)
    c.text(27, 152, '11-20 上线', 14, MUTED)
    d.line((27, 180, 250, 180), fill=LINE, width=1)
    c.text(27, 196, '休息提醒', 13, MUTED)
    c.text(27, 216, '30分 / 1小时 / 2小时', 14, INK)
    c.text(27, 244, '睡眠提醒', 13, MUTED)
    c.text(27, 264, '00:00 起', 14, INK)
    c.text(27, 292, '时间锁', 13, MUTED)
    c.text(27, 312, '单日时长 + 密码', 14, TEAL, True)
    c.text(27, 350, '数据截至 2026-11-21', 11, MUTED)

    # 中：手机面板与锁
    d.rectangle((272, 70, 618, 350), fill=SCREEN)
    d.rectangle((272, 70, 618, 76), fill=TEAL)
    c.text(288, 90, '单日使用', 12, SCREEN_MUTED)
    c.text(445, 112, '时间锁', 64, CREAM, True, center=445, critical=True)
    c.text(445, 184, '自己设 · 自己开', 18, CREAM, center=445)
    # 锁：锁梁 + 锁体 + 钥匙孔
    d.arc((409, 200, 481, 264), 180, 360, fill=CREAM, width=4)
    d.rounded_rectangle((397, 228, 493, 288), radius=10, outline=CREAM, width=4)
    d.ellipse((439, 246, 451, 258), fill=CREAM)
    d.rectangle((442, 252, 448, 270), fill=CREAM)
    c.text(445, 304, '输密码才能继续', 15, CREAM, center=445)
    c.text(445, 328, '锁的是 App 界面', 12, SCREEN_MUTED, center=445)

    # 右：版本对照与未披露项
    d.rectangle((640, 70, 880, 350), outline=LINE, width=1)
    c.text(658, 84, '10月版', 13, MUTED)
    c.text(658, 104, '只是提醒', 17, INK, True)
    c.text(658, 138, '11月版', 13, MUTED)
    c.text(658, 158, '多了把锁', 17, TEAL, True)
    d.line((658, 190, 862, 190), fill=LINE, width=1)
    c.text(658, 204, '通稿没提', 12, MUTED)
    c.text(658, 224, '家长模式', 14, RUST, True)
    c.text(658, 248, '默认开没开', 13, INK)
    c.text(658, 268, '时长档位', 13, INK)
    c.text(658, 288, '忘密码怎么办', 13, INK)
    d.line((658, 314, 862, 314), fill=LINE, width=1)
    c.text(658, 326, '功能未实测', 11, MUTED)

    c.finish(out / COVER_NAME)


if __name__ == '__main__':
    cover(HERE)
