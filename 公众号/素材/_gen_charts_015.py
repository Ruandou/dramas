# -*- coding: utf-8 -*-
"""015《厂牌盯数02｜100 万播放换 1,000 元：AI 剧回本率 1.3%，先算你的回本播放量》正文数据图 6 张
纯本地 Pillow，零扣费（严禁调用任何付费生成 API）。底层工具复用
_gen_charts_006/007/009/011/012（同一套纸底与字体；011 的 line/line_right/para/
note_box/src_foot/cjk_guard 与 012 的 dbl 直接 import，宽度校验与 LINES 登记同一套）。
注：Menlo 无中文字形，任何含 CJK 的行一律走 mix()/wrap()，禁止用 MONO 直接画整行；
「100 万次」这类数字+汉字混排同样走 dbl/mix。正文图单行文案宽度上限 980px，
每条打印 OK/OVER 校验并 assert。数据一字不改，来源：新黄河 10-14（张磊/郑曦案例）、
DataEye 9 月及上半年口径、钛媒体 9-23、10-12 行业观察（万播分成）；本号自算项
在图上注明（A 级可复核）。
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


# ── 图 1：一张账单的三个数 ──────────────────────────────────
def chart1():
    im, d = canvas(TALL)
    hdr_song(d, "一张账单的三个数：近 100 万播放换 1,000 元",
             "2026 年 6 月 · 20 人团队 · 新黄河 10-14 报道（转载皆为同文）")

    cw, ch = 304, 236
    y0 = 196
    cards = [
        ("6 月播放量", "100 万次", "海外社媒分发 · 不含投流", INK),
        ("6 月收入", "1,000 元", "折合约 10 元/万次播放", VERM),
        ("6 月成本", "20 万元", "人工 + 房租 + AI 算力", INK),
    ]
    for i, (label, big, sub, color) in enumerate(cards):
        x = 64 + i * (cw + 20)
        d.rectangle([x, y0, x + cw, y0 + ch], fill=(250, 246, 238), outline=LINE, width=2)
        d.rectangle([x, y0, x + cw, y0 + 10], fill=color)
        line(d, x + 24, y0 + 30, label, 22, DIM, maxw=cw - 48)
        dbl(d, x + 24, y0 + 70, big, 40, color)
        para(d, x + 24, y0 + 148, sub, 20, DIM, maxw=cw - 48, step=27)
    y = y0 + ch + 24

    d.rectangle([64, y, EDGE, y + 168], fill=(250, 240, 236), outline=VERM, width=3)
    line(d, 96, y + 20, "成本约 20 万元 - 收入 1,000 元 =", 26, INK)
    dbl(d, 96, y + 62, "净亏 19.9 万元", 42, VERM)
    line(d, 96, y + 124, "成本 = 人工 + 房租 + AI 算力，没有投流——不是买量买亏了，是纯制作运营亏的", 21, DIM, maxw=MAXW)
    y += 168 + 16
    line(d, 64, y, "19.9 万 = 20 万 - 1,000 元（本号按报道数相减，A 级）", 21, DIM, maxw=MAXW)
    y += 40

    y = note_box(d, y, [
        ("在同一篇报道里，一位群演的日片酬从 8,000 元跌到 1,000 元——制作端价格整体下移的一个切片。", 22, INK, 31),
    ], outline=INK)

    y = src_foot(d, y + 10, [
        "来源：新黄河 2026-10-14（记者刘成伟）；各门户转载为同文，非独立验证",
        "播放/收入/成本为报道原文；10 元/万次、19.9 万相减为本号折算（A 级）",
    ])
    return im.crop((0, 0, W, y)), "015_图1_账单三数_1080.png"


# ── 图 2：供给漏斗 ─────────────────────────────────────────
def chart2():
    im, d = canvas(TALL)
    hdr_song(d, "供给漏斗：半年 22.19 万部，破亿 1,055 部",
             "2026 上半年 · 折算每天超 1,200 部新剧 · DataEye 口径")

    rows = [
        (64, 952, "22.19 万部", "上半年新增 · 约每 200 部出 1 个爆款", INK),
        (192, 696, "约 2,886 部", "播放过 5,000 万 · 约 1.3%", VERM),
        (320, 440, "1,055 部", "播放破 1 亿 · 0.47%", BLUE),
    ]
    y = 200
    for x, w, big, sub, color in rows:
        h = 148
        d.rectangle([x, y, x + w, y + h], fill=color)
        dbl(d, x + 34, y + 26, big, 38, PAPER)
        line(d, x + 34, y + 92, sub, 22, PAPER, maxw=w - 68)
        y += h + 14

    y += 10
    y = note_box(d, y, [
        ("漏斗读法：每天超 1,200 部新剧上线、每 200 部出 1 个爆款；播放过 5,000 万（约 1.3%）才算站上行业回本线。",
         23, INK, 32),
        ("从业者 50 万+、用户 6 亿——供给与需求两端都在扩张（DataEye 口径）。", 22, INK, 31),
    ], outline=INK)

    y = src_foot(d, y + 10, [
        "来源：DataEye 公开口径（2026 上半年），多家转载一致",
        "「每天 1,200+ 部」= 22.19 万 ÷ 180 天，本号折算（A 级）",
    ])
    return im.crop((0, 0, W, y)), "015_图2_供给漏斗_1080.png"


# ── 图 3：回本线 ───────────────────────────────────────────
def chart3():
    im, d = canvas(TALL)
    hdr_song(d, "回本线：5,000 万播放算「达标」，1.3% 的剧做到",
             "2026 上半年 · DataEye 口径 · 「达标」= 播放量过 5,000 万")

    cw, ch = 304, 236
    y0 = 196
    cards = [
        ("达标线", "5,000 万", "播放量门槛（行业口径）", INK),
        ("做到的比例", "1.3%", "含破亿的 1,055 部", VERM),
        ("没做到", "98.7%", "未回本区间", DIM),
    ]
    for i, (label, big, sub, color) in enumerate(cards):
        x = 64 + i * (cw + 20)
        d.rectangle([x, y0, x + cw, y0 + ch], fill=(250, 246, 238), outline=LINE, width=2)
        d.rectangle([x, y0, x + cw, y0 + 10], fill=color)
        line(d, x + 24, y0 + 30, label, 22, DIM, maxw=cw - 48)
        dbl(d, x + 24, y0 + 70, big, 42, color)
        para(d, x + 24, y0 + 148, sub, 20, DIM, maxw=cw - 48, step=27)
    y = y0 + ch + 26

    line(d, 64, y, "把 100% 的剧压成一条线：红的是达标区（1.3%），灰的没回本（98.7%）", 22, INK, maxw=MAXW)
    y += 40
    d.rectangle([64, y, EDGE, y + 56], fill=TRACK)
    d.rectangle([64, y, 64 + 30, y + 56], fill=VERM)
    line(d, 110, y + 14, "1.3% · 约 2,886 部达标", 22, VERM, maxw=400)
    line_right(d, EDGE - 20, y + 14, "98.7% · 未回本", 22, DIM)
    y += 56 + 30

    y = note_box(d, y, [
        ("两个比例别读混：0.47%（1,055 部）= 播放破 1 亿；约 1.3%（约 2,886 部）= 播放过 5,000 万（含破亿）；两者相差约 1,831 部。", 23, INK, 32),
        ("对个人的意义（本号）：5,000 万播放是行业给正反馈的最低门票，而队伍有 22 万支。", 23, VERM, 32),
    ], outline=INK)

    y = src_foot(d, y + 10, [
        "来源：DataEye 公开口径（2026 上半年），多家转载一致",
        "条宽按 1.3% / 98.7% 等比绘制，红色段最小宽 30px 仅为可见性",
    ])
    return im.crop((0, 0, W, y)), "015_图3_回本线_1080.png"


# ── 图 4：钱去哪了 ─────────────────────────────────────────
def chart4():
    im, d = canvas(TALL)
    hdr_song(d, "单价端：四个塌方点，一个对照",
             "分成单价 10-12（C 级） · 投流结算 钛媒体 9-23")

    rows = [
        ("01", "万播分成", "近 100 元 → 5-10 元", "跌超九成 · 与张磊账单 10 元/万次互证", VERM),
        ("02", "投流抽成", "占充值流水 70%–90%", "《无双》投流吞噬超九成流水（两处口径一致）", BLUE),
        ("03", "结算周期", "1 个月 → 3 个月", "首期回款比例 35%", INK),
        ("04", "保底退场", "S+ 剧本 4 万 → 1 万", "保底机制取消 · -75%", INK),
    ]
    y = 210
    for num, tag, pair, sub, color in rows:
        h = 122
        d.rectangle([64, y, EDGE, y + h], fill=(250, 246, 238), outline=LINE, width=2)
        d.rectangle([64, y, 74, y + h], fill=color)
        dbl(d, 102, y + 24, num, 34, color)
        line(d, 102, y + 74, tag, 22, DIM)
        line(d, 250, y + 22, pair, 28, INK, maxw=500)
        line(d, 250, y + 72, sub, 21, DIM, maxw=EDGE - 250 - 32)
        y += h + 14

    y += 10
    d.rectangle([64, y, EDGE, y + 150], fill=(250, 240, 236), outline=VERM, width=3)
    line(d, 96, y + 22, "成本端对照：群演日片酬 8,000 → 1,000 元（-87.5%）", 24, INK, maxw=MAXW)
    line(d, 96, y + 66, "成本跌 87.5%，收入端跌 90% 以上——省下的，追不上丢掉的。", 26, VERM, maxw=MAXW)
    line(d, 96, y + 116, "（本号对照：两处跌幅分属制作端与分成单价，非同链路数据）", 20, DIM, maxw=MAXW)
    y += 150 + 20

    y = src_foot(d, y, [
        "来源：万播分成变化——10-12 行业观察（未标原始数据源，本号按 C 级处理）",
        "投流占流水 70–90%、结算与保底——钛媒体 9-23；片酬——新黄河 10-14",
    ])
    return im.crop((0, 0, W, y)), "015_图4_四个塌方点_1080.png"


# ── 图 5：一道除法 ─────────────────────────────────────────
def chart5():
    im, d = canvas(TALL)
    hdr_song(d, "一道除法：你的回本播放量",
             "回本播放量 = 成本 ÷ 每万次单价 · 单价取 5-10 元/万次 · 本号自算（A 级）")

    d.rectangle([64, 196, EDGE, 196 + 108], fill=INK)
    dbl(d, 96, 196 + 32, "回本播放量 = 制作成本 ÷ 每万次单价", 36, PAPER)
    y = 196 + 108 + 30

    rows = [
        ("张磊团队 · 6 月实际", "20 万 ÷ 10 元", "2 亿次", "离回本差约 200 倍（实际 100 万次）", VERM),
        ("86 集自制 · 乐观档", "1 万 ÷ 10 元", "1,000 万次", "成本 1 万 · 单价 10 元/万次", INK),
        ("86 集自制 · 保守档", "1.74 万 ÷ 5 元", "约 3,500 万次", "成本 1.74 万 · 单价 5 元/万次", BLUE),
    ]
    for tag, expr, res, sub, color in rows:
        h = 128
        d.rectangle([64, y, EDGE, y + h], fill=(250, 246, 238), outline=LINE, width=2)
        d.rectangle([64, y, 74, y + h], fill=color)
        line(d, 100, y + 20, tag, 23, INK, maxw=520)
        line(d, 100, y + 68, expr, 24, DIM, maxw=520)
        dbl(d, 636, y + 20, res, 40, color)
        line(d, 636, y + 84, sub, 20, DIM, maxw=360)
        y += h + 14

    y += 16
    y = note_box(d, y, [
        ("同一笔钱换个角度看：5,000 万播放按 5-10 元/万次折约 2.5 万~5 万元收入（本号推算，C 级）——对 1 万成本的自制剧赚 1.5~4 倍，对 20 万成本的团队亏 15 万上下。", 22, INK, 31),
        ("回本不是「够不够爆」，是「成本 ÷ 单价」：单价你控制不了，成本你能（本号）。", 23, VERM, 32),
    ], outline=INK)

    y = src_foot(d, y + 10, [
        "86 集成本口径：本号创刊期成本账（视频 ¥0.80/秒、90 秒/集、含返工约 1 万~1.74 万元）",
        "万播单价区间出处见 图 4；C 级推算依赖单价假设，仅作算例",
    ])
    return im.crop((0, 0, W, y)), "015_图5_一道除法_1080.png"


# ── 图 6：今天能做的三件事 ──────────────────────────────────
def chart6():
    im, d = canvas(TALL)
    hdr_song(d, "今天就能做的三件事",
             "前两件零成本 · 第三件决定投不投 · 依据见正文第四、五节")

    rows = [
        ("01", "算一次你的回本播放量", "制作成本 ÷ 你合同里的万播单价；单价未定，按 5-10 元算两档。算出两个数，写在每天看得见的地方。五分钟。", VERM),
        ("02", "签合同前对三格", "保底：有没有、多少钱（口头承诺不算数）｜ 结算周期：月结还是 3 个月 ｜ 首期回款：多少比例、何时到账。", BLUE),
        ("03", "投流预算当独立决策", "每 100 元充值，70-90 元先还投流账。投流要你出钱：先算投多少、能带回多少；不用你出钱：收入上限被单价锁死——回到第 01 件。", INK),
    ]
    y = 210
    for num, title, sub, color in rows:
        h = 158
        d.rectangle([64, y, EDGE, y + h], fill=(250, 246, 238), outline=INK, width=2)
        d.rectangle([64, y, 74, y + h], fill=color)
        dbl(d, 104, y + 38, num, 38, color)
        line(d, 196, y + 26, title, 27, INK, maxw=EDGE - 196 - 32)
        para(d, 196, y + 76, sub, 21, DIM, maxw=EDGE - 196 - 32, step=28)
        y += h + 14

    y += 10
    line(d, 64, y + 8, "顺序不能反：先算线，再决定投入。（本号归纳）", 23, VERM, maxw=MAXW)
    y += 48

    y = src_foot(d, y, [
        "第一件的公式与算例见 图 5；第二、三件的行业依据见 图 4",
        "保底/结算条款以合同原文为准、逐字核对；本文不构成投资建议",
    ])
    return im.crop((0, 0, W, y)), "015_图6_三件事_1080.png"


if __name__ == "__main__":
    for fn in (chart1, chart2, chart3, chart4, chart5, chart6):
        print(fn.__name__)
        im, name = fn()
        im.save(os.path.join(OUT, name))
        print(name, im.size)
    print()
    cjk_guard()
