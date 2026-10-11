# -*- coding: utf-8 -*-
"""006《AI 漫剧「4 月 1 日强制下线」我追到源头》封面两方向
纯本地 Pillow，零扣费。900×383（2.35:1）；关键信息落在中间 383×383 分享卡安全区。
工具函数与配色直接复用 _gen_cover_004.py。
"""
import os
from PIL import Image, ImageDraw
from _gen_cover_004 import (W, H, SONG, HIRA, MONO, CARBON, INK, BONE, VERM, DIM, FAINT,
                            f, mix, mixw, centered, mix_centered, tracked, safe_zone,
                            mode_mock, OUT)


def eyebrow(d, tag):
    d.rectangle([54, 52, 65, 52 + 26], fill=VERM)
    tracked(d, 78, 48, "一人短剧厂牌 · " + tag, f(HIRA, 20), DIM, 3)


# ── A：三层出处，只有一层有全文 ─────────────────────────────
def dir_a():
    im = Image.new("RGB", (W, H), CARBON)
    d = ImageDraw.Draw(im)
    eyebrow(d, "核规")
    cx = W / 2
    mix_centered(d, cx, 82, "「4 月 1 日 AI 漫剧强制下线」", 24, BONE)
    centered(d, cx, 120, "源头不是规章", f(SONG, 48, index=1), BONE, 2)
    rows = [("治理层", "拿不到全文", VERM), ("规章层", "有全文", (108, 148, 190)),
            ("平台层", "不上公告", (150, 142, 128))]
    y = 196
    for layer, avail, color in rows:
        w = mixw(d, layer + "　" + avail, 25)
        x = cx - w / 2
        mix(d, x, y, layer, 25, color)
        mix(d, x + mixw(d, layer, 25) + 22, y, avail, 25, BONE)
        y += 42
    d.line([(cx - 150, 328), (cx + 150, 328)], fill=(64, 60, 55), width=1)
    mix_centered(d, cx, 342, "我把三层分开核了一遍", 21, FAINT)
    return im, "封面_006_A_源头不是规章_900x383.png"


# ── B：巨字 0 次 ───────────────────────────────────────────
def dir_b():
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    eyebrow(d, "核规")
    cx = W / 2
    centered(d, cx, 66, "0", f(MONO, 120, index=1), BONE, -5)
    centered(d, cx, 192, "次", f(SONG, 40, index=1), VERM, 2)
    centered(d, cx, 240, "总局 16 号令全文里", f(SONG, 30, index=1), BONE, 1)
    mix_centered(d, cx, 296, "「漫剧」出现 0 次 · 「动画」0 次", 22, FAINT)
    mix_centered(d, cx, 330, "「人工智能」全文只有 1 次", 22, (150, 142, 128))
    return im, "封面_006_B_零次_900x383.png"


def mock(cover, dark, lines, date):
    bg = (28, 28, 30) if dark else (255, 255, 255)
    fg = (236, 236, 245) if dark else (28, 28, 30)
    cell = Image.new("RGB", (400, 320), bg)
    cd = ImageDraw.Draw(cell)
    for i, t in enumerate(lines):
        cd.text((20, 14 + i * 28), t, font=f(HIRA, 19), fill=fg)
    cd.text((20, 76), "一人短剧厂牌 · " + date, font=f(HIRA, 13),
            fill=(152, 152, 157) if dark else (138, 138, 138))
    cd.text((20, 104), "分享卡 383×383", font=f(HIRA, 12),
            fill=(152, 152, 157) if dark else (138, 138, 138))
    sq = cover.crop(((W - 383) // 2, 0, (W + 383) // 2, H)).resize((96, 96), Image.LANCZOS)
    cell.paste(sq, (20, 124))
    cd.rectangle([20, 124, 116, 220], outline=(110, 110, 110), width=1)
    cd.text((132, 104), "头条大图 2.35:1", font=f(HIRA, 12),
            fill=(152, 152, 157) if dark else (138, 138, 138))
    cell.paste(cover.resize((248, 106), Image.LANCZOS), (132, 124))
    cd.rectangle([132, 124, 380, 230], outline=(110, 110, 110), width=1)
    return cell


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
    ttl = ["AI 漫剧「4 月 1 日强制下线」", "我追到源头：它不是一部规章"]
    yy = pad
    for name, im in built:
        dbg = im.copy()
        safe_zone(ImageDraw.Draw(dbg))
        sd.text((pad, yy), name + "　（细框=分享卡安全区）", font=f(HIRA, 22, index=2), fill=(30, 30, 30))
        sheet.paste(dbg, (pad, yy + 34))
        sheet.paste(mock(im, True, ttl, "10-11"), (pad + W + pad, yy + 34))
        sheet.paste(mock(im, False, ttl, "10-11"), (pad + W + pad + 400 + gap, yy + 34))
        yy += H + 130 + 40
    p = os.path.join(OUT, "对照_006封面两方向.png")
    sheet.save(p)
    print("sheet", p, sheet.size)
