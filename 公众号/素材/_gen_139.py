from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
SCALE = 2
NAVY = "#102A31"
DEEP = "#14383F"
TEAL = "#167C80"
CYAN = "#65D1C5"
CORAL = "#E67B5A"
WHITE = "#FFFFFF"
PAPER = "#F2F4F1"
MUTED = "#5F7072"
PALE = "#C7D7D3"
LINE = "#D9E4E0"
GOLD = "#E9B44C"
SOFT = "#BEE6DF"
COVER = "封面_139_20261126_900x383.png"
FIGURE = "图1_139_四个数字_1080x1120.png"


class Panel:
    def __init__(self, size, background):
        self.size = size
        self.image = Image.new("RGB", tuple(v * SCALE for v in size), background)
        self.draw = ImageDraw.Draw(self.image)

    def box(self, values):
        return tuple(round(v * SCALE) for v in values)

    def points(self, values):
        return [tuple(round(v * SCALE) for v in point) for point in values]

    def rounded(self, values, radius, fill=None, outline=None, width=1):
        self.draw.rounded_rectangle(self.box(values), radius=radius * SCALE, fill=fill, outline=outline, width=width * SCALE)

    def ellipse(self, values, fill=None, outline=None, width=1):
        self.draw.ellipse(self.box(values), fill=fill, outline=outline, width=width * SCALE)

    def line(self, values, color, width=2):
        self.draw.line(self.points(values), fill=color, width=width * SCALE, joint="curve")

    def polygon(self, values, color):
        self.draw.polygon(self.points(values), fill=color)

    def text(self, x, y, value, size, color, bold=False, anchor="lt", box=None):
        font = ImageFont.truetype(FONT, size * SCALE, index=2 if bold else 0)
        bounds = self.draw.textbbox((x * SCALE, y * SCALE), value, font=font, anchor=anchor)
        safe = self.box(box or (0, 0, *self.size))
        assert safe[0] <= bounds[0] < bounds[2] <= safe[2] and safe[1] <= bounds[1] < bounds[3] <= safe[3], (value, bounds, safe)
        self.draw.text((x * SCALE, y * SCALE), value, font=font, fill=color, anchor=anchor)

    def width(self, value, size, bold=False):
        font = ImageFont.truetype(FONT, size * SCALE, index=2 if bold else 0)
        return self.draw.textlength(value, font=font) / SCALE

    def chip(self, x, y, value, size=13, fill=WHITE, outline=LINE, fg=NAVY, bold=True, height=30, pad=10):
        w = self.width(value, size, bold) + pad * 2
        self.rounded((x, y, x + w, y + height), height / 2, fill=fill, outline=outline, width=2)
        self.text(x + w / 2, y + height / 2, value, size, fg, bold, anchor="mm")
        return w

    def save(self, path):
        with path.open("xb") as stream:
            self.image.resize(self.size, Image.Resampling.LANCZOS).save(stream, "PNG", optimize=True)


def cover(path):
    p = Panel((900, 383), NAVY)
    p.polygon([(520, 0), (900, 0), (900, 383), (482, 383)], DEEP)
    p.text(54, 30, "美国短剧 App · 数据拆解", 16, CYAN, True)
    p.text(50, 64, "下载 +35%", 52, WHITE, True, box=(44, 54, 470, 124))
    p.text(52, 128, "内购 -28%", 44, CORAL, True, box=(44, 120, 470, 182))
    p.line([(54, 198), (466, 198)], TEAL, 2)
    p.text(54, 218, "68% 的下载来自付费渠道", 17, PALE, box=(48, 210, 476, 242))
    p.text(54, 248, "季度流失率近 60%", 17, PALE, box=(48, 240, 476, 272))
    p.text(54, 278, "净内购连降三季，不等于总收入下降", 14, CYAN, True, box=(48, 270, 476, 300))
    p.text(54, 340, "一人短剧厂牌 · 数据拆解", 13, PALE, box=(48, 332, 400, 360))

    p.text(556, 56, "68%", 84, CYAN, True, box=(548, 44, 800, 158))
    p.text(560, 160, "下载来自付费渠道", 24, WHITE, True, box=(554, 152, 872, 194))
    p.text(560, 196, "Sensor Tower 估算", 14, PALE, box=(554, 188, 872, 216))
    p.text(560, 220, "8款美国短剧App · 2026年年初至今", 13, PALE, box=(554, 212, 872, 240))
    p.text(560, 258, "下载 +35% · 月活 +93%", 15, CYAN, True, box=(554, 250, 872, 280))
    p.text(560, 286, "净内购 -7% / -33% / -28%", 14, CORAL, True, box=(554, 278, 872, 308))
    p.text(560, 316, "季度流失率近 60%", 14, PALE, box=(554, 308, 872, 338))
    p.text(560, 344, "广告支出 Q2 +42% / Q3 +61%", 12, PALE, box=(554, 336, 872, 364))
    p.save(path)


def figure(path):
    p = Panel((1080, 1120), PAPER)
    p.text(64, 38, "下载在涨，内购在降", 40, NAVY, True, box=(58, 26, 1018, 96))
    p.text(66, 100, "Sensor Tower 估算：8款美国短剧App，2026年年初至今", 19, MUTED, box=(60, 92, 1018, 136))

    p.rounded((64, 150, 516, 330), 22, fill=WHITE, outline=LINE, width=2)
    p.text(92, 170, "下载 +35%", 38, TEAL, True, box=(86, 160, 500, 220))
    p.text(92, 228, "2026年年初至今同比", 15, MUTED, box=(86, 220, 500, 248))
    p.text(92, 258, "2024 +324% / 2025 +119%", 14, NAVY, box=(86, 250, 500, 278))
    p.text(92, 286, "Q3 8款合计 +149%", 14, CORAL, True, box=(86, 278, 500, 306))

    p.rounded((564, 150, 1016, 330), 22, fill=WHITE, outline=LINE, width=2)
    p.text(592, 170, "月活 +93%", 38, TEAL, True, box=(586, 160, 1000, 220))
    p.text(592, 228, "2026年年初至今同比", 15, MUTED, box=(586, 220, 1000, 248))
    p.text(592, 258, "Q2 +48% → Q3 +123%", 14, NAVY, box=(586, 250, 1000, 278))
    p.text(592, 286, "增速在加快，Q4尚未结束", 14, MUTED, box=(586, 278, 1000, 306))

    p.rounded((64, 350, 516, 530), 22, fill=WHITE, outline=LINE, width=2)
    p.text(92, 368, "68%", 54, CORAL, True, box=(86, 358, 300, 430))
    p.text(92, 430, "下载来自付费渠道", 16, NAVY, True, box=(86, 422, 500, 452))
    p.text(92, 458, "2024 77% / 2025 67%", 14, MUTED, box=(86, 450, 500, 478))
    p.text(92, 486, "Q2广告支出 +42% / Q3 +61%", 13, MUTED, box=(86, 478, 500, 506))

    p.rounded((564, 350, 1016, 530), 22, fill=WHITE, outline=LINE, width=2)
    p.text(592, 368, "近60%", 54, CORAL, True, box=(586, 358, 900, 430))
    p.text(592, 430, "季度流失率", 16, NAVY, True, box=(586, 422, 1000, 452))
    p.text(592, 458, "PineDrama 66% / GoodShort 64%", 13, MUTED, box=(586, 450, 1000, 478))
    p.text(592, 486, "ReelShort 63% / NetShort 50%", 13, MUTED, box=(586, 478, 1000, 506))

    p.rounded((64, 550, 1016, 790), 22, fill=WHITE, outline=LINE, width=2)
    p.text(92, 568, "净内购收入同比：连续三季下降", 20, NAVY, True, box=(86, 560, 700, 598))
    p.text(92, 594, "8款App，2026年Q1—Q3；条形越长，跌幅越大", 13, MUTED, box=(86, 586, 640, 612))
    p.line([(140, 618), (140, 776)], LINE, 2)
    for y, q, val, w in [(628, "Q1", "-7%", 56), (682, "Q2", "-33%", 264), (736, "Q3", "-28%", 224)]:
        p.text(96, y + 2, q, 15, MUTED, True, box=(90, y - 2, 132, y + 30))
        p.rounded((140, y, 140 + w, y + 26), 6, fill=CORAL)
        p.text(152 + w, y + 13, val, 17, CORAL, True, anchor="lm", box=(140 + w + 6, y - 6, 660, y + 34))
    p.line([(700, 586), (700, 770)], LINE, 2)
    p.text(724, 586, "净内购 = 应用商店内购买；", 14, NAVY, box=(718, 578, 1000, 606))
    p.text(724, 610, "官网购买不在统计内。", 14, NAVY, box=(718, 602, 1000, 630))
    p.text(724, 640, "不能推出总收入下降", 15, CORAL, True, box=(718, 632, 1000, 662))
    p.text(724, 670, "报告未给官网购买规模，", 13, MUTED, box=(718, 662, 1000, 690))
    p.text(724, 692, "两种解释各占多少未知。", 13, MUTED, box=(718, 684, 1000, 712))

    p.rounded((64, 810, 1016, 990), 20, fill=NAVY)
    p.text(96, 828, "不能这么读", 18, CYAN, True, box=(90, 820, 300, 856))
    p.text(96, 860, "8款App ≠ 整个美国市场；8款Q3下载+149%，更宽市场+115%", 14, WHITE, box=(90, 852, 990, 880))
    p.text(96, 888, "净内购 ≠ 总收入；报告也未给8款App的绝对下载量、用户数与广告金额", 14, WHITE, box=(90, 880, 990, 908))
    p.text(96, 916, "AI只被提及，没有内容占比或贡献数据，不能把增长归因于AI", 14, WHITE, box=(90, 908, 990, 936))
    p.text(96, 944, "报告正文与图表在Q4月活由谁带动上不一致；2026年三类用户占比相加96%", 13, PALE, box=(90, 936, 990, 964))
    p.text(96, 968, "数据只适合做方向性趋势分析", 13, CYAN, box=(90, 960, 990, 986))

    p.text(66, 1044, "本图为编辑示意。数据来源：Sensor Tower 2026-11-23 报告，经 PPC Land、Net Influencer 转述；均为估算值。", 12, MUTED, box=(60, 1036, 1024, 1066))
    p.save(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    output = parser.parse_args().output.resolve()
    assert output.is_dir(), output
    targets = [output / COVER, output / FIGURE]
    assert all(not path.exists() for path in targets), "Refusing to overwrite images"
    cover(targets[0])
    figure(targets[1])
    for path, expected in zip(targets, [(900, 383), (1080, 1120)]):
        with Image.open(path) as image:
            image.load()
            assert image.size == expected
            assert image.mode == "RGB"
        print(path.name, expected, path.stat().st_size)


if __name__ == "__main__":
    main()
