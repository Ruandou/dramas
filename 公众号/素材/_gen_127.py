"""Render 127 cover and figure with Pillow. Reads nothing; writes only the two PNGs."""

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
COVER = "封面_127_20261124_900x383.png"
FIGURE = "127_图1_三条路_1080.png"


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
    p.text(70, 52, "抖音互动剧 / 影游", 25, MINT, True, "lt", safe)
    p.text(66, 94, "20", 82, WHITE, True, "lt", safe)
    p.text(176, 136, "万", 38, WHITE, True, "lt", safe)
    p.text(240, 140, "最高保底", 32, WHITE, True, "lt", safe)
    p.text(70, 196, "10 部精品 · S+/S/A 20/15/10", 22, "#B5C7C9", False, "lt", safe)
    p.text(70, 232, "30 分钟 / 90 分钟 两档门槛", 22, "#B5C7C9", False, "lt", safe)
    p.draw.rounded_rectangle((70, 276, 250, 282), radius=3, fill=MINT)
    p.text(70, 304, "12-31 报名截止", 23, MINT, True, "lt", safe)
    p.save(path)


def card(p, x, y, number, title, big, lines):
    p.draw.rounded_rectangle((x, y, x + 286, y + 380), 22, fill=WHITE, outline=LINE, width=2)
    p.text(x + 24, y + 18, number, 32, RUST, True,
           box=(x + 20, y + 16, x + 90, y + 60))
    p.text(x + 24, y + 64, title, 25, INK, True,
           box=(x + 20, y + 62, x + 270, y + 98))
    p.text(x + 24, y + 112, big, 29, RUST, True,
           box=(x + 20, y + 110, x + 270, y + 152))
    top = y + 174
    for line in lines:
        p.text(x + 24, top, line, 20, MUTED,
               box=(x + 20, top, x + 272, top + 30))
        top += 34


def figure(path):
    p = Panel((1080, 1240), PAPER)
    p.text(64, 44, "抖音集团短剧版权中心 · 11-12 官方", 27, MUTED, True)
    p.text(62, 88, "三条路", 64, INK, True)
    p.text(64, 178, "30 分钟 / 90 分钟 / 10 部精品", 28, RUST, True)
    p.text(64, 218, "20 万是最高档，不是报名就有", 24, MUTED)

    card(p, 62, 270, "01", "常规合作",
         "30 分钟+",
         ["非独家 · 纯分成", "优质有宣发/投放", "门槛最低"])
    card(p, 396, 270, "02", "IP 参投",
         "90 分钟+",
         ["番茄 IP 免采买", "或版权费补贴", "100% / 50%"])
    card(p, 730, 270, "03", "精品保底",
         "10 部",
         ["S+ 20 / S 15 / A 10 万", "独家 · 不叠加", "以合同为准"])

    p.draw.rounded_rectangle((62, 684, 1018, 842), 22, fill=WHITE, outline=LINE, width=2)
    p.text(88, 706, "两项激励", 27, INK, True,
           box=(84, 704, 500, 744))
    p.text(88, 754, "分成：+30%—50%（当月消费）", 23, MUTED,
           box=(84, 752, 1000, 786))
    p.text(88, 790, "投放：上线 30 天内达标，一次性奖金", 23, MUTED,
           box=(84, 788, 1000, 822))

    p.draw.rounded_rectangle((62, 876, 1018, 1008), 22, fill=MINT)
    p.text(88, 896, "11-1 报名开始 → 12-31 报名截止", 25, INK, True,
           box=(84, 894, 1000, 934))
    p.text(88, 942, "拿激励：12-31 前上线；IP 参投段写 2027-3-31", 21, INK,
           box=(84, 940, 1000, 972))
    p.text(88, 974, "两个上线日期官方文内不一致，报名前让商务确认", 20, MUTED,
           box=(84, 972, 1000, 1000))

    p.draw.line((64, 1040, 1014, 1040), fill=LINE, width=2)
    p.text(64, 1060, "来源：抖音集团短剧版权中心 11-12 官方文章；精品保底为政策图口径。", 21, MUTED,
           box=(60, 1058, 1020, 1098))
    p.text(64, 1098, "截至 2026-11-24；以官方表单与合同为准。", 21, MUTED,
           box=(60, 1096, 1020, 1134))
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
