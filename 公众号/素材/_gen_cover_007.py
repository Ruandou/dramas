# -*- coding: utf-8 -*-
"""007《微短剧到底有多少用户？五个数全都真，但没有一个能比》封面两方向
纯本地 Pillow，零扣费。900×383；关键信息落在中间 383×383 分享卡安全区。
"""
import os
from PIL import Image, ImageDraw
from _gen_cover_004 import (W, H, SONG, HIRA, MONO, CARBON, INK, BONE, VERM, DIM, FAINT,
                            f, mix, mixw, centered, mix_centered, tracked, safe_zone, OUT)
from _gen_cover_006 import mock


def eyebrow(d):
    d.rectangle([54, 52, 65, 52 + 26], fill=VERM)
    tracked(d, 78, 48, "一人短剧厂牌 · 核数", f(HIRA, 20), DIM, 3)


# ── A：三个数并排，全都真 ───────────────────────────────────
def dir_a():
    im = Image.new("RGB", (W, H), CARBON)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    cx = W / 2
    centered(d, cx, 76, "微短剧到底多少人？", f(SONG, 36, index=1), BONE, 1)
    rows = [("7.18 亿", "QuestMobile 2026-02", (196, 62, 46)),
            ("6.31 亿", "CSM 全媒体 2026-06", (150, 142, 128)),
            ("超 8 亿", "总局发布会 2026-09", (108, 148, 190))]
    y = 128
    for val, who, color in rows:
        mix_centered(d, cx, y, val, 34, color)
        mix_centered(d, cx, y + 42, who, 18, FAINT)
        y += 76
    return im, "封面_007_A_三个都真_900x383.png"


# ── B：巨字 4,400 万 ───────────────────────────────────────
def dir_b():
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    cx = W / 2
    centered(d, cx, 74, "4,400", f(MONO, 116, index=1), BONE, -5)
    centered(d, cx, 196, "万", f(SONG, 40, index=1), VERM, 2)
    mix_centered(d, cx, 252, "3.35+4.27=7.62≠7.18", 26, BONE)
    mix_centered(d, cx, 302, "同一家机构·同一页·同一时点", 21, FAINT)
    mix_centered(d, cx, 336, "分端数字永远不能相加", 24, (196, 62, 46))
    return im, "封面_007_B_4400万_900x383.png"


if __name__ == "__main__":
    built = []
    for fn in (dir_a, dir_b):
        im, name = fn()
        im.save(os.path.join(OUT, name))
        built.append((name, im))
        print(name, im.size)

    pad, gap = 26, 24
    sw = W + 400 + 400 + pad * 4
    sh = (H + 130 + 40) * 2 + pad * 2
    sheet = Image.new("RGB", (sw, sh), (244, 244, 244))
    sd = ImageDraw.Draw(sheet)
    ttl = ["QuestMobile 7.18 亿、CSM 6.31 亿、总局超 8 亿", "微短剧用户数为什么不能拿来比"]
    yy = pad
    for name, im in built:
        dbg = im.copy()
        safe_zone(ImageDraw.Draw(dbg))
        sd.text((pad, yy), name + "　（细框=分享卡安全区）", font=f(HIRA, 22, index=2), fill=(30, 30, 30))
        sheet.paste(dbg, (pad, yy + 34))
        sheet.paste(mock(im, True, ttl, "10-11"), (pad + W + pad, yy + 34))
        sheet.paste(mock(im, False, ttl, "10-11"), (pad + W + pad + 400 + gap, yy + 34))
        yy += H + 130 + 40
    p = os.path.join(OUT, "对照_007封面两方向.png")
    sheet.save(p)
    print("sheet", p, sheet.size)
