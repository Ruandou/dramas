# -*- coding: utf-8 -*-
"""004《AI 短剧每集都要打标识？我把广电总局第 16 号令 54 条读完》正文数据图 3 张
纯本地 Pillow，零扣费。统一 1080 宽，浅色纸底（微信正文深浅色模式都可读）
注：Menlo 无中文字形，混排行必须走 mix() 分段取字体，否则出豆腐块。
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

OUT = os.path.dirname(os.path.abspath(__file__))
W = 1080

SONG = "/System/Library/Fonts/Supplemental/Songti.ttc"   # index=1 Bold
HIRA = "/System/Library/Fonts/Hiragino Sans GB.ttc"      # index=2 = W6 粗
MONO = "/System/Library/Fonts/Menlo.ttc"                 # index=1 = Bold

PAPER = (243, 238, 228)
INK = (44, 41, 37)
DIM = (122, 114, 102)
LINE = (198, 190, 176)
TRACK = (222, 214, 199)
BOX = (233, 227, 216)
VERM = (176, 44, 32)
VERM_L = (216, 176, 168)
BLUE = (58, 92, 128)
BLUE_L = (176, 192, 210)
GREY = (168, 160, 146)

_cache = {}


def f(path, size, index=0):
    k = (path, size, index)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(path, size, index=index)
    return _cache[k]


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


def mix(d, x, y, text, size, fill, mono=True, tracking=0):
    """混排绘制：ASCII 段走 Menlo，中文段走 Hiragino W6，按垂直中线对齐。y 为文字顶。"""
    cy = y + size * 0.62
    for r in runs(text):
        fnt = f(MONO, size, index=1) if (mono and is_ascii(r)) else f(HIRA, size, index=2)
        d.text((x, cy), r, font=fnt, fill=fill, anchor="lm")
        x += d.textlength(r, font=fnt) + tracking
    return x


def mixw(d, text, size, mono=True):
    w = 0
    for r in runs(text):
        fnt = f(MONO, size, index=1) if (mono and is_ascii(r)) else f(HIRA, size, index=2)
        w += d.textlength(r, font=fnt)
    return w


def canvas(h):
    im = Image.new("RGB", (W, h), PAPER)
    return im, ImageDraw.Draw(im)


def header(d, title, kicker):
    d.rectangle([64, 58, 78, 58 + 46], fill=VERM)
    d.text((98, 50), title, font=f(SONG, 42, index=1), fill=INK)
    mix(d, 98, 114, kicker, 25, DIM, mono=False)
    d.line([(64, 162), (W - 64, 162)], fill=LINE, width=2)


def footer(d, y, text):
    d.line([(64, y), (W - 64, y)], fill=LINE, width=1)
    mix(d, 64, y + 16, text, 21, DIM, mono=False)


def grade_chip(d, x, y, text, color):
    w = mixw(d, text, 21) + 26
    d.rectangle([x, y, x + w, y + 40], fill=color)
    mix(d, x + 13, y + 8, text, 21, (243, 238, 228))
    return x + w


# ── 图 1：时间轴与各文件口径 ───────────────────────────────
def chart1():
    H = 1180
    im, d = canvas(H)
    header(d, "同一个「微短剧分级」，四份文件四种口径",
           "2026-10-10 我自己搜到并逐页读完的清单（右侧标证据等级）")

    rows = [
        ("2024-02-05", "广电总局办公厅公告（官网 2025-02-05 见）",
         "通用·旧｜重点≥100 万 / 普通 30-100 万 / 其他<30 万", "A 级", BLUE),
        ("2026-01-01", "门槛上调版（只见地方局转发）",
         "通用·新｜≥300 万 / 100-300 万 / <100 万", "C 级", GREY),
        ("2026-07-01", "《管理提示（AI微短剧分类分层标准）》",
         "AI 专项｜≥80 万 / 30-80 万 / <30 万（新华社 06-25 报道）", "A 级", BLUE),
        ("2026-09-01", "《微短剧发展管理办法》总局令第 16 号",
         "改叫一类/二类/三类，全文一个金额数字都没写", "A 级", VERM),
    ]
    top, spine = 236, 252
    d.line([(spine, top + 8), (spine, top + 3 * 150 + 20)], fill=LINE, width=2)
    y = top
    for date, name, note, grade, gcolor in rows:
        mix(d, 64, y + 4, date, 25, INK)
        d.ellipse([spine - 8, y + 8, spine + 8, y + 24], fill=gcolor)
        mix(d, 288, y, name, 27, INK, mono=False)
        mix(d, 288, y + 48, note, 24, DIM, mono=False)
        if grade == "C 级":
            mix(d, W - 64 - mixw(d, grade, 21), y + 10, grade, 21, gcolor, mono=False)
        else:
            grade_chip(d, W - 64 - (mixw(d, grade, 21) + 26), y, grade, gcolor)
        y += 150

    d.rectangle([64, y + 14, W - 64, y + 120], fill=BOX)
    mix(d, 84, y + 28, "第三十四条（同样 2026-09-01 起）", 27, VERM, mono=False)
    mix(d, 84, y + 70, "「使用人工智能技术生成、制作的微短剧……在每集明显位置添加提示标识」", 24, INK, mono=False)

    mix(d, 64, y + 152, "注意：300/100 那份我在总局官网没定位到原文页，只当二手材料用", 23, VERM, mono=False)
    footer(d, 1106, "来源：nrta.gov.cn（令第 16 号 / 2025-02-05 公告）· news.cn 2026-06-25 · 宝鸡市文旅局")
    return im, "004_图1_四份文件时间轴_1080.png"


# ── 图 2：三套数字并排（同一根万元轴，切点不同）─────────────
def chart2():
    H = 1010
    im, d = canvas(H)
    header(d, "三套金额线并排：切点不同，管的范围也不同",
           "同一根「万元」轴，色块由浅到深 = 其他 → 普通 → 重点")

    MAXV = 320.0
    x0, x1 = 64, W - 64
    def X(v):
        return x0 + (x1 - x0) * (v / MAXV)

    ruler = 246
    mk = X(1.7321)
    mix(d, mk + 22, ruler - 58, "1.7 万 = 我一部 86 集剧的生成费上限（含返工）", 24, VERM, mono=False)
    d.polygon([(mk - 9, ruler - 22), (mk + 9, ruler - 22), (mk, ruler - 2)], fill=VERM)

    d.line([(x0, ruler), (x1, ruler)], fill=INK, width=2)
    for v in (0, 30, 80, 100, 300):
        d.line([(X(v), ruler - 9), (X(v), ruler + 9)], fill=INK, width=2)
        mix(d, X(v) - 22, ruler + 16, "%d" % v, 22, DIM)
    mix(d, x1 - 34, ruler + 16, "万元", 22, DIM, mono=False)

    for v in (30, 80, 100, 300):
        yy = ruler + 44
        while yy < 736:
            d.line([(X(v), yy), (X(v), min(yy + 9, 736))], fill=LINE, width=2)
            yy += 18

    bars = [
        ("AI 微短剧专项（新华社引原文 · 2026-07-01 起）",
         [(0, 30), (30, 80), (80, 320)],
         [(206, 216, 228), (128, 156, 186), BLUE],
         "不足 30 万 ｜ 30-80 万 ｜ 80 万以上"),
        ("通用·旧（总局官网公告 · 落款 2024-02-05）",
         [(0, 30), (30, 100), (100, 320)],
         [(222, 214, 199), (168, 160, 146), (110, 102, 90)],
         "不足 30 万 ｜ 30-100 万 ｜ 100 万以上"),
        ("通用·新（仅见地方局转发 · 2026-01-01 起）",
         [(0, 100), (100, 300), (300, 320)],
         [VERM_L, (198, 96, 82), VERM],
         "不足 100 万 ｜ 100-300 万 ｜ 300 万以上"),
    ]
    y = 336
    bh = 62
    for label, spans, tones, caption in bars:
        mix(d, 64, y - 34, label, 25, DIM, mono=False)
        for (lo, hi), tone in zip(spans, tones):
            d.rectangle([X(lo), y, X(hi), y + bh], fill=tone, outline=PAPER, width=2)
        mix(d, 64, y + bh + 12, caption, 24, INK)
        y += 148

    d.rectangle([64, 790, W - 64, 908], fill=BOX)
    mix(d, 84, 806, "三套数字彼此不打架：80/30 只管 AI 微短剧，100/30 是旧通用，300/100 是新通用", 24, INK, mono=False)
    mix(d, 84, 848, "我犯的错是把 AI 专项的 80/30 当成通用分级，抄进了项目规则文件", 24, VERM, mono=False)

    footer(d, 944, "来源：nrta.gov.cn（令第 16 号 / 2025-02-05 公告）· news.cn 2026-06-25 · 宝鸡市文旅局")
    return im, "004_图2_三套分档并排_1080.png"


# ── 图 3：对数轴上的数量级差 ───────────────────────────────
def chart3():
    H = 1020
    im, d = canvas(H)
    header(d, "差的不是一点，是一到两个数量级",
           "横轴取对数：等距离 = 等倍数。我的生成费 vs 最低那条金额线")

    LO, HI = 3.5, 6.35
    x0, x1 = 118, W - 100
    def X(v):
        return x0 + (math.log10(v) - LO) / (HI - LO) * (x1 - x0)

    base = 580
    pts = [(6186, "¥6,186", "86 集 × 90 秒纯生成费", VERM, "up"),
           (17321, "¥17,321", "含返工 1.6~2.8 倍", VERM, "down"),
           (300000, "30 万", "AI 专项最低档线", BLUE, "up"),
           (1000000, "100 万", "通用·新 门槛（C 级）", (110, 102, 90), "down")]

    d.line([(x0 - 34, base), (x1 + 34, base)], fill=INK, width=2)
    for v, lab in ((10000, "1 万"), (100000, "10 万")):
        d.line([(X(v), base - 10), (X(v), base + 10)], fill=INK, width=2)
        mix(d, X(v) - mixw(d, lab, 22) / 2, base - 40, lab, 22, DIM, mono=False)
    for v, lab, sub, color, side in pts:
        x = X(v)
        if side == "up":
            d.line([(x, base), (x, base - 150)], fill=color, width=2)
            d.ellipse([x - 11, base - 11, x + 11, base + 11], fill=color)
            mix(d, x - mixw(d, lab, 32) / 2, base - 208, lab, 32, color)
            mix(d, x - mixw(d, sub, 21) / 2, base - 176, sub, 21, DIM, mono=False)
        else:
            d.line([(x, base), (x, base + 128)], fill=color, width=2)
            d.ellipse([x - 11, base - 11, x + 11, base + 11], fill=color)
            mix(d, x - mixw(d, lab, 32) / 2, base + 144, lab, 32, color)
            mix(d, x - mixw(d, sub, 21) / 2, base + 186, sub, 21, DIM, mono=False)

    def bracket(v1, v2, text, yy):
        xa, xb = X(v1), X(v2)
        for xx in (xa, xb):
            d.line([(xx, yy), (xx, yy + 14)], fill=DIM, width=2)
        d.line([(xa, yy), (xb, yy)], fill=DIM, width=2)
        mix(d, (xa + xb) / 2 - mixw(d, text, 24) / 2, yy - 40, text, 24, INK)

    bracket(6186, 300000, "相差 48.5 倍", 276)
    bracket(17321, 300000, "17.3 倍", 328)

    d.rectangle([64, 800, W - 64, 918], fill=BOX)
    mix(d, 84, 816, "对 100 万线：¥17,321 → 57.7 倍；¥6,186 → 161.7 倍", 26, INK)
    mix(d, 84, 856, "反向算：一集要花 ¥3,488（= ¥38.8/秒，我当前单价的 48 倍）才够到 30 万", 24, DIM, mono=False)
    mix(d, 84, 892, "「投资额度」含人力/剧本/后期/投流，我无可核账，此处只比生成费量级", 22, VERM, mono=False)

    footer(d, 944, "数据源：本号后台账单与 56 条任务归档（¥0.037/千 token、每秒 21,600 token）")
    return im, "004_图3_数量级对比_1080.png"


if __name__ == "__main__":
    for fn in (chart1, chart2, chart3):
        im, name = fn()
        im.save(os.path.join(OUT, name))
        print(name, im.size)
