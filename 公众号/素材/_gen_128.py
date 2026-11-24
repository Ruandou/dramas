"""Render 128 cover and branch figure with Pillow. Reads nothing; writes only the two PNGs."""

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
COVER = "封面_128_20261124c_900x383.png"
FIGURE = "128_图1_一条主线三个分叉_1080.png"


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
    safe = (60, 20, 850, 364)
    p.text(70, 52, "《天坑追匪》· 互动剧", 25, MINT, True, "lt", safe)
    p.text(66, 94, "5 章", 76, WHITE, True, "lt", safe)
    p.text(228, 132, "约 350 分钟", 34, WHITE, True, "lt", safe)
    p.text(70, 196, "一条主线，三个分叉", 26, "#B5C7C9", False, "lt", safe)
    p.draw.rounded_rectangle((70, 250, 250, 256), radius=3, fill=MINT)
    p.text(70, 278, "互动剧到底怎么互动", 24, "#B5C7C9", False, "lt", safe)
    p.text(70, 316, "文末有 B 站实机演示", 23, MINT, True, "lt", safe)
    p.save(path)


def figure(path):
    p = Panel((1080, 1240), PAPER)
    p.text(64, 44, "互动剧 · 分叉结构", 27, MUTED, True)
    p.text(62, 88, "一条主线，三个分叉", 56, INK, True)
    p.text(64, 170, "每个选择点都要有代价；结局要能回收前面的伏笔", 24, RUST, True,
           box=(60, 168, 1020, 206))

    top, bottom = 300, 900
    mid = 600
    p.draw.line((120, mid, 300, mid), fill=INK, width=4)
    p.draw.ellipse((104, mid - 10, 124, mid + 10), fill=INK)
    p.text(70, mid - 52, "开场", 22, MUTED, True)
    p.text(70, mid + 18, "第 1 章", 20, MUTED)

    ys = (top, mid, bottom)
    labels = ("选 A：追进密林", "选 B：留下守夜", "选 C：先查脚印")
    ends = ("结局 1", "结局 2", "结局 3")
    for i, (y, label, end) in enumerate(zip(ys, labels, ends)):
        p.draw.line((300, mid, 420, mid), fill=INK, width=3)
        p.draw.line((420, mid, 620, y), fill=INK, width=3)
        p.draw.rounded_rectangle((620, y - 46, 900, y + 46), 14, fill=WHITE, outline=LINE, width=2)
        p.text(644, y - 24, label, 26, INK, True,
               box=(640, y - 26, 890, y + 8))
        p.text(644, y + 8, "后面要还的选择", 19, MUTED,
               box=(640, y + 6, 890, y + 34))
        p.draw.line((900, y, 950, y), fill=INK, width=3)
        p.text(960, y - 14, end, 21, RUST, True,
               box=(956, y - 18, 1040, y + 14))

    p.text(64, 960, "选 A 和选 B 是两条素材；演员按不同选择下的情绪各演一遍。", 22, MUTED,
           box=(60, 958, 1020, 994))
    p.text(64, 998, "只换台词、不换后果的，是伪分支。", 22, RUST, True,
           box=(60, 996, 1020, 1032))

    p.draw.line((64, 1060, 1014, 1060), fill=LINE, width=2)
    p.text(64, 1080, "示意结构，不代表《天坑追匪》实际分支数。", 21, MUTED,
           box=(60, 1078, 1020, 1114))
    p.text(64, 1118, "官方口径：5 章约 350 分钟，多结局、可重玩。", 21, MUTED,
           box=(60, 1116, 1020, 1152))
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
