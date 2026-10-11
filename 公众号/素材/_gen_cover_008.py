# -*- coding: utf-8 -*-
"""008《正文一个字没提 AI，报名表却问「是否为 AI 作品」》封面两方向
纯本地 Pillow，零扣费。900×383；关键信息必须落在中间 383×383 分享卡安全区内。
注：MONO（Menlo）无中文字形，中英混排行一律走 mix/mix_centered，否则出豆腐块。
"""
import os
from PIL import Image, ImageDraw
from _gen_cover_004 import (W, H, SONG, HIRA, MONO, CARBON, INK, BONE, VERM, DIM, FAINT,
                            f, mix, mixw, centered, mix_centered, tracked, safe_zone, OUT)
from _gen_cover_006 import mock

SAFE = 383
TOP = 86          # eyebrow 占 48–78，正文行一律从 86 起
RUST = (214, 96, 78)


def chk(d, text, size, mono=False):
    w = mixw(d, text, size, mono=mono)
    print("   %s %4dpx  %s" % ("OK " if w <= SAFE else "OVER", w, text))
    return w


def eyebrow(d):
    d.rectangle([54, 52, 65, 52 + 26], fill=VERM)
    tracked(d, 78, 48, "一人短剧厂牌 · 政策", f(HIRA, 20), DIM, 3)


# ── A：巨字 AI ＋ 0 次 ──────────────────────────────────────
def dir_a():
    im = Image.new("RGB", (W, H), CARBON)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    cx = W / 2
    chk(d, "广电办发〔2026〕245 号", 19)
    chk(d, "正文一个字没提", 27)
    chk(d, "0 次", 42)
    chk(d, "报名表却问「是否为 AI 作品」", 21)
    centered(d, cx, TOP, "广电办发〔2026〕245 号", f(HIRA, 19), FAINT, 1)
    centered(d, cx, TOP + 30, "正文一个字没提", f(SONG, 27, index=1), BONE, 2)
    centered(d, cx, TOP + 66, "AI", f(MONO, 84, index=1), BONE, -3)
    mix_centered(d, cx, TOP + 166, "0 次", 42, RUST)
    mix_centered(d, cx, TOP + 220, "报名表却问「是否为 AI 作品」", 21, (226, 216, 202))
    return im, "封面_008_A_零次_900x383.png"


# ── B：把那一栏画成表格 ─────────────────────────────────────
def dir_b():
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    cx = W / 2
    chk(d, "2026 国际微短剧大赛 · 报名表", 20)
    chk(d, "正文 1,566 字，一个「AI」也没有", 22)
    chk(d, "正文写方向，表格要口径", 24)
    chk(d, "13 行 15 栏 · 申报截至 11-30", 20)
    mix_centered(d, cx, TOP, "2026 国际微短剧大赛 · 报名表", 20, FAINT)
    mix_centered(d, cx, TOP + 30, "正文 1,566 字，一个「AI」也没有", 22, BONE)

    bx0, bx1 = cx - 176, cx + 176
    div = bx0 + 214
    for k, (label, y, on) in enumerate((("是否为 AI 作品", 152, True),
                                        ("制作成本（万元）", 210, False))):
        col = RUST if on else BONE
        d.rectangle([bx0, y, bx1, y + 50], fill=(30, 28, 26),
                    outline=RUST if on else (88, 82, 74), width=2)
        d.line([(div, y), (div, y + 50)], fill=(88, 82, 74), width=2)
        mix(d, bx0 + 14, y + 12, label, 24, col, mono=False)

    mix_centered(d, cx, 276, "正文写方向，表格要口径", 24, BONE)
    mix_centered(d, cx, 318, "13 行 15 栏 · 申报截至 11-30", 20, FAINT)
    return im, "封面_008_B_那一栏_900x383.png"


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
    ttl = ["正文一个字没提 AI，报名表却问「是否为 AI 作品」", "广电办发〔2026〕245 号 · 拆报名表"]
    yy = pad
    for name, im in built:
        dbg = im.copy()
        safe_zone(ImageDraw.Draw(dbg))
        sd.text((pad, yy), name + "　（细框=分享卡安全区）", font=f(HIRA, 22, index=2), fill=(30, 30, 30))
        sheet.paste(dbg, (pad, yy + 34))
        sheet.paste(mock(im, True, ttl, "10-11"), (pad + W + pad, yy + 34))
        sheet.paste(mock(im, False, ttl, "10-11"), (pad + W + pad + 400 + gap, yy + 34))
        yy += H + 130 + 40
    p = os.path.join(OUT, "对照_008封面两方向.png")
    sheet.save(p)
    print("sheet", p, sheet.size)
