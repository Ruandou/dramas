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
COVER = "封面_141_模型比价条件_20261127_r2_900x383.png"
FIGURE = "图1_141_同规格比价_20261127_r2_1080x1120.png"


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
    p.polygon([(548, 0), (900, 0), (900, 383), (500, 383)], DEEP)
    p.text(52, 30, "AI 制作 · 官方 API 比价", 16, CYAN, True)
    p.text(48, 72, "先锁规格", 52, WHITE, True, box=(42, 60, 470, 140))
    p.text(48, 138, "再看单价", 52, GOLD, True, box=(42, 126, 470, 206))
    p.line([(52, 218), (474, 218)], TEAL, 2)
    p.text(52, 240, "输出只是账单的一部分", 18, PALE, box=(46, 232, 478, 270))
    p.text(52, 278, "输入、声音与二次生成按型号核算", 18, CYAN, True, box=(46, 270, 480, 314))
    p.text(52, 338, "一人短剧厂牌 · 2026-11-27 官方页面核查", 14, PALE, box=(46, 330, 486, 362))

    p.rounded((574, 64, 846, 182), 18, fill=NAVY, outline=TEAL, width=2)
    p.text(596, 82, "图片", 18, CYAN, True, box=(590, 74, 830, 110))
    p.text(594, 112, "1K / 2K", 30, WHITE, True, box=(588, 104, 832, 150))
    p.text(596, 154, "输入费用按型号核查", 14, PALE, box=(590, 146, 832, 178))

    p.rounded((574, 202, 846, 320), 18, fill=NAVY, outline=CORAL, width=2)
    p.text(596, 220, "视频", 18, GOLD, True, box=(590, 212, 830, 248))
    p.text(594, 250, "5秒示例", 30, WHITE, True, box=(588, 242, 832, 290))
    p.text(596, 292, "规格、声音、输入逐项核对", 15, PALE, box=(590, 284, 832, 316))
    p.save(path)


def price_card(p, x, title, accent, rows, note):
    p.rounded((x, 198, x + 464, 486), 20, fill=WHITE, outline=LINE, width=2)
    p.text(x + 24, 216, title, 22, accent, True, box=(x + 18, 208, x + 446, 250))
    p.line([(x + 24, 254), (x + 440, 254)], LINE, 2)
    for i, (name, price) in enumerate(rows):
        y = 276 + i * 52
        p.text(x + 26, y, name, 24, NAVY, box=(x + 20, y - 8, x + 328, y + 36))
        p.text(x + 450, y, price, 26, accent, True, anchor="rt", box=(x + 300, y - 10, x + 454, y + 38))
    p.text(x + 26, 448, note, 16, MUTED, box=(x + 20, 438, x + 444, 474))


def figure(path):
    p = Panel((1080, 1120), PAPER)
    p.text(64, 38, "图片看规格，视频看条件", 44, NAVY, True, box=(58, 26, 1018, 100))
    p.text(66, 108, "官方 API 公开价｜2026-11-27｜人民币与美元分开看", 22, MUTED, box=(60, 98, 1018, 144))

    p.text(66, 158, "图片 · 1K 输出示例", 24, NAVY, True, box=(60, 148, 600, 192))
    price_card(p, 64, "人民币档 / 张", TEAL, [
        ("qwen-image-2.1-turbo", "¥0.10"),
        ("Seedream 5.0 Flash", "¥0.12"),
        ("wan2.7-image", "¥0.20"),
    ], "输入费用按具体型号核查")
    price_card(p, 552, "美元档 / 张", CORAL, [
        ("FLUX 3 Image Klein", "$0.009"),
        ("Nano Banana 2.1", "≈$0.0336"),
        ("FLUX 3 Image", "$0.048"),
    ], "Nano Banana 为图片输出估算")

    p.text(66, 520, "视频 · 5 秒输出示例", 24, NAVY, True, box=(60, 510, 700, 556))
    p.text(66, 554, "代表型号，分辨率、声音与购买条件见正文表", 18, MUTED, box=(60, 546, 1016, 584))
    p.rounded((64, 594, 1016, 804), 20, fill=WHITE, outline=LINE, width=2)
    p.text(92, 612, "模型", 18, MUTED, True, box=(86, 602, 410, 642))
    p.text(526, 612, "五秒输出", 18, MUTED, True, box=(520, 602, 706, 642))
    p.text(766, 612, "条件", 18, MUTED, True, box=(760, 602, 988, 642))
    p.line([(92, 646), (988, 646)], LINE, 2)
    rows = [
        ("MiniMax H3-Lite", "$0.20", "768P｜参考图≤5张"),
        ("Wan 2.6 I2V Flash", "¥1.50", "720P｜有声｜首帧不计"),
        ("Vidu Q3 Turbo", "≈¥1.88", "720P｜套餐 credit"),
    ]
    for i, (name, price, condition) in enumerate(rows):
        y = 668 + i * 44
        p.text(92, y, name, 24, NAVY, box=(86, y - 8, 410, y + 38))
        p.text(526, y, price, 28, TEAL, True, box=(520, y - 10, 718, y + 40))
        p.text(766, y, condition, 20, MUTED, box=(760, y - 8, 988, y + 40))

    p.rounded((64, 830, 1016, 1006), 22, fill=NAVY)
    p.text(92, 852, "完整账单按型号和任务核算", 24, CYAN, True, box=(86, 842, 988, 886))
    p.text(92, 900, "可能追加：输入视频、额外参考图、Draft/Enhance、重试", 22, WHITE, True, box=(86, 890, 988, 934))
    p.line([(92, 948), (988, 948)], TEAL, 2)
    p.text(92, 968, "错峰 ≠ 静音半价    套餐 ≠ 长期统一价    平台价 ≠ 官方直连价", 17, GOLD, True, box=(86, 958, 988, 996))

    p.text(66, 1030, "来源：阿里云、火山方舟、MiniMax、Vidu、可灵、BFL、Runway、OpenAI、Google 官方页面。", 16, MUTED, box=(60, 1020, 1020, 1054))
    p.text(66, 1060, "本图仅为费用示例；完整条件见正文，实际以请求规格、控制台账单及服务协议为准。", 16, MUTED, box=(60, 1050, 1020, 1086))
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
