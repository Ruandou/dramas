# -*- coding: utf-8 -*-
"""014《厂牌盯数01｜9 月海外收入 2.85 亿美元下滑，ReelShort 靠 AI 剧占比 88% 登顶》正文数据图 6 张
纯本地 Pillow，零扣费（严禁调用任何付费生成 API）。底层工具复用
_gen_charts_006/007/009/011/012（同一套纸底与字体；011 的 line/line_right/para/
note_box/src_foot/cjk_guard 与 012 的 dbl 直接 import，宽度校验与 LINES 登记同一套）。
注：Menlo 无中文字形，任何含 CJK 的行一律走 mix()/wrap()，禁止用 MONO 直接画整行；
「2.42 亿次」这类数字+汉字混排同样走 mix/dbl。正文图单行文案宽度上限 980px，
每条打印 OK/OVER 校验并 assert。数据一字不改，全部来自 DataEye 研究院 9 月海外月报
（2026-10-13 发布；36kr 与流媒体网同文转载）；本号自算项在图上注明。
"""
import os
from PIL import Image, ImageDraw
from _gen_charts_006 import (W, PAPER, INK, DIM, LINE, TRACK, BOX, VERM, VERM_L,
                             BLUE, BLUE_L, GREY, SONG, HIRA, MONO, f, mix, mixw,
                             canvas, header, footer, grade_chip, runs, is_ascii)
from _gen_charts_007 import wrap, block
from _gen_charts_009 import cb, tx, hdr, foot, panel, EDGE, MAXW, MONEY, TEAL, TALL
from _gen_charts_011 import BODY, LINES, line, line_right, para, note_box, src_foot, cjk_guard, hdr_song
from _gen_charts_012 import dbl

OUT = os.path.dirname(os.path.abspath(__file__))


# ── 图 1：9 月大盘四指标 ────────────────────────────────────
def chart1():
    im, d = canvas(TALL)
    hdr_song(d, "9 月海外短剧大盘：四个指标同时回落",
             "2026 年 9 月环比 8 月 · DataEye-ADX 双端预估口径 · 2026-10-13 发布")

    cards = [
        ("双端预估下载量", "2.42 亿次", "-13.5%", "环比下滑"),
        ("双端预估内购收入", "2.85 亿美元", "-1.3%", "环比微降"),
        ("广告素材投放量", "525 万组", "-15%", "终结两连增"),
        ("在投 App 及网页", "1,192 款", "-7%", "当月新增仅 56 款"),
    ]
    cw, ch = 466, 208
    y0 = 196
    for i, (label, big, delta, sub) in enumerate(cards):
        x = 64 + (i % 2) * (cw + 20)
        y = y0 + (i // 2) * (ch + 20)
        d.rectangle([x, y, x + cw, y + ch], fill=(250, 246, 238), outline=LINE, width=2)
        d.rectangle([x, y, x + 10, y + ch], fill=VERM)
        line(d, x + 30, y + 16, label, 23, DIM, maxw=cw - 60)
        dbl(d, x + 30, y + 56, big, 46, INK)
        line(d, x + 30, y + 128, delta + "　" + sub, 24, VERM, maxw=cw - 60)
    y = y0 + 2 * (ch + 20) + 6

    y = note_box(d, y, [
        ("四组数一个方向——降。月报给出的两个直接原因：投放节奏放缓；新增入局玩家收缩。", 23, INK, 32),
        ("本号读数（A 级）：下载降幅（-13.5%）是收入降幅（-1.3%）的约 10 倍——买量买来的下载跟着投放退潮，"
         "存量用户的付费几乎没动。这个市场不是在「掉需求」，是在「停拉新」。", 23, VERM, 32),
        ("变现结构：IAA（纯广告）产品增速最快 142 → 154 款（+8%）；IAAP 341 → 353 款（+4%）；"
         "纯内购 IAP 224 → 220 款（-2%）。", 22, INK, 31),
    ], outline=INK)

    y = src_foot(d, y + 10, [
        "来源：DataEye 研究院 9 月海外月报（2026-10-13 发布），36kr 与流媒体网同日同文转载",
        "数字为 DataEye-ADX 双端预估口径（单一原始来源，非独立多源）",
        "「约 10 倍」为本号自算（A 级）· 过程可复核",
    ])
    return im.crop((0, 0, W, y)), "014_图1_大盘四指标_1080.png"


# ── 图 2：ReelShort AI 占比曲线 ─────────────────────────────
def chart2():
    im, d = canvas(TALL)
    hdr_song(d, "ReelShort 的 AI 内容占比：5 个月，10% → 88%",
             "GASP 统计经 DataEye 引用 · 同期真人实拍月产量稳定 10—30 部")

    px0, px1 = 230, 950
    py_t, py_b = 290, 620
    months = ["5 月", "6 月", "7 月", "8 月", "9 月"]
    vals = [10, 22, 45, 72, 88]
    n = len(months)

    def X(i):
        return px0 + (px1 - px0) * i / (n - 1)

    def Y(v):
        return py_b - (py_b - py_t) * v / 100.0

    for v in (0, 25, 50, 75, 100):
        d.line([(px0, Y(v)), (px1, Y(v))], fill=LINE if v else INK, width=2 if v in (0, 100) else 1)
        line_right(d, px0 - 16, Y(v) - 13, "%d%%" % v, 20, DIM)
    d.line([(px0, py_t - 16), (px0, py_b)], fill=INK, width=3)

    pts = [(X(i), Y(v)) for i, v in enumerate(vals)]
    d.line(pts, fill=VERM, width=5)
    for i, (x, yv) in enumerate(pts):
        r = 11 if i == n - 1 else 7
        d.ellipse([x - r, yv - r, x + r, yv + r], fill=VERM, outline=PAPER, width=2)
        line_right(d, x + mixw(d, "%d%%" % vals[i], 24) / 2 + 16, yv - 44, "%d%%" % vals[i], 24, VERM)
        line_right(d, x + mixw(d, months[i], 22) / 2 + 16, py_b + 14, months[i], 22, INK)
    line_right(d, EDGE, py_t - 44, "内容占比 · 单位：%", 21, DIM)

    y = py_b + 66
    y = note_box(d, y, [
        ("同一份月报里必须一起读的一句：ReelShort 真人实拍剧集产出没有收缩，月产量稳定 10—30 部。"
         "原文判断：并非以 AI 取代真人拍摄，而是在稳固真人内容产能基本盘的基础上，依靠 AI 放大整体内容供给规模。",
         23, INK, 32),
        ("同期 TOP5 下载环比：ReelShort +3%（唯一正增长）· Dramawave -40% 以上 · NetShort -36% · DramaBox -24% · PineDrama -6%。",
         23, INK, 32),
        ("对做 AI 剧的人：海外头部 App 的内容里已有 88% 是 AI 做的，平台对 AI 的接受度不再是问题，"
         "门槛转移到了「你的 AI 剧能不能留住人」（本号归纳）。", 23, VERM, 32),
    ], outline=INK)

    y = src_foot(d, y + 10, [
        "AI 占比：GASP 统计、经 DataEye 引用（本号未回 GASP 原始报告，按转述口径引用）",
        "真人产量与下载环比：DataEye 9 月海外月报（2026-10-13）",
        "月报未写明 GASP 的统计方法（上新占比或库存占比）",
    ])
    return im.crop((0, 0, W, y)), "014_图2_ReelShortAI占比曲线_1080.png"


# ── 图 3：AI 素材结构 + 占大盘比 ────────────────────────────
def chart3():
    im, d = canvas(TALL)
    hdr_song(d, "AI 剧与漫剧：170 万组素材，94% 是仿真人",
             "2026 年 9 月海外投放 · 环比 -15% · 占 525 万组大盘约 32%（本号算）")

    rows = [("AI 仿真人", "超 160 万组", "约 94%", VERM),
            ("3D 漫剧", "近 5 万组", "约 3%", BLUE),
            ("2D 漫剧", "超 2 万组", "约 1%", GREY)]
    x0, track_w = 340, 440
    y = 216
    line(d, 64, y - 32, "AI 剧/漫剧素材内部结构（条宽按组数比例；百分比为该类占 170 万组的比）", 22, INK)
    for name, n_txt, pct, color in rows:
        line_right(d, x0 - 20, y + 9, name, 24, INK if color != GREY else DIM)
        d.rectangle([x0, y, x0 + track_w, y + 44], fill=TRACK)
        frac = {"AI 仿真人": 1.0, "3D 漫剧": 0.031, "2D 漫剧": 0.013}[name]
        bw = max(round(track_w * frac), 6)
        d.rectangle([x0, y, x0 + bw, y + 44], fill=color)
        line(d, x0 + track_w + 20, y - 2, n_txt, 22, color if color != GREY else DIM, maxw=196)
        line(d, x0 + track_w + 20, y + 30, pct, 21, DIM, maxw=196)
        y += 64
    y += 26

    # 全市场占比条
    d.rectangle([64, y, EDGE, y + 132], fill=(250, 246, 238), outline=INK, width=2)
    line(d, 92, y + 14, "放进全市场投放池：525 万组里，AI/漫剧约 170 万组", 24, INK)
    bx0, bx1 = 92, EDGE - 30
    d.rectangle([bx0, y + 66, bx1, y + 106], fill=TRACK)
    cut = bx0 + round((bx1 - bx0) * 170.0 / 525.0)
    d.rectangle([bx0, y + 66, cut, y + 106], fill=VERM)
    line(d, bx0 + 8, y + 72, "AI/漫剧 约 32%", 22, PAPER, maxw=270)
    line_right(d, cut - 10, y + 72, "（本号算）", 21, PAPER)
    line_right(d, bx1 - 8, y + 72, "其余约 68%", 22, DIM)
    y += 152

    y = note_box(d, y, [
        ("月报定性句：「已从早期补充品类，升级为海外微短剧投放核心赛道」——AI 仿真人是绝对主力形态，不是 3D 漫剧。",
         23, INK, 32),
        ("占比变化：本月 AI 素材与全市场同步回落约 15%，占比与 8 月基本持平（本号据两处「下降约 15%」推算，A 级）。",
         22, INK, 31),
        ("题材侧：男频素材占 52%（较上月再升 4 个百分点），女频 48%；情感 22% 蝉联第一，逆袭重回第二；"
         "甜宠、豪门上升，玄幻、悬疑下滑。", 22, INK, 31),
    ], outline=INK)

    y = src_foot(d, y + 10, [
        "来源：DataEye 研究院 9 月海外月报（2026-10-13，36kr 与流媒体网同文转载）",
        "组数与占比为 DataEye-ADX 口径；32%、94% 为本号自算（A 级，过程可复核）",
    ])
    return im.crop((0, 0, W, y)), "014_图3_AI素材结构_1080.png"


# ── 图 4：下载榜 TOP5 ───────────────────────────────────────
def chart4():
    im, d = canvas(TALL)
    hdr_song(d, "9 月海外下载榜 TOP5：只有第一名在涨",
             "单位：万次 · 环比变化标注在条上 · ReelShort 为唯一正增长")

    apps = [("ReelShort", 2800, "+3%", VERM),
            ("Dramawave", 1700, "-40% 以上", GREY),
            ("PineDrama", 1600, "-6%", GREY),
            ("DramaBox", 1600, "-24%", GREY),
            ("NetShort", 1400, "-36%", GREY)]
    x0, track_w = 300, 470
    y = 216
    line(d, 64, y - 32, "条宽按下载量比例；「超」为月报原文（各数值均含「超」字口径）", 22, INK)
    for name, v, delta, color in apps:
        line_right(d, x0 - 20, y + 9, name, 24, INK if color == VERM else DIM)
        d.rectangle([x0, y, x0 + track_w, y + 44], fill=TRACK)
        bw = max(round(track_w * v / 2800.0), 6)
        d.rectangle([x0, y, x0 + bw, y + 44], fill=color)
        line(d, x0 + track_w + 18, y - 4, "超 %s 万" % format(v, ","), 23,
             VERM if color == VERM else DIM, maxw=170)
        line(d, x0 + track_w + 18, y + 28, delta, 21,
             VERM if color == VERM else DIM, maxw=170)
        y += 64
    y += 24
    line(d, 64, y, "TOP20 合计下载量超 1.8 亿次 · 环比约 -14% · 仅 ReelShort 正增长", 23, INK)

    y = note_box(d, y + 40, [
        ("同一份榜里还有一个必读信号：腾讯系新面孔 PineDrama（TikTok 推出）升到第三，单月下载超 1,600 万次；"
         "而老牌 Dramawave、NetShort、DramaBox 全面下滑——榜单在换血。", 23, INK, 32),
        ("对照收入侧（见图 5）：AI 原生 App 集体上桌，StoryReel 破千万美元、BlinkDrama 下载 +500%——"
         "「AI 剧能不能赚钱」，9 月的答案是新入场者身上最快。", 23, VERM, 32),
    ], outline=INK)

    y = src_foot(d, y + 10, [
        "来源：DataEye 研究院 9 月海外月报（2026-10-13，36kr 与流媒体网同文转载）",
        "下载量为 DataEye-ADX 双端预估口径；「超」为月报原文措辞",
    ])
    return im.crop((0, 0, W, y)), "014_图4_下载榜TOP5_1080.png"


# ── 图 5：AI 原生 App 收入侧 ────────────────────────────────
def chart5():
    im, d = canvas(TALL)
    hdr_song(d, "AI 原生 App 的 9 月：两款破千万，黑马 +500%",
             "内购收入为 9 月预估 · 环比标注在卡上 · AI 短剧为主打品类")

    cards = [
        ("StoryReel", "内购 > 1,000 万美元", "+25% · 榜单第 7", "主打 AI 短剧 · 本月新晋千万美元梯队", VERM),
        ("VibeShort", "内购 > 900 万美元", "+6% · 榜单第 8", "主打 AI 短剧", BLUE),
        ("FlickReels", "内购 近 800 万美元", "+34%", "一批 AI 爆款拉动（萌宝救赎、情感、隐藏富豪）", BLUE),
        ("BlinkDrama", "下载 > 780 万次", "+500% · 升至第 10", "AI 短剧 App · 今年 5 月才上架", VERM),
    ]
    cw, ch = 466, 220
    y0 = 196
    for i, (name, big, delta, sub, color) in enumerate(cards):
        x = 64 + (i % 2) * (cw + 20)
        y = y0 + (i // 2) * (ch + 20)
        d.rectangle([x, y, x + cw, y + ch], fill=(250, 246, 238), outline=LINE, width=2)
        d.rectangle([x, y, x + 10, y + ch], fill=color)
        line(d, x + 30, y + 14, name, 27, INK, maxw=cw - 60)
        dbl(d, x + 30, y + 56, big, 38, INK)
        line(d, x + 30, y + 116, delta, 24, color, maxw=cw - 60)
        para(d, x + 30, y + 152, sub, 20, DIM, maxw=cw - 60, step=27)
    y = y0 + 2 * (ch + 20) + 4

    y = note_box(d, y, [
        ("本月 App 内购破千万美元的产品共 7 款，比上月多 2 款；StoryReel 和 ShortMax 是新晋的"
         "（DramaBox、NetShort、ReelShort 仍包揽收入前三，合计占 TOP20 总收入的 45%）。", 23, INK, 32),
        ("对照老牌：Dramawave -40%、NetShort -36%、DramaBox -24%；本土产品（德/韩/乌/以四款入围收入 TOP20）"
         "整体低迷，韩国 Vigloo 环比跌近 60%。", 23, INK, 32),
        ("归因别偷跑：BlinkDrama 暴涨，月报原文用「或许与大规模买量投放相关」（9 月投放素材超 8.2 万组，"
         "海外短剧 App 投放榜第九）——「或许」是月报自己的措辞，不是实锤。", 22, VERM, 31),
    ], outline=INK)

    y = src_foot(d, y + 10, [
        "来源：DataEye 研究院 9 月海外月报（2026-10-13，36kr 与流媒体网同文转载）",
        "收入与下载为 DataEye-ADX 双端预估口径；爆款剧目名称为月报原文",
    ])
    return im.crop((0, 0, W, y)), "014_图5_AI原生App_1080.png"


# ── 图 6：区域结构 ──────────────────────────────────────────
def chart6():
    im, d = canvas(TALL)
    hdr_song(d, "钱在美国，量在印尼和印度",
             "2026 年 9 月海外收入与下载的区域结构 · 占比构成")

    colw = 466
    lx, rx = 64, 64 + colw + 20
    top, colh = 200, 560

    # 左：收入
    d.rectangle([lx, top, lx + colw, top + colh], fill=(250, 240, 236), outline=VERM, width=3)
    d.rectangle([lx, top, lx + colw, top + 56], fill=VERM)
    line(d, lx + 18, top + 12, "收入占比 TOP5", 25, PAPER)
    rev = [("美国", "约 28%", 1.0), ("日本", "6.7%", 0.24), ("英国", "4.3%", 0.15),
           ("韩国", "4.09%", 0.146), ("澳大利亚", "4.08%", 0.146)]
    yy = top + 86
    for name, pct, frac in rev:
        line(d, lx + 20, yy, name, 24, INK)
        line_right(d, lx + colw - 20, yy, pct, 24, VERM if frac == 1.0 else INK)
        d.rectangle([lx + 20, yy + 40, lx + colw - 20, yy + 58], fill=TRACK)
        d.rectangle([lx + 20, yy + 40, lx + 20 + max(round((colw - 40) * frac), 6), yy + 58], fill=VERM)
        yy += 78
    line(d, lx + 20, top + colh - 60, "TOP5 合计约 47% · TOP10 约 61.3%", 22, DIM, maxw=colw - 40)

    # 右：下载
    d.rectangle([rx, top, rx + colw, top + colh], fill=(244, 240, 234), outline=BLUE, width=3)
    d.rectangle([rx, top, rx + colw, top + 56], fill=BLUE)
    line(d, rx + 18, top + 12, "下载占比 TOP5", 25, PAPER)
    dls = [("印尼", "12.6%", 1.0), ("印度", "12.2%", 0.968), ("巴西", "11.1%", 0.881),
           ("美国", "9.7%", 0.77), ("菲律宾", "6.9%", 0.548)]
    yy = top + 86
    for name, pct, frac in dls:
        line(d, rx + 20, yy, name, 24, INK)
        line_right(d, rx + colw - 20, yy, pct, 24, BLUE if frac == 1.0 else INK)
        d.rectangle([rx + 20, yy + 40, rx + colw - 20, yy + 58], fill=TRACK)
        d.rectangle([rx + 20, yy + 40, rx + 20 + max(round((colw - 40) * frac), 6), yy + 58], fill=BLUE)
        yy += 78
    line(d, rx + 20, top + colh - 100, "TOP5 合计约 53%", 22, DIM, maxw=colw - 40)
    line(d, rx + 20, top + colh - 68, "南美三国合计 15.6%", 22, DIM, maxw=colw - 40)
    line(d, rx + 20, top + colh - 36, "（环比 +2.4 个百分点）", 22, DIM, maxw=colw - 40)

    y = top + colh + 24
    y = note_box(d, y, [
        ("一句话记法（本号归纳）：拉新看东南亚和南美，变现守北美和日韩澳。"
         "你的剧是卖给「付费用户」还是给「免费用户」刷的，应该决定试投的第一枪打向哪里。", 24, VERM, 34),
    ], outline=INK)

    y = src_foot(d, y + 10, [
        "来源：DataEye 研究院 9 月海外月报（2026-10-13，36kr 与流媒体网同文转载）",
        "占比为 DataEye-ADX 双端预估口径；条宽按占比等比绘制",
    ])
    return im.crop((0, 0, W, y)), "014_图6_区域结构_1080.png"


if __name__ == "__main__":
    for fn in (chart1, chart2, chart3, chart4, chart5, chart6):
        print(fn.__name__)
        im, name = fn()
        im.save(os.path.join(OUT, name))
        print(name, im.size)
    print()
    cjk_guard()
