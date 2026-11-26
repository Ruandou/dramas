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
COVER = "封面_138_20261126_900x383.png"
FIGURE = "图1_138_成本三把尺_1080x1120.png"


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
    p.text(54, 30, "AI 短剧成本 · 报道拆解", 16, CYAN, True)
    p.text(50, 64, "3000元", 56, WHITE, True, box=(44, 54, 470, 126))
    p.text(52, 132, "只是直接成本", 40, CYAN, True, box=(44, 124, 470, 184))
    p.line([(54, 200), (466, 200)], TEAL, 2)
    p.text(54, 220, "3天有前提：20多套流程 + 约4000项素材", 15, PALE, box=(48, 212, 476, 242))
    p.text(54, 250, "人工、返工、素材库，报道没拆开", 15, PALE, box=(48, 242, 476, 272))
    p.text(54, 286, "6.5亿播放是团队自报，不是收入", 15, CORAL, True, box=(48, 278, 476, 308))
    p.text(54, 340, "一人短剧厂牌 · 成本拆解", 13, PALE, box=(48, 332, 400, 360))

    p.text(556, 48, "3天", 96, CYAN, True, box=(548, 36, 760, 162))
    p.text(560, 160, "最快速度", 28, WHITE, True, box=(554, 152, 760, 198))
    p.chip(560, 206, "有前提", 14, CORAL, CORAL, WHITE, True, 30, 12)
    p.text(556, 264, "20+ 套流程 · 4000 项素材", 14, PALE, box=(550, 256, 872, 284))
    p.text(556, 292, "100 个成片镜头", 15, WHITE, True, box=(550, 284, 872, 314))
    p.text(556, 316, "≈ 1000 个生成镜头", 15, CORAL, True, box=(550, 308, 872, 338))
    p.save(path)


def figure(path):
    p = Panel((1080, 1120), PAPER)
    p.text(64, 38, "三个成本数字，不是同一把尺子", 40, NAVY, True, box=(58, 26, 1018, 96))
    p.text(66, 100, "同一篇报道里的三个数，量的不是同一件事", 20, MUTED, box=(60, 92, 1018, 136))

    p.rounded((64, 150, 1016, 300), 22, fill=WHITE, outline=LINE, width=2)
    p.text(92, 174, "3000元", 44, NAVY, True, box=(86, 164, 420, 230))
    p.text(92, 232, "3人获奖团队 · 流程素材较为完备", 16, MUTED, box=(86, 224, 700, 254))
    p.text(92, 260, "直接制作成本 · 最快3天", 17, TEAL, True, box=(86, 252, 700, 284))
    p.chip(800, 180, "明细未披露", 14, CORAL, CORAL, WHITE, True, 30, 12)

    p.rounded((64, 322, 1016, 472), 22, fill=WHITE, outline=LINE, width=2)
    p.text(92, 346, "20万元以内", 40, NAVY, True, box=(86, 336, 500, 400))
    p.text(92, 404, "一家转型企业 · 60集×2分钟", 16, MUTED, box=(86, 396, 700, 426))
    p.text(92, 432, "AI制作成本（口径未展开）", 17, TEAL, True, box=(86, 424, 760, 456))

    p.rounded((64, 494, 1016, 644), 22, fill=WHITE, outline=LINE, width=2)
    p.text(92, 518, "五六十万元", 40, NAVY, True, box=(86, 508, 500, 572))
    p.text(92, 576, "同长度真人短剧 · 中等预算", 16, MUTED, box=(86, 568, 700, 598))
    p.text(92, 604, "报道中的原有制作成本", 17, TEAL, True, box=(86, 596, 700, 628))

    p.rounded((64, 672, 1016, 772), 20, fill=NAVY)
    p.text(96, 692, "3000 vs 20万：差几十倍", 24, CYAN, True, box=(90, 684, 700, 724))
    p.text(96, 730, "不是AI便宜几十倍，是拿小团队直接支出比企业完整制作", 15, WHITE, box=(90, 722, 990, 752))

    p.rounded((64, 800, 1016, 942), 20, fill=WHITE, outline=LINE, width=2)
    p.text(96, 820, "更稳的参照：罗翀《瓷韵》", 22, NAVY, True, box=(90, 812, 700, 852))
    p.text(96, 856, "实景：30人×约1个月 → AI：1周，成本降至 1/3", 16, MUTED, box=(90, 848, 990, 878))
    p.text(96, 892, "最终100个镜头，背后约生成1000个镜头", 17, CORAL, True, box=(90, 884, 990, 916))
    p.text(96, 916, "生成便宜，挑选和返工不便宜", 14, MUTED, box=(90, 908, 990, 934))

    p.rounded((64, 964, 1016, 1046), 18, fill=WHITE, outline=LINE, width=2)
    p.rounded((64, 964, 72, 1046), 8, fill=CORAL)
    p.text(96, 980, "6.5亿播放为团队自报", 20, NAVY, True, box=(90, 972, 700, 1008))
    p.text(96, 1008, "未给平台、周期、去重口径与收入；不能直接换算观众或收入", 13, MUTED, box=(90, 1000, 990, 1028))

    p.text(66, 1066, "本图为编辑示意。数据来源：中国青年报 2026-11-24 报道；金额口径见正文。", 12, MUTED, box=(60, 1058, 1020, 1088))
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
