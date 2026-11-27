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
COVER = "封面_142_政策变剧情_20261127_r2_900x383.png"
FIGURE = "图1_142_剧情政策地图_20261127_r2_1080x1120.png"


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

    def ellipse(self, values, fill=None, outline=None, width=1):
        self.draw.ellipse(self.box(values), fill=fill, outline=outline, width=width * SCALE)

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
    p.text(52, 30, "政务 AI 短剧 · 案例拆解", 16, CYAN, True)
    p.text(48, 72, "政策变剧情", 52, WHITE, True, box=(42, 60, 470, 140))
    p.text(48, 138, "20集剧情拆解", 52, GOLD, True, box=(42, 126, 470, 206))
    p.line([(52, 218), (474, 218)], TEAL, 2)
    p.text(52, 240, "一集一个政策落点", 18, PALE, box=(46, 232, 478, 270))
    p.text(52, 278, "片尾15秒讲办事路径", 18, CYAN, True, box=(46, 270, 480, 314))
    p.text(52, 338, "一人短剧厂牌 · 2026-11-27 公开页面核查", 14, PALE, box=(46, 330, 486, 362))

    p.rounded((574, 64, 846, 182), 18, fill=NAVY, outline=TEAL, width=2)
    p.text(596, 82, "海淀惠企政策", 18, CYAN, True, box=(590, 74, 830, 110))
    p.text(594, 112, "20集", 30, WHITE, True, box=(588, 104, 832, 150))
    p.text(596, 154, "单集1—3分钟｜总约40分钟", 14, PALE, box=(590, 146, 832, 178))

    p.rounded((574, 202, 846, 320), 18, fill=NAVY, outline=CORAL, width=2)
    p.text(596, 220, "剧情节点", 18, GOLD, True, box=(590, 212, 830, 248))
    p.text(594, 250, "注册·算力", 26, WHITE, True, box=(588, 242, 832, 282))
    p.text(596, 286, "融资·法治·场景试点", 15, PALE, box=(590, 278, 832, 316))
    p.save(path)


def figure(path):
    p = Panel((1080, 1120), PAPER)
    p.text(64, 38, "20集剧情与政策落点地图", 44, NAVY, True, box=(58, 26, 1018, 100))
    p.text(66, 108, "海淀政策解读AI短剧｜官网剧集列表｜2026-11-27", 22, MUTED, box=(60, 98, 1018, 144))

    stages = [
        ("01", "起步与注册", "第1—4集", "OPC扶持｜创业就业一类事｜营业执照｜启动资金", TEAL),
        ("02", "算力与能力", "第5—10集", "弹性算力实验室｜AI工具平台｜OPC夜校｜路演", CORAL),
        ("03", "融资与补贴", "第11—13集", "财金协同平台｜融资担保与贴息｜安居与房租补贴", TEAL),
        ("04", "法治维权", "第14—18集", "反不正当竞争法｜商业诋毁｜证据固定｜12315", CORAL),
        ("05", "场景试点", "第19—20集", "创新应用场景专项｜政策兑现专区公示", TEAL),
    ]
    p.line([(112, 196), (112, 872)], LINE, 4)
    for i, (num, name, eps, policy, accent) in enumerate(stages):
        y = 176 + i * 148
        p.ellipse((96, y + 40, 128, y + 72), fill=accent)
        p.text(112, y + 56, num, 16, WHITE, True, anchor="mm", box=(96, y + 40, 128, y + 72))
        p.rounded((160, y, 1016, y + 128), 18, fill=WHITE, outline=LINE, width=2)
        p.text(184, y + 18, name, 26, NAVY, True, box=(178, y + 10, 620, y + 54))
        p.text(992, y + 20, eps, 22, accent, True, anchor="rt", box=(700, y + 12, 996, y + 52))
        p.line([(184, y + 62), (992, y + 62)], LINE, 2)
        p.text(184, y + 78, policy, 20, MUTED, box=(178, y + 70, 996, y + 112))

    p.rounded((64, 930, 1016, 1064), 22, fill=NAVY)
    p.text(92, 950, "可复用的是编排，不是霸总外壳", 24, CYAN, True, box=(86, 942, 988, 986))
    p.text(92, 996, "一集一个创业冲突＋片尾15秒办事路径；备案与AI标识需单独核", 21, WHITE, True, box=(86, 988, 988, 1030))
    p.text(92, 1034, "分发：政务矩阵＋红果等商业平台（官方口径，播放/分账未公开）", 16, GOLD, True, box=(86, 1026, 988, 1058))

    p.text(66, 1082, "来源：海淀区政府官网专题剧集列表；科技日报、北京商报、北京海淀官方发布。未观看全集，未核红果端片单与播放。", 15, MUTED, box=(60, 1074, 1020, 1108))
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