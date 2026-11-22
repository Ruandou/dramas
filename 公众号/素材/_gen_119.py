"""Render 119 cover and figure with Pillow. Reads nothing; writes only the two PNGs."""

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
COVER = "封面_119_20261122_900x383.png"
FIGURE = "119_图1_两条申报路径_1080.png"


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
    p.text(70, 58, "AI短剧扶持", 26, MINT, True, "lt", safe)
    p.text(68, 108, "单部最高30万", 74, WHITE, True, "lt", safe)
    p.text(70, 208, "抓马剧场 · 12月31日截止", 36, WHITE, True, "lt", safe)
    p.draw.rounded_rectangle((70, 276, 250, 282), radius=3, fill=MINT)
    p.text(70, 304, "现金15万＋积分15万，分开算", 25, "#B5C7C9", False, "lt", safe)
    p.save(path)


def figure(path):
    p = Panel((1080, 1240), PAPER)
    p.text(64, 44, "抓马剧场 · 官方规则图整理", 27, MUTED, True)
    p.text(62, 88, "两条申报路径", 64, INK, True)
    p.text(64, 178, "先看手里有没有已经上线的剧", 30, MUTED)

    # 已上线：爆款档
    p.draw.rounded_rectangle((62, 240, 1018, 726), 24, fill=WHITE, outline=LINE, width=2)
    p.draw.rounded_rectangle((92, 268, 244, 316), 13, fill=PALE)
    p.text(112, 279, "已上线", 29, INK, True)
    p.text(268, 276, "爆款档：按单部数据对档", 29, MUTED, True)
    tiers = (
        ("红果≥8000万 或 TikTok≥1亿", "15万现金＋15万积分", INK),
        ("红果6000万—8000万 或 TikTok6000万—1亿", "5万现金＋5万积分", INK),
        ("红果5000万—6000万 或 TikTok2500万—6000万", "1.5万现金＋1.5万积分", INK),
    )
    y = 344
    for line, reward, color in tiers:
        p.text(94, y, line, 27, color, True, box=(90, y, 1000, y + 42))
        p.text(94, y + 40, reward, 30, RUST, True, box=(90, y + 40, 1000, y + 86))
        y += 122
    p.text(94, 676, "抖音、YouTube、河马剧场等：综合评审定档", 25, MUTED,
           box=(90, 676, 1000, 716))

    # 未上线：精品IP专项
    p.draw.rounded_rectangle((62, 760, 1018, 1060), 24, fill=WHITE, outline=LINE, width=2)
    p.draw.rounded_rectangle((92, 788, 244, 836), 13, fill=PALE)
    p.text(112, 799, "未上线", 29, INK, True)
    p.text(268, 796, "精品IP专项：按项目评审", 29, MUTED, True)
    for i, item in enumerate(("剧本或样片", "IP权属", "制作发行计划")):
        p.text(94, 862 + i * 46, "· " + item, 28, INK, True,
               box=(90, 862 + i * 46, 1000, 862 + i * 46 + 42))
    p.text(94, 1000, "不需要已有上线播放数据", 27, RUST, True,
           box=(90, 1000, 1000, 1044))

    p.draw.line((64, 1094, 1014, 1094), fill=LINE, width=2)
    p.text(64, 1118, "金额为「现金＋等值积分」，积分非现金；", 25, MUTED)
    p.text(64, 1156, "档位仅列爆款档，机构档与报名入口以官网细则为准。", 25, MUTED)
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
