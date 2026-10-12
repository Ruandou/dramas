# -*- coding: utf-8 -*-
"""010《9 月备案公示 296 部里，「微短剧」出现 0 次：这个赛道到底怎么被统计》封面两方向
纯本地 Pillow，零扣费。900×383；每条关键文案宽度必须 ≤383（分享卡只保留中间方形区）。
注：Menlo 无中文字形，中英混排行一律走 mix/mix_centered。
"""
import os
from PIL import Image, ImageDraw
from _gen_cover_004 import (W, H, SONG, HIRA, MONO, CARBON, INK, BONE, VERM, DIM, FAINT,
                            BLUE, f, mix, mixw, centered, mix_centered, tracked, safe_zone, OUT)
from _gen_cover_006 import mock

SAFE = 383
TOP = 84
RUST = (214, 96, 78)
TEAL = (74, 138, 132)


def chk(d, text, size, mono=True):
    w = mixw(d, text, size, mono=mono)
    print("   %s %4dpx  %s" % ("OK " if w <= SAFE else "OVER", w, text))
    assert w <= SAFE, (text, w)


def eyebrow(d, tag="数据"):
    d.rectangle([54, 50, 65, 50 + 26], fill=VERM)
    tracked(d, 78, 46, "一人短剧厂牌 · " + tag, f(HIRA, 20), DIM, 3)


# ── A：0 次 ─────────────────────────────────────────────────
def dir_a():
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    cx = W / 2
    chk(d, "9 月全国备案公示 296 部", 20, mono=False)
    chk(d, "0 次", 92)
    chk(d, "「微短剧」三个字", 26, mono=False)
    chk(d, "在 296 行里一次没出现", 26, mono=False)
    chk(d, "它不在这张表里，却在另一张表被统计", 19, mono=False)

    mix_centered(d, cx, TOP, "9 月全国备案公示 296 部", 20, FAINT)
    mix_centered(d, cx, TOP + 26, "0 次", 92, BONE)
    mix_centered(d, cx, TOP + 148, "「微短剧」三个字", 26, RUST)
    mix_centered(d, cx, TOP + 190, "在 296 行里一次没出现", 26, BONE)
    d.line([(cx - 150, TOP + 236), (cx + 150, TOP + 236)], fill=(64, 60, 55), width=1)
    mix_centered(d, cx, TOP + 248, "它不在这张表里，却在另一张表被统计", 19, FAINT)
    # 两侧装饰（分享卡会裁掉）
    mix(d, 24, 150, "中剧 53 部", 19, (86, 82, 76), mono=False)
    mix(d, 726, 190, "网络故事片 176 部", 19, (86, 82, 76), mono=False)
    return im, "封面_010_A_零次_900x383.png"


# ── B：159 部 / 39.4→33.9 ──────────────────────────────────
def dir_b():
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    cx = W / 2
    chk(d, "同一个季度，两套数", 22, mono=False)
    chk(d, "159 部", 76)
    chk(d, "季度通告里的微短剧", 21, RUST)
    chk(d, "月度公示 296 部里 0 部", 21, BLUE)
    chk(d, "平均集数 39.4 → 33.9，一年在变薄", 19, BONE)

    mix_centered(d, cx, TOP, "同一个季度，两套数", 22, FAINT)
    mix_centered(d, cx, TOP + 28, "159 部", 76, BONE)
    mix_centered(d, cx, TOP + 132, "季度通告里的微短剧", 21, RUST)
    mix_centered(d, cx, TOP + 166, "月度公示 296 部里 0 部", 21, BLUE)
    d.line([(cx - 160, TOP + 208), (cx + 160, TOP + 208)], fill=(64, 60, 55), width=1)
    mix_centered(d, cx, TOP + 220, "平均集数 39.4 → 33.9，一年在变薄", 19, BONE)
    return im, "封面_010_B_一百五十九部_900x383.png"


if __name__ == "__main__":
    built = []
    for fn in (dir_a, dir_b):
        print(fn.__name__)
        im, name = fn()
        im.save(os.path.join(OUT, name))
        built.append((name, im))
        print(name, im.size)

    pad, gap = 26, 24
    sw = W + 400 + 400 + pad * 4
    sh = (H + 130 + 40) * 2 + pad * 2
    sheet = Image.new("RGB", (sw, sh), (244, 244, 244))
    sd = ImageDraw.Draw(sheet)
    ttl = ["9 月备案公示 296 部里", "「微短剧」出现 0 次：这个赛道怎么被统计"]
    yy = pad
    for name, im in built:
        dbg = im.copy()
        safe_zone(ImageDraw.Draw(dbg))
        sd.text((pad, yy), name + "　（细框=分享卡安全区）", font=f(HIRA, 22, index=2), fill=(30, 30, 30))
        sheet.paste(dbg, (pad, yy + 34))
        sheet.paste(mock(im, True, ttl, "10-12"), (pad + W + pad, yy + 34))
        sheet.paste(mock(im, False, ttl, "10-12"), (pad + W + pad + 400 + gap, yy + 34))
        yy += H + 130 + 40
    p = os.path.join(OUT, "对照_010封面两方向.png")
    sheet.save(p)
    print("sheet", p, sheet.size)
