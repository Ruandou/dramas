# -*- coding: utf-8 -*-
"""105 采购案例图：原生 Pillow，零 API 扣费；只新建，不覆盖既有文件。

核读来源：湖北省演艺集团官网 news-details/804.html、805.html。
默认写本目录；--preview-dir 可先将同名图输出到新的临时预览目录。
"""
from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_HALF_UP
from functools import lru_cache
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONT_PATH = '/System/Library/Fonts/Hiragino Sans GB.ttc'
PAPER = '#F4F0E6'
WHITE = '#FFFDF8'
GREEN = '#153E33'
GREEN_2 = '#41695A'
PALE = '#DFE6DC'
RED = '#AE3E30'
INK = '#203B32'
MUTED = '#617068'
LINE = '#C9CFC3'
LIMIT = Decimal('200000')
DEAL = Decimal('158500')
MINUTES = Decimal('150')
DIFF = LIMIT - DEAL
PCT = DIFF / LIMIT * 100
PER_MIN = (DEAL / MINUTES).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
DELIVERY_NAME = '105_图2_交付范围_v2_1080.png'


@lru_cache(None)
def font(size, bold=False):
    return ImageFont.truetype(FONT_PATH, size, index=2 if bold else 0)


class Canvas:
    def __init__(self, w, h, background=PAPER):
        self.im = Image.new('RGB', (w, h), background)
        self.d = ImageDraw.Draw(self.im)
        self.w, self.h = w, h
        self.boxes = []
        self.characters = {0: set(), 2: set()}
        self.critical_boxes = []

    def text(self, x, y, text, size, fill=INK, bold=False, region=None, critical=False):
        face = font(size, bold)
        box = self.d.textbbox((x, y), text, font=face, anchor='lt')
        bounds = region or (0, 0, self.w, self.h)
        assert bounds[0] <= box[0] < box[2] <= bounds[2], ('文字横向越界', text, box, bounds)
        assert bounds[1] <= box[1] < box[3] <= bounds[3], ('文字纵向越界', text, box, bounds)
        for previous_text, previous in self.boxes:
            overlap = min(box[2], previous[2]) > max(box[0], previous[0]) and min(box[3], previous[3]) > max(box[1], previous[1])
            assert not overlap, ('文字重叠', text, previous_text, box, previous)
        if critical:
            left = (self.w - self.h) / 2
            right = left + self.h
            assert left + 8 <= box[0] and box[2] <= right - 8, ('封面方形裁切丢字', text, box)
            self.critical_boxes.append((text, box))
        self.characters[2 if bold else 0].update(text)
        self.boxes.append((text, box))
        self.d.text((x, y), text, font=face, fill=fill, anchor='lt')
        return box

    def finish(self, path):
        for index, characters in self.characters.items():
            face = TTFont(FONT_PATH, fontNumber=index)
            cmap = face.getBestCmap()
            missing = sorted(c for c in characters if ord(c) not in cmap)
            face.close()
            assert not missing, ('字体缺字', index, missing)
        # xb 只允许新建，避免误覆盖任何既有素材。
        with path.open('xb') as out:
            self.im.save(out, format='PNG', optimize=True)
        with Image.open(path) as saved:
            assert saved.size == (self.w, self.h)
            saved.verify()
        print(f'PASS {path} | {self.w}x{self.h} | {len(self.boxes)} text boxes | glyphs/bounds/overlap checked | {path.stat().st_size:,} bytes')
        if self.critical_boxes:
            print('CENTER CROP PASS:', '; '.join(t for t, _ in self.critical_boxes))


def checkmark(d, x, y, size=12, fill=RED):
    d.line((x, y + size // 2, x + size // 3, y + size, x + size, y), fill=fill, width=3)


def cover(out):
    c = Canvas(900, 383)
    d = c.d
    # 左侧档案脊、全幅纸页、右侧交付流程，避免居中文字卡。
    d.rectangle((0, 0, 230, 383), fill=GREEN)
    d.rectangle((230, 0, 900, 6), fill=GREEN)
    c.text(25, 25, '一人短剧厂牌', 17, PAPER, True)
    c.text(708, 25, '105 / 采购拆解', 16, GREEN)
    d.line((271, 53, 873, 53), fill=LINE, width=1)

    # 左侧采购文件，作为横幅扩展内容。
    d.rectangle((29, 99, 194, 297), fill='#0D2C24')
    d.polygon(((39, 88), (176, 88), (205, 117), (205, 287), (39, 287)), fill=PAPER)
    d.polygon(((176, 88), (205, 117), (176, 117)), fill='#C5CDBF')
    c.text(55, 116, '采购文件', 22, GREEN, True)
    c.text(55, 158, '全流程服务', 19, MUTED)
    for yy, length in ((201, 113), (218, 91), (235, 118), (252, 66)):
        d.line((55, yy, 55 + length, yy), fill=LINE, width=3)
    c.text(29, 326, '公告＋成交结果', 18, PAPER)

    # 核心内容左对齐，均位于 x258.5—641.5 的中心方形。
    d.rectangle((278, 76, 437, 102), fill=RED)
    c.text(286, 80, '9月已成交案例', 18, WHITE, True, critical=True)
    c.text(275, 119, '《黑暗传》', 35, GREEN, True, critical=True)
    c.text(275, 172, '15.85万', 73, GREEN, True, critical=True)
    d.line((279, 258, 616, 258), fill=RED, width=4)
    c.text(278, 276, 'AI短剧采购单', 31, GREEN, True, critical=True)
    c.text(278, 326, '甲方买什么？', 26, RED, True, critical=True)

    # 右侧为交付流程，不承诺已完成交付。
    c.text(703, 83, '一份整包交付', 20, GREEN, True)
    d.line((692, 135, 692, 285), fill=LINE, width=2)
    for yy, label in ((129, '剧本改编'), (179, '成片制作'), (229, '源文件'), (279, '实操培训')):
        d.ellipse((686, yy + 4, 698, yy + 16), fill=RED)
        c.text(717, yy, label, 21, GREEN)
    c.text(703, 337, '含税成交金额', 18, MUTED)
    c.finish(out / '封面_105_20261115_900x383.png')
    return c


def price(out):
    c = Canvas(1080, 1120)
    d = c.d
    d.rectangle((0, 0, 1080, 218), fill=GREEN)
    c.text(64, 32, '一人短剧厂牌', 22, PAPER, True)
    c.text(804, 34, '105 / 价格与日期', 20, '#CEDAD1')
    c.text(64, 91, '20万 → 15.85万', 62, WHITE, True)
    c.text(64, 176, '《黑暗传》｜公告限价与含税成交额', 28, '#DAE1D6')

    c.text(64, 258, '同一采购，两种金额口径', 31, GREEN, True)
    c.text(833, 266, '2026年9月', 23, RED, True)
    x0, xmax = 300, 1016
    usable = xmax - x0
    bars = ((350, 200000, GREEN_2), (526, 158500, GREEN))
    for y, value, color in bars:
        d.rectangle((x0, y, xmax, y + 76), fill=PALE)
        d.rectangle((x0, y, x0 + usable * value / 200000, y + 76), fill=color)
    c.text(64, 348, '09.15', 42, GREEN, True)
    c.text(64, 407, '询比公告', 25, MUTED)
    c.text(300, 310, '最高限价 · 公告未明税口径', 25, MUTED)
    c.text(324, 367, '200,000元', 45, WHITE, True)
    c.text(64, 525, '09.29', 42, GREEN, True)
    c.text(64, 583, '成交公告', 25, MUTED)
    c.text(300, 486, '含税成交金额', 25, MUTED)
    c.text(324, 544, '158,500元', 45, WHITE, True)

    # 共用比例尺，差额只描述两份公告中的数值差。
    deal_end = x0 + usable * float(DEAL / LIMIT)
    d.line((deal_end, 616, deal_end, 633, xmax, 633, xmax, 616), fill=RED, width=2)
    d.line((64, 677, 1016, 677), fill=LINE, width=2)
    c.text(64, 708, '41,500元', 65, RED, True)
    c.text(575, 720, '20.75%', 57, GREEN, True)
    c.text(67, 792, '公告金额之差', 27, MUTED)
    c.text(578, 792, '差额 ÷ 最高限价', 27, MUTED)
    c.text(64, 850, '200,000 - 158,500 = 41,500', 29, GREEN)

    d.rectangle((64, 916, 1016, 1015), fill=WHITE)
    d.rectangle((64, 916, 71, 1015), fill=RED)
    c.text(88, 934, '只比较公告限价与含税成交额', 28, GREEN, True)
    c.text(88, 978, '不代表利润、制作成本或实际节省', 25, RED)
    c.text(64, 1043, '来源：湖北省演艺集团官网｜804询比公告（9-15）、805成交公告（9-29）', 21, MUTED)
    c.text(64, 1080, '9月已成交旧案例｜成交公告不证明项目已完成或已回款', 22, MUTED)
    c.finish(out / '105_图1_价格与日期_1080.png')


def delivery(out):
    c = Canvas(1080, 1360)
    d = c.d
    d.rectangle((0, 0, 1080, 205), fill=GREEN)
    c.text(64, 32, '一人短剧厂牌', 22, PAPER, True)
    c.text(821, 34, '105 / 整包摊算', 20, '#CEDAD1')
    c.text(64, 88, '这笔钱，摊到每分钟是多少', 49, WHITE, True)
    c.text(64, 160, '《黑暗传》｜含税成交服务包 ÷ 约定成片时长', 27, '#DAE1D6')

    # 分数是数据图主体；下方范围不按面积或颜色虚构费用占比。
    c.text(64, 249, '分子：含税整包成交金额', 28, MUTED)
    c.text(64, 296, '158,500元', 81, GREEN, True)
    d.line((64, 396, 1016, 396), fill=GREEN, width=3)
    c.text(64, 427, '150分钟', 65, GREEN, True)
    c.text(493, 452, '分母：采购约定成片总时长', 28, MUTED)

    d.rectangle((64, 538, 1016, 684), fill=GREEN)
    c.text(87, 567, '≈1,056.67', 83, WHITE, True)
    c.text(624, 610, '元 / 成片分钟', 34, PAPER, True)

    c.text(64, 730, '分子里买的是一整包服务', 32, GREEN, True)
    d.line((64, 784, 1016, 784), fill=LINE, width=2)
    # 两列交付组成只表明包含关系；未公开分项报价，不画金额占比。
    for x, y, title in (
        (64, 810, '剧本改编'),
        (555, 810, '全流程成片制作'),
        (64, 890, '源文件、素材、字幕'),
        (555, 890, '一对一培训及课件'),
        (64, 970, '多轮修改'),
    ):
        d.rectangle((x + 5, y + 7, x + 19, y + 21), fill=RED)
        c.text(x + 53, y - 2, title, 28, GREEN, True)
    c.text(555, 971, '修改轮数未公布', 25, MUTED)
    d.line((64, 1033, 1016, 1033), fill=LINE, width=2)

    c.text(64, 1063, '含税整包按约定时长摊算', 32, RED, True)
    c.text(64, 1114, '不能当纯生成单价，也不能反推工具费或利润', 27, GREEN)
    c.text(64, 1178, '总价包干｜项目成果知识产权归采购人', 27, GREEN, True)
    c.text(64, 1226, '2026.12.31前终审交付要求 ≠ 已经完成交付', 26, GREEN)
    c.text(64, 1291, '来源：湖北省演艺集团官网 804询比公告、805成交公告（2026年9月）', 22, MUTED)
    c.text(64, 1329, '复算：158,500 ÷ 150 ≈ 1,056.67｜未公开分项费用，不拆分假设成本', 21, MUTED)
    c.finish(out / DELIVERY_NAME)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preview-dir', type=Path)
    parser.add_argument('--only', choices=('all', 'cover', 'price', 'delivery'), default='all')
    args = parser.parse_args()
    out = args.preview_dir or HERE
    out.mkdir(parents=True, exist_ok=True)
    targets = {
        'cover': ('封面_105_20261115_900x383.png', cover),
        'price': ('105_图1_价格与日期_1080.png', price),
        'delivery': (DELIVERY_NAME, delivery),
    }
    selected = targets if args.only == 'all' else {args.only: targets[args.only]}
    names = tuple(name for name, _ in selected.values())
    assert all(not (out / n).exists() for n in names), '目标已存在，禁止覆盖；预览请另取新的临时目录'
    assert DIFF == Decimal('41500') and PCT == Decimal('20.7500') and PER_MIN == Decimal('1056.67')
    print(f'MATH PASS: {LIMIT}-{DEAL}={DIFF}; {DIFF}/{LIMIT}={PCT}%; {DEAL}/{MINUTES}≈{PER_MIN}')
    c = None
    for key, (_, draw) in selected.items():
        result = draw(out)
        if key == 'cover':
            c = result
    if args.preview_dir and c is not None:
        left = (900 - 383) // 2
        crop = c.im.crop((left, 0, left + 383, 383))
        crop.save(out / '105_封面中心方形_校验.png')
        print(f'CROP: {out / "105_封面中心方形_校验.png"}')


if __name__ == '__main__':
    main()
