"""Render 122 cover and figure with Pillow. Reads nothing; writes only the two PNGs."""

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
COVER = "封面_122_20261122_900x383.png"
FIGURE = "122_图1_产量注意力与榜位_1080.png"


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
    p.text(70, 58, "2026短剧供给", 26, MINT, True, "lt", safe)
    p.text(68, 108, "55万部", 74, WHITE, True, "lt", safe)
    p.text(70, 204, "94%是AI，榜上留不住", 36, WHITE, True, "lt", safe)
    p.draw.rounded_rectangle((70, 276, 250, 282), radius=3, fill=MINT)
    p.text(70, 304, "前10个月上线量", 25, "#B5C7C9", False, "lt", safe)
    p.save(path)


def stat(p, box, number, label, note, color=RUST):
    x0, y0, x1, y1 = box
    p.draw.rounded_rectangle(box, 24, fill=WHITE, outline=LINE, width=2)
    p.text(x0 + 30, y0 + 26, number, 58, color, True,
           box=(x0 + 26, y0 + 26, x1 - 20, y0 + 110))
    p.text(x0 + 30, y0 + 118, label, 27, INK, True,
           box=(x0 + 26, y0 + 118, x1 - 20, y0 + 160))
    p.text(x0 + 30, y0 + 176, note, 23, MUTED,
           box=(x0 + 26, y0 + 176, x1 - 20, y0 + 250))


def figure(path):
    p = Panel((1080, 1240), PAPER)
    p.text(64, 44, "2026短剧供给 · 公开数据整理", 27, MUTED, True)
    p.text(62, 88, "55万部，去哪了", 64, INK, True)
    p.text(64, 178, "产量上去了，注意力没有", 30, MUTED)

    stat(p, (62, 240, 520, 530), "55万", "前10个月上线",
         "是2025年全年的近17倍")
    stat(p, (560, 240, 1018, 530), "94%", "AI剧占比（前10个月）",
         "供给已经不是瓶颈")
    stat(p, (62, 560, 520, 850), "5%", "真人剧产量占比",
         "春节档播放是AI剧25倍")
    stat(p, (560, 560, 1018, 850), "2,428", "本号榜档剧目",
         "117个采样日；963部只出现1期")

    p.text(62, 900, "最近一天：新进18、掉出18。", 30, INK, True,
           box=(58, 900, 1010, 946))
    p.text(62, 948, "榜位是稀缺的，产量不是。", 30, MUTED,
           box=(58, 948, 1010, 994))

    p.draw.line((64, 1100, 1014, 1100), fill=LINE, width=2)
    p.text(64, 1120, "数据口径见正文；榜档为第三方转算，非平台官方。", 23, MUTED)
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
