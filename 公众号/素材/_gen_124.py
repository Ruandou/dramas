"""Render 124 cover and figure with Pillow. Reads nothing; writes only the two PNGs."""

from __future__ import annotations

import argparse
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
PAPER = "#F2F2EC"
WHITE = "#FCFCF9"
INK = "#132C35"
MUTED = "#486269"
LINE = "#CAD7D3"
MINT = "#D9EDAD"
RUST = "#B0503C"
COVER = "封面_124_20261123_900x383.png"
FIGURE = "124_图1_十个入口_1080.png"

OPEN = [
    "抖音（红果/番茄）",
    "快手星芒",
    "腾讯十分",
    "优酷",
    "爱奇艺微剧",
    "微信视频号",
    "微信小程序",
    "B站",
    "百家号",
    "七猫",
]
REVIEW = [
    "芒果大芒",
    "咪咕",
    "点众双十亿",
    "麦芽",
    "山海",
    "阅文",
    "番茄（IP）",
    "中文在线",
]


@lru_cache
def font(size: int, bold: bool = False):
    return ImageFont.truetype(FONT, size, index=2 if bold else 0)


class Panel:
    def __init__(self, size, background):
        self.image = Image.new("RGB", size, background)
        self.draw = ImageDraw.Draw(self.image)

    def text(self, x, y, value, size, color=INK, bold=False, anchor="lt", box=None):
        face = font(size, bold)
        left, top, right, bottom = self.draw.textbbox(
            (x, y), value, font=face, anchor=anchor
        )
        bounds = box or (0, 0, *self.image.size)
        assert (
            bounds[0] <= left < right <= bounds[2]
            and bounds[1] <= top < bottom <= bounds[3]
        ), (value, (left, top, right, bottom), bounds)
        self.draw.text((x, y), value, font=face, fill=color, anchor=anchor)

    def grid(self, x, y, names, size=26, gap=45, per_column=5):
        for index, name in enumerate(names):
            column = index // per_column
            row = index % per_column
            left = x + column * 460
            self.text(
                left,
                y + row * gap,
                name,
                size,
                INK,
                box=(left - 4, y + row * gap, left + 450, y + row * gap + 40),
            )

    def save(self, path):
        with path.open("xb") as f:
            self.image.save(f, "PNG", optimize=True)
        with Image.open(path) as image:
            assert image.size == self.image.size
            image.verify()


def cover(path):
    p = Panel((900, 383), INK)
    p.draw.rectangle((0, 0, 10, 383), fill=MINT)
    safe = (60, 20, 846, 364)
    p.text(70, 56, "短剧分发 · 国内 40 个平台", 25, MINT, True, "lt", safe)
    p.text(68, 100, "10 个", 76, WHITE, True, "lt", safe)
    p.text(70, 196, "有公开入口", 36, WHITE, True, "lt", safe)
    p.draw.rounded_rectangle((70, 266, 250, 272), radius=3, fill=MINT)
    p.text(70, 294, "8 个要过会，其余采买/带货/待核", 24, "#B5C7C9", False, "lt", safe)
    p.text(70, 330, "可投稿 ≠ 自主上架", 22, MINT, True, "lt", safe)
    p.save(path)


def figure(path):
    p = Panel((1080, 1240), PAPER)
    p.text(64, 44, "短剧分发 · 国内 40 个平台", 27, MUTED, True)
    p.text(62, 88, "10 个有公开入口", 64, INK, True)
    p.text(64, 178, "8 个要过会；其余采买/带货/待核", 28, MUTED)
    p.text(64, 218, "可投稿 ≠ 自主上架", 26, RUST, True)

    p.draw.rounded_rectangle((62, 270, 1018, 660), 24, fill=WHITE, outline=LINE, width=2)
    p.text(88, 292, "10 个公开入口", 30, RUST, True)
    p.text(88, 334, "有公开后台/邮箱的入口", 23, MUTED)
    p.grid(88, 380, OPEN)

    p.draw.rounded_rectangle((62, 690, 1018, 1010), 24, fill=WHITE, outline=LINE, width=2)
    p.text(88, 712, "8 个要过会", 30, RUST, True)
    p.text(88, 754, "公开征集/商务对接，不是自助上架", 23, MUTED)
    p.grid(88, 800, REVIEW, gap=43, per_column=4)

    p.draw.rounded_rectangle((62, 1040, 1018, 1098), 18, fill=MINT)
    p.text(84, 1056, "把剧本群发给采买渠道，是最常见的白费功夫。", 25, INK, True,
           box=(80, 1056, 1000, 1090))

    p.draw.line((64, 1130, 1014, 1130), fill=LINE, width=2)
    p.text(64, 1150, "数据：本号资料库，截至 2026-10-29；平台政策月度变，签约前复核。", 21, MUTED,
           box=(60, 1150, 1020, 1190))
    p.save(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    output = parser.parse_args().output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    assert not any((output / x).exists() for x in (COVER, FIGURE))
    cover(output / COVER)
    figure(output / FIGURE)
    for name in (COVER, FIGURE):
        with Image.open(output / name) as image:
            print(name, image.size)


if __name__ == "__main__":
    main()
