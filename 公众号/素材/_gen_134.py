from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
CREAM = "#F7F1E7"
INK = "#302E2B"
RED = "#A84D3F"
GOLD = "#BC8B42"
TEAL = "#386D68"
MUTED = "#766E64"
SCALE = 2
COVER = "封面_134_20261126_900x383.png"
FIGURE = "图1_134_观看记忆_1080x1000.png"


class Panel:
    def __init__(self, size):
        self.size = size
        self.image = Image.new("RGB", tuple(v * SCALE for v in size), CREAM)
        self.draw = ImageDraw.Draw(self.image)

    def points(self, points):
        return [(round(x * SCALE), round(y * SCALE)) for x, y in points]

    def polygon(self, points, color):
        self.draw.polygon(self.points(points), fill=color)

    def line(self, points, color, width=2):
        self.draw.line(self.points(points), fill=color, width=width * SCALE, joint="curve")

    def ellipse(self, box, fill=None, outline=None, width=2):
        self.draw.ellipse(tuple(round(v * SCALE) for v in box), fill=fill, outline=outline, width=width * SCALE)

    def text(self, x, y, value, size, color=INK, bold=False, anchor="lt", box=None):
        font = ImageFont.truetype(FONT, size * SCALE, index=2 if bold else 0)
        bounds = self.draw.textbbox((x * SCALE, y * SCALE), value, font=font, anchor=anchor)
        safe = tuple(v * SCALE for v in (box or (0, 0, *self.size)))
        assert safe[0] <= bounds[0] < bounds[2] <= safe[2] and safe[1] <= bounds[1] < bounds[3] <= safe[3], (value, bounds, safe)
        self.draw.text((x * SCALE, y * SCALE), value, font=font, fill=color, anchor=anchor)

    def curve(self, points, color, width=2):
        p0, p1, p2, p3 = points
        curve = []
        for i in range(61):
            t = i / 60
            curve.append(tuple((1 - t) ** 3 * p0[j] + 3 * (1 - t) ** 2 * t * p1[j] + 3 * (1 - t) * t ** 2 * p2[j] + t ** 3 * p3[j] for j in (0, 1)))
        self.line(curve, color, width)

    def save(self, path):
        with path.open("xb") as f:
            self.image.resize(self.size, Image.Resampling.LANCZOS).save(f, "PNG", optimize=True)


def wheel(p, x, y, r):
    p.ellipse((x - r, y - r, x + r, y + r), fill="#EBDDC2", outline=GOLD, width=5)
    p.ellipse((x - r * 0.7, y - r * 0.7, x + r * 0.7, y + r * 0.7), outline=GOLD, width=2)
    for i in range(10):
        a = i * math.tau / 10
        p.line([(x, y), (x + math.cos(a) * r * 0.87, y + math.sin(a) * r * 0.87)], GOLD, 2)
    p.ellipse((x - r * 0.13, y - r * 0.13, x + r * 0.13, y + r * 0.13), fill=RED)
    for dx, dy in [(-1, -0.55), (-0.15, -1), (0.8, -0.7)]:
        cx, cy = x + dx * r, y + dy * r
        p.polygon([(cx - r * 0.12, cy), (cx - r * 0.25, cy - r * 0.4), (cx + r * 0.12, cy - r * 0.23), (cx + r * 0.04, cy - r * 0.65), (cx + r * 0.35, cy - r * 0.08), (cx + r * 0.2, cy + r * 0.12)], RED)


def festival(p, x, y, s):
    for offset, direction in [(-0.45, -1), (0.25, 1), (0.8, 1)]:
        fx = x + offset * s
        p.line([(fx, y + s * 0.55), (fx, y - s * 0.75)], TEAL, 3)
        p.polygon([(fx, y - s * 0.75), (fx + direction * s * 0.42, y - s * 0.55), (fx, y - s * 0.3)], RED if offset < 0 else GOLD)
    p.curve([(x - s * 0.7, y + s * 0.58), (x - s * 0.1, y + s * 0.25), (x + s * 0.2, y + s * 0.93), (x + s, y + s * 0.55)], TEAL, 3)
    for i, height in enumerate([0.15, 0.35, 0.55, 0.28, 0.45, 0.18]):
        bx = x - s * 0.3 + i * s * 0.19
        p.line([(bx, y + s * 1.05), (bx, y + s * (1.05 - height))], TEAL, 5)


def cover(path):
    p = Panel((900, 383))
    p.polygon([(606, 0), (900, 0), (900, 383), (550, 383)], "#EEE4D5")
    p.line([(51, 41), (51, 73)], RED, 4)
    p.text(66, 42, "哪吒与电音三太子", 29, RED, True)
    p.text(49, 106, "同一个名字", 62, INK, True)
    p.text(52, 190, "画稿为什么反复改", 42, INK, True)
    p.text(54, 282, "《活宝档案》的人物选择", 25, MUTED)
    p.text(54, 337, "一人短剧厂牌 · 人物案例", 18, MUTED)
    wheel(p, 721, 130, 47)
    festival(p, 736, 267, 59)
    p.curve([(711, 190), (678, 227), (796, 193), (797, 231)], RED, 3)
    p.save(path)


def figure(path):
    p = Panel((1080, 1000))
    p.text(65, 49, "同一个名字，不同的观看记忆", 46, INK, True)
    p.text(66, 119, "基于江国铭的受访表述，不是观众分组调查", 24, MUTED)
    p.text(540, 201, "三太子", 64, RED, True, "mt")
    p.curve([(540, 287), (540, 332), (267, 274), (267, 362)], GOLD, 3)
    p.curve([(540, 287), (540, 332), (813, 274), (813, 362)], TEAL, 3)
    p.polygon([(259, 352), (275, 352), (267, 367)], GOLD)
    p.polygon([(805, 352), (821, 352), (813, 367)], TEAL)
    p.text(267, 389, "神话故事里的哪吒", 31, INK, True, "mt")
    p.text(813, 389, "庙会里的电音三太子", 31, INK, True, "mt")
    wheel(p, 268, 564, 75)
    p.curve([(113, 608), (205, 470), (291, 689), (400, 537)], RED, 8)
    p.curve([(118, 628), (209, 492), (289, 710), (410, 555)], "#D6B4A4", 3)
    festival(p, 787, 539, 85)
    p.text(267, 697, "故事与人物身份", 25, MUTED, anchor="mt")
    p.text(813, 697, "战袍、彩旗与舞步", 25, MUTED, anchor="mt")
    p.line([(67, 761), (1013, 761)], "#CEBFA9", 1)
    p.line([(92, 812), (114, 796), (143, 826), (121, 844), (92, 812)], GOLD, 3)
    p.line([(121, 844), (97, 857), (101, 832)], GOLD, 3)
    p.text(180, 792, "团队的画稿取舍", 25, RED, True)
    p.text(180, 840, "把庙宇三太子的服饰、神态融入设计", 31, INK, True)
    p.text(67, 939, "符号为本号编辑示意，非剧中形象或原作画稿。", 22, MUTED)
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
    for path, expected in zip(targets, [(900, 383), (1080, 1000)]):
        with Image.open(path) as image:
            image.load()
            assert image.size == expected
        print(path.name, expected, path.stat().st_size)


if __name__ == "__main__":
    main()
