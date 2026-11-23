"""Render 123 cover and figure with Pillow. Reads nothing; writes only the two PNGs."""

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
COVER = "封面_123_20261123_900x383.png"
FIGURE = "123_图1_一个多月四波_1080.png"

LISTS = (
    ("11-10", "上海证券报", ["华智数媒", "华策影视", "慈文传媒", "掌阅科技", "引力传媒"], []),
    ("11-13", "证券时报", ["幸福蓝海", "华是科技", "横店影视"], []),
    (
        "11-23",
        "人民财讯 / 财闻",
        ["上海电影", "横店影视", "新炬网络", "浙文影业", "幸福蓝海", "海看股份", "果麦文化", "德才股份"],
        [],
    ),
)
REPEAT = {"横店影视", "幸福蓝海"}


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

    def names(self, x, y, names, size=30):
        face = font(size, False)
        sep_width = self.draw.textlength("、", font=face)
        for index, name in enumerate(names):
            color = RUST if name in REPEAT else INK
            self.draw.text((x, y), name, font=face, fill=color)
            x += self.draw.textlength(name, font=face)
            if index < len(names) - 1:
                self.draw.text((x, y), "、", font=face, fill=MUTED)
                x += sep_width
        return x

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
    p.text(70, 58, "AI短剧概念 · 2026-11-23", 26, MINT, True, "lt", safe)
    p.text(68, 104, "14个名字", 74, WHITE, True, "lt", safe)
    p.text(70, 200, "只有2只重复", 36, WHITE, True, "lt", safe)
    p.draw.rounded_rectangle((70, 272, 250, 278), radius=3, fill=MINT)
    p.text(70, 300, "三份行情稿并排，其余12个各出现一次", 24, "#B5C7C9", False, "lt", safe)
    p.save(path)


def figure(path):
    p = Panel((1080, 1240), PAPER)
    p.text(64, 44, "AI短剧概念 · 2026-11-23", 27, MUTED, True)
    p.text(62, 88, "14个名字，2只重复", 64, INK, True)
    p.text(64, 178, "三份行情稿并排：11-10 / 11-13 / 11-23", 28, MUTED)
    p.text(64, 218, "只有横店影视、幸福蓝海出现两次", 28, MUTED)

    p.draw.rounded_rectangle((62, 270, 1018, 720), 24, fill=WHITE, outline=LINE, width=2)
    rows = ((294, 330, 368), (424, 460, 498), (554, 590, 628))
    for (date, source, names, _), (date_y, source_y, names_y) in zip(LISTS, rows):
        p.text(84, date_y, date, 30, INK, True)
        p.text(84, source_y, source, 21, MUTED,
               box=(80, source_y, 980, source_y + 30))
        if len(names) > 5:
            p.names(84, names_y, names[:4], 30)
            p.names(84, names_y + 43, names[4:], 30)
        else:
            p.names(84, names_y, names, 30)
    p.draw.line((84, 410, 996, 410), fill=LINE, width=2)
    p.draw.line((84, 540, 996, 540), fill=LINE, width=2)

    p.draw.rounded_rectangle((62, 760, 1018, 1100), 24, fill=WHITE, outline=LINE, width=2)
    p.text(90, 786, "抽查：德才股份（605287）", 30, INK, True)
    p.text(90, 838, "1.9%", 76, RUST, True)
    p.text(90, 940, "AI漫剧孙公司营收 ÷ 公司营收", 26, INK, True,
           box=(86, 940, 520, 978))
    p.text(90, 982, "2,457.09 万 ÷ 12.86 亿", 24, MUTED,
           box=(86, 982, 520, 1018))
    p.text(90, 1032, "占比不到2%，同期还在亏损", 26, MUTED,
           box=(86, 1032, 520, 1070))

    p.draw.line((565, 826, 565, 1058), fill=LINE, width=2)
    p.text(600, 838, "净亏 562.17 万", 40, RUST, True,
           box=(596, 838, 996, 892))
    p.text(600, 902, "奇想无限 2026 上半年", 24, MUTED,
           box=(596, 902, 996, 934))
    p.text(600, 940, "营收 2,457.09 万", 24, INK,
           box=(596, 940, 996, 972))
    p.text(600, 982, "10-12 异动公告披露", 22, MUTED,
           box=(596, 982, 996, 1014))

    p.draw.line((64, 1140, 1014, 1140), fill=LINE, width=2)
    p.text(64, 1160, "名单来自行情稿，不是完整成分；财务数据来自公司公告与半年报。", 22, MUTED,
           box=(60, 1160, 1020, 1200))
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
