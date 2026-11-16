# -*- coding: utf-8 -*-
"""107 Seedance 2.5 Flash 价目核读：封面 + 两张正文图。

数据来源（2026-11-16 只读复核）：
- 火山方舟「创建视频生成任务」文档：Seedance 2.5 / 2.5 flash 已全面公开；开通条件。
- 火山方舟「模型定价」页：480p/720p/1080p、输入是否含视频两段价目。
本图只复算公开价目，不代表成片成本或可承接订单；xb 模式只新建，不覆盖。
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
FLASH_BG = '#F3E3D8'
COVER_NAME = '封面_107_20261116_900x383.png'
FIG1_NAME = '107_图1_三档价目_1080.png'
FIG2_NAME = '107_图2_九十秒账单_1080.png'

# 官方价目页：5 秒、16:9、输入不含视频，元/个
PRICES = {
    '480p': {'2.5': 3.36, 'flash': 2.21, '2.0': 2.31, 'fast': 1.86, 'mini': 1.16},
    '720p': {'2.5': 7.56, 'flash': 4.97, '2.0': 4.97, 'fast': 4.00, 'mini': 2.48},
    '1080p': {'2.5': 18.71, 'flash': None, '2.0': 12.39, 'fast': None, 'mini': None},
}


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


def cover(out):
    c = Canvas(900, 383)
    d = c.d
    c.text(27, 24, '一人短剧厂牌', 17, INK, True)
    c.text(727, 26, '107 / 价目核读', 15, MUTED)
    d.line((27, 58, 873, 58), fill=LINE, width=1)

    c.text(29, 92, '火山方舟', 20, MUTED)
    c.text(29, 124, 'Seedance', 34, INK, True)
    c.text(29, 166, '2.5 Flash', 34, INK, True)

    # 中心方形 258.5—641.5 保留核心信息
    c.text(274, 88, 'Flash 开放后', 30, INK, True, critical=True)
    c.text(270, 142, '0.99', 88, RUST, True, critical=True)
    c.text(492, 180, '元/秒', 30, RUST, True, critical=True)
    c.text(274, 258, '720p 5 秒 4.97 元', 27, INK, True, critical=True)
    c.text(274, 302, '上限只到 720p', 22, MUTED, critical=True)

    # 右侧：三档对照竖条
    bars = [('720p', 4.97), ('480p', 2.21), ('1080p', None)]
    c.text(686, 96, '元/个（5 秒）', 17, MUTED)
    y = 136
    for label, val in bars:
        c.text(686, y, label, 18, INK, True)
        c.text(762, y, '不支持' if val is None else f'{val:.2f}', 20, MUTED if val is None else RUST, val is not None)
        y += 62
    c.text(686, 322, '2.0 同规格也是 4.97', 16, TEAL, True)
    c.finish(out / COVER_NAME)


def header(c, label, title, subtitle, color):
    d = c.d
    d.rectangle((0, 0, 14, c.h), fill=color)
    c.text(64, 34, '一人短剧厂牌', 21, INK, True)
    lw = c.d.textlength(label, font=font(19))
    c.text(c.w - 64 - lw, 36, label, 19, MUTED, region=(c.w - 400, 30, c.w - 30, 70))
    c.text(64, 92, title, 44, INK, True)
    c.text(64, 158, subtitle, 27, MUTED)


def fig1(out):
    c = Canvas(1080, 1010)
    header(c, '107 / 价目', '三档分辨率，五种模型', '5 秒、16:9、输入不含视频；官方示例价，元/个', RUST)
    d = c.d

    cols = [('2.5 旗舰', '2.5'), ('2.5 Flash', 'flash'), ('2.0', '2.0'), ('2.0 fast', 'fast'), ('2.0 mini', 'mini')]
    left, right = 64, 1016
    x0 = 234
    col_w = (right - left - (x0 - left)) / len(cols)

    d.rectangle((left, 214, right, 266), fill='#EFE8DA')
    c.text(left + 18, 226, '分辨率', 22, MUTED, True)
    for i, (name, key) in enumerate(cols):
        cx = x0 + col_w * i + col_w / 2
        c.text(0, 226, name, 22, RUST if key == 'flash' else INK, True, center=cx,
               region=(x0 + col_w * i + 2, 222, x0 + col_w * (i + 1) - 2, 264))

    fx = x0 + col_w
    d.rectangle((fx + 2, 266, fx + col_w - 2, 726), fill=FLASH_BG)

    y = 266
    for band in ('480p', '720p', '1080p'):
        c.text(left + 18, y + 40, band, 28, INK, True)
        for i, (_name, key) in enumerate(cols):
            v = PRICES[band][key]
            txt = '不支持' if v is None else f'{v:.2f}'
            c.text(0, y + 36, txt, 26 if v is not None else 21, MUTED if v is None else (RUST if key == 'flash' else INK),
                   v is not None, center=x0 + col_w * i + col_w / 2,
                   region=(x0 + col_w * i + 2, y + 30, x0 + col_w * (i + 1) - 2, y + 80))
        y += 150
        d.line((left, y, right, y), fill=LINE, width=1)

    d.rounded_rectangle((64, 760, 1016, 856), radius=12, fill='#F7E9E3')
    c.text(88, 774, 'Flash 720p 4.97 元，比 2.5 旗舰 7.56 元低 34%；', 27, RUST, True)
    c.text(88, 814, '但 2.0 标准档 720p 同样是 4.97 元——降价只对 2.5 成立。', 27, RUST, True)

    c.text(64, 886, '带参考视频（输入 2—30 秒）另按区间计价：720p Flash 5.44—21.17 元/个；1080p 不支持。', 21, MUTED)
    c.text(64, 920, '口径：官方价目页 2026-11-16 读取；按 token 计费，仅对成功生成收费。', 21, MUTED)
    c.finish(out / FIG1_NAME)


def fig2(out):
    c = Canvas(1080, 1120)
    header(c, '107 / 账单', '一条 90 秒＝18 个 5 秒镜头', '全部一次过、无废片；按官方示例价折算，元', TEAL)
    d = c.d

    shots = 18
    rows = [
        ('2.0 mini 720p', PRICES['720p']['mini']),
        ('2.0 fast 720p', PRICES['720p']['fast']),
        ('2.5 Flash 720p', PRICES['720p']['flash']),
        ('2.0 标准 720p', PRICES['720p']['2.0']),
        ('2.5 旗舰 720p', PRICES['720p']['2.5']),
        ('2.5 旗舰 1080p', PRICES['1080p']['2.5']),
    ]
    totals = [(name, unit * shots) for name, unit in rows]
    max_total = max(t for _n, t in totals)

    left, bar_x, bar_w = 64, 380, 430
    y = 232
    for name, total in totals:
        d.line((left, y + 62, 1016, y + 62), fill='#E6DED0', width=1)
        c.text(left, y + 14, name, 24, INK, True)
        width = bar_w * total / max_total
        color = RUST if 'Flash' in name else ('#A2988A' if '2.5' in name else TEAL)
        d.rectangle((bar_x, y + 8, bar_x + width, y + 50), fill=color)
        c.text(bar_x + width + 12, y + 14, f'{total:.1f}', 24, color, True,
               region=(bar_x + width + 10, y + 6, 1016, y + 56))
        y += 78

    c.text(64, 706, 'Flash 与 2.0 标准档同价；1080p 只能走 2.5 旗舰。', 27, INK, True)

    d.rounded_rectangle((64, 766, 1016, 900), radius=12, fill='#E3EDE9')
    c.text(88, 782, '带参考视频时，Flash 720p 单镜 5.44—21.17 元。', 26, TEAL, True)
    c.text(88, 822, '同一条 18 镜：97.9—381.1 元，是 0.99 元/秒的 1.1—4.3 倍。', 24, TEAL)
    c.text(88, 860, '做续写、视频编辑的镜头，别按 0.99 元/秒估。', 22, MUTED)

    d.line((64, 950, 1016, 950), fill=LINE, width=1)
    c.text(64, 966, '口径：18 镜 × 5 秒＝90 秒，全部成功且不重试；未计参考素材、配音、人工。', 20, MUTED)
    c.text(64, 1000, '按 token 计费，准确用量以 API 返回 usage 为准；官方演示未实测。', 20, MUTED)
    c.finish(out / FIG2_NAME)


def verify_math():
    assert abs(PRICES['720p']['flash'] * 18 - 89.46) < 1e-9
    assert abs(PRICES['720p']['2.5'] * 18 - 136.08) < 1e-9
    assert abs(PRICES['720p']['flash'] / PRICES['720p']['2.5'] - 0.6574) < 0.001
    assert abs(PRICES['480p']['flash'] - 2.21) < 1e-9
    assert abs(5.44 * 18 - 97.92) < 1e-9 and abs(21.17 * 18 - 381.06) < 1e-9
    assert PRICES['720p']['flash'] == PRICES['720p']['2.0']


if __name__ == '__main__':
    verify_math()
    out = HERE
    cover(out)
    fig1(out)
    fig2(out)
    print('done')