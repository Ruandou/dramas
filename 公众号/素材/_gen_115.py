# -*- coding: utf-8 -*-
"""115 封面：总局扶持短剧，慈文传媒归属收入约50万，只对应《开标之战》。"""
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
PANEL = '#F3EFE5'

COVER_NAME = '封面_115_20261120_900x383.png'


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
    c.text(760, 24, '115 / 口径', 15, MUTED)
    d.line((27, 56, 873, 56), fill=LINE, width=1)

    # 左侧：事件时间线
    c.text(27, 84, '慈文传媒', 28, INK, True)
    c.text(27, 126, '《开标之战》', 22, INK, True)
    c.text(27, 164, '总局「五个一批」扶持', 14, MUTED)
    c.text(27, 188, '9-26 三平台上线', 14, MUTED)
    c.text(27, 212, '10-20《铁血信使》红果上线', 13, MUTED)
    c.text(27, 252, '11-19 互动易答复', 15, TEAL, True)
    c.text(27, 276, '仍无播放数', 15, TEAL, True)
    c.text(27, 350, '数据截至 2026-11-19', 11, MUTED)

    # 中间：一个数字与三层否定
    d.rectangle((278, 68, 590, 348), fill=PANEL, outline=LINE, width=1)
    d.rectangle((278, 68, 282, 348), fill=TEAL)
    c.text(292, 82, '归属于公司的收入', 17, INK, True)
    c.text(292, 110, '约50万', 64, RUST, True, critical=True)
    d.line((292, 198, 540, 198), fill=LINE, width=1)
    c.text(292, 206, '10-14 公告口径', 15, MUTED)
    c.text(292, 234, '不是播放量、流水或利润', 16, INK)
    c.text(292, 266, '50万只算《开标之战》', 16, TEAL, True)
    c.text(292, 296, '《铁血信使》10-20 才上线', 14, TEAL)
    c.text(292, 322, '两部剧不能合并算', 14, MUTED)

    # 右侧：公告没给的四项
    d.line((645, 80, 645, 340), fill=LINE, width=1)
    c.text(660, 82, '公告没给', 15, MUTED)
    d.line((660, 106, 873, 106), fill=LINE, width=1)
    c.text(660, 116, '播放量', 19, INK, True)
    c.text(660, 146, '投资金额', 19, INK, True)
    c.text(660, 176, '分账方式', 19, INK, True)
    c.text(660, 206, '项目盈亏', 19, INK, True)
    c.text(660, 246, '11-19 仍未更新数字', 13, TEAL, True)
    c.text(660, 274, '短剧业务 2025 年亏损', 13, MUTED)
    c.text(660, 300, 'AIGC 尚无收入', 14, RUST, True)
    c.text(660, 330, '7天6板 ≠ 项目收入', 13, MUTED)

    c.finish(out / COVER_NAME)


if __name__ == '__main__':
    cover(HERE)
