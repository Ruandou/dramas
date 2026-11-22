"""Render 120 cover and figure with Pillow. Reads nothing; writes only the two PNGs."""

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
PALE = "#DDEAE3"
MINT = "#D9EDAD"
RUST = "#B0503C"
COVER = "封面_120_20261122_900x383.png"
FIGURE = "120_图1_50万奖金分档_1080.png"


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
    safe = (64, 24, 840, 360)
    p.text(70, 58, "网文大赛", 26, MINT, True, "lt", safe)
    p.text(68, 108, "单部50万", 74, WHITE, True, "lt", safe)
    p.text(70, 208, "30万现金＋20万看落地", 36, WHITE, True, "lt", safe)
    p.draw.rounded_rectangle((70, 276, 250, 282), radius=3, fill=MINT)
    p.text(70, 304, "征稿至2027年8月31日", 25, "#B5C7C9", False, "lt", safe)
    p.save(path)


def figure(path):
    p = Panel((1080, 1240), PAPER)
    p.text(64, 44, "天e网络文学大赛 · 官方征稿启事整理", 27, MUTED, True)
    p.text(62, 88, "单部50万，怎么分", 64, INK, True)
    p.text(64, 178, "30万基础奖金 ＋ 20万IP改编/海外传播基金", 30, MUTED)

    p.draw.rounded_rectangle((62, 240, 1018, 348), 22, fill=WHITE, outline=LINE, width=2)
    p.text(94, 258, "30万", 54, RUST, True, box=(90, 258, 360, 330))
    p.text(250, 268, "基础奖金，获奖后全额发放", 30, INK, True,
           box=(240, 268, 760, 318))
    p.text(760, 276, "税前，代扣个税", 23, MUTED, box=(755, 276, 1000, 316))

    p.draw.rounded_rectangle((62, 376, 1018, 1090), 24, fill=WHITE, outline=LINE, width=2)
    p.text(94, 404, "20万专项基金：看短剧和出海", 34, INK, True,
           box=(90, 404, 1000, 452))

    rows = (
        ("没短剧、没出海", "作者0，组委会用于改编和宣发"),
        ("只完成国内短剧改编（含AI）", "作者10万，10万用于海外宣发"),
        ("有海外平台连载和完整外译", "作者10万，10万用于短剧改编"),
        ("短剧＋海外都落地", "20万全给作者，自由支配"),
    )
    y = 480
    for i, (condition, result) in enumerate(rows):
        if i:
            p.draw.line((94, y - 18, 986, y - 18), fill=LINE, width=2)
        p.text(96, y, condition, 28, INK, True, box=(90, y, 1000, y + 44))
        p.text(96, y + 46, result, 30, RUST, True, box=(90, y + 46, 1000, y + 96))
        y += 146

    p.draw.line((64, 1112, 1014, 1112), fill=LINE, width=2)
    p.text(64, 1134, "两个赛道各1部，共2部；征稿至2027-08-31。", 25, MUTED)
    p.text(64, 1172, "AI短剧可作改编材料、须注明；纯AI文学禁赛。", 25, MUTED)
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
