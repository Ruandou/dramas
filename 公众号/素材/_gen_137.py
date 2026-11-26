from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
SCALE = 2
NAVY = "#102A31"
DEEP = "#14383F"
TEAL = "#167C80"
CYAN = "#65D1C5"
CORAL = "#E67B5A"
WHITE = "#FFFFFF"
PAPER = "#F2F4F1"
MUTED = "#5F7072"
PALE = "#C7D7D3"
LINE = "#D9E4E0"
GOLD = "#E9B44C"
SOFT = "#BEE6DF"
COVER = "封面_137_20261126_900x383.png"
FIGURE = "图1_137_奖励包拆解_1080x1120.png"


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
        self.draw.rounded_rectangle(self.box(values), radius=radius * SCALE, fill=fill, outline=outline, width=width * SCALE)

    def ellipse(self, values, fill=None, outline=None, width=1):
        self.draw.ellipse(self.box(values), fill=fill, outline=outline, width=width * SCALE)

    def line(self, values, color, width=2):
        self.draw.line(self.points(values), fill=color, width=width * SCALE, joint="curve")

    def polygon(self, values, color):
        self.draw.polygon(self.points(values), fill=color)

    def text(self, x, y, value, size, color, bold=False, anchor="lt", box=None):
        font = ImageFont.truetype(FONT, size * SCALE, index=2 if bold else 0)
        bounds = self.draw.textbbox((x * SCALE, y * SCALE), value, font=font, anchor=anchor)
        safe = self.box(box or (0, 0, *self.size))
        assert safe[0] <= bounds[0] < bounds[2] <= safe[2] and safe[1] <= bounds[1] < bounds[3] <= safe[3], (value, bounds, safe)
        self.draw.text((x * SCALE, y * SCALE), value, font=font, fill=color, anchor=anchor)

    def width(self, value, size, bold=False):
        font = ImageFont.truetype(FONT, size * SCALE, index=2 if bold else 0)
        return self.draw.textlength(value, font=font) / SCALE

    def chip(self, x, y, value, size=13, fill=WHITE, outline=LINE, fg=NAVY, bold=True, height=30, pad=10):
        w = self.width(value, size, bold) + pad * 2
        self.rounded((x, y, x + w, y + height), height / 2, fill=fill, outline=outline, width=2)
        self.text(x + w / 2, y + height / 2, value, size, fg, bold, anchor="mm")
        return w

    def save(self, path):
        with path.open("xb") as stream:
            self.image.resize(self.size, Image.Resampling.LANCZOS).save(stream, "PNG", optimize=True)


def cover(path):
    p = Panel((900, 383), NAVY)
    p.polygon([(520, 0), (900, 0), (900, 383), (482, 383)], DEEP)
    p.text(54, 30, "海南 AI 短漫剧大赛 · 赛事拆解", 16, CYAN, True)
    p.text(50, 64, "50万奖励包", 46, WHITE, True, box=(44, 54, 470, 118))
    p.text(52, 120, "先拆开，再报名", 40, CYAN, True, box=(44, 112, 470, 172))
    p.text(54, 182, "七份奖励包：现金 + 算力券 + 免租 + 公寓", 15, PALE, box=(48, 174, 476, 204))
    p.line([(54, 218), (466, 218)], TEAL, 2)
    p.text(54, 238, "A组剧本 / B组成片，只能选一个", 15, PALE, box=(48, 230, 476, 260))
    p.text(54, 268, "12月5日24:00 截止", 22, WHITE, True, box=(48, 258, 470, 300))
    p.text(54, 340, "一人短剧厂牌 · 赛事拆解", 13, PALE, box=(48, 332, 400, 360))

    p.text(556, 58, "50", 104, CYAN, True, box=(548, 46, 730, 180))
    p.text(716, 130, "万元", 26, WHITE, True, box=(712, 118, 790, 164))
    p.rounded((790, 66, 872, 100), 17, fill=CORAL)
    p.text(831, 83, "总价值", 14, WHITE, True, anchor="mm")

    p.text(556, 178, "A组 21万 + B组 25万 + 最佳 4万", 13, PALE, box=(550, 170, 872, 198))
    x = 556
    for label in ["现金奖金", "算力券", "免租办公", "公寓补贴"]:
        x += p.chip(x, 216, label, 13, WHITE, LINE, NAVY, True, 30, 10) + 8
    p.text(556, 258, "后两项须在复兴城注册入驻后兑现", 12, CORAL, True, box=(550, 250, 872, 276))
    p.text(556, 280, "学生团队可置换 · 占比未披露", 12, PALE, box=(550, 272, 872, 298))
    p.save(path)


def figure(path):
    p = Panel((1080, 1120), PAPER)
    p.text(64, 38, "50万，拆成七份奖励包", 40, NAVY, True, box=(58, 26, 1018, 96))
    p.text(66, 100, "按大赛海报奖项表相加；每份都是“总价值”，不是现金", 20, MUTED, box=(60, 92, 1018, 136))

    p.rounded((64, 150, 1016, 286), 22, fill=WHITE, outline=LINE, width=2)
    p.text(96, 172, "七份合计", 14, TEAL, True, box=(90, 164, 360, 192))
    p.text(94, 196, "50万元", 40, NAVY, True, box=(88, 188, 370, 260))
    p.line([(390, 170), (390, 266)], LINE, 2)
    p.rounded((420, 174, 566, 206), 16, fill=CORAL)
    p.text(493, 190, "不是现金奖池", 14, WHITE, True, anchor="mm")
    p.text(420, 222, "每份均为“单份奖励包总价值”", 15, NAVY, box=(414, 214, 998, 244))
    p.text(420, 250, "现金、算力券、免租、公寓各占多少，未披露", 13, MUTED, box=(414, 242, 1000, 268))

    p.rounded((64, 310, 516, 566), 24, fill=NAVY)
    p.text(92, 332, "A组 · 剧本与IP开发", 22, WHITE, True, box=(86, 322, 500, 366))
    p.text(92, 368, "故事梗概、人物设定、分集大纲、不少于3集剧本", 12, PALE, box=(86, 360, 502, 386))
    for y, label, value in [(404, "一等奖", "10万元"), (448, "二等奖", "7万元"), (492, "三等奖", "4万元")]:
        p.text(92, y + 4, label, 15, PALE, box=(86, y, 220, y + 34))
        p.text(300, y, value, 24, CYAN, True, box=(294, y - 6, 496, y + 38))
    p.line([(92, 526), (488, 526)], "#2B5057", 2)
    p.text(92, 536, "小计 21万元", 15, PALE, box=(86, 528, 488, 558))

    p.rounded((564, 310, 1016, 566), 24, fill=TEAL)
    p.text(592, 332, "B组 · 成品短漫剧", 22, WHITE, True, box=(586, 322, 1000, 366))
    p.text(592, 366, "MP4、1080P、中文字幕", 12, SOFT, box=(586, 358, 1004, 382))
    p.text(592, 383, "系列至少3集 · 单集1-3分钟 · 总长不超15分钟", 11, SOFT, box=(586, 375, 1004, 397))
    for y, label, value in [(404, "一等奖", "12万元"), (448, "二等奖", "8万元"), (492, "三等奖", "5万元")]:
        p.text(592, y + 4, label, 15, SOFT, box=(586, y, 720, y + 34))
        p.text(800, y, value, 24, WHITE, True, box=(794, y - 6, 996, y + 38))
    p.line([(592, 526), (988, 526)], "#4FA39C", 2)
    p.text(592, 536, "小计 25万元 · 单集作品3-15分钟", 14, SOFT, box=(586, 528, 988, 558))

    p.rounded((64, 586, 1016, 658), 18, fill=WHITE, outline=LINE, width=2)
    p.rounded((64, 586, 72, 658), 8, fill=CORAL)
    p.text(92, 602, "最佳自贸港与出海内容奖", 18, NAVY, True, box=(86, 594, 560, 632))
    p.text(92, 630, "1名 · 4万元，计入七份奖励包", 13, MUTED, box=(86, 622, 560, 650))
    p.text(640, 616, "21 + 25 + 4 = 50万元", 15, TEAL, True, box=(634, 606, 1000, 640))

    p.text(64, 690, "每份奖励包默认含四类权益", 22, NAVY, True, box=(58, 680, 700, 726))
    cards = [
        ("现金奖金", "颁奖后发放", GOLD),
        ("算力工具券", "仅用于创作", CYAN),
        ("免租办公空间", "入驻后兑现", TEAL),
        ("人才公寓补贴", "入驻后兑现", CORAL),
    ]
    for index, (label, note, color) in enumerate(cards):
        x = 64 + index * 238
        p.rounded((x, 732, x + 226, 828), 16, fill=WHITE, outline=LINE, width=2)
        p.rounded((x + 16, 744, x + 60, 750), 3, fill=color)
        p.text(x + 16, 760, label, 17, NAVY, True, box=(x + 10, 752, x + 220, 790))
        p.text(x + 16, 794, note, 12, CORAL if color == CORAL else MUTED, box=(x + 10, 786, x + 220, 820))
    p.text(64, 842, "海报原文：以上金额均为单份奖励包总价值；三项非现金权益均不可折现。", 13, MUTED, box=(58, 834, 1020, 862))

    p.rounded((64, 884, 1016, 1010), 20, fill=NAVY)
    p.rounded((64, 884, 72, 1010), 8, fill=CORAL)
    p.text(96, 904, "对大多数线上创作者：", 14, CYAN, True, box=(90, 896, 500, 926))
    p.text(96, 928, "能带走的主要是现金、算力券和对接机会；", 17, WHITE, box=(90, 920, 1000, 952))
    p.text(96, 954, "免租办公与公寓补贴，须在复兴城注册入驻后才兑现。", 17, WHITE, box=(90, 946, 1000, 978))
    p.text(96, 982, "在校学生团队：三项非现金权益可置换实训、实习或发行对接。", 13, CYAN, box=(90, 974, 1000, 1004))

    p.text(66, 1044, "本图为编辑示意。数据来源：大赛海报（山海秀英，2026-11-23）；金额为单份奖励包总价值，优秀作品奖10名未计入。", 13, MUTED, box=(60, 1034, 1020, 1066))
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
