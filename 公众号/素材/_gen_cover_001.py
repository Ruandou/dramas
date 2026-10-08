# -*- coding: utf-8 -*-
"""001《一条 90 秒的 AI 竖屏短剧，真实账单是多少钱？》封面三方向
纯本地 Pillow，零扣费。输出 900x383（微信订阅号头条封面 2.35:1）
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 900, 383

SONG = "/System/Library/Fonts/Supplemental/Songti.ttc"   # index=1 Bold
HIRA = "/System/Library/Fonts/Hiragino Sans GB.ttc"       # index=2 = W6 粗
MONO = "/System/Library/Fonts/Menlo.ttc"                  # index=1 = Bold

CARBON = (52, 49, 44)     # 与头像 E3 底色一致，深浅色模式下都不消失
INK = (26, 24, 22)
BONE = (238, 232, 219)
VERMIL = (176, 44, 32)
DIM = (154, 146, 132)
PAPER = (243, 238, 228)
PAPER_DIM = (122, 114, 102)
PAPER_LINE = (198, 190, 176)
PAPER_INK = (44, 41, 37)


def f(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)


def tracked(d, x, y, text, fnt, fill, tracking=0):
    for c in text:
        d.text((x, y), c, font=fnt, fill=fill)
        x += d.textlength(c, font=fnt) + tracking
    return x


def right(d, x1, y, text, fnt, fill, tracking=0):
    return x1 - d.textlength(text, font=fnt)


def eyebrow(d, x, y, label="一人短剧厂牌"):
    d.rectangle([x, y + 4, x + 11, y + 4 + 26], fill=VERMIL)
    tracked(d, x + 24, y, label, f(HIRA, 21), DIM, 3)


def receipt(d, box, title, rows, total):
    """竖版小票。box=(x0,y0,x1,y1)，底部撕齿边"""
    x0, y0, x1, y1 = box
    pad = 20
    d.rectangle([x0, y0, x1, y1], fill=PAPER)
    teeth, step = 11, (x1 - x0) / 11.0
    for i in range(teeth):
        cx = x0 + step * (i + 0.5)
        d.polygon([(cx - step / 2, y1), (cx + step / 2, y1), (cx, y1 + 10)], fill=PAPER)
    d.rectangle([x0, y0, x1, y0 + 4], fill=VERMIL)

    tracked(d, x0 + pad, y0 + 22, title, f(HIRA, 16), PAPER_DIM, 2)
    yy = y0 + 54
    d.line([(x0 + pad, yy), (x1 - pad, yy)], fill=PAPER_LINE, width=1)
    yy += 18
    for name, val in rows:
        tracked(d, x0 + pad, yy, name, f(HIRA, 16), PAPER_INK, 1)
        vf = f(MONO, 17, index=1)
        tracked(d, x1 - pad - d.textlength(val, font=vf), yy - 1, val, vf, PAPER_INK, 0)
        yy += 29
    for px in range(int(x0 + pad), int(x1 - pad), 9):
        d.line([(px, yy), (min(px + 5, x1 - pad), yy)], fill=PAPER_LINE, width=1)
    yy += 13
    tracked(d, x0 + pad, yy + 5, total[0], f(HIRA, 18, index=2), PAPER_INK, 2)
    tf = f(MONO, 25, index=1)
    tracked(d, x1 - pad - d.textlength(total[1], font=tf), yy, total[1], tf, VERMIL, 0)


# ── A：左标题 + 右小票 ─────────────────────────────────────
def dir_a():
    im = Image.new("RGB", (W, H), CARBON)
    d = ImageDraw.Draw(im)
    eyebrow(d, 54, 50)
    song = f(SONG, 60, index=1)
    tracked(d, 54, 104, "一集 90 秒", song, BONE, 2)
    tracked(d, 54, 182, "真实账单 ¥73", song, BONE, 2)
    tracked(d, 54, 258, "含返工落在 ¥116 ~ ¥208", f(HIRA, 22), DIM, 2)
    tracked(d, 54, 294, "单价、倍率、逐段金额全部可复算", f(HIRA, 19), (120, 114, 104), 1)
    receipt(d, (556, 34, 856, 300), "EP01 · 90 秒竖屏 · 720p",
            [("视频生成 91 秒", "73.03"),
             ("返工重做 169 秒", "134.76"),
             ("配音 / 字幕", "0.00")],
            ("合计", "207.79"))
    return im, "封面_001_A_小票_900x383.png"


# ── B：巨字金额当主视觉 ────────────────────────────────────
def dir_b():
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    eyebrow(d, 54, 44)
    big = f(MONO, 158, index=1)
    tracked(d, 48, 88, "¥73", big, BONE, -3)
    w73 = d.textlength("¥73", font=big)
    tracked(d, 48 + w73 + 30, 150, "一次全过", f(HIRA, 25), DIM, 4)
    sub = f(MONO, 58, index=1)
    tracked(d, 118, 258, "→", f(HIRA, 46), DIM, 0)
    tracked(d, 186, 258, "¥208", sub, VERMIL, -2)
    w208 = d.textlength("¥208", font=sub)
    tracked(d, 186 + w208 + 24, 268, "含返工", f(HIRA, 25), DIM, 4)

    song = f(SONG, 42, index=1)
    tracked(d, 486, 96, "一条 90 秒的", song, BONE, 2)
    tracked(d, 486, 156, "AI 竖屏短剧", song, BONE, 2)
    tracked(d, 486, 216, "到底花多少钱", f(SONG, 30, index=1), DIM, 2)
    d.line([(486, 268), (846, 268)], fill=(64, 60, 55), width=1)
    tracked(d, 486, 286, "token 单价 · 逐段账单 · 返工倍率", f(HIRA, 19), (126, 119, 107), 1)
    return im, "封面_001_B_巨字金额_900x383.png"


# ── C：账单结构条形 ────────────────────────────────────────
def dir_c():
    im = Image.new("RGB", (W, H), CARBON)
    d = ImageDraw.Draw(im)
    eyebrow(d, 54, 44)
    tracked(d, 54, 92, "钱几乎全压在「出片」这一下", f(SONG, 46, index=1), BONE, 2)
    tracked(d, 54, 154, "一集 90 秒竖屏 AI 短剧的账单结构", f(HIRA, 21), DIM, 2)
    y = 214
    x0, full = 54, 700
    for name, ratio, val in [("视频生成", 0.955, "¥73 ~ ¥208"),
                             ("参考图 50 张", 0.030, "¥36 / 部"),
                             ("剧本 · 配音 · 字幕", 0.015, "≈¥0")]:
        tracked(d, x0, y - 22, name, f(HIRA, 19), BONE, 1)
        vf = f(HIRA, 19, index=2)
        tracked(d, x0 + full - d.textlength(val, font=vf), y - 23, val, vf, DIM, 1)
        d.rectangle([x0, y, x0 + full, y + 18], fill=(70, 66, 60))
        d.rectangle([x0, y, x0 + full * ratio, y + 18],
                    fill=VERMIL if ratio > 0.5 else (124, 116, 103))
        y += 50
    return im, "封面_001_C_账单结构_900x383.png"


def mode_mock(cover, dark):
    """微信订阅号列表页头条：标题 + 2.35:1 大图。iOS @3x 约 351x150px 图区"""
    bg = (28, 28, 30) if dark else (255, 255, 255)
    fg = (236, 236, 245) if dark else (28, 28, 30)
    cell = Image.new("RGB", (400, 300), bg)
    cd = ImageDraw.Draw(cell)
    cd.text((20, 18), "一条 90 秒的 AI 竖屏短剧，", font=f(HIRA, 19), fill=fg)
    cd.text((20, 46), "真实账单是多少钱？", font=f(HIRA, 19), fill=fg)
    cd.text((20, 80), "一人短剧厂牌 · 09-30", font=f(HIRA, 13),
            fill=(152, 152, 157) if dark else (138, 138, 138))
    cd.rectangle([20, 108, 380, 260], outline=(110, 110, 110), width=1)
    cell.paste(cover.resize((360, 153), Image.LANCZOS), (20, 108))
    return cell


if __name__ == "__main__":
    built = []
    for fn in (dir_a, dir_b, dir_c):
        im, name = fn()
        im.save(os.path.join(OUT, name))
        built.append((name, im))
        print(name, im.size)

    pad, gap = 26, 34
    row_h = max(H, 300)
    sw = W + 400 + 400 + pad * 4
    sh = (row_h + 70) * 3 + pad * 2
    sheet = Image.new("RGB", (sw, sh), (244, 244, 244))
    sd = ImageDraw.Draw(sheet)
    yy = pad
    for name, im in built:
        sd.text((pad, yy), name, font=f(HIRA, 24, index=2), fill=(30, 30, 30))
        sd.text((pad + 470, yy + 6), "｜原图 900×383 → 微信列表页实际尺寸（深色 / 浅色）",
                font=f(HIRA, 17), fill=(120, 120, 120))
        sheet.paste(im, (pad, yy + 40))
        sheet.paste(mode_mock(im, True), (pad + W + pad, yy + 40))
        sheet.paste(mode_mock(im, False), (pad + W + pad + 400 + gap, yy + 40))
        yy += row_h + 70
    p = os.path.join(OUT, "对照_001封面三方向.png")
    sheet.save(p)
    print("sheet", p, sheet.size)
