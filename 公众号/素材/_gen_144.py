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
COVER = "封面_144_海外短剧成本_20261127_r2_900x383.png"
FIGURE = "图1_144_海外短剧账本_20261127_r2_1080x1120.png"


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
    p.text(48, 26, "MPA 2026 全球微短剧报告", 15, CYAN, True, box=(42, 18, 470, 52))
    p.text(44, 58, "海外短剧", 38, WHITE, True, box=(38, 50, 470, 110))
    p.text(44, 104, "48.7亿美元", 52, GOLD, True, box=(38, 96, 470, 168))
    p.text(46, 180, "56%收入花在营销", 24, WHITE, True, box=(40, 172, 478, 216))
    p.line([(48, 220), (466, 220)], TEAL, 2)
    p.text(48, 236, "18%交商店与支付", 15, PALE, box=(42, 228, 478, 262))
    p.text(48, 260, "26%留给制作与人力（不是利润）", 13, PALE, box=(42, 252, 486, 284))
    p.text(48, 342, "一人短剧厂牌 · 2026-11-27 公开页面核查", 12, PALE, box=(42, 334, 486, 366))

    p.text(588, 28, "中国以外每1美元", 13, CYAN, True, box=(582, 20, 860, 52))
    p.rounded((580, 58, 850, 112), 14, fill=NAVY, outline=TEAL, width=2)
    p.text(596, 72, "56 美分", 21, WHITE, True, box=(590, 64, 844, 102))
    p.text(596, 96, "营销", 11, PALE, box=(596, 92, 844, 110))
    p.rounded((580, 128, 820, 182), 14, fill=NAVY, outline=TEAL, width=2)
    p.text(596, 142, "18 美分", 21, WHITE, True, box=(590, 134, 814, 172))
    p.text(596, 166, "商店/支付", 11, PALE, box=(596, 162, 814, 180))
    p.rounded((610, 198, 790, 252), 14, fill=NAVY, outline=GOLD, width=2)
    p.text(624, 212, "26 美分", 21, GOLD, True, box=(618, 204, 784, 242))
    p.text(624, 236, "剩余（不是利润）", 10, PALE, box=(624, 232, 784, 250))
    p.rounded((580, 276, 850, 328), 14, fill=NAVY, outline=CORAL, width=2)
    p.text(596, 288, "前四家 65% · 1/12 每月付费", 12, CYAN, True, box=(590, 280, 844, 314))
    p.text(596, 307, "两个 65% 不是同一口径", 10, PALE, box=(596, 303, 844, 323))
    p.save(path)


def figure(path):
    p = Panel((1080, 1120), PAPER)
    p.text(64, 38, "200亿美元是全球盘，海外是48.7亿", 40, NAVY, True, box=(58, 26, 1022, 100))
    p.text(66, 104, "MPA《The Micro-Drama Economy 2026》｜2026年估算／预测", 18, MUTED, box=(60, 96, 1022, 140))

    # zone 1: global split
    p.text(64, 158, "全球收入的76%在中国，24%在中国以外", 21, NAVY, True, box=(58, 150, 1022, 192))
    p.rounded((60, 200, 790, 270), 12, fill=TEAL)
    p.rounded((790, 200, 1020, 270), 12, fill=GOLD)
    p.text(90, 222, "中国 152亿美元 · 76%", 20, WHITE, True, box=(80, 214, 780, 260))
    p.text(810, 224, "中国以外 48.7亿美元 · 24%", 14, NAVY, True, box=(800, 216, 1014, 260))
    p.text(64, 280, "152 + 48.7 = 200.7；差0.7亿美元来自四舍五入。中国以外只含专营App及web store，不含社交信息流。", 13, MUTED, box=(58, 272, 1022, 306))

    # zone 2: dollar split
    p.text(64, 326, "中国以外：每1美元收入怎么分", 22, NAVY, True, box=(58, 318, 1022, 362))
    p.rounded((60, 380, 598, 450), 12, fill=CORAL)
    p.rounded((598, 380, 771, 450), 12, fill=NAVY)
    p.rounded((771, 380, 1020, 450), 12, fill=TEAL)
    p.text(80, 400, "56美分 营销", 18, WHITE, True, box=(70, 392, 590, 440))
    p.text(612, 394, "18美分", 16, WHITE, True, box=(606, 386, 766, 420))
    p.text(612, 418, "商店/支付", 12, PALE, box=(606, 414, 766, 442))
    p.text(790, 394, "26美分 剩余", 16, WHITE, True, box=(784, 386, 1014, 420))
    p.text(790, 418, "制作/带宽/人力", 12, PALE, box=(784, 414, 1014, 442))
    p.text(64, 462, "26美分要覆盖制作、带宽、人力、税费，最后才是利润；报告没有说制作占多少。", 14, MUTED, box=(58, 454, 1022, 490))
    p.rounded((60, 500, 520, 548), 12, fill=WHITE, outline=LINE, width=2)
    p.text(76, 512, "前四家拿走65%收入", 16, NAVY, True, box=(70, 504, 510, 540))
    p.rounded((540, 500, 1020, 548), 12, fill=WHITE, outline=LINE, width=2)
    p.text(556, 512, "每12个用户约1个每月付费", 16, NAVY, True, box=(550, 504, 1006, 540))

    # zone 3: AI supply vs viewing
    p.text(64, 570, "AI把上新打下来，没把观看抢过来", 24, NAVY, True, box=(58, 562, 1022, 606))
    p.rounded((60, 620, 530, 890), 18, fill=WHITE, outline=TEAL, width=2)
    p.text(82, 638, "上新", 14, MUTED, box=(76, 630, 520, 660))
    p.text(82, 660, "44万条", 38, TEAL, True, box=(76, 652, 520, 712))
    p.text(82, 716, "2025年约10万条", 14, MUTED, box=(76, 708, 520, 738))
    p.text(82, 746, "AI占75%", 22, CORAL, True, box=(76, 738, 520, 782))
    p.text(82, 784, "2025年为15%", 12, MUTED, box=(76, 776, 520, 806))
    p.text(82, 812, "一条=一部作品×一种语言×一个应用", 12, MUTED, box=(76, 804, 520, 836))
    p.text(82, 840, "44万条≠44万部唯一作品", 12, NAVY, True, box=(76, 832, 520, 864))

    p.rounded((550, 620, 1020, 890), 18, fill=WHITE, outline=GOLD, width=2)
    p.text(572, 638, "观看", 14, MUTED, box=(566, 630, 1010, 660))
    p.text(572, 660, "5/6", 38, GOLD, True, box=(566, 652, 1010, 712))
    p.text(572, 716, "中国以外6个平台中，5个平台前50名以真人实拍为主", 13, MUTED, box=(566, 708, 1010, 760))
    p.text(572, 770, "中国：AI约9成新剧", 18, NAVY, True, box=(566, 762, 1010, 802))
    p.text(572, 800, "但只占20%收入", 18, CORAL, True, box=(566, 792, 1010, 832))
    p.text(572, 840, "作品数≠收入；不能算单部回报", 12, MUTED, box=(566, 832, 1010, 864))

    # bottom note
    p.rounded((60, 910, 1020, 1020), 16, fill=WHITE, outline=LINE, width=2)
    p.text(78, 922, "读法：收入未扣商店与支付费用；中国以外只含专营App及web store，不含社交信息流。", 12, MUTED, box=(72, 914, 1012, 954))
    p.text(78, 954, "MPA估算/预测；56%、18%为市场平均，65%为份额，不是每部剧的账本；26美分不是利润。", 12, MUTED, box=(72, 946, 1012, 986))
    p.text(78, 992, "来源：MPA公开稿（AVIA，2026-11-26）；NXRTE中文编译（2026-11-27）。", 11, MUTED, box=(72, 984, 1012, 1014))
    p.text(64, 1064, "一人短剧厂牌 · 2026-11-27", 11, MUTED, box=(58, 1056, 1022, 1092))
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
