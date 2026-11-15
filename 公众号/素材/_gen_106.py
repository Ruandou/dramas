# -*- coding: utf-8 -*-
"""106 优酷AI短片拆集复算：原生Pillow，零API，xb模式只新建。

来源核读：/private/tmp/youku-ai-short-policy-20261115.jpg，优酷电影官方完整规则图。
先用 --preview-dir 输出到新的临时目录目检，确认后再无参数生成正式素材。
本图仅复算公开时长限制，不将时长合规等同于审核获批或分账收益。
"""
from __future__ import annotations

import argparse
from functools import lru_cache
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONT_PATH = '/System/Library/Fonts/Hiragino Sans GB.ttc'
PAPER = '#FBF7EF'
WHITE = '#FFFFFF'
INK = '#292443'
PURPLE = '#6253C7'
BLUE = '#365FC6'
LILAC = '#E9E4FA'
BLUE_PALE = '#DDE7FA'
CORAL = '#B85149'
CORAL_PALE = '#F4E3DD'
MUTED = '#696777'
LINE = '#D5D0DE'
MAX_SECONDS = 600
PLAN_20 = (400, 400, 400)
PLAN_60 = (540, 540, 540, 540, 540, 540, 360)
COVER_NAME = '封面_106_20261115_900x383.png'
BODY_NAME = '106_图1_拆集复算_1080.png'


@lru_cache(None)
def font(size, bold=False):
    return ImageFont.truetype(FONT_PATH, size, index=2 if bold else 0)


class Canvas:
    def __init__(self, w, h):
        self.im = Image.new('RGB', (w, h), PAPER)
        self.d = ImageDraw.Draw(self.im)
        self.w, self.h = w, h
        self.boxes = []
        self.characters = {0: set(), 2: set()}
        self.critical = []

    def text(self, x, y, text, size, fill=INK, bold=False, center=None, region=None, critical=False):
        face = font(size, bold)
        if center is not None:
            x = center - self.d.textlength(text, font=face) / 2
        box = self.d.textbbox((x, y), text, font=face, anchor='lt')
        region = region or (0, 0, self.w, self.h)
        assert region[0] <= box[0] < box[2] <= region[2], ('文字横向越界', text, box, region)
        assert region[1] <= box[1] < box[3] <= region[3], ('文字纵向越界', text, box, region)
        for previous_text, previous in self.boxes:
            overlap = min(box[2], previous[2]) > max(box[0], previous[0]) and min(box[3], previous[3]) > max(box[1], previous[1])
            assert not overlap, ('文字重叠', text, previous_text, box, previous)
        if critical:
            left = (self.w - self.h) / 2
            assert left + 8 <= box[0] and box[2] <= left + self.h - 8, ('封面中心裁切丢字', text, box)
            self.critical.append((text, box))
        self.boxes.append((text, box))
        self.characters[2 if bold else 0].update(text)
        self.d.text((x, y), text, font=face, fill=fill, anchor='lt')
        return box

    def finish(self, path):
        for index, chars in self.characters.items():
            face = TTFont(FONT_PATH, fontNumber=index)
            cmap = face.getBestCmap()
            missing = sorted(c for c in chars if ord(c) not in cmap)
            face.close()
            assert not missing, ('字体缺字', index, missing)
        with path.open('xb') as out:
            self.im.save(out, format='PNG', optimize=True)
        with Image.open(path) as saved:
            assert saved.size == (self.w, self.h)
            saved.verify()
        print(f'PASS {path} | {self.w}x{self.h} | {len(self.boxes)} text boxes | glyphs/bounds/overlap checked | {path.stat().st_size:,} bytes')
        if self.critical:
            print('CENTER CROP PASS:', '; '.join(t for t, _ in self.critical))


def cut(d, x, y, color=PURPLE):
    """原生矢量剪辑切点符号，不使用品牌logo或图片素材。"""
    d.line((x, y - 9, x, y + 9), fill=color, width=3)
    d.polygon(((x - 5, y - 12), (x + 5, y - 12), (x, y - 6)), fill=color)
    d.polygon(((x - 5, y + 12), (x + 5, y + 12), (x, y + 6)), fill=color)


def cover(out):
    c = Canvas(900, 383)
    d = c.d
    # 以剪辑时间尺和斜切色块铺满横幅，不做居中文字卡。
    c.text(27, 25, '一人短剧厂牌', 17, INK, True)
    c.text(732, 27, '106 / 时长复算', 15, MUTED)
    d.line((27, 60, 873, 60), fill=LINE, width=1)
    for x in range(28, 874, 18):
        d.line((x, 60, x, 67 if (x - 28) % 90 else 73), fill=LINE, width=1)

    # 左：一段20分钟，直接切成两段10分钟仍不满足严格上限。
    c.text(30, 102, '一段正片', 18, MUTED)
    c.text(29, 138, '20:00', 47, INK, True)
    for x in (29, 130):
        d.polygon(((x + 10, 211), (x + 91, 211), (x + 81, 261), (x, 261)), fill=CORAL_PALE)
        c.text(x + 14, 229, '10:00', 20, CORAL, True)
    cut(d, 124, 236, CORAL)
    c.text(30, 289, '10分钟整不满足', 19, CORAL, True)
    c.text(30, 323, '严格小于10分钟', 18, MUTED)

    # 中心方形 x258.5—641.5 完整保留核心信息。
    c.text(277, 94, '优酷AI短片', 36, INK, True, critical=True)
    c.text(274, 151, '50%', 94, PURPLE, True, critical=True)
    c.text(501, 213, '分账', 24, PURPLE, True, critical=True)
    c.text(277, 275, '20分钟怎么拆', 33, INK, True, critical=True)
    c.text(279, 330, '11月规则拆解', 18, MUTED, critical=True)

    # 右：一条时长不变的三集示意，色块采用剪辑片段的斜切边。
    c.text(687, 98, '一种时长方案', 18, MUTED)
    for i, y in enumerate((138, 191, 244)):
        color = PURPLE if i % 2 == 0 else BLUE
        d.polygon(((684, y), (859, y), (849, y + 40), (674, y + 40)), fill=color)
        c.text(720, y + 8, '6:40', 23, WHITE, True)
    c.text(689, 309, '至少3集', 23, PURPLE, True)
    d.line((0, 371, 900, 371), fill=PURPLE, width=12)
    for x in range(8, 900, 33):
        d.rectangle((x, 369, x + 13, 374), fill=PAPER)
    c.finish(out / COVER_NAME)
    return c


def segments(c, x, y, w, h, durations, labels, color, label_color, size=28):
    """同一行覆盖完整正片；每段宽度按该段占总时长的比例分配。"""
    assert len(durations) == len(labels)
    gap = 8
    available = w - gap * (len(durations) - 1)
    total = sum(durations)
    cursor = float(x)
    for duration, label in zip(durations, labels):
        width = available * duration / total
        end = cursor + width
        c.d.rectangle((round(cursor), y, round(end), y + h), fill=color)
        c.text(0, y + (h - size) / 2 - 1, label, size, label_color, True,
               center=(cursor + end) / 2, region=(cursor + 3, y + 3, end - 3, y + h - 3))
        cursor = end + gap
    assert abs(cursor - gap - (x + w)) < 0.001


def body(out):
    c = Canvas(1080, 1330)
    d = c.d
    d.rectangle((0, 0, 14, 1330), fill=PURPLE)
    c.text(64, 35, '一人短剧厂牌', 22, INK, True)
    c.text(813, 37, '106 / 拆集复算', 20, MUTED)
    c.text(64, 98, '10分钟整，不满足“小于10分钟”', 46, INK, True)
    c.text(64, 169, '总正片时长不变，重新分配每集时长', 29, MUTED)

    d.rectangle((64, 224, 1016, 295), fill=LILAC)
    c.text(87, 243, '每集严格 < 10分钟；本图示例均须至少拆成2集', 30, PURPLE, True)

    # 20分钟：2×10并不满足严格小于10，至少3集；给出精确总时长方案。
    c.text(64, 335, '20分钟正片', 39, INK, True)
    c.text(826, 341, '至少3集', 33, PURPLE, True)
    c.text(64, 397, '不满足：2 × 10分钟 = 20分钟', 30, CORAL, True)
    segments(c, 64, 447, 952, 64, (600, 600), ('10分钟', '10分钟'), CORAL_PALE, CORAL, 28)
    c.text(64, 541, '一种可行拆法：3 × 6分40秒 = 20分钟', 30, PURPLE, True)
    segments(c, 64, 590, 952, 70, PLAN_20, ('6分40秒',) * 3, PURPLE, WHITE, 30)

    d.line((64, 707, 1016, 707), fill=LINE, width=2)

    # 60分钟：6×10同样失败；6×9+1×6为7集的精确方案。
    c.text(64, 747, '60分钟正片', 39, INK, True)
    c.text(826, 753, '至少7集', 33, BLUE, True)
    c.text(64, 810, '不满足：6 × 10分钟 = 60分钟', 30, CORAL, True)
    segments(c, 64, 859, 952, 64, (600,) * 6, ('10分钟',) * 6, CORAL_PALE, CORAL, 25)
    c.text(64, 953, '一种可行拆法：6 × 9分钟 + 1 × 6分钟 = 60分钟', 28, BLUE, True)
    segments(c, 64, 1002, 952, 70, PLAN_60, ('9分',) * 6 + ('6分',), BLUE, WHITE, 29)

    d.line((64, 1120, 1016, 1120), fill=LINE, width=2)
    c.text(64, 1151, '按公开时长限制复算，不代表获批', 30, INK, True)
    c.text(64, 1200, '图示仅检验时长；不代表审核结果或分账收益。', 26, MUTED)
    c.text(64, 1253, '适用范围：全流程AI、横屏，总正片不超过60分钟。', 24, MUTED)
    c.text(64, 1293, '来源：优酷电影《AI电影短片分账规则》官方完整规则图（2026年11月）', 21, MUTED)
    c.finish(out / BODY_NAME)


def verify_math():
    for total, bad, good, minimum in (
        (1200, (600, 600), PLAN_20, 3),
        (3600, (600,) * 6, PLAN_60, 7),
    ):
        assert sum(bad) == sum(good) == total
        assert not all(0 < seconds < MAX_SECONDS for seconds in bad)
        assert all(0 < seconds < MAX_SECONDS for seconds in good)
        assert total // MAX_SECONDS + 1 == minimum == len(good)
        assert len(good) >= 2
    print('MATH PASS: 20min=3×400s; 60min=6×540s+360s; every valid episode <600s; minimum counts=3/7')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preview-dir', type=Path)
    args = parser.parse_args()
    out = args.preview_dir or HERE
    out.mkdir(parents=True, exist_ok=True)
    assert all(not (out / n).exists() for n in (COVER_NAME, BODY_NAME)), '目标已存在；禁止覆盖，请用新的临时目录预览'
    verify_math()
    c = cover(out)
    body(out)
    if args.preview_dir:
        left = (900 - 383) // 2
        crop = c.im.crop((left, 0, left + 383, 383))
        crop.save(out / '106_封面中心方形_校验.png')
        print(f'CROP: {out / "106_封面中心方形_校验.png"}')


if __name__ == '__main__':
    main()
