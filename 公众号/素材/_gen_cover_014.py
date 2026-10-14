# -*- coding: utf-8 -*-
"""014《厂牌盯数01｜9月海外收入2.85亿美元下滑，ReelShort靠AI剧占比88%登顶》封面两方向 + 对照图
纯本地 Pillow，零扣费（严禁调用任何付费生成 API）。900×383；关键文案宽度必须 ≤383
（分享卡只保留中间方形区），每条打印 OK/OVER 并 assert。两方向底色拉开区分度：
A=CARBON(52,49,44)，B=INK(26,24,22)（沿用 011/012/013 做法）。不放任何人脸/拟人形象。
注：Menlo 无中文字形，任何含汉字的行（含「5 个月」这类数字+汉字混排）一律走
mix/mix_centered，禁止直接用 MONO 画整行；末尾 cjk_guard() 断言含 CJK 的行段不得用 MONO。
写法照抄 _gen_cover_013.py（工具函数直接 import 复用）。
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
    tracked(d, 78, 46, "一人短剧厂牌 · 盯数", f(HIRA, 20), DIM, 3)


def corner_badge(d, text):
    """右上角角标「厂牌盯数 01」（分享卡裁边后仍在大图右上可见）。"""
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


# ── A：88% 主题（CARBON 深底）──────────────────────────────
def dir_a():
    im = Image.new("RGB", (W, H), CARBON)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    corner_badge(d, "厂牌盯数 01")
    cx = W / 2
    chk(d, "ReelShort 内容里", 22, mono=False)
    chk(d, "AI 剧占比 88%", 52, mono=False)
    chk(d, "5 个月：10% → 88%", 28, mono=False)
    chk(d, "真人产量没降 · 供给被 AI 放大", 22, mono=False)

    mix_centered(d, cx, 74, "ReelShort 内容里", 22, FAINT)
    centered(d, cx, 104, "AI 剧占比 88%", f(SONG, 52, index=1), BONE, 3)
    d.line([(cx - 150, 186), (cx + 150, 186)], fill=(64, 60, 55), width=1)
    mix_centered(d, cx, 198, "5 个月：10% → 88%", 28, RUST)
    mix_centered(d, cx, 244, "真人产量没降 · 供给被 AI 放大", 22, BONE)
    badge(d, cx, 292, "DataEye 9 月海外月报")
    # 两侧装饰（分享卡会裁掉）
    mix(d, 30, 150, "-13.5%", 24, (86, 82, 76))
    mix(d, 796, 150, "+500%", 24, (86, 82, 76))
    mix(d, 34, 240, "+3%", 20, (86, 82, 76))
    mix(d, 802, 240, "-1.3%", 20, (86, 82, 76))
    return im, "封面_014_A_AI剧占比88_900x383.png"


# ── B：拉新停了，钱还在（INK 更深底）────────────────────────
def dir_b():
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    corner_badge(d, "厂牌盯数 01")
    cx = W / 2
    chk(d, "9 月海外短剧大盘：四个指标同降", 22, mono=False)
    chk(d, "拉新停了", 58, mono=False)
    chk(d, "钱还在", 40, mono=False)
    chk(d, "下载 -13.5% · 收入 -1.3%", 22, mono=False)

    mix_centered(d, cx, 56, "9 月海外短剧大盘：四个指标同降", 22, FAINT)
    mix_centered(d, cx, 84, "拉新停了", 58, RUST)
    centered(d, cx, 168, "钱还在", f(SONG, 40, index=1), BONE, 2)
    d.line([(cx - 150, 226), (cx + 150, 226)], fill=(64, 60, 55), width=1)
    mix_centered(d, cx, 240, "下载 -13.5% · 收入 -1.3%", 22, BONE)
    badge(d, cx, 290, "本号读数 · 降幅差 10 倍")
    # 两侧装饰（分享卡会裁掉）
    mix(d, 30, 120, "2.42 亿", 20, (86, 82, 76), mono=False)
    mix(d, 788, 200, "2.85 亿", 20, (86, 82, 76), mono=False)
    return im, "封面_014_B_拉新停了钱还在_900x383.png"


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
    ttl = ["厂牌盯数01｜9 月海外收入 2.85 亿美元下滑", "ReelShort 靠 AI 剧占比 88% 登顶"]
    yy = pad
    for name, im in built:
        dbg = im.copy()
        safe_zone(ImageDraw.Draw(dbg))
        sd.text((pad, yy), name + "　（细框=分享卡安全区）", font=f(HIRA, 22, index=2), fill=(30, 30, 30))
        sheet.paste(dbg, (pad, yy + 34))
        sheet.paste(mock(im, True, ttl, "10-14"), (pad + W + pad, yy + 34))
        sheet.paste(mock(im, False, ttl, "10-14"), (pad + W + pad + 400 + gap, yy + 34))
        yy += H + 130 + 40
    p = os.path.join(OUT, "对照_014封面两方向.png")
    sheet.save(p)
    print("sheet", p, sheet.size)
