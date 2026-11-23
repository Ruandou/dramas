"""Render 125 cover and figure with Pillow. Reads nothing; writes only the two PNGs."""

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
COVER = "封面_125_20261127_900x383.png"
FIGURE = "125_图1_海外入口_1080.png"

APPS = [
    "ReelShort",
    "DramaBox",
    "ShortMax",
    "GoodShort",
    "DramaWave",
    "PineDrama",
    "FlexTV",
    "MoboReels",
    "iDrama",
    "Vigloo",
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
    p.text(70, 56, "海外短剧分发 · 33 个 APP", 25, MINT, True, "lt", safe)
    p.text(68, 100, "0 个", 76, WHITE, True, "lt", safe)
    p.text(70, 196, "可投稿", 36, WHITE, True, "lt", safe)
    p.draw.rounded_rectangle((70, 266, 250, 272), radius=3, fill=MINT)
    p.text(70, 294, "23 个查不到自助入口", 24, "#B5C7C9", False, "lt", safe)
    p.text(70, 330, "能直接投的几乎没有", 22, MINT, True, "lt", safe)
    p.save(path)


def stat(p, box, number, label, note):
    x0, y0, x1, y1 = box
    p.draw.rounded_rectangle(box, 24, fill=WHITE, outline=LINE, width=2)
    p.text(x0 + 28, y0 + 22, number, 74, RUST, True,
           box=(x0 + 24, y0 + 22, x1 - 18, y0 + 112))
    p.text(x0 + 28, y0 + 120, label, 24, INK, True,
           box=(x0 + 24, y0 + 120, x1 - 18, y0 + 156))
    p.text(x0 + 28, y0 + 172, note, 21, MUTED,
           box=(x0 + 24, y0 + 172, x1 - 18, y0 + 222))


def figure(path):
    p = Panel((1080, 1240), PAPER)
    p.text(64, 44, "海外短剧分发 · 33 个 APP", 27, MUTED, True)
    p.text(62, 88, "0 个可投稿", 64, INK, True)
    p.text(64, 178, "23 个查不到自助入口；2 个待核", 28, MUTED)
    p.text(64, 218, "App Store 能搜到，不等于能投稿", 26, RUST, True)

    stat(p, (62, 270, 360, 520), "0", "可投稿", "清单里没有")
    stat(p, (375, 270, 673, 520), "23", "查不到自助入口", "APP 里最多")
    stat(p, (688, 270, 1018, 520), "2", "待核", "先别投")

    p.draw.rounded_rectangle((62, 560, 1018, 960), 24, fill=WHITE, outline=LINE, width=2)
    p.text(88, 582, "10 个主 APP：8 个 A 级、2 个 B 级", 28, INK, True)
    p.text(88, 624, "全部查不到公开投稿入口", 23, MUTED)
    for index, name in enumerate(APPS):
        column = index // 5
        row = index % 5
        p.text(
            88 + column * 460,
            676 + row * 48,
            name,
            25,
            INK,
            box=(84 + column * 460, 676 + row * 48, 540 + column * 460, 676 + row * 48 + 40),
        )

    p.draw.rounded_rectangle((62, 990, 1018, 1052), 18, fill=MINT)
    p.text(84, 1008, "Vigloo 12-07 截止；先选市场，再找入口。", 25, INK, True,
           box=(80, 1008, 1000, 1044))

    p.draw.line((64, 1090, 1014, 1090), fill=LINE, width=2)
    p.text(64, 1110, "数据：本号资料库，截至 2026-10-29；A20/B11/C2。", 21, MUTED,
           box=(60, 1110, 1020, 1150))
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
