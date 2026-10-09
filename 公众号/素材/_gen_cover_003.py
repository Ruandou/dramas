# -*- coding: utf-8 -*-
"""003《「98.7% 的 AI 短剧在赔钱」？我把 27 页原报告翻完了》封面
纯本地 Pillow，零扣费。900×383（2.35:1）；关键信息落在中间 383×383 分享卡安全区
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 900, 383

SONG = "/System/Library/Fonts/Supplemental/Songti.ttc"
HIRA = "/System/Library/Fonts/Hiragino Sans GB.ttc"
MONO = "/System/Library/Fonts/Menlo.ttc"

CARBON = (52, 49, 44)
INK = (26, 24, 22)
BONE = (238, 232, 219)
VERM = (176, 44, 32)
DIM = (154, 146, 132)
FAINT = (120, 114, 104)
BLUE = (108, 148, 190)

_c = {}


def f(path, size, index=0):
    k = (path, size, index)
    if k not in _c:
        _c[k] = ImageFont.truetype(path, size, index=index)
    return _c[k]


def tracked(d, x, y, text, fnt, fill, tracking=0):
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += d.textlength(ch, font=fnt) + tracking
    return x


def centered(d, cx, y, text, fnt, fill, tracking=0):
    w = sum(d.textlength(ch, font=fnt) for ch in text) + tracking * (len(text) - 1)
    return tracked(d, cx - w / 2, y, text, fnt, fill, tracking)


def is_ascii(run):
    return all(ord(c) < 0x2100 for c in run)


def runs(text):
    out, cur = [], ""
    for c in text:
        a = ord(c) < 0x2100
        if cur and a != (ord(cur[0]) < 0x2100):
            out.append(cur)
            cur = ""
        cur += c
    if cur:
        out.append(cur)
    return out


def mix(d, x, y, text, size, fill, mono=True):
    """混排：ASCII 段走 Menlo，中文段走 Hiragino W6。Menlo 无中文字形，整行 MONO 会出豆腐块。"""
    cy = y + size * 0.62
    for r in runs(text):
        fnt = f(MONO, size, index=1) if (mono and is_ascii(r)) else f(HIRA, size, index=2)
        d.text((x, cy), r, font=fnt, fill=fill, anchor="lm")
        x += d.textlength(r, font=fnt)
    return x


def mixw(d, text, size, mono=True):
    return sum(d.textlength(r, font=f(MONO, size, index=1) if (mono and is_ascii(r))
                            else f(HIRA, size, index=2)) for r in runs(text))


def mix_centered(d, cx, y, text, size, fill, mono=True):
    return mix(d, cx - mixw(d, text, size, mono) / 2, y, text, size, fill, mono)


def eyebrow(d):
    d.rectangle([54, 52, 65, 52 + 26], fill=VERM)
    tracked(d, 78, 48, "一人短剧厂牌 · 核数", f(HIRA, 20), DIM, 3)


def safe_zone(d):
    """调试用：画出中间 383×383 分享卡安全区"""
    x0 = (W - 383) / 2
    d.rectangle([x0, 0, x0 + 383, 383], outline=(90, 86, 80), width=1)


# ── A：巨字 98.7% 划掉 ─────────────────────────────────────
def dir_a():
    im = Image.new("RGB", (W, H), CARBON)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    cx = W / 2
    big = f(MONO, 118, index=1)
    centered(d, cx, 80, "98.7%", big, BONE, -4)
    w = d.textlength("98.7%", font=big)
    d.line([(cx - w / 2 - 16, 156), (cx + w / 2 + 16, 156)], fill=VERM, width=7)
    centered(d, cx, 224, "原报告 27 页 · 出现 0 次", f(SONG, 34, index=1), BONE, 1)
    d.line([(cx - 150, 292), (cx + 150, 292)], fill=(78, 74, 68), width=1)
    centered(d, cx, 308, "1.3% 是真的，「赔钱」是别人替它下的结论", f(HIRA, 21), FAINT, 1)
    return im, "封面_003_A_划掉的98.7_900x383.png"


# ── B：左结论右核对动作 ────────────────────────────────────
def dir_b():
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    cx = W / 2
    song = f(SONG, 44, index=1)
    centered(d, cx, 66, "我把那句", song, BONE, 1)
    mix_centered(d, cx, 130, "「98.7% 在赔钱」", 40, BLUE)
    centered(d, cx, 196, "的原文翻了一遍", song, BONE, 1)
    d.line([(cx - 176, 276), (cx + 176, 276)], fill=(64, 60, 55), width=1)
    mix_centered(d, cx, 292, "DataEye 报告 PDF · 27 页 · 逐字核对", 20, DIM)
    # 左侧补数示意（分享卡会裁掉，只作大图装饰）
    mix(d, 56, 118, "100%", 32, (86, 82, 76))
    mix(d, 56, 162, "- 1.3%", 32, (86, 82, 76))
    d.line([(54, 210), (196, 210)], fill=(86, 82, 76), width=2)
    mix(d, 56, 224, "= 98.7%", 32, VERM)
    return im, "封面_003_B_补数算式_900x383.png"


def mode_mock(cover, dark, lines):
    bg = (28, 28, 30) if dark else (255, 255, 255)
    fg = (236, 236, 245) if dark else (28, 28, 30)
    cell = Image.new("RGB", (400, 320), bg)
    cd = ImageDraw.Draw(cell)
    for i, t in enumerate(lines):
        cd.text((20, 14 + i * 28), t, font=f(HIRA, 19), fill=fg)
    cd.text((20, 76), "一人短剧厂牌 · 10-09", font=f(HIRA, 13),
            fill=(152, 152, 157) if dark else (138, 138, 138))
    # 分享卡（正方形裁切）
    cd.text((20, 104), "分享卡 383×383", font=f(HIRA, 12),
            fill=(152, 152, 157) if dark else (138, 138, 138))
    sq = cover.crop(((W - 383) // 2, 0, (W + 383) // 2, H)).resize((96, 96), Image.LANCZOS)
    cell.paste(sq, (20, 124))
    cd.rectangle([20, 124, 116, 220], outline=(110, 110, 110), width=1)
    # 头条大图 2.35:1
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
    ttl = ["「98.7% 的 AI 短剧在赔钱」？", "我把 27 页原报告翻完了"]
    yy = pad
    for name, im in built:
        dbg = im.copy()
        safe_zone(ImageDraw.Draw(dbg))
        sd.text((pad, yy), name + "　（细框=分享卡安全区）", font=f(HIRA, 22, index=2), fill=(30, 30, 30))
        sheet.paste(dbg, (pad, yy + 34))
        sheet.paste(mode_mock(im, True, ttl), (pad + W + pad, yy + 34))
        sheet.paste(mode_mock(im, False, ttl), (pad + W + pad + 400 + gap, yy + 34))
        yy += H + 130 + 40
    p = os.path.join(OUT, "对照_003封面两方向.png")
    sheet.save(p)
    print("sheet", p, sheet.size)
