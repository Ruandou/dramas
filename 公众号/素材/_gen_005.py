# -*- coding: utf-8 -*-
"""005《广电总局报了 43 万部》正文数据图 2 张 + 封面 2 方向
纯本地 Pillow，零扣费。图 1080 宽浅色纸底；封面 900×383，关键信息落中间 383×383 安全区。
Menlo 无中文字形，混排行走 mix() 分段取字体。
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.dirname(os.path.abspath(__file__))
W = 1080

HIRA = "/System/Library/Fonts/Hiragino Sans GB.ttc"   # index=2 = W6 粗
MONO = "/System/Library/Fonts/Menlo.ttc"              # index=1 = Bold

PAPER = (243, 238, 228)
INK = (44, 41, 37)
DIM = (122, 114, 102)
LINE = (198, 190, 176)
BOX = (233, 227, 216)
VERM = (176, 44, 32)
VERM_L = (216, 176, 168)
BLUE = (58, 92, 128)
BLUE_L = (176, 192, 210)

CARBON = (52, 49, 44)
BONE = (238, 232, 219)

_c = {}


def f(path, size, index=0):
    k = (path, size, index)
    if k not in _c:
        _c[k] = ImageFont.truetype(path, size, index=index)
    return _c[k]


def is_ascii(run):
    return all(ord(c) < 0x2100 for c in run)


def runs(text):
    out, cur = [], ""
    for ch in text:
        a = ord(ch) < 0x2100
        if cur and a != (ord(cur[0]) < 0x2100):
            out.append(cur)
            cur = ""
        cur += ch
    if cur:
        out.append(cur)
    return out


def textw(d, text, size, mono=True):
    t = 0.0
    for r in runs(text):
        fnt = f(MONO, size, index=1) if (mono and is_ascii(r)) else f(HIRA, size, index=2)
        t += d.textlength(r, font=fnt)
    return t


def mix(d, x, y, text, size, fill, mono=True):
    """基线混排：ASCII 走 Menlo，中文走 Hiragino W6。y 是行的视觉顶。"""
    cy = y + size * 0.62
    for r in runs(text):
        fnt = f(MONO, size, index=1) if (mono and is_ascii(r)) else f(HIRA, size, index=2)
        d.text((x, cy), r, font=fnt, fill=fill, anchor="lm")
        x += d.textlength(r, font=fnt)
    return x


def mixc(d, cx, y, text, size, fill, mono=True):
    mix(d, cx - textw(d, text, size, mono) / 2, y, text, size, fill, mono)


def wrap(d, text, size, maxw, mono=True):
    lines, cur = [], ""
    for ch in text:
        t = cur + ch
        if textw(d, t, size, mono) > maxw and cur:
            lines.append(cur)
            cur = ch
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def ruled(d, y, x0=44, x1=None, color=LINE, w=1):
    d.line([(x0, y), (x1 or W - 44, y)], fill=color, width=w)


# ---------------------------------------------------------------- 图 1
def chart1():
    rows = [
        ("43万部", "2026 年 1—8 月，上线微短剧总量",
         "我的除法：÷ 243 天 = 日均 1,770 部 = 每 48.8 秒一部",
         "答不了：统计范围没写；「部」按剧还是按集计，没写"),
        ("13倍", "前 8 个月总量 ÷ 去年全年总量",
         "我的除法：反推去年 3.31 万部 → 月均比月均 = 19.5 倍",
         "答不了：去年基数官方没报，13 倍是哪两个时间段在比"),
        ("超九成", "其中 AI 剧占比，下界取 90%",
         "我的除法：43 万 × 0.9 = 不少于 38.7 万部",
         "答不了：真人剧与 AI 剧是否共用同一个分母"),
        ("6.8万部", "今年以来，全网下架违规微短剧",
         "我的除法：÷ 43 万 = 15.8%",
         "答不了：窗口不同、下架含存量 → 这个比值不是淘汰率"),
    ]
    pad = 44
    head_h = 190
    body = []
    probe = ImageDraw.Draw(im0 := Image.new("RGB", (10, 10), PAPER))
    for a, b, c, e in rows:
        l1 = wrap(probe, b, 23, 760)
        l2 = wrap(probe, c, 24, 760)
        l3 = wrap(probe, e, 23, 760)
        h1, h2, h3 = len(l1) * 32, len(l2) * 36, len(l3) * 32
        body.append((a, l1, l2, l3, h1, h2, h3, max(152, h1 + h2 + h3 + 76)))
    H = head_h + sum(r[7] for r in body) + 106
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)

    mix(d, pad, 44, "43万部：官方原话给了什么", 40, INK)
    mix(d, pad, 100, "左边是原话，右边三行分别是口径、我的除法、它答不了的", 23, DIM)
    ruled(d, 146)

    y = 146
    x2 = pad + 262
    for k, (a, l1, l2, l3, h1, h2, h3, rh) in enumerate(body):
        mix(d, pad, y + rh / 2 - 26, a, 40, INK)
        mix(d, pad, y + rh / 2 + 26, "官方原话", 19, DIM)
        d.line([(pad + 232, y + 26), (pad + 232, y + rh - 26)], fill=LINE, width=2)
        yy = y + 26
        for ln in l1:
            mix(d, x2, yy, ln, 23, DIM)
            yy += 32
        yy += 8
        for ln in l2:
            mix(d, x2, yy, ln, 24, BLUE)
            yy += 36
        yy += 6
        for ln in l3:
            mix(d, x2, yy, ln, 23, VERM)
            yy += 32
        y += rh
        if k < len(body) - 1:
            ruled(d, y, color=LINE)

    mix(d, pad, H - 74, "除之前先对齐三要素：统计范围 · 时间窗 · 计数单位", 26, INK)
    im.save(os.path.join(OUT, "005_图1_43万部拆算_1080.png"))
    return im.size


# ---------------------------------------------------------------- 图 2
def chart2():
    panels = [
        ("广电办发〔2026〕244 号", "2026 国际短视频大赛", False,
         [("参赛对象", "…高等院校及自媒体创作者"),
          ("技术条款", "单集 10 分钟以内 · 1280×720 起 · 竖屏横屏不限"),
          ("AI 标识", "「AI 生成合成内容务必按《标识办法》标注」"),
          ("名额", "团队作者限 5 人以内 · 不收报名费")],
         ""),
        ("广电办发〔2026〕245 号", "2026 年国际微短剧大赛", True,
         [("参赛范围", "…高等院校及自媒体和个人创作者"),
          ("单元五", "原创剧本 赋能出海：交完整剧本大纲 + 人物小传"),
          ("硬条件", "境内已播出须注明许可证号或备案号"),
          ("报送", "多集提交首、中、尾三集完整成片")],
         "没有成片也能投的那一条"),
    ]
    pad, pw, gap = 44, 484, 24
    lw, vs, top = 118, 31, 234
    vw = pw - lw - 26
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10), PAPER))
    laid = []
    for no, name, hi, items, note in panels:
        rows2 = [(k, wrap(probe, v, 22, vw)) for k, v in items]
        hh = sum(max(1, len(ls)) * vs + 22 for _, ls in rows2)
        laid.append((no, name, hi, rows2, note, hh))
    content = max(l[5] for l in laid)
    panel_h = top - 122 + content + (52 if any(l[4] for l in laid) else 0)
    H = 122 + panel_h + 74

    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    mix(d, pad, 40, "同一天落款的两份通知：只有 245 号把「个人」写进正文", 36, INK)
    ruled(d, 100)

    for i, (no, name, hi, rows2, note, hh) in enumerate(laid):
        x0 = pad + i * (pw + gap)
        if hi:
            d.rectangle([x0, 122, x0 + pw, 122 + panel_h], fill=BOX)
        d.rectangle([x0, 122, x0 + pw, 122 + panel_h], outline=VERM if hi else LINE,
                    width=3 if hi else 1)
        mix(d, x0 + 22, 146, no, 27, VERM if hi else BLUE)
        mix(d, x0 + 22, 186, name, 24, INK)
        yy = top
        for k, ls in rows2:
            mix(d, x0 + 22, yy + 2, k, 20, DIM)
            for j, ln in enumerate(ls):
                mix(d, x0 + lw, yy + j * vs, ln, 22,
                    VERM if (k == "AI 标识") else INK)
            yy += max(1, len(ls)) * vs + 22
        if note:
            d.line([(x0 + 22, yy + 2), (x0 + pw - 22, yy + 2)], fill=VERM_L, width=2)
            mix(d, x0 + 22, yy + 12, note, 21, VERM)

    mixc(d, W / 2, H - 56, "两份都截止 2026 年 11 月 30 日 · 今天 10 月 10 日，还有 51 天", 26, INK)
    im.save(os.path.join(OUT, "005_图2_两份通知并排_1080.png"))
    return im.size


# ---------------------------------------------------------------- 封面
def cover(mode, path):
    CW, CH = 900, 383
    cx = CW / 2
    dark = mode == "B"
    bg = CARBON if dark else PAPER
    fg = BONE if dark else INK
    sub = (154, 146, 132)
    ac = (214, 92, 66) if dark else VERM
    im = Image.new("RGB", (CW, CH), bg)
    d = ImageDraw.Draw(im)

    if mode == "A":
        lines = [(36, "广电总局 9-17 发布会口径", 22, sub),
                 (72, "今年前 8 个月上线微短剧", 26, fg),
                 (110, "43万部", 96, fg),
                 (228, "＝每 48.8 秒一部？", 36, ac),
                 (288, "问号是我加的：那行除法官方没做", 20, sub)]
    else:
        lines = [(46, "官方给了总量，除法是我做的", 22, sub),
                 (84, "48.8 秒", 88, fg),
                 (196, "一部", 36, ac),
                 (252, "43万部 · 13倍 · 下架6.8万部", 21, fg),
                 (296, "附：正文点名「个人创作者」的那份文件", 18, sub)]

    for y, t, s, col in lines:
        mixc(d, cx, y, t, s, col)
    im.save(path)
    return im.size


if __name__ == "__main__":
    print("chart1", chart1())
    print("chart2", chart2())
    a = os.path.join(OUT, "封面_005_A_43万部_900x383.png")
    b = os.path.join(OUT, "封面_005_B_48秒一部_900x383.png")
    print("coverA", cover("A", a))
    print("coverB", cover("B", b))
    sheet = Image.new("RGB", (900, 383 * 2 + 26), (210, 204, 194))
    sheet.paste(Image.open(a), (0, 0))
    sheet.paste(Image.open(b), (0, 409))
    sd = ImageDraw.Draw(sheet)
    for top in (0, 409):
        sd.rectangle([458.5, top, 461.5, top + 383], fill=VERM)
        sd.rectangle([258.5, top, 900 - 258.5, top + 383], outline=VERM, width=2)
    sheet.save(os.path.join(OUT, "对照_005封面两方向.png"))
    print("sheet", sheet.size)
