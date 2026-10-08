# -*- coding: utf-8 -*-
"""配图：同一张脸，原图 vs 叠网格版（纯本地 Pillow，零扣费）
素材取自 dramas/满级师尊她装作刚入门/assets/looks/CHAR-001-L01.png（1600x2848）
网格坐标由 script/detect_face_rect.py 实测得到：791,418,204,240
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.dirname(os.path.abspath(__file__))
SRC = "/Users/lei/Movies/demo1/dramas/满级师尊她装作刚入门/assets/looks/CHAR-001-L01.png"
MESH = os.path.join(OUT, "_demo_mesh.png")

INK = (26, 24, 22)
BONE = (238, 232, 219)
DIM = (150, 143, 130)
VERMIL = (176, 44, 32)
LINE = (70, 66, 60)

HIRA = "/System/Library/Fonts/Hiragino Sans GB.ttc"
HEI = "/System/Library/Fonts/STHeiti Medium.ttc"

CELL = 560
PAD = 40
TOP = 96
W = PAD * 3 + CELL * 2
H = TOP + CELL + 108

CROP = (481, 110, 1101, 730)  # 以面部为中心裁方形


def f(path, size):
    return ImageFont.truetype(path, size)


def tracked(d, y, text, fnt, fill, cx=None, x=None, tracking=0):
    widths = [d.textlength(c, font=fnt) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    px = (cx - total / 2) if cx is not None else x
    for c, w in zip(text, widths):
        d.text((px, y), c, font=fnt, fill=fill, anchor="ls")
        px += w + tracking


def main():
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)

    tracked(d, TOP - 34, "同一张脸，唯一差别是这层网格", f(HEI, 40), BONE, cx=W / 2, tracking=2)

    for i, (path, cap, sub) in enumerate([
        (SRC, "原图 · 提交被拒", "HTTP 400 PrivacyInformation"),
        (MESH, "叠网格 · 提交通过", "网格不会进入成片"),
    ]):
        x = PAD + i * (CELL + PAD)
        tile = Image.open(path).convert("RGB").crop(CROP).resize((CELL, CELL), Image.LANCZOS)
        im.paste(tile, (x, TOP))
        d.rectangle([x, TOP, x + CELL, TOP + CELL], outline=LINE, width=1)
        tracked(d, TOP + CELL + 46, cap, f(HEI, 30), BONE, cx=x + CELL / 2, tracking=1)
        tracked(d, TOP + CELL + 84, sub, f(HIRA, 20), DIM, cx=x + CELL / 2, tracking=1)

    d.line([(W / 2, TOP + 18), (W / 2, TOP + CELL - 18)], fill=LINE, width=1)
    im.save(os.path.join(OUT, "对比_mesh面具.png"))
    print(im.size)


SONG = "/System/Library/Fonts/Supplemental/Songti.ttc"


def cover():
    """文章封面 900x383：左标题区 / 右 mesh 面部特写"""
    CW, CH = 900, 383
    im = Image.new("RGB", (CW, CH), INK)
    d = ImageDraw.Draw(im)

    fw = 383
    tile = Image.open(MESH).convert("RGB").crop(CROP).resize((fw, CH), Image.LANCZOS)
    im.paste(tile, (CW - fw, 0))
    d.line([(CW - fw, 0), (CW - fw, CH)], fill=LINE, width=1)

    x = 54
    d.rectangle([x, 66, x + 12, 66 + 30], fill=VERMIL)
    tracked(d, 90, "一人短剧厂牌", f(HIRA, 22), DIM, x = x + 26, tracking=3)

    song = ImageFont.truetype(SONG, 62, index=1)
    tracked(d, 186, "给每张 AI 脸", song, BONE, x=x, tracking=2)
    tracked(d, 268, "戴上三角网格", song, BONE, x=x, tracking=2)
    tracked(d, 320, "视频模型说这张脸是真人，于是整集开不了工", f(HIRA, 22), DIM, x=x, tracking=1)

    im.save(os.path.join(OUT, "封面_三角网格面具_900x383.png"))
    print("cover", im.size)


if __name__ == "__main__":
    main()
    cover()
