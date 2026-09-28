# -*- coding: utf-8 -*-
"""一人短剧厂牌 头像（纯 PIL 字形版，零扣费）
A 竖屏画框 / B 宋体竖排+朱印 / C 场记板 / E 一人大字（抗小尺寸主推）
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.dirname(os.path.abspath(__file__))
S = 800

SONG = "/System/Library/Fonts/Supplemental/Songti.ttc"   # 0=Regular 1=Bold
HEI = "/System/Library/Fonts/STHeiti Medium.ttc"
HIRA = "/System/Library/Fonts/Hiragino Sans GB.ttc"

INK = (26, 24, 22)
BONE = (238, 232, 219)
PAPER = (244, 239, 229)
CARBON = (18, 19, 22)
VERMIL = (176, 44, 32)


def font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)


def tracked(d, y, text, fnt, fill, tracking=0, cx=None, x=None):
    widths = [d.textlength(c, font=fnt) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    px = (cx - total / 2) if cx is not None else x
    for c, w in zip(text, widths):
        d.text((px, y), c, font=fnt, fill=fill, anchor="ls")
        px += w + tracking
    return total


def tracked_v(d, x, y0, text, fnt, fill, step):
    for k, c in enumerate(text):
        d.text((x, y0 + k * step), c, font=fnt, fill=fill)


# ---------------- A. 竖屏画框 ----------------
def dir_a():
    im = Image.new("RGB", (S, S), CARBON)
    d = ImageDraw.Draw(im)
    fw, fh = 320, 560
    fl, ft = (S - fw) // 2, 92
    d.rectangle([fl, ft, fl + fw, ft + fh], outline=(96, 91, 82), width=3)
    d.rectangle([fl + 18, ft + 18, fl + 40, ft + 40], fill=VERMIL)

    cx = S / 2
    tracked(d, ft + 130, "一人", font(HIRA, 44), (178, 169, 152), tracking=22, cx=cx)
    tracked(d, ft + 300, "短剧", font(HEI, 118), BONE, tracking=6, cx=cx)
    tracked(d, ft + 434, "厂牌", font(HEI, 118), BONE, tracking=6, cx=cx)
    im.save(os.path.join(OUT, "A_竖屏画框.png"))


# ---------------- B. 宋体竖排 + 朱印 ----------------
def dir_b():
    im = Image.new("RGB", (S, S), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle([46, 46, S - 46, S - 46], outline=(205, 195, 178), width=1)

    song = font(SONG, 118, index=1)
    for col, x in zip(["一人", "短剧", "厂牌"], [566, 412, 258]):
        tracked_v(d, x, 150, col, song, INK, 128)

    # 白文印：红底白字，居中竖排
    sw, sh = 108, 224
    sx, sy = 118, 452
    d.rectangle([sx, sy, sx + sw, sy + sh], fill=VERMIL)
    seal = font(SONG, 74, index=1)
    cxc = sx + sw / 2
    for k, c in enumerate("厂牌"):
        d.text((cxc, sy + 52 + k * 92), c, font=seal, fill=PAPER, anchor="mm")

    tracked(d, 700, "AI 短剧流水线实录", font(HIRA, 22), (126, 118, 105),
            tracking=4, cx=S / 2)
    im.save(os.path.join(OUT, "B_宋体竖排.png"))


# ---------------- C. 场记板 ----------------
def dir_c():
    im = Image.new("RGB", (S, S), CARBON)
    d = ImageDraw.Draw(im)
    bt, bb = 156, 262
    d.polygon([(96, bb), (172, bt), (704, bt), (628, bb)], fill=BONE)
    for i in range(5):
        x0 = 118 + i * 118
        d.polygon([(x0, bb), (x0 + 58, bt), (x0 + 100, bt), (x0 + 42, bb)], fill=CARBON)

    d.rectangle([96, bb, 704, 664], outline=(78, 80, 88), width=2)
    tracked(d, 430, "一人短剧厂牌", font(HEI, 104), BONE, tracking=3, cx=S / 2)
    d.line([(156, 512), (644, 512)], fill=(86, 88, 96), width=1)
    tracked(d, 578, "TAKE 01", font(HIRA, 30), (150, 152, 160), tracking=9, cx=S / 2)
    im.save(os.path.join(OUT, "C_场记板.png"))


# ---------------- E. 一人大字（主推） ----------------
def dir_e():
    im = Image.new("RGB", (S, S), INK)
    d = ImageDraw.Draw(im)
    big = font(SONG, 300, index=1)

    d.text((S / 2, 262), "一", font=big, fill=BONE, anchor="mm")
    d.text((S / 2, 466), "人", font=big, fill=BONE, anchor="mm")

    # 页脚锁定组合：朱块 + 短剧厂牌（小尺寸下读作一个整体）
    cap = font(HIRA, 36)
    cap_w = sum(d.textlength(c, font=cap) for c in "短剧厂牌") + 18 * 3
    blk = 40
    total = blk + 24 + cap_w
    left = (S - total) / 2
    d.rectangle([left, 702, left + blk, 702 + 34], fill=VERMIL)
    tracked(d, 738, "短剧厂牌", cap, (204, 196, 180), tracking=18, x=left + blk + 24)
    im.save(os.path.join(OUT, "E_一人大字.png"))


# ---------------- 对照表 ----------------
def sheet(names, out):
    cell, pad, top = 260, 28, 50
    W = pad + (cell + pad) * len(names)
    H = top + cell + 210
    sh = Image.new("RGB", (W, H), (250, 250, 250))
    d = ImageDraw.Draw(sh)
    fm = font(HIRA, 21)
    for i, n in enumerate(names):
        im = Image.open(os.path.join(OUT, n))
        x, y = pad + i * (cell + pad), top
        sh.paste(im.resize((cell, cell), Image.LANCZOS), (x, y))
        d.text((x + 2, y + cell + 12), n[0] + "  120 / 64 / 40 px", font=fm, fill=(70, 70, 70))
        for k, s in enumerate((120, 64, 40)):
            sh.paste(im.resize((s, s), Image.LANCZOS), (x + 2 + sum((120, 64, 40)[:k]) + 10 * k, y + cell + 48))
    d.text((pad, 12), "左：原图 800px；右：微信实际显示档位（会话列表约 40-64px）", font=fm, fill=(120, 120, 120))
    sh.save(os.path.join(OUT, out))
    return sh.size


if __name__ == "__main__":
    for fn in (dir_a, dir_b, dir_c, dir_e):
        fn()
    print(sheet(["A_竖屏画框.png", "B_宋体竖排.png", "C_场记板.png", "E_一人大字.png"], "对照_四方向.png"))
