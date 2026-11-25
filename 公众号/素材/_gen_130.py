"""Render 130 cover with Pillow. Reads nothing; writes one PNG."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
INK = "#132C35"
WHITE = "#FCFCF9"
MUTED = "#B5C7C9"
MINT = "#D9EDAD"
COVER = "封面_130_20261124_900x383.png"


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
    p.text(70, 44, "快手 · 抖音 · 天马", 25, MINT, True, "lt", safe)
    p.text(66, 86, "保底 3—30 万+", 62, WHITE, True, "lt", safe)
    p.text(70, 180, "数字之外，先算三个账本", 30, MUTED, False, "lt", safe)
    p.draw.rounded_rectangle((70, 236, 300, 242), radius=3, fill=MINT)
    p.text(70, 262, "门槛 / 结算 / 权利", 26, WHITE, True, "lt", safe)
    p.text(70, 310, "互动内容，怎么报", 23, MINT, False, "lt", safe)
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
