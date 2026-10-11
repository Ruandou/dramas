# -*- coding: utf-8 -*-
"""006《AI 漫剧「4 月 1 日未备案强制下线」我追到源头》正文数据图 3 张
纯本地 Pillow，零扣费。统一 1080 宽、浅色纸底（微信深浅色模式都可读）。
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
    for i, ln in enumerate(text.split("\n")):
        mix(d, 64, y + 16 + i * 32, ln, 21, DIM, mono=False)


def grade_chip(d, x, y, text, color):
    w = mixw(d, text, 21) + 26
    d.rectangle([x, y, x + w, y + 40], fill=color)
    mix(d, x + 13, y + 8, text, 21, PAPER)
    return x + w


# ── 图 1：一条刷屏规定的三层出处 ────────────────────────────
def chart1():
    H = 1380
    im, d = canvas(H)
    header(d, "「4 月 1 日 AI 漫剧强制下线」的三层出处",
           "三层里只有中间那层能拿到全文 · 2026-10-11 我逐页核完")

    rows = [
        ("治理层", "2025-11-09《专项治理工作提示》",
         ["「自即日起至 2026 年 3 月……不良动画微短剧",
          "和动画短视频网络传播专项治理」",
          "首次将 AIGC 类、漫画类、表情包类纳入分类分层审核"],
         "拿不到全文", VERM),
        ("规章层", "《微短剧发展管理办法》总局令第 16 号",
         ["八章五十四条，2026-09-01 施行",
          "全文：漫剧 0 次 · 动画 0 次 · 人工智能 1 次",
          "第三十三条（二）三类由播出单位审核并标注节目编号"],
         "有全文", BLUE),
        ("平台层", "红果平台上传规则",
         ["「单个账户真人剧、漫剧单日上传总量上限为 30 部」",
          "2026-06-03 又启一轮「有害低俗内容和侵权盗版」",
          "专项治理，为期 2 个月（正文无 AI/动画/漫剧字样）"],
         "不上公告", GREY),
    ]
    y = 224
    for layer, name, lines, avail, color in rows:
        d.rectangle([64, y, W - 64, y + 274], fill=BOX, outline=LINE, width=2)
        d.rectangle([64, y, 74, y + 274], fill=color)
        mix(d, 98, y + 20, layer, 28, color)
        mix(d, 98 + mixw(d, layer, 28) + 22, y + 20, name, 28, INK, mono=False)
        yy = y + 78
        for ln in lines:
            mix(d, 98, yy, ln, 24, DIM if yy > y + 130 else INK, mono=False)
            yy += 46
        grade_chip(d, W - 64 - (mixw(d, avail, 21) + 26), y + 18, avail, color)
        y += 302

    d.rectangle([64, y + 6, W - 64, y + 110], fill=(250, 246, 238), outline=VERM, width=2)
    mix(d, 84, y + 20, "把三层压成一句「4 月 1 日新规」，压掉的正好是你最需要的那层：", 24, INK, mono=False)
    mix(d, 84, y + 62, "编号跟着平台走，不跟着剧走（非独播要标本播出单位自己的号）", 26, VERM, mono=False)

    footer(d, y + 140, "来源：广电总局官网四页 · 16 号令全文页 · 广电办发〔2024〕35 号 art_113_70148\n"
                       "· 有害低俗内容专项治理 art_114_73404 · 漫剧报道 art_3731_72968")
    return im, "006_图1_三层出处_1080.png"


# ── 图 2：三类三样编号格式 ──────────────────────────────────
def chart2():
    H = 1080
    im, d = canvas(H)
    header(d, "那个号的三种格式：三类三样，由谁发是关键",
           "广电办发〔2024〕35 号原句（官网 2025-02-05 公布，落款 2024-02-05）")

    rows = [
        ("一类（原「重点」）", "（总局或属地省份简称）网微剧审字（年份）第 xxx 号",
         "省以上广电主管部门发", BLUE, False),
        ("二类（原「普通」）", "（总局或属地省份简称）网微剧备字（年份）第 xxx 号",
         "省以上广电主管部门发", (110, 102, 90), False),
        ("三类（原「其他」）", "（播出平台简称）网微剧备字（年份）第 xxx 号",
         "播出平台自审后发 ← 我一个人做剧就落这档", VERM, True),
    ]
    y = 226
    for name, fmt, who, color, me in rows:
        h = 220 if me else 148
        d.rectangle([64, y, W - 64, y + h], fill=BOX if not me else (250, 244, 236),
                    outline=color, width=3 if me else 1)
        mix(d, 92, y + 18, name, 27, color, mono=False)
        mix(d, 92, y + 64, fmt, 26, INK)
        mix(d, 92, y + 110, who, 24, DIM, mono=False)
        if me:
            mix(d, 92, y + 146, "第三十三条（二）：非独播的三类「应当根据各自审核版本", 21, VERM, mono=False)
            mix(d, 92, y + 178, "标注本播出单位的节目编号，不得使用其他播出单位的节目编号」", 21, VERM, mono=False)
        y += h + 22

    d.rectangle([64, y + 8, W - 64, y + 132], fill=(250, 246, 238), outline=VERM, width=2)
    mix(d, 84, y + 22, "同一句原文还写着：「网络视听平台不得上线传播未标注许可证或备案号的微短剧，", 24, INK, mono=False)
    mix(d, 84, y + 62, "也不得为其引流、推送。」", 24, INK, mono=False)
    mix(d, 84, y + 100, "→ 没有号，缺的不只是一个角标，是平台的推荐位。", 25, VERM, mono=False)

    footer(d, y + 176, "口径：引号内为逐字引用；「← 我一个人做剧就落这档」是我按 004 核过的金额档作出的个人判断")
    return im, "006_图2_三类三样编号_1080.png"


# ── 图 3：字面命中计数（我自己跑的那次）─────────────────────
def chart3():
    H = 1200
    im, d = canvas(H)
    header(d, "我把 16 号令全文 curl 下来，数了这七个词",
           "统计口径：剥标签后正文，自「第一条」起至「第五十四条」止，共 6,419 字")

    words = [("漫剧", 0), ("动画", 0), ("动漫", 0), ("漫画", 0), ("AIGC", 0), ("AI", 0), ("人工智能", 1)]
    x0 = 340
    slot_w = 66
    y = 244
    for w, n in words:
        mix(d, 64, y + 6, w, 30, INK, mono=False)
        if n == 0:
            d.rectangle([x0, y, x0 + 12, y + 40], outline=GREY, width=2)
            mix(d, x0 + 34, y + 8, "0 次", 27, GREY)
        else:
            d.rectangle([x0, y, x0 + 12, y + 40], fill=VERM)
            mix(d, x0 + 34, y + 4, "1 次", 30, VERM)
            mix(d, x0 + 122, y + 8, "→ 第三十四条", 25, DIM, mono=False)
        y += 66

    d.line([(64, y + 6), (W - 64, y + 6)], fill=LINE, width=2)
    mix(d, 64, y + 28, "「使用人工智能技术生成、制作的微短剧，制作机构和播出单位应当遵守国家有关规定，", 24, INK, mono=False)
    mix(d, 64, y + 68, "并依据有关规定在每集明显位置添加提示标识。」——全文唯一一句提到 AI 的话。", 24, INK, mono=False)

    box_y = y + 118
    d.rectangle([64, box_y, W - 64, box_y + 196], fill=BOX)
    mix(d, 84, box_y + 18, "读出来的三件事：", 26, INK, mono=False)
    for i, t in enumerate([
        "① 规章里没有「漫剧」这个类别，它按第五/十七条的通用类别走",
        "② 规章对 AI 的全部要求就是一句标识，没有单独备案制",
        "③ 所以「AI 漫剧专门新规」这个说法在规章层找不到落点",
    ]):
        mix(d, 84, box_y + 62 + i * 44, t, 24, DIM if i else VERM, mono=False)

    mix(d, 64, box_y + 232, "复算法：curl -A 官网页 → 剥 script/style 与全部标签 → 按条号截正文 → count()", 21, DIM)
    footer(d, H - 76, "来源：nrta.gov.cn art_113_73785（2026-10-11 抓取并计数，页面导航区不计入）")
    return im, "006_图3_字面命中计数_1080.png"


if __name__ == "__main__":
    for fn in (chart1, chart2, chart3):
        im, name = fn()
        im.save(os.path.join(OUT, name))
        print(name, im.size)
