"""Render 126 cover and figure with Pillow. Reads nothing; writes only the two PNGs."""

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
COVER = "封面_126_20261124_900x383.png"
FIGURE = "126_图1_350分钟_1080.png"


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
    p.text(70, 52, "《大话西游》改互动影游", 25, MINT, True, "lt", safe)
    p.text(66, 94, "30", 82, WHITE, True, "lt", safe)
    p.text(190, 136, "天", 38, WHITE, True, "lt", safe)
    p.text(70, 196, "横店 · 预计 12 月中旬开机（招募图）", 22, "#B5C7C9", False, "lt", safe)
    p.draw.rounded_rectangle((70, 250, 250, 256), radius=3, fill=MINT)
    p.text(70, 278, "短剧团队能接哪段？", 24, "#B5C7C9", False, "lt", safe)
    p.text(70, 316, "先看三道门槛", 23, MINT, True, "lt", safe)
    p.save(path)


def gate(p, x, y, number, title, lines):
    p.draw.rounded_rectangle((x, y, x + 286, y + 250), 20, fill=WHITE, outline=LINE, width=2)
    p.text(x + 24, y + 20, number, 34, RUST, True,
           box=(x + 20, y + 18, x + 90, y + 68))
    p.text(x + 24, y + 72, title, 26, INK, True,
           box=(x + 20, y + 70, x + 270, y + 110))
    top = y + 124
    for line in lines:
        p.text(x + 24, top, line, 20, MUTED,
               box=(x + 20, top, x + 272, top + 32))
        top += 36


def figure(path):
    p = Panel((1080, 1240), PAPER)
    p.text(64, 44, "《大话西游》官宣 · 天坑 11-24 上线", 27, MUTED, True)
    p.text(62, 88, "350 分钟", 64, INK, True)
    p.text(64, 178, "天坑：5 章 · 6 万+ 愿望单 · Demo 98% 好评", 24, MUTED)
    p.text(64, 214, "大话西游：横店 · 30 天 · 预计 12 月中旬开机（招募图）", 23, MUTED)
    p.text(64, 246, "短剧团队能接哪段？先看三道门槛", 25, RUST, True)

    p.draw.rounded_rectangle((62, 284, 1018, 634), 24, fill=WHITE, outline=LINE, width=2)
    p.text(88, 306, "成片时长：350 分钟 vs 129 分钟", 27, INK, True,
           box=(84, 304, 1000, 344))
    p.text(88, 358, "互动影游 · 5 章", 22, INK,
           box=(84, 356, 600, 388))
    p.draw.rounded_rectangle((88, 392, 788, 438), 10, fill=MINT)
    p.text(806, 396, "350 分钟", 24, INK, True,
           box=(800, 394, 1000, 438))
    p.text(88, 466, "86 集短剧 · 每集 90 秒", 22, INK,
           box=(84, 464, 600, 496))
    p.draw.rounded_rectangle((88, 500, 346, 546), 10, fill=LINE)
    p.text(364, 504, "129 分钟", 24, INK, True,
           box=(358, 502, 600, 546))
    p.text(88, 570, "约 2.7 部短剧；多结局、可重玩", 21, MUTED,
           box=(84, 568, 1000, 600))
    p.text(88, 602, "AI 资产 <1%，用于场景概念/异象/边界", 21, MUTED,
           box=(84, 600, 1000, 630))

    p.text(64, 650, "接活前，先过三道门槛", 28, INK, True,
           box=(60, 648, 800, 688))
    gate(p, 62, 700, "01", "剧本",
         ["3 个选择点、2 个结局", "写不出选择—后果—回收", "先别接主控"])
    gate(p, 397, 700, "02", "预算",
         ["350 分钟成片", "单分钟数万（受访口径）", "无发行伙伴，不主投"])
    gate(p, 732, 700, "03", "发行",
         ["Steam / 互影派", "谁发行、怎么结算", "有没有保底，先问清"])

    p.draw.rounded_rectangle((62, 1000, 1018, 1062), 18, fill=MINT)
    p.text(84, 1018, "三项缺两项，先从编剧或承制接活。", 25, INK, True,
           box=(80, 1016, 1000, 1056))

    p.draw.line((64, 1100, 1014, 1100), fill=LINE, width=2)
    p.text(64, 1120, "数据：Steam 页、证券日报/观点网、游戏茶馆/虎嗅；截至 2026-11-23。", 21, MUTED,
           box=(60, 1118, 1020, 1158))
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
