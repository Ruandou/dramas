from __future__ import annotations

import argparse
import math
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
GREEN = "#2F8F6B"
COVER = "封面_136_20261126_900x383.png"
FIGURE = "图1_136_两道门_1080x1120.png"


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

    def arrow(self, start, end, color, width=3):
        self.line([start, end], color, width)
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        length = 11
        spread = 0.55
        p1 = (end[0] - length * math.cos(angle - spread), end[1] - length * math.sin(angle - spread))
        p2 = (end[0] - length * math.cos(angle + spread), end[1] - length * math.sin(angle + spread))
        self.polygon([end, p1, p2], color)

    def save(self, path):
        with path.open("xb") as stream:
            self.image.resize(self.size, Image.Resampling.LANCZOS).save(stream, "PNG", optimize=True)


def gate(p, x, y, w, h, color):
    post = max(6, w * 0.18)
    beam = max(8, h * 0.12)
    p.rounded((x, y, x + post, y + h), 3, fill=color)
    p.rounded((x + w - post, y, x + w, y + h), 3, fill=color)
    p.rounded((x, y, x + w, y + beam), 3, fill=color)


def avatar(p, cx, cy, scale=1.0, color=CYAN, fill=DEEP):
    p.ellipse((cx - 12 * scale, cy - 30 * scale, cx + 12 * scale, cy - 6 * scale), fill=fill, outline=color, width=2)
    p.rounded((cx - 20 * scale, cy - 2 * scale, cx + 20 * scale, cy + 28 * scale), 10, fill=fill, outline=color, width=2)


def lens(p, cx, cy, r, ring=CORAL, hole=WHITE):
    p.ellipse((cx - r, cy - r, cx + r, cy + r), fill=hole, outline=ring, width=3)
    p.ellipse((cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55), outline=ring, width=2)


def check(p, cx, cy, r, color=GREEN):
    p.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
    p.line([(cx - r * 0.48, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.4), (cx + r * 0.52, cy - r * 0.34)], WHITE, 3)


def chip(p, x, y, value, size=15, fill=WHITE, outline=LINE, fg=NAVY, bold=False, height=32, pad=12):
    w = p.width(value, size, bold) + pad * 2
    p.rounded((x, y, x + w, y + height), height / 2, fill=fill, outline=outline, width=2)
    p.text(x + w / 2, y + height / 2, value, size, fg, bold, anchor="mm")
    return w


def cover(path):
    p = Panel((900, 383), NAVY)
    p.polygon([(536, 0), (900, 0), (900, 383), (498, 383)], DEEP)
    p.text(54, 34, "AI 代言 · 罚单拆解", 18, CYAN, True)
    p.text(52, 78, "方桃子美瞳广告", 36, WHITE, True, box=(40, 62, 520, 122))
    p.text(52, 124, "被罚6.8万", 46, WHITE, True, box=(40, 112, 520, 180))
    p.text(55, 190, "AI代言先看品类", 30, CYAN, True, box=(40, 182, 520, 228))
    p.text(55, 242, "品类门 · 话术门", 19, PALE, box=(40, 236, 520, 266))
    p.line([(55, 286), (470, 286)], TEAL, 2)
    p.text(55, 318, "一人短剧厂牌 · 合规观察", 16, PALE, box=(40, 310, 520, 340))

    p.line([(566, 272), (866, 272)], TEAL, 4)
    avatar(p, 600, 232, 1.0)
    p.rounded((610, 168, 640, 190), 8, fill=CORAL)
    p.text(625, 179, "AI", 12, WHITE, True, anchor="mm")

    gate(p, 678, 128, 30, 144, CYAN)
    p.text(693, 106, "品类", 17, CYAN, True, anchor="ms", box=(660, 86, 726, 124))
    p.ellipse((686, 148, 700, 162), fill=CORAL)
    p.text(693, 155, "!", 10, WHITE, True, anchor="mm")

    gate(p, 768, 128, 30, 144, CYAN)
    p.text(783, 106, "话术", 17, CYAN, True, anchor="ms", box=(750, 86, 816, 124))
    p.ellipse((776, 148, 790, 162), fill=CORAL)
    p.text(783, 155, "!", 10, WHITE, True, anchor="mm")

    p.rounded((818, 196, 876, 272), 10, fill=WHITE, outline=CORAL, width=3)
    lens(p, 847, 224, 13, ring=CORAL, hole=WHITE)
    p.line([(826, 204), (868, 264)], CORAL, 4)

    p.arrow((636, 232), (672, 232), CYAN, 2)
    p.arrow((712, 232), (762, 232), CYAN, 2)
    p.arrow((802, 232), (812, 232), CYAN, 2)
    p.text(610, 300, "AI 角色", 14, PALE, anchor="mt", box=(560, 292, 660, 320))
    p.text(783, 300, "广告发布", 14, PALE, anchor="mt", box=(730, 292, 840, 320))
    p.save(path)


def figure(path):
    p = Panel((1080, 1120), PAPER)
    p.text(64, 42, "两道门，决定 AI 能不能开口", 42, NAVY, True, box=(60, 30, 1018, 104))
    p.text(66, 108, "品类门看规则，话术门看有没有真实使用", 22, MUTED, box=(60, 98, 1018, 146))

    p.rounded((64, 168, 1016, 304), 24, fill=WHITE, outline=LINE, width=2)
    p.rounded((64, 168, 82, 304), 12, fill=CORAL)
    p.text(104, 188, "罚单", 14, CORAL, True)
    p.text(104, 212, "方桃子 × 美瞳广告 → 6.8288 万元", 27, NAVY, True, box=(100, 202, 880, 250))
    chip(p, 104, 258, "未取得审查证明", 15, WHITE, CORAL, CORAL, False, 30)
    chip(p, 288, 258, "虚构使用体验", 15, WHITE, CORAL, CORAL, False, 30)
    p.ellipse((884, 190, 980, 286), fill=WHITE, outline=CORAL, width=3)
    p.text(932, 224, "1×", 30, CORAL, True, anchor="mm")
    p.text(932, 258, "广告费", 13, MUTED, anchor="mm")

    p.rounded((64, 336, 516, 764), 28, fill=NAVY)
    gate(p, 100, 372, 54, 72, CYAN)
    p.text(172, 382, "品类门", 30, WHITE, True, box=(160, 368, 500, 422))
    p.text(172, 424, "先看能不能做", 16, PALE, box=(160, 418, 500, 448))
    p.text(100, 486, "医疗器械：发布前须审查", 18, WHITE, box=(96, 476, 490, 512))
    p.text(100, 520, "医疗器械广告：不得有安全性断言，", 18, WHITE, box=(96, 510, 495, 546))
    p.text(100, 554, "不得用代言人（第16条）", 18, WHITE, box=(96, 544, 490, 580))
    p.text(100, 596, "美瞳属第三类 → 此路不通", 18, CORAL, True, box=(96, 586, 495, 622))
    p.line([(100, 638), (480, 638)], "#2B5057", 2)
    check(p, 114, 672, 12, GREEN)
    p.text(138, 660, "普通食品 / 调味品", 17, CYAN, True, box=(134, 650, 495, 684))
    p.text(100, 704, "品类可通过，话术门仍在", 16, PALE, box=(96, 696, 495, 728))

    p.rounded((564, 336, 1016, 764), 28, fill=TEAL)
    gate(p, 600, 372, 54, 72, CYAN)
    p.text(672, 382, "话术门", 30, WHITE, True, box=(660, 368, 1000, 422))
    p.text(672, 424, "再看能不能说", 16, "#BEE6DF", box=(660, 418, 1000, 448))
    p.text(600, 486, "AI 没戴过、没尝过、没吃过", 18, WHITE, box=(596, 476, 995, 512))
    p.text(600, 520, "第一人称体验 = 虚构使用效果", 18, WHITE, box=(596, 510, 995, 546))
    p.text(600, 552, "（第28条第2款第4项）", 15, "#BEE6DF", box=(596, 546, 995, 574))

    p.rounded((600, 596, 826, 660), 18, fill=WHITE)
    p.polygon([(638, 658), (662, 658), (646, 680)], WHITE)
    p.line([(612, 604), (814, 652)], CORAL, 4)
    p.text(620, 614, "戴了一天很舒服", 17, NAVY, True, box=(612, 604, 818, 648))
    p.text(838, 618, "虚构体验", 14, CORAL, True, box=(832, 608, 1000, 640))
    check(p, 614, 704, 12, GREEN)
    p.text(638, 692, "配料表 / 规格 / 产地", 16, WHITE, box=(634, 682, 995, 716))
    p.text(600, 734, "可举证的产品事实，才是 AI 能念的", 14, "#BEE6DF", box=(596, 726, 1000, 752))

    p.rounded((64, 796, 1016, 1008), 24, fill=WHITE, outline=LINE, width=2)
    p.text(96, 818, "发布前，按顺序核", 22, NAVY, True, box=(90, 808, 990, 850))
    items = ["品类", "审查", "话术", "授权", "标识", "数据", "合同"]
    x = 96
    for item in items:
        w = chip(p, x, 862, item, 17, PAPER, TEAL, NAVY, True, 44, 16)
        x += w + 16
    p.text(96, 926, "审查证明解决“能不能发”，话术核对解决“能不能这么说”。", 16, MUTED, box=(90, 918, 990, 952))
    p.text(66, 1044, "本图为编辑示意；条文引自《广告法》2021年修正，罚单信息引自南方都市报转引的“信用广东”公示。", 15, MUTED, box=(60, 1036, 1020, 1068))
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
