# -*- coding: utf-8 -*-
"""104 修订视觉：本地 Pillow 绘制，零 API、零扣费；不覆盖既有素材。"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
BODY = HERE / '104_图1_成本口径_v2_1080.png'
COVER = HERE / '封面_104_v2_900x383.png'
FONT_PATH = '/System/Library/Fonts/Hiragino Sans GB.ttc'
NAVY = '#142B3D'
BLUE = '#315F7C'
PAPER = '#F5F2EA'
WHITE = '#FFFEFA'
ORANGE = '#F0A05B'
RUST = '#9C4B18'
MUTED = '#60717A'
LINE = '#CCD2CF'
PALE = '#E2E7E5'


@lru_cache(None)
def font(size, bold=False):
    return ImageFont.truetype(FONT_PATH, size, index=2 if bold else 0)


class Canvas:
    def __init__(self, w, h, color):
        self.im = Image.new('RGB', (w, h), color)
        self.d = ImageDraw.Draw(self.im)
        self.w, self.h = w, h
        self.boxes = []
        self.chars = {0: set(), 2: set()}

    def text(self, x, y, value, size, fill=NAVY, bold=False, center=None, critical=False):
        ff = font(size, bold)
        if center is not None:
            x = center - self.d.textlength(value, font=ff) / 2
        box = self.d.textbbox((x, y), value, font=ff, anchor='lt')
        assert 0 <= box[0] < box[2] <= self.w, ('横向越界', value, box)
        assert 0 <= box[1] < box[3] <= self.h, ('纵向越界', value, box)
        if critical:
            safe_l, safe_r = (self.w-self.h)/2, (self.w+self.h)/2
            assert safe_l+12 <= box[0] and box[2] <= safe_r-12, ('中心方形裁切', value, box)
        for other, previous in self.boxes:
            overlap = min(box[2], previous[2]) > max(box[0], previous[0]) and min(box[3], previous[3]) > max(box[1], previous[1])
            assert not overlap, ('文字重叠', value, other, box, previous)
        self.boxes.append((value, box))
        self.chars[2 if bold else 0].update(value)
        self.d.text((x, y), value, font=ff, fill=fill, anchor='lt')
        return box

    def finish(self, path):
        for index, chars in self.chars.items():
            face = TTFont(FONT_PATH, fontNumber=index)
            cmap = face.getBestCmap()
            missing = sorted(c for c in chars if ord(c) not in cmap)
            face.close()
            assert not missing, ('缺失字形', index, missing)
        self.im.save(path, optimize=True)
        with Image.open(path) as saved:
            assert saved.size == (self.w, self.h)
            saved.verify()
        print(f'PASS {path}: {self.w}x{self.h}, {path.stat().st_size:,} bytes, {len(self.boxes)} text boxes')


def arrow(d, x, y, size=22, fill=NAVY):
    d.line((x-size, y, x+size, y), fill=fill, width=3)
    d.line((x+size-10, y-10, x+size, y, x+size-10, y+10), fill=fill, width=3)


def body():
    c = Canvas(1080, 1500, PAPER)
    d = c.d
    d.rectangle((0, 0, 1080, 230), fill=NAVY)
    d.rectangle((64, 71, 110, 76), fill=ORANGE)
    c.text(64, 30, '一人短剧厂牌', 22, PAPER, True)
    c.text(812, 30, '104 / 文档算例', 20, '#BBC7CA')
    c.text(64, 99, '指标低了，积分没少花', 54, WHITE, True)
    c.text(64, 174, '同样1万积分，计入外部通过视频后会怎样？', 29, '#D4DDDE')

    # 账页：两种口径的分子保持不变，而非宣称平台降低了积分扣费。
    d.rectangle((64, 270, 1016, 451), fill=WHITE, outline=LINE, width=2)
    d.rectangle((64, 270, 73, 451), fill=ORANGE)
    d.line((551, 292, 551, 427), fill=LINE, width=2)
    d.polygon(((973, 270), (1016, 313), (973, 313)), fill=PALE)
    c.text(96, 294, '固定的分子 / 视频生成积分', 24, MUTED, True)
    c.text(96, 347, '10,000', 76, NAVY, True)
    c.text(414, 391, '积分', 25, MUTED)
    c.text(589, 323, '两种口径，分子相同', 30, NAVY, True)
    c.text(589, 383, '视频积分支出保持不变', 24, MUTED)

    # 时间条共用同一比例尺，新增60秒仅位于分母。
    c.text(64, 496, '变化的分母 / 审阅通过的视频时长', 29, NAVY, True)
    start, end = 306, 1016
    base_end = start + (end-start)*312/372
    c.text(64, 576, '只计项目内', 25, MUTED)
    d.rectangle((start, 557, end, 616), fill=PALE)
    d.rectangle((start, 557, base_end, 616), fill=BLUE)
    c.text(0, 573, '312秒', 30, WHITE, True, center=(start+base_end)/2)
    c.text(64, 666, '再计入外部', 25, MUTED)
    d.rectangle((start, 647, base_end, 706), fill=BLUE)
    d.rectangle((base_end, 647, end, 706), fill=ORANGE)
    c.text(0, 663, '312秒', 30, WHITE, True, center=(start+base_end)/2)
    c.text(0, 665, '+60秒', 25, NAVY, True, center=(base_end+end)/2)
    d.line((base_end, 715, base_end, 728, end, 728, end, 715), fill=RUST, width=2)
    c.text(562, 746, '60秒 = 外部上传且通过审阅的视频', 23, RUST)

    # 真正的分数算式，而非装饰性大数字。
    for mid, label, secs, result, col in (
        (279, '仅计项目内通过视频', '312秒', '32.1', NAVY),
        (801, '再计入外部通过视频', '372秒', '26.9', RUST),
    ):
        c.text(0, 814, label, 25, MUTED, center=mid)
        c.text(0, 868, '10,000', 52, NAVY, True, center=mid)
        d.line((mid-169, 937, mid+169, 937), fill=NAVY, width=3)
        c.text(0, 958, secs, 42, NAVY, True, center=mid)
        c.text(0, 1030, result, 74, col, True, center=mid)
        c.text(0, 1120, '积分 / 通过秒', 24, MUTED, center=mid)
    arrow(d, 540, 1065, 27, MUTED)

    d.rectangle((64, 1180, 1016, 1305), fill=NAVY)
    c.text(93, 1209, '约 -16%', 55, ORANGE, True)
    c.text(432, 1206, '指标变化来自分母增加', 28, WHITE, True)
    c.text(432, 1255, '不代表实际节省，也不是生成单价下降', 23, '#D4DDDE')

    c.text(64, 1334, '外部费用通常未计入项目成本，需要另记账。', 27, NAVY, True)
    c.text(64, 1388, '按官方文档样例作假设对照 · 非实测 · 积分未折算人民币', 23, MUTED)
    c.text(64, 1433, '来源：纳逗Pro《制片管理与数据统计》｜通过素材时长不等于成片交付时长', 20, MUTED)
    c.finish(BODY)


def cover():
    c = Canvas(900, 383, NAVY)
    d = c.d
    # 全幅版面：左账页、中心标题、右时长条。没有居中圆角文字卡。
    d.line((32, 54, 868, 54), fill='#3B4E59', width=1)
    c.text(32, 23, '一人短剧厂牌', 16, '#D2D9D6', True)
    c.text(747, 24, '104 / 成本口径', 14, '#9FADB2')

    # 左侧账页，固定数额的含义可独立读出。
    d.polygon(((32, 95), (205, 95), (230, 120), (230, 307), (32, 307)), fill=PAPER)
    d.polygon(((205, 95), (230, 120), (205, 120)), fill='#C9D0CA')
    d.rectangle((32, 95, 38, 307), fill=ORANGE)
    c.text(50, 121, '视频积分', 20, MUTED, True)
    c.text(48, 164, '10,000', 44, NAVY, True)
    d.line((50, 224, 211, 224), fill=LINE, width=1)
    c.text(50, 244, '支出保持不变', 21, NAVY, True)
    for yy, length in ((280, 80), (290, 125)):
        d.line((50, yy, 50+length, yy), fill=LINE, width=2)

    # 三行核心完整保留在居中的383×383方形裁切内。
    c.text(284, 91, '纳逗Pro', 30, PAPER, True, critical=True)
    d.rectangle((284, 135, 328, 139), fill=ORANGE)
    c.text(282, 164, '指标降了', 54, WHITE, True, critical=True)
    c.text(282, 239, '积分没少花', 54, ORANGE, True, critical=True)
    c.text(284, 323, '官方文档假设算例 · 非实测', 17, '#C7D2D3', critical=True)

    # 右侧同尺度时长条，橙色仅标新增的外部通过时长。
    c.text(678, 99, '审阅通过时长', 17, '#BCC9CC', True)
    c.text(678, 137, '312秒', 34, PAPER, True)
    d.rectangle((680, 196, 837, 209), fill=BLUE)
    d.rectangle((837, 196, 868, 209), fill=ORANGE)
    d.line((837, 215, 837, 226, 868, 226, 868, 215), fill=ORANGE, width=2)
    c.text(779, 237, '+60秒外部', 17, ORANGE, True)
    c.text(678, 275, '372秒', 34, PAPER, True)
    c.text(678, 328, '外部费用另记', 17, '#BCC9CC')
    c.finish(COVER)


if __name__ == '__main__':
    # 仅这两个新图可写入；本脚本不会覆盖任何旧封面/正文/元数据。
    assert not BODY.exists() and not COVER.exists(), '新版本文件已存在，请审查后另取版本号，禁止覆盖'
    body()
    cover()
