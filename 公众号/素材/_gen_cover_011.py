# -*- coding: utf-8 -*-
"""011《「81 秒」：完播率第一次有了官方公式》封面两方向
纯本地 Pillow，零扣费。900×383；每条关键文案宽度必须 ≤383（分享卡只保留中间方形区）。
两方向底色拉开区分度：A=CARBON(52,49,44)，B=INK(26,24,22)（沿用 010 做法）。
注：Menlo 无中文字形，任何含汉字的行（含「81 秒」这类数字+汉字混排）一律走 mix/mix_centered，
禁止直接用 MONO 画整行；末尾 cjk_guard() 断言含 CJK 的行段不得用 MONO。
"""
import os
from PIL import Image, ImageDraw
from _gen_cover_004 import (W, H, SONG, HIRA, MONO, CARBON, INK, BONE, VERM, DIM, FAINT,
                            BLUE, f, mix, mixw, centered, mix_centered, tracked, safe_zone,
                            runs, is_ascii, OUT)
from _gen_cover_006 import mock

SAFE = 383
TOP = 84
RUST = (214, 96, 78)
TEAL = (74, 138, 132)

LINES = []  # (text, size, mono)


def chk(d, text, size, mono=True):
    w = mixw(d, text, size, mono=mono)
    print("   %s %4dpx  %s" % ("OK " if w <= SAFE else "OVER", w, text))
    assert w <= SAFE, (text, w)
    LINES.append((text, size, mono))


def cjk_guard():
    bad = []
    for text, size, mono in LINES:
        for r in runs(text):
            font_choice = MONO if (mono and is_ascii(r)) else HIRA
            if (not is_ascii(r)) and font_choice == MONO:
                bad.append((text, r))
    assert not bad, bad
    n_cjk = sum(1 for t, _, _ in LINES if any(ord(c) >= 0x2100 for c in t))
    print("cjk_guard: 共登记 %d 条文案（其中 %d 条含 CJK，全部经 mix 分流，无一走 MONO）→ 通过"
          % (len(LINES), n_cjk))


def eyebrow(d, tag="数据"):
    d.rectangle([54, 50, 65, 50 + 26], fill=VERM)
    tracked(d, 78, 46, "一人短剧厂牌 · " + tag, f(HIRA, 20), DIM, 3)


# ── A：81 秒（CARBON 深底）──────────────────────────────────
def dir_a():
    im = Image.new("RGB", (W, H), CARBON)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    cx = W / 2
    chk(d, "完播率第一次有了公式", 22, mono=False)
    chk(d, "81 秒", 96)
    chk(d, "90 秒的剧，要看到 81 秒", 24, mono=False)

    mix_centered(d, cx, TOP, "完播率第一次有了公式", 22, FAINT)
    mix_centered(d, cx, TOP + 30, "81 秒", 96, BONE)
    d.line([(cx - 150, TOP + 158), (cx + 150, TOP + 158)], fill=(64, 60, 55), width=1)
    mix_centered(d, cx, TOP + 170, "90 秒的剧，要看到 81 秒", 24, BONE)
    # 两侧装饰（分享卡会裁掉）
    mix(d, 26, 164, "90 × 90%", 19, (86, 82, 76))
    mix(d, 690, 200, "D_C ≤ 5 min", 19, (86, 82, 76))
    return im, "封面_011_A_八十一秒_900x383.png"


# ── B：10 天窗口（INK 更深底）───────────────────────────────
def dir_b():
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    cx = W / 2
    chk(d, "10 天", 96)
    chk(d, "今天起可对国家收视指标提意见", 22, mono=False)
    chk(d, "10-13 → 10-22 · kjsbzc@nrta.gov.cn", 17)

    mix_centered(d, cx, TOP - 4, "今天起可对国家收视指标提意见", 22, BONE)
    mix_centered(d, cx, TOP + 26, "10 天", 96, RUST)
    d.line([(cx - 150, TOP + 154), (cx + 150, TOP + 154)], fill=(64, 60, 55), width=1)
    mix_centered(d, cx, TOP + 166, "10-13 → 10-22 · kjsbzc@nrta.gov.cn", 17, FAINT)
    # 两侧装饰（分享卡会裁掉）
    mix(d, 26, 164, "公示期", 19, (86, 82, 76), mono=False)
    mix(d, 700, 200, "报批稿", 19, (86, 82, 76), mono=False)
    return im, "封面_011_B_十天窗口_900x383.png"


if __name__ == "__main__":
    built = []
    for fn in (dir_a, dir_b):
        print(fn.__name__)
        im, name = fn()
        im.save(os.path.join(OUT, name))
        built.append((name, im))
        print(name, im.size)
    print()
    cjk_guard()

    pad, gap = 26, 24
    sw = W + 400 + 400 + pad * 4
    sh = (H + 130 + 40) * 2 + pad * 2
    sheet = Image.new("RGB", (sw, sh), (244, 244, 244))
    sd = ImageDraw.Draw(sheet)
    ttl = ["「81 秒」：完播率第一次有了公式", "国家收视指标报批稿公示，异议窗口只有 10 天"]
    yy = pad
    for name, im in built:
        dbg = im.copy()
        safe_zone(ImageDraw.Draw(dbg))
        sd.text((pad, yy), name + "　（细框=分享卡安全区）", font=f(HIRA, 22, index=2), fill=(30, 30, 30))
        sheet.paste(dbg, (pad, yy + 34))
        sheet.paste(mock(im, True, ttl, "10-13"), (pad + W + pad, yy + 34))
        sheet.paste(mock(im, False, ttl, "10-13"), (pad + W + pad + 400 + gap, yy + 34))
        yy += H + 130 + 40
    p = os.path.join(OUT, "对照_011封面两方向.png")
    sheet.save(p)
    print("sheet", p, sheet.size)
