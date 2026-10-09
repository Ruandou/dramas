# -*- coding: utf-8 -*-
"""003《「98.7% 的 AI 短剧在赔钱」？我翻完了原报告》正文数据图 3 张
纯本地 Pillow，零扣费。统一 1080 宽，浅色纸底（微信正文深浅色模式都可读）
注：Menlo 无中文字形，混排行必须走 mix() 分段取字体，否则出豆腐块。
"""
from PIL import Image, ImageDraw, ImageFont
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


# ── 图 1：三个数字的分子分母 ───────────────────────────────
def chart1():
    H = 960
    im, d = canvas(H)
    header(d, "报告第 7 页只有两个分子",
           "分母是同一个：22.19 万部（抖音端原生 AI 剧漫剧，2026.1.1–6.30）")

    y = 226
    mix(d, 64, y - 36, "上半年新剧总数", 25, DIM, mono=False)
    d.rectangle([64, y, W - 64, y + 56], fill=TRACK)
    mix(d, 84, y + 10, "22.19 万部", 32, INK)

    rows = [("播放量破亿", "1055 部", "0.48%", VERM, 0.035),
            ("过 5000 万播放基线", "2886 部", "1.3%", BLUE, 0.075)]
    y = 348
    for label, num, pct, color, ratio in rows:
        mix(d, 64, y - 36, label, 25, DIM, mono=False)
        pf = f(SONG, 42, index=1)
        d.text((W - 64 - d.textlength(pct, font=pf), y - 44), pct, font=pf, fill=color)
        bw = max(96, int((W - 128) * ratio))
        d.rectangle([64, y, W - 64, y + 56], fill=TRACK)
        d.rectangle([64, y, 64 + bw, y + 56], fill=color)
        mix(d, 64 + bw + 18, y + 10, num, 30, INK)
        y += 150

    d.rectangle([64, y + 6, W - 64, y + 96], fill=BOX)
    mix(d, 84, y + 20, "1055 ÷ 221900 = 0.4754%", 26, INK)
    mix(d, 84, y + 56, "2886 ÷ 221900 = 1.3005% → 和报告的 0.48%、1.3% 对得上", 26, INK)

    y2 = y + 130
    d.rectangle([64, y2, W - 64, y2 + 100], outline=VERM, width=3)
    mix(d, 86, y2 + 12, "100% - 1.3% = 98.7%", 36, VERM)
    mix(d, 86, y2 + 60, "这一步，报告里没有做——是转述的人减出来的。", 27, INK, mono=False)

    footer(d, 880, "数据源：DataEye《2026上半年国内AI剧漫剧数据报告》第 7 页　Source: DataEye-ADX行业版")
    return im, "003_图1_分子分母_1080.png"


# ── 图 2：两套月度的数，两个机构 ───────────────────────────
def chart2():
    H = 940
    im, d = canvas(H)
    header(d, "「每 36 秒」和「1.3%」不是同一家出的数",
           "1–6 月来自 DataEye 报告；7 月单月来自澎湃美数课工作室统计")

    months = ["1月", "2月", "3月", "4月", "5月", "6月"]
    vals = [1.96, 3.43, 4.67, 4.41, 3.95, 3.77]
    base, top, maxv = 566, 210, 7.8
    colw, gap, x0 = 108, 18, 84

    for i, (m, v) in enumerate(zip(months, vals)):
        x = x0 + i * (colw + gap)
        h = int((base - top) * (v / maxv))
        d.rectangle([x, base - h, x + colw, base], fill=GREY)
        mix(d, x + 16, base - h - 42, "%.2f" % v, 26, INK)
        mix(d, x + 24, base + 14, m, 25, DIM, mono=False)

    px = x0 + 6 * (colw + gap) + 12
    d.line([(px, base), (px, top - 10)], fill=LINE, width=2)

    x = px + 30
    h7 = int((base - top) * (7.4313 / maxv))
    d.rectangle([x, base - h7, x + colw, base], fill=BLUE)
    mix(d, x + 16, base - h7 - 42, "7.43", 26, BLUE)
    mix(d, x + 20, base + 14, "7月＊", 25, BLUE, mono=False)
    d.line([(64, base), (W - 64, base)], fill=INK, width=2)

    mix(d, 64, base + 62, "1–6 月合计 22.19 万部（逐月相加严格对上）", 25, DIM, mono=False)

    d.rectangle([64, 688, 780, 790], fill=BOX)
    mix(d, 84, 704, "6 月 3.77 → 7 月 7.43，几乎翻倍", 29, INK, mono=False)
    mix(d, 84, 748, "＊另一机构、另一抓取规则、单月口径，不可与左图连用", 22, VERM, mono=False)

    mix(d, 64, 812, "36 秒的算法：31 天 × 86400 秒 ÷ 74313 部 = 36.04 秒", 26, INK)

    footer(d, 858, "数据源：DataEye 报告第 7、8 页 / 中国新闻网 2026-08-11（引澎湃美数课工作室）")
    return im, "003_图2_两套月度_1080.png"


# ── 图 3：把基线换算成钱 ──────────────────────────────────
def chart3():
    H = 1010
    im, d = canvas(H)
    header(d, "报告只给播放数，成本这一半我自己补",
           "把「5000 万播放 = 盈亏平衡基线」翻成钱：")

    d.rectangle([64, 198, W - 64, 284], fill=BOX)
    mix(d, 84, 218, "5000万 ÷ 10000 × 5元/万次 ≈ ¥25,000", 34, INK)

    scale = (W - 128) / 34000.0
    bars = [("基线隐含的可承受成本", None, 25000, "≈ ¥25,000", BLUE),
            ("本号实测：86 集 / 129 分钟含返工", 9900, 17400, "¥9,900~17,400", VERM),
            ("报道称「有团队压到」", None, 10000, "约 ¥1 万", GREY)]
    y = 336
    for label, lo, hi, val, color in bars:
        mix(d, 64, y - 34, label, 25, DIM, mono=False)
        if lo is None:
            d.rectangle([64, y, 64 + int(hi * scale), y + 56], fill=color)
        else:
            d.rectangle([64, y, 64 + int(hi * scale), y + 56], fill=VERM_L)
            d.rectangle([64 + int(lo * scale), y, 64 + int(hi * scale), y + 56], fill=color)
        mix(d, 64 + int(hi * scale) + 16, y + 10, val, 28, INK)
        y += 126

    mix(d, 64, y + 8, "读法：制作费压在两万五以下的团队，摸到 5000 万播放就不亏", 32, INK, mono=False)

    yy = y + 70
    d.polygon([(64, yy + 18), (64 + 15, yy), (64 + 30, yy + 18)], fill=VERM)
    mix(d, 104, yy - 2, "只能当数量级，三条原因：", 25, VERM, mono=False)
    for i, t in enumerate(["分账模式各家不同（按播放 / 按拉新 / 包底）",
                           "播放量 ≠ 有效播放；收益侧我没有一手账单",
                           "「5 元/万次」是 2026-05 媒体报道用词（被曝，非平台公告）"]):
        mix(d, 64, yy + 42 + i * 36, "· " + t, 23, DIM, mono=False)

    footer(d, 936, "数据源：DataEye 报告第 7 页 · 中国新闻网 2026-08-11 · 新浪财经 2026-05-23 · 本号上一篇账单")
    return im, "003_图3_换算成钱_1080.png"


if __name__ == "__main__":
    for fn in (chart1, chart2, chart3):
        im, name = fn()
        im.save(os.path.join(OUT, name))
        print(name, im.size)
