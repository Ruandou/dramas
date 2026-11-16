# -*- coding: utf-8 -*-
"""108 短剧产业链角色地图：封面 + 两张正文图。

数据口径：
- 投中网 2026-11-04 转述：平台与投流 82.5%，制作/演员/剧本 14%，其余 3.5%。
- 承制价 300—500 元/分钟、代工净利率 5%—8%、活跃承制方 1216→698 家，均为媒体口径。
- 红果 4.30 亿、绿泡泡 1.56 亿、漫剧 7883 万，来自 QuestMobile 2026-09。
本图只做公开口径可视化，不代表审计数据；xb 模式只新建，不覆盖。
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONT_PATH = '/System/Library/Fonts/Hiragino Sans GB.ttc'
PAPER = '#FAF6EE'
INK = '#2C2925'
MUTED = '#756D61'
LINE = '#D4C9B8'
RUST = '#AE422C'
TEAL = '#28695E'
GOLD = '#B9853D'
SAND = '#EFE8DA'
SAND2 = '#F4EDE1'
RUST_BG = '#F7E9E3'
TEAL_BG = '#E3EDE9'

COVER_NAME = '封面_108_20261116_900x383.png'
FIG1_NAME = '108_图1_五个钱包_1080.png'
FIG2_NAME = '108_图2_成本结构_1080.png'


@lru_cache(None)
def font(size, bold=False):
    return ImageFont.truetype(FONT_PATH, size, index=2 if bold else 0)


class Canvas:
    def __init__(self, w, h):
        self.im = Image.new('RGB', (w, h), PAPER)
        self.d = ImageDraw.Draw(self.im)
        self.w, self.h = w, h
        self.boxes = []
        self.chars = {0: set(), 2: set()}
        self.critical = []

    def text(self, x, y, text, size, fill=INK, bold=False, center=None, region=None, critical=False):
        face = font(size, bold)
        if center is not None:
            x = center - self.d.textlength(text, font=face) / 2
        box = self.d.textbbox((x, y), text, font=face, anchor='lt')
        region = region or (0, 0, self.w, self.h)
        assert region[0] <= box[0] < box[2] <= region[2], ('横向越界', text, box, region)
        assert region[1] <= box[1] < box[3] <= region[3], ('纵向越界', text, box, region)
        for prev_text, prev in self.boxes:
            overlap = min(box[2], prev[2]) > max(box[0], prev[0]) and min(box[3], prev[3]) > max(box[1], prev[1])
            assert not overlap, ('文字重叠', text, prev_text, box, prev)
        if critical:
            left = (self.w - self.h) / 2
            assert left + 8 <= box[0] and box[2] <= left + self.h - 8, ('方形裁切丢字', text, box)
            self.critical.append((text, box))
        self.boxes.append((text, box))
        self.chars[2 if bold else 0].update(text)
        self.d.text((x, y), text, font=face, fill=fill, anchor='lt')
        return box

    def finish(self, path):
        for idx, chars in self.chars.items():
            face = TTFont(FONT_PATH, fontNumber=idx)
            cmap = face.getBestCmap()
            missing = sorted(c for c in chars if ord(c) not in cmap)
            face.close()
            assert not missing, ('字体缺字', idx, missing)
        with path.open('xb') as out:
            self.im.save(out, format='PNG', optimize=True)
        with Image.open(path) as saved:
            assert saved.size == (self.w, self.h)
            saved.verify()
        print(f'PASS {path.name} | {self.w}x{self.h} | {len(self.boxes)} boxes | {path.stat().st_size:,} bytes')
        if self.critical:
            print('CENTER CROP PASS:', '; '.join(t for t, _ in self.critical))


def pill(c, x, y, w, h, label, fill, color):
    c.d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=fill)
    c.text(0, y + (h - 22) / 2 - 1, label, 17, color, True, center=x + w / 2,
           region=(x + 4, y + 2, x + w - 4, y + h - 2))


def header(c, label, title, subtitle, color):
    c.d.rectangle((0, 0, 14, c.h), fill=color)
    c.text(64, 34, '一人短剧厂牌', 21, INK, True)
    lw = c.d.textlength(label, font=font(19))
    c.text(c.w - 64 - lw, 36, label, 19, MUTED, region=(c.w - 420, 30, c.w - 30, 70))
    c.text(64, 92, title, 44, INK, True)
    c.text(64, 158, subtitle, 24, MUTED)


def cover(out):
    c = Canvas(900, 383)
    d = c.d
    d.rectangle((0, 0, 9, 383), fill=RUST)
    c.text(27, 24, '一人短剧厂牌', 17, INK, True)
    c.text(727, 26, '108 / 产业链', 15, MUTED)
    d.line((27, 58, 873, 58), fill=LINE, width=1)

    c.text(29, 92, '都在做短剧', 20, MUTED)
    c.text(29, 124, '赚的不是', 34, INK, True)
    c.text(29, 166, '同一种钱', 34, INK, True)

    c.text(270, 86, '5 个钱包', 44, RUST, True, critical=True)
    c.text(270, 146, '14 种角色', 34, INK, True, critical=True)
    c.text(270, 214, '一张产业链角色地图', 23, MUTED, critical=True)
    c.text(270, 310, '先看钱包，再看名头', 21, TEAL, True, critical=True)

    c.text(686, 96, '钱从哪来', 17, MUTED)
    y = 136
    for label, color in [('IP / 剧本', INK), ('制作', INK), ('分发', INK), ('数据', TEAL)]:
        c.text(686, y, label, 20, color, True)
        y += 54
    d.line((672, 96, 672, 330), fill=LINE, width=1)
    c.finish(out / COVER_NAME)


def fig1(out):
    c = Canvas(1080, 1180)
    header(c, '108 / 地图', '五个钱包，一条链', '内容往下走，钱往回走；每个角色只拿自己那一段', RUST)

    labels = [('观众钱包', RUST_BG, RUST), ('广告主钱包', SAND, INK),
              ('平台钱包', TEAL_BG, TEAL), ('制作方钱包', SAND, INK),
              ('工具 / 服务', SAND2, MUTED)]
    x = 64
    for label, fill, color in labels:
        pill(c, x, 210, 170, 42, label, fill, color)
        x += 182

    bands = [
        ('上游', 'IP / 剧本', '番茄、七猫、版权中心、编剧工作室', '授权费 · 稿费 · 分成', RUST, SAND2),
        ('制作', '承制 / 自制 / 工具', '承制方、出品方、Seedance、纳逗 Pro', '承制费 · 工具费 · 场地费', TEAL, SAND),
        ('分发', '平台 / 发行 / 品牌', '红果、抖音、微信、优酷、NetShort、京东', '广告 · 分账 · 内购 · 佣金', RUST, SAND2),
        ('观众', '充值 / 会员 / 下单', '最终买单的人', '五个钱包的源头', TEAL, TEAL_BG),
    ]

    top = 290
    band_h = 150
    gap = 18
    for i, (stage, title, examples, money, color, bg) in enumerate(bands):
        y = top + i * (band_h + gap)
        c.d.rounded_rectangle((64, y, 1016, y + band_h), radius=14, fill=bg)
        c.d.rectangle((64, y, 72, y + band_h), fill=color)
        c.text(92, y + 26, stage, 22, color, True)
        c.text(92, y + 66, f'0{i + 1}', 30, color, True)
        c.text(234, y + 28, title, 31, INK, True, region=(230, y + 20, 700, y + 72))
        c.text(234, y + 84, examples, 20, MUTED, region=(230, y + 76, 700, y + 128))
        c.d.rounded_rectangle((714, y + 24, 1004, y + 126), radius=10, fill='#FFFFFF')
        c.text(734, y + 46, '这一层收', 18, MUTED)
        c.text(734, y + 78, money, 19, color, True, region=(730, y + 72, 998, y + 120))

    # 内容流 / 钱流
    c.d.line((44, top, 44, top + 4 * band_h + 3 * gap), fill=LINE, width=2)
    c.d.polygon([(44, top + 4 * band_h + 3 * gap + 14), (36, top + 4 * band_h + 3 * gap), (52, top + 4 * band_h + 3 * gap)], fill=LINE)
    c.text(18, 258, '内容流 ↓', 15, MUTED)
    c.d.line((1036, top + 4 * band_h + 3 * gap, 1036, top), fill=LINE, width=2)
    c.d.polygon([(1036, top - 14), (1028, top), (1044, top)], fill=LINE)
    c.text(1000, 950, '钱流 ↑', 15, RUST, True, region=(990, 946, 1074, 974))

    # 横向支撑
    c.d.rounded_rectangle((64, 974, 1016, 1104), radius=14, fill=SAND)
    c.text(88, 992, '横向支撑：数据与规则', 24, INK, True)
    c.text(88, 1032, 'DataEye / 云合 / 艺恩 · 备案 / 审核 / 确权', 20, MUTED)
    c.text(88, 1066, '卖订阅、报告、服务费；不参与分账', 20, TEAL, True)

    c.text(64, 1136, '同一部剧可以被五个钱包同时付费；但每个角色只拿自己那一段。', 21, INK, True)
    c.finish(out / FIG1_NAME)


def fig2(out):
    c = Canvas(1080, 980)
    header(c, '108 / 成本', 'AI 省的是制作费，不是流量费', '投中网 11-04 转述的行业测算；全链路综合成本，不是单部财报', TEAL)
    d = c.d

    rows = [
        ('平台与投流', 82.5, RUST),
        ('制作、演员、剧本', 14.0, TEAL),
        ('其他', 3.5, GOLD),
    ]
    left, bar_x, bar_max = 64, 420, 470
    y = 250
    for name, pct, color in rows:
        c.text(left, y + 12, name, 25, INK, True, region=(left, y, 400, y + 66))
        width = bar_max * pct / 82.5
        d.rectangle((bar_x, y, bar_x + width, y + 60), fill=color)
        c.text(bar_x + width + 14, y + 10, f'{pct:.1f}%', 28, color, True,
               region=(bar_x + width + 10, y, 1016, y + 66))
        y += 112

    d.line((64, 590, 1016, 590), fill=LINE, width=1)
    c.text(64, 616, '每 100 元综合成本：', 27, MUTED, True)
    c.text(332, 610, '82.5 元给平台与投流', 34, RUST, True)
    c.text(64, 662, '14 元给制作、演员、剧本；3.5 元是其他。', 25, INK)

    d.rounded_rectangle((64, 724, 1016, 856), radius=12, fill='#F7E9E3')
    c.text(88, 742, 'AI 降的是那 14% 里的制作费；', 27, RUST, True)
    c.text(88, 782, '降不到 82.5% 的流量费。', 27, RUST, True)
    c.text(88, 820, '承制价 300—500 元/分钟；代工净利率 5%—8%；活跃承制方 1216→698 家。', 20, MUTED)

    c.text(64, 888, '口径：投中网 2026-11-04 转述；综合成本含平台与投流，方法未披露，不是审计数据。', 19, MUTED)
    c.text(64, 922, '承制价、净利率与承制方数量为同一篇报道的媒体口径，不能外推为行业平均。', 19, MUTED)
    c.finish(out / FIG2_NAME)


def verify_math():
    assert abs(82.5 + 14.0 + 3.5 - 100.0) < 1e-9
    assert abs(470 * 82.5 / 82.5 - 470) < 1e-9
    assert abs(470 * 14.0 / 82.5 - 79.75757575757575) < 1e-9
    assert abs(470 * 3.5 / 82.5 - 19.939393939393938) < 1e-9


if __name__ == '__main__':
    verify_math()
    out = HERE
    cover(out)
    fig1(out)
    fig2(out)
    print('done')
