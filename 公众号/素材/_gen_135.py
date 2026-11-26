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
COVER = "封面_135_20261126_900x383.png"
FIGURE = "图1_135_两种需求_1080x1120.png"


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

    def arrow(self, start, end, color, width=3):
        self.line([start, end], color, width)
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        length = 12
        spread = 0.55
        p1 = (end[0] - length * math.cos(angle - spread), end[1] - length * math.sin(angle - spread))
        p2 = (end[0] - length * math.cos(angle + spread), end[1] - length * math.sin(angle + spread))
        self.polygon([end, p1, p2], color)

    def save(self, path):
        with path.open("xb") as stream:
            self.image.resize(self.size, Image.Resampling.LANCZOS).save(stream, "PNG", optimize=True)


def phone(p, x, y, w, h, dark=False):
    outline = CYAN if dark else WHITE
    fill = DEEP if dark else TEAL
    p.rounded((x, y, x + w, y + h), 18, fill=fill, outline=outline, width=3)
    p.rounded((x + 12, y + 20, x + w - 12, y + h - 20), 10, fill=NAVY if dark else "#1B8B8D")
    p.line([(x + w * 0.38, y + 10), (x + w * 0.62, y + 10)], outline, 2)
    p.polygon([(x + w * 0.43, y + h * 0.38), (x + w * 0.43, y + h * 0.62), (x + w * 0.65, y + h * 0.5)], CORAL)
    p.line([(x + 27, y + h * 0.74), (x + w - 27, y + h * 0.74)], PALE if dark else "#BEE6DF", 3)
    p.line([(x + 27, y + h * 0.82), (x + w - 43, y + h * 0.82)], PALE if dark else "#BEE6DF", 2)


def network(p, cx, cy, radius, dark=False):
    node_fill = DEEP if dark else "#1B8B8D"
    node_outline = CYAN if dark else WHITE
    center_fill = CORAL
    points = []
    for i in range(6):
        angle = -math.pi / 2 + i * math.tau / 6
        points.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
    for i, point in enumerate(points):
        p.line([(cx, cy), point], CYAN if dark else "#BEE6DF", 3)
        p.line([point, points[(i + 1) % len(points)]], CYAN if dark else "#BEE6DF", 2)
    for x, y in points:
        p.ellipse((x - 18, y - 18, x + 18, y + 18), fill=node_fill, outline=node_outline, width=3)
        p.ellipse((x - 5, y - 5, x + 5, y + 5), fill=node_outline)
    p.ellipse((cx - 25, cy - 25, cx + 25, cy + 25), fill=center_fill)
    p.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=WHITE)


def cover(path):
    p = Panel((900, 383), NAVY)
    p.polygon([(574, 0), (900, 0), (900, 383), (525, 383)], DEEP)
    p.text(54, 35, "B 站 Q3 · 短剧问答", 18, CYAN, True)
    p.text(52, 91, "陈睿把短剧比作薯片", 40, WHITE, True)
    p.text(52, 151, "B站靠什么留住人", 47, WHITE, True)
    p.text(55, 230, "平台增长，不等于短剧影响为零", 23, PALE)
    p.line([(55, 279), (475, 279)], TEAL, 2)
    p.text(55, 320, "一人短剧厂牌 · 公司观察", 17, PALE)

    phone(p, 625, 62, 116, 232, dark=True)
    network(p, 795, 180, 76, dark=True)
    p.arrow((747, 180), (758, 180), CYAN, 2)
    p.text(684, 328, "一次打开", 18, PALE, anchor="mt")
    p.text(800, 328, "持续关系", 18, CYAN, True, anchor="mt")
    p.save(path)


def figure(path):
    p = Panel((1080, 1120), PAPER)
    p.text(66, 48, "两种需求，可以落在同一批用户身上", 42, NAVY, True)
    p.text(66, 116, "“薯片与米饭”分的是使用需求，不是互斥人群", 23, MUTED)

    p.rounded((64, 196, 506, 694), 30, fill=NAVY)
    p.rounded((574, 196, 1016, 694), 30, fill=TEAL)
    phone(p, 235, 270, 100, 188, dark=True)
    network(p, 795, 364, 88, dark=False)

    p.text(285, 512, "短内容", 38, WHITE, True, anchor="mt")
    p.text(285, 571, "持续吸引注意力", 26, WHITE, anchor="mt")
    p.text(285, 630, "一次打开，完成一个故事", 20, PALE, anchor="mt")
    p.text(795, 512, "B 站", 38, WHITE, True, anchor="mt")
    p.text(795, 571, "优质内容与用户心智", 26, WHITE, anchor="mt")
    p.text(795, 630, "关注创作者，形成回访", 20, "#BEE6DF", anchor="mt")

    p.ellipse((472, 382, 608, 518), fill=PAPER, outline=CORAL, width=3)
    p.text(540, 449, "同一用户", 21, CORAL, True, anchor="mm")
    p.arrow((448, 449), (475, 449), CORAL, 3)
    p.arrow((632, 449), (605, 449), CORAL, 3)

    p.rounded((64, 758, 1016, 1007), 26, fill=WHITE, outline=LINE, width=2)
    p.text(96, 786, "需要分开的两件事", 26, NAVY, True)
    p.text(120, 858, "平台总量创新高", 27, NAVY, True)
    p.text(120, 908, "DAU 1.235亿 · 总时长 +14%", 20, MUTED)
    p.line([(500, 872), (580, 872)], CORAL, 5)
    p.line([(500, 896), (580, 896)], CORAL, 5)
    p.line([(567, 850), (513, 918)], CORAL, 5)
    p.text(706, 858, "短剧影响为零", 27, CORAL, True)
    p.text(706, 908, "公开数据不足以证明", 20, MUTED)
    p.text(66, 1054, "本图为编辑示意；平台数据来自 B 站 2026 Q3 官方财报。", 18, MUTED)
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
