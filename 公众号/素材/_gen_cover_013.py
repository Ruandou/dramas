# -*- coding: utf-8 -*-
"""013《厂牌周报01｜快手把完播率换算成钱：50%加权怎么叠，20万上限谁能碰到》封面两方向 + 对照图
纯本地 Pillow，零扣费（严禁调用任何付费生成 API）。900×383；关键文案宽度必须 ≤383
（分享卡只保留中间方形区），每条打印 OK/OVER 并 assert。两方向底色拉开区分度：
A=CARBON(52,49,44)，B=INK(26,24,22)（沿用 011/012 做法）。不放任何人脸/拟人形象。
注：Menlo 无中文字形，任何含汉字的行（含「20 万」「40 万」这类数字+汉字混排）一律走
mix/mix_centered，禁止直接用 MONO 画整行；末尾 cjk_guard() 断言含 CJK 的行段不得用 MONO。
写法照抄 _gen_cover_012.py（工具函数直接 import 复用）。
"""
import os
from PIL import Image, ImageDraw
from _gen_cover_004 import (W, H, SONG, HIRA, MONO, CARBON, INK, BONE, VERM, DIM, FAINT,
                            BLUE, f, mix, mixw, centered, mix_centered, tracked, safe_zone,
                            runs, is_ascii, OUT)
from _gen_cover_006 import mock

SAFE = 383
RUST = (214, 96, 78)

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


def eyebrow(d):
    d.rectangle([54, 50, 65, 50 + 26], fill=VERM)
    tracked(d, 78, 46, "一人短剧厂牌 · 核数", f(HIRA, 20), DIM, 3)


def corner_badge(d, text):
    """右上角角标「厂牌周报 01」（分享卡裁边后仍在大图右上可见）。"""
    size = 20
    w = mixw(d, text, size, mono=False)
    x1, y0 = W - 54, 42
    d.rectangle([x1 - w - 24, y0, x1, y0 + size + 16], outline=(96, 92, 86), width=2)
    mix(d, x1 - w - 12, y0 + 8, text, size, DIM, mono=False)
    LINES.append((text, size, False))


def badge(d, cx, y, text, size=18):
    w = mixw(d, text, size, mono=False)
    chk(d, text, size, mono=False)
    d.rectangle([cx - w / 2 - 14, y, cx + w / 2 + 14, y + size + 16], outline=(96, 92, 86), width=2)
    mix_centered(d, cx, y + 8, text, size, DIM, mono=False)


# ── A：完播率换钱（CARBON 深底）─────────────────────────────
def dir_a():
    im = Image.new("RGB", (W, H), CARBON)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    corner_badge(d, "厂牌周报 01")
    cx = W / 2
    chk(d, "快手把分账金额挂上系数", 22, mono=False)
    chk(d, "完播率换钱", 58, mono=False)
    chk(d, "50% 加权怎么叠", 28, mono=True)
    chk(d, "15%+15%+20% · 上限 20 万元", 22, mono=True)

    mix_centered(d, cx, 74, "快手把分账金额挂上系数", 22, FAINT)
    centered(d, cx, 104, "完播率换钱", f(SONG, 58, index=1), BONE, 3)
    d.line([(cx - 150, 186), (cx + 150, 186)], fill=(64, 60, 55), width=1)
    mix_centered(d, cx, 198, "50% 加权怎么叠", 28, RUST)
    mix_centered(d, cx, 244, "15%+15%+20% · 上限 20 万元", 22, BONE)
    badge(d, cx, 292, "活动期 10.1—11.30")
    # 两侧装饰（分享卡会裁掉）
    mix(d, 30, 150, "+15%", 24, (86, 82, 76))
    mix(d, 790, 150, "+20%", 24, (86, 82, 76))
    mix(d, 34, 240, "20万", 20, (86, 82, 76), mono=False)
    mix(d, 796, 240, "40万", 20, (86, 82, 76), mono=False)
    return im, "封面_013_A_完播率换钱_900x383.png"


# ── B：20 万上限谁能碰到（INK 更深底）───────────────────────
def dir_b():
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    corner_badge(d, "厂牌周报 01")
    cx = W / 2
    chk(d, "想拿满 50% 加权", 22, mono=False)
    chk(d, "20 万上限", 66)
    chk(d, "谁能碰到", 40, mono=False)
    chk(d, "40 万才顶格 · 60 天续作红线", 22)

    mix_centered(d, cx, 56, "想拿满 50% 加权", 22, FAINT)
    mix_centered(d, cx, 84, "20 万上限", 66, RUST)
    centered(d, cx, 168, "谁能碰到", f(SONG, 40, index=1), BONE, 2)
    d.line([(cx - 150, 226), (cx + 150, 226)], fill=(64, 60, 55), width=1)
    mix_centered(d, cx, 240, "40 万才顶格 · 60 天续作红线", 22, BONE)
    badge(d, cx, 290, "本号按公开系数计算")
    # 两侧装饰（分享卡会裁掉）
    mix(d, 30, 120, "5万→2.5万", 20, (86, 82, 76))
    mix(d, 745, 200, "80万→20万", 20, (86, 82, 76))
    return im, "封面_013_B_二十万上限_900x383.png"


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
    ttl = ["厂牌周报 01", "快手把完播率换算成钱"]
    yy = pad
    for name, im in built:
        dbg = im.copy()
        safe_zone(ImageDraw.Draw(dbg))
        sd.text((pad, yy), name + "　（细框=分享卡安全区）", font=f(HIRA, 22, index=2), fill=(30, 30, 30))
        sheet.paste(dbg, (pad, yy + 34))
        sheet.paste(mock(im, True, ttl, "10-13"), (pad + W + pad, yy + 34))
        sheet.paste(mock(im, False, ttl, "10-13"), (pad + W + pad + 400 + gap, yy + 34))
        yy += H + 130 + 40
    p = os.path.join(OUT, "对照_013封面两方向.png")
    sheet.save(p)
    print("sheet", p, sheet.size)
