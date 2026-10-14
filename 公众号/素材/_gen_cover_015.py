# -*- coding: utf-8 -*-
"""015《厂牌盯数02｜100 万播放换 1,000 元：AI 剧回本率 1.3%，先算你的回本播放量》封面两方向 + 对照图
纯本地 Pillow，零扣费（严禁调用任何付费生成 API）。900×383；关键文案宽度必须 ≤383
（分享卡只保留中间方形区），每条打印 OK/OVER 并 assert。两方向底色拉开区分度：
A=CARBON(52,49,44)，B=INK(26,24,22)（沿用 011/012/013/014 做法）。不放任何人脸/拟人形象。
注：Menlo 无中文字形，任何含汉字的行（含「5 个月」这类数字+汉字混排）一律走
mix/mix_centered，禁止直接用 MONO 画整行；末尾 cjk_guard() 断言含 CJK 的行段不得用 MONO。
写法照抄 _gen_cover_014.py（工具函数直接 import 复用）。
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
    """右上角角标「厂牌盯数 02」（分享卡裁边后仍在大图右上可见）。"""
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


# ── A：100 万播放换 1,000 元（CARBON 深底）────────────────────
def dir_a():
    im = Image.new("RGB", (W, H), CARBON)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    corner_badge(d, "厂牌盯数 02")
    cx = W / 2
    chk(d, "20 人团队 · 6 月账单", 22, mono=False)
    chk(d, "100 万播放", 54, mono=False)
    chk(d, "换 1,000 元", 54, mono=False)
    chk(d, "净亏 19.9 万 · 没花一分投流", 22, mono=False)

    mix_centered(d, cx, 72, "20 人团队 · 6 月账单", 22, FAINT)
    mix_centered(d, cx, 102, "100 万播放", 54, BONE)
    mix_centered(d, cx, 168, "换 1,000 元", 54, RUST)
    d.line([(cx - 150, 242), (cx + 150, 242)], fill=(64, 60, 55), width=1)
    mix_centered(d, cx, 254, "净亏 19.9 万 · 没花一分投流", 22, BONE)
    badge(d, cx, 298, "新黄河 10-14 · DataEye")
    # 两侧装饰（分享卡会裁掉）
    mix(d, 30, 150, "-87.5%", 24, (86, 82, 76))
    mix(d, 778, 150, "-90%+", 24, (86, 82, 76))
    mix(d, 34, 240, "20 万元", 20, (86, 82, 76), mono=False)
    mix(d, 796, 240, "10 元/万次", 20, (86, 82, 76), mono=False)
    return im, "封面_015_A_100万播放换1000元_900x383.png"


# ── B：回本率 1.3%（INK 更深底）────────────────────────────
def dir_b():
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    corner_badge(d, "厂牌盯数 02")
    cx = W / 2
    chk(d, "AI 短剧回本率", 22, mono=False)
    chk(d, "1.3%", 66, mono=False)
    chk(d, "5,000 万播放才算达标", 30, mono=False)
    chk(d, "98.7% 没回本 · 先算你的线", 22, mono=False)

    mix_centered(d, cx, 72, "AI 短剧回本率", 22, FAINT)
    mix_centered(d, cx, 100, "1.3%", 66, RUST)
    d.line([(cx - 150, 200), (cx + 150, 200)], fill=(64, 60, 55), width=1)
    mix_centered(d, cx, 214, "5,000 万播放才算达标", 30, BONE)
    mix_centered(d, cx, 260, "98.7% 没回本 · 先算你的线", 22, BONE)
    badge(d, cx, 302, "DataEye · 本号算例")
    # 两侧装饰（分享卡会裁掉）
    mix(d, 30, 130, "22.19 万部", 20, (86, 82, 76), mono=False)
    mix(d, 790, 200, "每天 1,200 部", 20, (86, 82, 76), mono=False)
    mix(d, 34, 260, "5-10 元", 20, (86, 82, 76))
    mix(d, 800, 130, "2 亿次", 20, (86, 82, 76))
    return im, "封面_015_B_回本率1.3_900x383.png"


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
    ttl = ["厂牌盯数02｜100 万播放换 1,000 元", "AI 剧回本率 1.3%：先算你的回本播放量"]
    yy = pad
    for name, im in built:
        dbg = im.copy()
        safe_zone(ImageDraw.Draw(dbg))
        sd.text((pad, yy), name + "　（细框=分享卡安全区）", font=f(HIRA, 22, index=2), fill=(30, 30, 30))
        sheet.paste(dbg, (pad, yy + 34))
        sheet.paste(mock(im, True, ttl, "10-14"), (pad + W + pad, yy + 34))
        sheet.paste(mock(im, False, ttl, "10-14"), (pad + W + pad + 400 + gap, yy + 34))
        yy += H + 130 + 40
    p = os.path.join(OUT, "对照_015封面两方向.png")
    sheet.save(p)
    print("sheet", p, sheet.size)
