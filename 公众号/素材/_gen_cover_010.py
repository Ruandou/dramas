# -*- coding: utf-8 -*-
"""010《"微短剧不能碰司法、公安题材"？官方季度数据里 17 部拿到了发行许可》封面两方向
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


# ── A：17 部拿到发行许可（打脸"不能碰"）────────────────────
def dir_a():
    im = Image.new("RGB", (W, H), CARBON)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    cx = W / 2
    chk(d, "2026 二季度拿到发行许可的微短剧", 20, mono=False)
    chk(d, "17 部", 92)
    chk(d, "司法 6 · 公安 10 · 国家安全 1", 24, mono=False)
    chk(d, "平均 30.0 集/部，不是试水短内容", 24, mono=False)
    chk(d, "「微短剧不能碰司法公安」和官方数字不吻合", 17, mono=False)

    mix_centered(d, cx, TOP, "2026 二季度拿到发行许可的微短剧", 20, FAINT)
    mix_centered(d, cx, TOP + 26, "17 部", 92, BONE)
    mix_centered(d, cx, TOP + 150, "司法 6 · 公安 10 · 国家安全 1", 24, RUST)
    mix_centered(d, cx, TOP + 192, "平均 30.0 集/部，不是试水短内容", 24, BONE)
    d.line([(cx - 150, TOP + 236), (cx + 150, TOP + 236)], fill=(64, 60, 55), width=1)
    mix_centered(d, cx, TOP + 248, "「微短剧不能碰司法公安」和官方数字不吻合", 17, FAINT)
    # 两侧装饰（分享卡会裁掉）
    mix(d, 24, 150, "510 集", 19, (86, 82, 76), mono=False)
    mix(d, 740, 190, "〔2026〕5 号通告", 19, (86, 82, 76), mono=False)
    return im, "封面_010_A_十七部拿证_900x383.png"


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
    ttl = ["微短剧不能碰司法、公安题材？", "官方季度数据里 17 部拿到了发行许可"]
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
