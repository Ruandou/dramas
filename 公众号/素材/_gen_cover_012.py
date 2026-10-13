# -*- coding: utf-8 -*-
"""012《只有 8 个粉丝的号，文章怎么会有 777 个人读？》封面两方向
纯本地 Pillow，零扣费（严禁调用任何付费生成 API）。900×383；每条关键文案宽度必须
≤383（分享卡只保留中间方形区）。两方向底色拉开区分度：A=CARBON(52,49,44)，
B=INK(26,24,22)（沿用 011 做法）。不放任何人脸/拟人形象。
注：Menlo 无中文字形，任何含汉字的行（含「8 个粉丝」「777 个人」这类数字+汉字混排）
一律走 mix/mix_centered，禁止直接用 MONO 画整行；末尾 cjk_guard() 断言含 CJK 的
行段不得用 MONO。写法照抄 _gen_cover_011.py。
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


def eyebrow(d, tag="数据"):
    d.rectangle([54, 50, 65, 50 + 26], fill=VERM)
    tracked(d, 78, 46, "一人短剧厂牌 · " + tag, f(HIRA, 20), DIM, 3)


def badge(d, cx, y, text, size=18):
    """角标：圆角感边框 chip，居中放，宽度按安全区校验。"""
    w = mixw(d, text, size, mono=False)
    chk(d, text, size, mono=False)
    box = (cx - w / 2 - 14, y, cx + w / 2 + 14, y + size + 16)
    d.rectangle(box, outline=(96, 92, 86), width=2)
    mix_centered(d, cx, y + 8, text, size, DIM, mono=False)


# ── A：8 个粉丝（CARBON 深底）───────────────────────────────
def dir_a():
    im = Image.new("RGB", (W, H), CARBON)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    cx = W / 2
    chk(d, "本号的关注数", 22, mono=False)
    chk(d, "8 个粉丝", 84)
    chk(d, "30 天 777 个人读过", 24, mono=False)

    mix_centered(d, cx, 82, "本号的关注数", 22, FAINT)
    mix_centered(d, cx, 112, "8 个粉丝", 84, BONE)
    d.line([(cx - 150, 218), (cx + 150, 218)], fill=(64, 60, 55), width=1)
    mix_centered(d, cx, 232, "30 天 777 个人读过", 24, RUST)
    badge(d, cx, 292, "本号后台原始读数")
    # 两侧装饰（分享卡会裁掉）
    mix(d, 30, 164, "fans 8", 19, (86, 82, 76))
    mix(d, 690, 200, "readers 777", 19, (86, 82, 76))
    return im, "封面_012_A_8个粉丝_900x383.png"


# ── B：91.4% 推荐（INK 更深底）──────────────────────────────
def dir_b():
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    cx = W / 2
    chk(d, "12 篇阅读人数里推荐渠道占", 22, mono=False)
    chk(d, "91.4%", 92)
    chk(d, "推荐", 40, mono=False)
    chk(d, "8 个粉丝不是分发变量", 24, mono=False)

    mix_centered(d, cx, 60, "12 篇阅读人数里推荐渠道占", 22, FAINT)
    mix_centered(d, cx, 90, "91.4%", 92, RUST)
    mix_centered(d, cx, 192, "推荐", 40, BONE)
    d.line([(cx - 150, 250), (cx + 150, 250)], fill=(64, 60, 55), width=1)
    mix_centered(d, cx, 262, "8 个粉丝不是分发变量", 24, BONE)
    badge(d, cx, 316, "12 篇逐篇拉总")
    # 两侧装饰（分享卡会裁掉）
    mix(d, 26, 150, "710/777", 19, (86, 82, 76))
    mix(d, 700, 190, "推荐驱动型", 19, (86, 82, 76), mono=False)
    return im, "封面_012_B_91点4推荐_900x383.png"


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
    ttl = ["只有 8 个粉丝", "文章怎么会有 777 个人读？"]
    yy = pad
    for name, im in built:
        dbg = im.copy()
        safe_zone(ImageDraw.Draw(dbg))
        sd.text((pad, yy), name + "　（细框=分享卡安全区）", font=f(HIRA, 22, index=2), fill=(30, 30, 30))
        sheet.paste(dbg, (pad, yy + 34))
        sheet.paste(mock(im, True, ttl, "10-13"), (pad + W + pad, yy + 34))
        sheet.paste(mock(im, False, ttl, "10-13"), (pad + W + pad + 400 + gap, yy + 34))
        yy += H + 130 + 40
    p = os.path.join(OUT, "对照_012封面两方向.png")
    sheet.save(p)
    print("sheet", p, sheet.size)
