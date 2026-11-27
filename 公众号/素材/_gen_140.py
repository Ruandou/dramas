from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
SCALE = 2
NAVY = "#102A31"
DEEP = "#173D43"
TEAL = "#167C80"
CYAN = "#65D1C5"
CORAL = "#E67B5A"
WHITE = "#FFFFFF"
PAPER = "#F2F4F1"
MUTED = "#5F7072"
PALE = "#C7D7D3"
LINE = "#D9E4E0"
GOLD = "#E9B44C"
COVER = "封面_140_剧本采购地图_20261127_r2_900x383.png"
FIGURE = "图1_140_四条采购路线_20261127_r2_1080x1120.png"


class Panel:
    def __init__(self, size, background):
        self.size = size
        self.image = Image.new("RGB", tuple(v * SCALE for v in size), background)
        self.draw = ImageDraw.Draw(self.image)

    def box(self, values):
        return tuple(round(v * SCALE) for v in values)

    def points(self, values):
        return [tuple(round(v * SCALE) for v in point) for point in values]

    def rounded(self, values, radius, fill=None, outline=None, width=1):
        self.draw.rounded_rectangle(
            self.box(values), radius=radius * SCALE, fill=fill, outline=outline, width=width * SCALE
        )

    def line(self, values, color, width=2):
        self.draw.line(self.points(values), fill=color, width=width * SCALE, joint="curve")

    def polygon(self, values, color):
        self.draw.polygon(self.points(values), fill=color)

    def text(self, x, y, value, size, color, bold=False, anchor="lt", box=None):
        font = ImageFont.truetype(FONT, size * SCALE, index=2 if bold else 0)
        bounds = self.draw.textbbox((x * SCALE, y * SCALE), value, font=font, anchor=anchor)
        safe = self.box(box or (0, 0, *self.size))
        assert (
            safe[0] <= bounds[0] < bounds[2] <= safe[2]
            and safe[1] <= bounds[1] < bounds[3] <= safe[3]
        ), (value, bounds, safe)
        self.draw.text((x * SCALE, y * SCALE), value, font=font, fill=color, anchor=anchor)

    def save(self, path):
        with path.open("xb") as stream:
            self.image.resize(self.size, Image.Resampling.LANCZOS).save(stream, "PNG", optimize=True)


def cover(path):
    p = Panel((900, 383), NAVY)
    p.polygon([(548, 0), (900, 0), (900, 383), (500, 383)], DEEP)
    p.text(52, 30, "短剧制作 · 采购地图", 16, GOLD, True)
    p.text(48, 72, "先找路线", 52, WHITE, True, box=(42, 60, 470, 140))
    p.text(48, 138, "再签权限", 52, CORAL, True, box=(42, 126, 470, 206))
    p.line([(52, 218), (474, 218)], TEAL, 2)
    p.text(52, 240, "成品 / 定制 / 小说改编 / 公版", 18, PALE, box=(46, 232, 478, 270))
    p.text(52, 278, "能读、能下载，不等于能拍能发行", 16, CYAN, True, box=(46, 270, 480, 308))
    p.text(52, 338, "一人短剧厂牌 · 2026-11-27 公开页面核查", 14, PALE, box=(46, 330, 486, 362))

    items = [
        ("01", "成品剧本", "完整稿＋约定授权"),
        ("02", "委托定制", "试稿、修改与验收"),
        ("03", "小说改编权", "书面 IP 许可"),
        ("04", "公版与样稿", "研究用途与版本边界"),
    ]
    for i, (num, title, sub) in enumerate(items):
        y = 48 + i * 72
        p.rounded((574, y, 846, y + 58), 14, fill=NAVY, outline=TEAL, width=2)
        p.text(592, y + 29, num, 16, GOLD, True, anchor="lm", box=(586, y + 8, 626, y + 50))
        p.text(636, y + 8, title, 20, WHITE, True, box=(630, y + 2, 836, y + 34))
        p.text(636, y + 34, sub, 16, PALE, box=(630, y + 28, 836, y + 54))
    p.save(path)


def route_card(p, x, y, num, title, accent, rows):
    p.rounded((x, y, x + 464, y + 246), 22, fill=WHITE, outline=LINE, width=2)
    p.rounded((x + 24, y + 24, x + 82, y + 82), 16, fill=accent)
    p.text(x + 53, y + 53, num, 20, WHITE, True, anchor="mm", box=(x + 28, y + 28, x + 78, y + 78))
    p.text(x + 100, y + 28, title, 30, NAVY, True, box=(x + 94, y + 18, x + 444, y + 76))
    p.line([(x + 24, y + 98), (x + 440, y + 98)], LINE, 2)
    for i, (label, value) in enumerate(rows):
        yy = y + 122 + i * 62
        p.text(x + 26, yy, label, 20, accent, True, box=(x + 20, yy - 8, x + 94, yy + 34))
        p.text(x + 100, yy - 1, value, 26, NAVY, box=(x + 94, yy - 10, x + 444, yy + 42))


def figure(path):
    p = Panel((1080, 1120), PAPER)
    p.text(64, 38, "四条剧本采购路线", 46, NAVY, True, box=(58, 26, 1018, 102))
    p.text(66, 108, "交付物不同，授权边界也不同", 22, MUTED, box=(60, 98, 1018, 142))

    route_card(p, 64, 158, "01", "成品剧本", TEAL, [
        ("拿到", "完整稿＋约定授权"),
        ("先核", "全本、修改记录、发行权限"),
    ])
    route_card(p, 552, 158, "02", "委托定制", CORAL, [
        ("拿到", "大纲、分集、修改稿"),
        ("先核", "试稿、轮次、验收标准"),
    ])
    route_card(p, 64, 432, "03", "小说改编权", TEAL, [
        ("拿到", "具体作品的书面许可"),
        ("先核", "作品、权利、平台与期限"),
    ])
    route_card(p, 552, 432, "04", "公版与样稿", CORAL, [
        ("用途", "学习结构、研究故事"),
        ("先核", "原作、现代版本、使用边界"),
    ])

    p.rounded((64, 714, 1016, 992), 22, fill=NAVY)
    p.text(92, 742, "付款前，再拆开两类凭证", 26, CYAN, True, box=(86, 732, 988, 778))
    p.line([(92, 790), (988, 790)], TEAL, 2)
    p.text(92, 820, "会员费 / 联系方式费", 22, GOLD, True, box=(86, 810, 474, 852))
    p.text(512, 818, "≠ 剧本授权费", 28, WHITE, True, box=(506, 806, 988, 856))
    p.text(92, 888, "存证 / 实名 / 备案标识", 20, GOLD, True, box=(86, 878, 474, 922))
    p.text(512, 884, "≠ 权利链已查清", 28, WHITE, True, box=(506, 874, 988, 926))

    p.text(
        66,
        1030,
        "来源：华语剧本网、万众编剧网、抖几句、小说版权入口、国家图书馆及著作权法。",
        16,
        MUTED,
        box=(60, 1020, 1020, 1054),
    )
    p.text(
        66,
        1060,
        "本图只区分采购路线；具体作品能否拍、改、发行，以权利文件和合同为准。",
        16,
        MUTED,
        box=(60, 1050, 1020, 1086),
    )
    p.save(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    output = parser.parse_args().output.resolve()
    assert output.is_dir(), output
    targets = [output / COVER, output / FIGURE]
    assert all(not path.exists() for path in targets), "Refusing to overwrite images"
    cover(targets[0])
    figure(targets[1])
    for path, expected in zip(targets, [(900, 383), (1080, 1120)]):
        with Image.open(path) as image:
            image.load()
            assert image.size == expected
            assert image.mode == "RGB"
        print(path.name, expected, path.stat().st_size)


if __name__ == "__main__":
    main()
