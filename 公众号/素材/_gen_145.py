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
COVER = "封面_145_郑州位次_20261127_900x383.png"
FIGURE = "图1_145_郑州三个位次_20261127_1080x1120.png"


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
    p.polygon([(540, 0), (900, 0), (900, 383), (492, 383)], DEEP)
    p.text(44, 24, "DataEye 2026 上半年 AI 剧漫剧城市报告", 13, CYAN, True, box=(38, 16, 470, 50))
    p.text(42, 50, "郑州短剧", 34, WHITE, True, box=(36, 44, 470, 96))
    p.text(42, 92, "制作第3", 46, GOLD, True, box=(36, 84, 470, 152))
    p.text(42, 146, "发行第13", 46, CORAL, True, box=(36, 138, 470, 206))
    p.line([(44, 218), (464, 218)], TEAL, 2)
    p.text(44, 228, "制作实力 86.9 分，全国第三", 13, PALE, box=(38, 222, 470, 252))
    p.text(44, 250, "出海第八；发行第十三", 13, PALE, box=(38, 244, 470, 274))
    p.text(44, 276, "日均100部开机，一栋楼只剩1个剧组", 11, PALE, box=(38, 270, 474, 298))
    p.text(44, 344, "一人短剧厂牌 · 2026-11-27 公开报道核查", 10, PALE, box=(38, 338, 474, 366))

    p.text(560, 24, "同一份榜单，三个位次", 12, CYAN, True, box=(554, 16, 860, 46))
    p.rounded((556, 52, 860, 108), 12, fill=NAVY, outline=TEAL, width=2)
    p.text(570, 64, "制作  第3", 17, WHITE, True, box=(564, 58, 854, 96))
    p.text(570, 88, "86.9分 · 杭州、西安之后", 9, PALE, box=(570, 84, 854, 104))
    p.rounded((556, 118, 830, 174), 12, fill=NAVY, outline=TEAL, width=2)
    p.text(570, 130, "出海  第8", 17, WHITE, True, box=(564, 124, 824, 162))
    p.text(570, 154, "发行能力是另一项得分", 9, PALE, box=(570, 150, 824, 170))
    p.rounded((556, 184, 800, 240), 12, fill=NAVY, outline=CORAL, width=2)
    p.text(570, 196, "发行  第13", 17, CORAL, True, box=(564, 190, 794, 228))
    p.text(570, 220, "制作强 ≠ 发行强", 9, PALE, box=(570, 216, 794, 236))
    p.text(560, 258, "郑州的剧在别人平台上跑：", 10, PALE, box=(554, 252, 860, 278))
    p.text(560, 276, "2025年以来海外发行100多部，", 10, PALE, box=(554, 270, 860, 296))
    p.text(560, 294, "累计下载近5500万次", 10, CYAN, True, box=(554, 288, 860, 314))
    p.text(560, 330, "行通四海：12个剧组 → 1个（2026年11月）", 9, PALE, box=(554, 324, 866, 348))
    p.save(path)


def figure(path):
    p = Panel((1080, 1120), PAPER)
    p.text(62, 34, "郑州：制作第3，发行第13", 40, NAVY, True, box=(56, 22, 1022, 96))
    p.text(64, 98, "DataEye《2026上半年中国AI剧漫剧产业综合实力城市数据报告》｜2026-08-14 郑州文旅发布、九派娱乐转载", 13, MUTED, box=(58, 92, 1022, 124))

    # zone 1: three ranks
    p.text(62, 136, "同一份报告里的三个位次", 21, NAVY, True, box=(56, 128, 1022, 168))
    p.rounded((60, 176, 360, 304), 16, fill=WHITE, outline=TEAL, width=2)
    p.text(80, 188, "制作实力", 12, MUTED, box=(74, 182, 354, 208))
    p.text(80, 208, "第3", 38, TEAL, True, box=(74, 200, 354, 262))
    p.text(80, 254, "86.9分", 17, NAVY, True, box=(74, 248, 354, 280))
    p.text(80, 280, "杭州、西安之后（西安87.4）", 10, MUTED, box=(74, 276, 354, 298))

    p.rounded((390, 176, 690, 304), 16, fill=WHITE, outline=LINE, width=2)
    p.text(410, 188, "出海实力", 12, MUTED, box=(404, 182, 684, 208))
    p.text(410, 208, "第8", 38, NAVY, True, box=(404, 200, 684, 262))
    p.text(410, 254, "海外发行", 17, NAVY, True, box=(404, 248, 684, 280))
    p.text(410, 280, "100多部，下载近5500万次", 10, MUTED, box=(404, 276, 684, 298))

    p.rounded((720, 176, 1020, 304), 16, fill=WHITE, outline=CORAL, width=2)
    p.text(740, 188, "发行实力", 12, MUTED, box=(734, 182, 1014, 208))
    p.text(740, 208, "第13", 38, CORAL, True, box=(734, 200, 1014, 262))
    p.text(740, 254, "差在哪里", 17, NAVY, True, box=(734, 248, 1014, 280))
    p.text(740, 280, "转载稿没有展开", 10, MUTED, box=(734, 276, 1014, 298))

    p.text(62, 312, "四个维度：综合实力 / 发行实力 / 制作实力 / 出海实力；郑州综合实力位次未公开。", 12, MUTED, box=(56, 306, 1022, 334))

    # zone 2: supply side
    p.text(62, 348, "供给端：产能还在，剧组在减", 21, NAVY, True, box=(56, 340, 1022, 380))
    p.rounded((60, 390, 536, 648), 16, fill=WHITE, outline=TEAL, width=2)
    p.text(80, 402, "郑州市公布、腾讯科技引述", 11, MUTED, box=(74, 396, 530, 422))
    p.text(80, 424, "从业人员  3万 → 4.2万+", 15, NAVY, True, box=(74, 418, 530, 448))
    p.text(80, 452, "相关企业  820+ → 1020+（持证）", 13, NAVY, box=(74, 446, 530, 474))
    p.text(80, 478, "2025年上线  6900多部", 13, NAVY, box=(74, 472, 530, 500))
    p.text(80, 504, "基地/取景地  31家，接待剧组7138个", 12, NAVY, box=(74, 498, 530, 524))
    p.text(80, 530, "制作成本比一线城市低三到四成", 12, MUTED, box=(74, 524, 530, 550))
    p.text(80, 560, "40集的短剧，3天拍完", 14, TEAL, True, box=(74, 554, 530, 584))
    p.text(80, 588, "场景、群演、场务、后期、住宿，几条街凑齐", 11, MUTED, box=(74, 582, 530, 608))
    p.text(80, 614, "这套能力是产能，不是观众。", 12, NAVY, True, box=(74, 608, 530, 636))

    p.rounded((556, 390, 1020, 648), 16, fill=WHITE, outline=GOLD, width=2)
    p.text(576, 402, "现场记录（腾讯科技 / 霞光社）", 11, MUTED, box=(570, 396, 1014, 422))
    p.text(576, 424, "12个剧组 → 1个剧组", 24, CORAL, True, box=(570, 418, 1014, 468))
    p.text(576, 462, "行通四海基地，2026年11月初", 10, MUTED, box=(570, 458, 1014, 480))
    p.text(576, 486, "日均约100部开机", 20, NAVY, True, box=(570, 480, 1014, 516))
    p.text(576, 514, "全郑州口径", 10, MUTED, box=(570, 510, 1014, 532))
    p.text(576, 540, "男二号日薪：三位数", 14, NAVY, True, box=(570, 534, 1014, 562))
    p.text(576, 564, "2024年日薪800，2025年能报到上万", 10, MUTED, box=(570, 560, 1014, 582))
    p.text(576, 590, "40万元项目，净利可能1万元", 12, NAVY, box=(570, 584, 1014, 612))
    p.text(576, 614, "男女主角片酬合计可能8万元", 11, MUTED, box=(570, 608, 1014, 634))

    p.text(62, 654, "12→1 是一栋楼；日均100部是全郑州；两个数不能相减。", 12, MUTED, box=(56, 648, 1022, 676))

    # zone 3: cost vs split
    p.text(62, 690, "AI打下来的是报价，不是分账比例", 21, NAVY, True, box=(56, 682, 1022, 722))
    p.rounded((60, 732, 536, 916), 16, fill=WHITE, outline=TEAL, width=2)
    p.text(80, 744, "一分钟成本", 11, MUTED, box=(74, 738, 530, 764))
    p.text(80, 766, "2000元/分钟", 26, MUTED, True, box=(74, 760, 530, 806))
    p.text(80, 794, "此前主流报价", 10, MUTED, box=(74, 790, 530, 814))
    p.text(80, 818, "→ 60元/分钟", 30, CORAL, True, box=(74, 812, 530, 864))
    p.text(80, 856, "Seedance 2.0 年会员、10:1抽卡的算力成本", 10, MUTED, box=(74, 850, 530, 874))
    p.text(80, 876, "一个是报价，一个是算力，不同口径", 10, NAVY, True, box=(74, 870, 530, 896))

    p.rounded((556, 732, 1020, 916), 16, fill=WHITE, outline=GOLD, width=2)
    p.text(576, 744, "钱分到谁手里（钛媒体行业口径）", 11, MUTED, box=(570, 738, 1014, 764))
    p.text(576, 766, "制作方净利  5%—10%", 14, NAVY, True, box=(570, 760, 1014, 792))
    p.text(576, 792, "平台方  >30%", 14, NAVY, True, box=(570, 786, 1014, 818))
    p.text(576, 818, "渠道拿走流水  35%—45%", 14, NAVY, True, box=(570, 812, 1014, 844))
    p.text(576, 844, "纯制作方分账  10%—15%", 14, NAVY, True, box=(570, 838, 1014, 870))
    p.text(576, 872, "约5%制作方盈利；近七成剧集微利及以下", 10, MUTED, box=(570, 866, 1014, 892))

    p.text(62, 924, "AI降低的是进场门槛，不是被分走的比例。", 12, NAVY, True, box=(56, 918, 1022, 946))

    # bottom note
    p.rounded((60, 954, 1020, 1058), 16, fill=WHITE, outline=LINE, width=2)
    p.text(78, 966, "读法：排名来自 DataEye 报告转载，报告原文与分项得分未公开；郑州官方数据经腾讯科技引述。", 10, MUTED, box=(72, 960, 1012, 988))
    p.text(78, 988, "2000元为报价、60元为算力成本，不是同一口径；成本、分账与买量为行业口径，不是单部剧账本。", 10, MUTED, box=(72, 982, 1012, 1010))
    p.text(78, 1010, "来源：腾讯科技（2026-11-12）、霞光社（2026-11-18）、钛媒体（2026-11-23）、九派娱乐转载郑州文旅（2026-08-14）。", 9, MUTED, box=(72, 1004, 1012, 1030))
    p.text(78, 1034, "行通四海数据来自腾讯科技走访；海外发行与下载数据来自霞光社，均非本号独立核验。", 9, MUTED, box=(72, 1028, 1012, 1052))
    p.text(62, 1072, "一人短剧厂牌 · 2026-11-27", 10, MUTED, box=(56, 1066, 1022, 1096))
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
