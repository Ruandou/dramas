# -*- coding: utf-8 -*-
"""一人短剧厂牌 首屏封面（纯 PIL，零扣费）
输出 900x383（微信首屏封面比例 2.35:1）
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 900, 383

SONG = "/System/Library/Fonts/Supplemental/Songti.ttc"   # 1=Bold
HIRA = "/System/Library/Fonts/Hiragino Sans GB.ttc"

CARBON = (52, 49, 44)      # 与头像 E3 底色逐像素一致，避免拼缝
BONE = (238, 232, 219)
VERMIL = (176, 44, 32)
DIM = (154, 146, 132)


def font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)


def tracked(d, x, y, text, fnt, fill, tracking):
    for c in text:
        d.text((x, y), c, font=fnt, fill=fill)
        x += d.textlength(c, font=fnt) + tracking
    return x


def build(mark_path):
    im = Image.new("RGB", (W, H), CARBON)
    d = ImageDraw.Draw(im)

    # 只取「一人」大字带，裁掉头像自带的页脚（右侧已有全称，不重复）
    mark = Image.open(mark_path).convert("RGB").crop((150, 90, 650, 620))
    ms = 270
    mh = int(mark.height * ms / mark.width)
    im.paste(mark.resize((ms, mh), Image.LANCZOS), (52, (H - mh) // 2))

    x0 = 52 + ms + 62
    d.rectangle([x0, 118, x0 + 12, 118 + 148], fill=VERMIL)
    tx = x0 + 42
    tracked(d, tx, 124, "一人短剧厂牌", font(SONG, 62, index=1), BONE, 4)
    tracked(d, tx, 216, "AI 短剧流水线实录", font(HIRA, 28), DIM, 5)

    p = os.path.join(OUT, "封面_一人短剧厂牌_900x383.png")
    im.save(p)
    return p, im.size


if __name__ == "__main__":
    print(build(os.path.join(OUT, "E3_一人大字_暖炭.png")))
