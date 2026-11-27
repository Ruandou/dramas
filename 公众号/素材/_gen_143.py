from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
SCALE = 2
NAVY = "#102A31"
DEEP = "#173D43"
TEAL = "#167C80"
CYAN = "#65D1C5"
CORAL = "#E67B5A"
WHITE = "#FFFFFF"
PAPER = "#F2F4F1"
MUTED = "#5F7072"
PALE = "#C7D7D3"
LINE = "#D9E4E0"
GOLD = "#E9B44C"
COVER = "封面_143_追光计划_20261127_r3_900x383.png"
FIGURE = "图1_143_追光转化漏斗_20261127_r3_1080x1120.png"


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
        self.draw.rounded_rectangle(
            self.box(values), radius=radius * SCALE, fill=fill, outline=outline, width=width * SCALE
        )

    def line(self, values, color, width=2):
        self.draw.line(self.points(values), fill=color, width=width * SCALE, joint="curve")

    def polygon(self, values, color):
        self.draw.polygon(self.points(values), fill=color)

    def ellipse(self, values, fill=None, outline=None, width=1):
        self.draw.ellipse(self.box(values), fill=fill, outline=outline, width=width * SCALE)

    def text(self, x, y, value, size, color, bold=False, anchor="lt", box=None):
        font = ImageFont.truetype(FONT, size * SCALE, index=2 if bold else 0)
        bounds = self.draw.textbbox((x * SCALE, y * SCALE), value, font=font, anchor=anchor)
        safe = self.box(box or (0, 0, *self.size))
        assert (
            safe[0] <= bounds[0] < bounds[2] <= safe[2]
            and safe[1] <= bounds[1] < bounds[3] <= safe[3]
        ), (value, bounds, safe)
        self.draw.text((x * SCALE, y * SCALE), value, font=font, fill=color, anchor=anchor)

    def save(self, path):
        with path.open("xb") as stream:
            self.image.resize(self.size, Image.Resampling.LANCZOS).save(stream, "PNG", optimize=True)


def cover(path):
    p = Panel((900, 383), NAVY)
    p.polygon([(520, 0), (900, 0), (900, 383), (472, 383)], DEEP)
    p.text(48, 26, "微短剧赛事 · 成果转化", 15, CYAN, True, box=(42, 18, 470, 52))
    p.text(44, 58, "评奖之后", 46, WHITE, True, box=(38, 50, 470, 120))
    p.text(46, 122, "1206部参赛", 28, PALE, True, box=(40, 114, 478, 158))
    p.text(46, 158, "百强中64部获平台认领", 28, GOLD, True, box=(40, 150, 478, 194))
    p.line([(48, 212), (466, 212)], TEAL, 2)
    p.text(48, 230, "总决赛后 → 展播前：58 → 64", 17, CYAN, True, box=(42, 222, 478, 258))
    p.text(48, 262, "25部好故事孵化 · 7个平台展播至2027-02-26", 15, PALE, box=(42, 254, 486, 288))
    p.text(48, 342, "一人短剧厂牌 · 2026-11-27 公开页面核查", 13, PALE, box=(42, 334, 486, 366))

    p.text(588, 28, "项目池 → 平台认领", 13, CYAN, True, box=(582, 20, 860, 52))
    p.rounded((580, 58, 850, 112), 14, fill=NAVY, outline=TEAL, width=2)
    p.text(596, 74, "1206 部参赛", 20, WHITE, True, box=(590, 66, 844, 104))
    p.rounded((610, 128, 820, 182), 14, fill=NAVY, outline=TEAL, width=2)
    p.text(624, 144, "100 个优秀项目", 18, WHITE, True, box=(618, 136, 814, 174))
    p.rounded((640, 198, 790, 252), 14, fill=NAVY, outline=GOLD, width=2)
    p.text(654, 214, "64 部获认领", 18, GOLD, True, box=(648, 206, 784, 244))
    p.polygon([(712, 116), (724, 116), (718, 124)], TEAL)
    p.polygon([(712, 186), (724, 186), (718, 194)], TEAL)
    p.rounded((580, 276, 850, 328), 14, fill=NAVY, outline=CORAL, width=2)
    p.text(596, 288, "25 部好故事孵化", 16, CORAL, True, box=(590, 280, 844, 312))
    p.text(596, 310, "与64部是否重叠未公开", 11, PALE, box=(590, 304, 844, 326))
    p.save(path)


def figure(path):
    p = Panel((1080, 1120), PAPER)
    p.text(64, 38, "追光计划：从1206到64", 42, NAVY, True, box=(58, 26, 1022, 100))
    p.text(66, 104, "第二届百强展播｜官方公开口径｜2026-11-27", 20, MUTED, box=(60, 96, 1022, 140))

    # funnel strip
    p.rounded((60, 156, 300, 246), 16, fill=WHITE, outline=TEAL, width=2)
    p.text(80, 172, "1206", 34, TEAL, True, box=(74, 164, 294, 216))
    p.text(80, 214, "部参赛", 16, MUTED, box=(74, 206, 294, 238))
    p.line([(306, 201), (338, 201)], TEAL, 3)
    p.polygon([(338, 193), (338, 209), (348, 201)], TEAL)

    p.rounded((360, 156, 600, 246), 16, fill=WHITE, outline=TEAL, width=2)
    p.text(380, 172, "100", 34, TEAL, True, box=(374, 164, 594, 216))
    p.text(380, 214, "个优秀项目", 16, MUTED, box=(374, 206, 594, 238))
    p.line([(606, 201), (638, 201)], TEAL, 3)
    p.polygon([(638, 193), (638, 209), (648, 201)], TEAL)

    p.rounded((660, 156, 900, 246), 16, fill=WHITE, outline=GOLD, width=2)
    p.text(680, 172, "64", 34, GOLD, True, box=(674, 164, 894, 216))
    p.text(680, 214, "部获平台认领", 16, MUTED, box=(674, 206, 894, 238))

    p.rounded((920, 156, 1020, 246), 16, fill=WHITE, outline=CORAL, width=2)
    p.text(940, 172, "25", 30, CORAL, True, box=(934, 164, 1014, 210))
    p.text(938, 212, "好故事孵化", 13, MUTED, box=(932, 204, 1014, 236))

    p.rounded((60, 266, 1020, 318), 14, fill=WHITE, outline=LINE, width=2)
    p.text(80, 278, "并行口径：25部“好故事”孵化；官方未说明与64部作品是否重叠，不能相加。", 17, CORAL, True, box=(74, 270, 1014, 310))

    # timeline
    p.line([(112, 366), (112, 860)], LINE, 4)
    cards = [
        ("10-30", "评审结果", "1206部参赛 → 100个优秀项目；43位创作者", TEAL, 340),
        ("11-04", "总决赛", "15个项目路演、年度十强；11-06报道：58部获认领、18部好故事孵化；3组集中签约", CORAL, 520),
        ("11-26", "展播启动", "截至展播前：64部获认领、25部好故事孵化；7个平台展播至2027-02-26", GOLD, 700),
    ]
    for date, name, detail, accent, y in cards:
        p.ellipse((96, y + 28, 128, y + 60), fill=accent)
        p.rounded((150, y, 1020, y + 132), 18, fill=WHITE, outline=LINE, width=2)
        p.text(176, y + 18, date, 24, accent, True, box=(170, y + 10, 360, y + 52))
        p.text(176, y + 54, name, 24, NAVY, True, box=(170, y + 46, 500, y + 88))
        p.line([(176, y + 92), (994, y + 92)], LINE, 2)
        p.text(176, y + 102, detail, 18, MUTED, box=(170, y + 94, 1000, y + 126))

    # bottom rules
    p.rounded((60, 892, 1020, 1048), 22, fill=NAVY)
    p.text(86, 910, "读这几个数，别跨口径", 22, CYAN, True, box=(80, 902, 994, 944))
    p.text(86, 950, "64 + 25 不能相加", 18, WHITE, True, box=(80, 942, 994, 978))
    p.text(86, 980, "64部获认领 ≠ 64部已上线", 18, WHITE, True, box=(80, 972, 994, 1010))
    p.text(86, 1010, "“100部”是项目池；正文限定“具备播出条件”", 16, GOLD, True, box=(80, 1002, 1000, 1038))

    p.text(66, 1074, "来源：首都广电官方稿（2026-11-27）、总决赛稿（2026-11-06）、评审结果（2026-10-30）。未核各平台实际片单。", 13, MUTED, box=(60, 1066, 1022, 1100))
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
