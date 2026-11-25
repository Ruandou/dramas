"""Render 132 cover with Pillow. Reads nothing; writes one PNG."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
INK = "#132C35"
WHITE = "#FCFCF9"
MUTED = "#B5C7C9"
MINT = "#D9EDAD"
COVER = "封面_132_20261125_900x383.png"


class Panel:
    def __init__(self, size, background):
        self.image = Image.new("RGB", size, background)
        self.draw = ImageDraw.Draw(self.image)

    def text(self, x, y, value, size, color=INK, bold=False, anchor="lt", box=None):
        face = ImageFont.truetype(FONT, size, index=2 if bold else 0)
        left, top, right, bottom = self.draw.textbbox((x, y), value, font=face, anchor=anchor)
        bounds = box or (0, 0, *self.image.size)
        assert (
            bounds[0] <= left < right <= bounds[2]
            and bounds[1] <= top < bottom <= bounds[3]
        ), (value, (left, top, right, bottom), bounds)
        self.draw.text((x, y), value, font=face, fill=color, anchor=anchor)

    def save(self, path):
        with path.open("xb") as f:
            self.image.save(f, "PNG", optimize=True)


def cover(path):
    p = Panel((900, 383), INK)
    p.draw.rectangle((0, 0, 10, 383), fill=MINT)
    safe = (60, 16, 850, 368)
    p.text(70, 44, "广东 · 短剧出海", 25, MINT, True, "lt", safe)
    p.text(66, 86, "横琴补翻译 深圳补发行", 62, WHITE, True, "lt", safe)
    p.text(70, 180, "1.8 万家企业 · 94 个景", 30, MUTED, False, "lt", safe)
    p.draw.rounded_rectangle((70, 236, 300, 242), radius=3, fill=MINT)
    p.text(70, 262, "两套补贴，怎么选", 26, WHITE, True, "lt", safe)
    p.text(70, 310, "政策原文与申报门槛", 23, MINT, False, "lt", safe)
    p.save(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    output = parser.parse_args().output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    assert not (output / COVER).exists()
    cover(output / COVER)
    with Image.open(output / COVER) as image:
        print(COVER, image.size)


if __name__ == "__main__":
    main()
