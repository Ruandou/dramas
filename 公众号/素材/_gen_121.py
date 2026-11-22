"""Render 121 cover and figure with Pillow. Reads nothing; writes only the two PNGs."""

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
COVER = "封面_121_20261122_900x383.png"
FIGURE = "121_图1_三种支持别混_1080.png"


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
    p.text(70, 58, "AIGC视听扶持", 26, MINT, True, "lt", safe)
    p.text(68, 108, "最高10万Token", 66, WHITE, True, "lt", safe)
    p.text(70, 204, "申报入口还没开", 40, WHITE, True, "lt", safe)
    p.draw.rounded_rectangle((70, 276, 250, 282), radius=3, fill=MINT)
    p.text(70, 304, "截至2026-11-22，细则未发布", 24, "#B5C7C9", False, "lt", safe)
    p.save(path)


def card(p, top, badge, title, line1, line2, status):
    p.draw.rounded_rectangle((62, top, 1018, top + 296), 24, fill=WHITE, outline=LINE, width=2)
    p.draw.rounded_rectangle((92, top + 28, 236, top + 72), 12, fill=PALE)
    p.text(112, top + 37, badge, 25, INK, True, box=(108, top + 37, 232, top + 70))
    p.text(260, top + 34, title, 31, INK, True, box=(256, top + 34, 1000, top + 78))
    p.text(94, top + 96, line1, 27, MUTED, box=(90, top + 96, 1000, top + 138))
    p.text(94, top + 142, line2, 27, MUTED, box=(90, top + 142, 1000, top + 184))
    p.text(94, top + 216, status, 28, RUST, True, box=(90, top + 216, 1000, top + 264))


def figure(path):
    p = Panel((1080, 1240), PAPER)
    p.text(64, 44, "北京AIGC视听扶持 · 公开信息整理", 27, MUTED, True)
    p.text(62, 88, "三种支持，别混", 64, INK, True)
    p.text(64, 178, "最高10万Token，但申报入口还没开", 30, MUTED)

    card(p, 240, "11-20", "算力扶持计划",
         "最高10万Token；面向好作品、好项目",
         "另一项面向超创、OPC、内容企业",
         "仅发布，未见申报指南")
    card(p, 560, "2025", "朝阳政策12条",
         "与创新中心签约的生态伙伴",
         "开放算力测试资源，购买算力给支持",
         "签约或对接制")
    card(p, 880, "2026-07", "平台伙伴征集",
         "面向平台型企业，不是普通制作团队",
         "要营业执照、完税证明等企业材料",
         "按通知申报")

    p.draw.line((64, 1192, 1014, 1192), fill=LINE, width=2)
    p.text(64, 1204, "Token不是现金；使用平台与折算方式未公布。", 23, MUTED)
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
