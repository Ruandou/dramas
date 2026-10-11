# -*- coding: utf-8 -*-
"""008《正文一个字没提 AI，报名表却问「是否为 AI 作品」》正文数据图 3 张
纯本地 Pillow，零扣费。绘图工具与配色复用 _gen_charts_006.py。
注：Menlo 无中文字形、Hiragino 无 ✗✓ 与 U+2212，特殊符号一律避开，否则出豆腐块。
"""
import os
from PIL import Image, ImageDraw
from _gen_charts_006 import (W, PAPER, INK, DIM, LINE, TRACK, BOX, VERM, VERM_L,
                             BLUE, BLUE_L, GREY, SONG, HIRA, MONO, f, mix, mixw,
                             canvas, header, footer, grade_chip, runs, is_ascii)
from _gen_charts_007 import wrap, block

OUT = os.path.dirname(os.path.abspath(__file__))
MONEY = (110, 102, 90)
STEEL = (84, 118, 152)
TEAL = (44, 96, 96)
GREEN = (74, 106, 74)


# ── 图 1：正文四个词零命中，报名表两栏把它们要回来 ──────────
def chart1():
    H = 1120
    im, d = canvas(H)
    header(d, "正文一个字没提的两件事，报名表一栏一栏要",
           "245 号文正文 1,566 字 · 附件 1 报名表 13 行 15 栏")

    mix(d, 64, 196, "正文词频（我数的）", 27, INK, mono=False)
    words = [("AI", 0), ("人工智能", 0), ("智能", 0), ("成本", 0),
             ("备案号", 1), ("国际", 10), ("微短剧", 17)]
    y = 246
    for wd, n in words:
        mix(d, 64, y + 6, wd, 27, INK, mono=False)
        bx, bw = 268, 560
        d.rectangle([bx, y + 8, bx + bw, y + 30], fill=TRACK)
        if n:
            d.rectangle([bx, y + 8, bx + bw * n / 17.0, y + 30],
                        fill=(VERM if n == 1 else BLUE))
        lab = "%d 次" % n
        mix(d, bx + bw + 16, y + 4, lab, 26, VERM if n == 0 else INK)
        if n == 0:
            mix(d, bx + bw + 92, y + 8, "← 零", 22, VERM, mono=False)
        y += 52

    d.line([(64, 632), (W - 64, 632)], fill=LINE, width=2)

    mix(d, 64, 660, "附件 1 报名表里，正文找不到对应的两栏", 27, INK, mono=False)
    rows = [("第 5 行", "制作成本（万元）", "正文「成本」0 次"),
            ("第 7 行右半", "是否为 AI 作品", "正文「AI」0 次 ·「人工智能」0 次")]
    y = 712
    for tag, field, note in rows:
        d.rectangle([64, y, W - 64, y + 96], fill=(250, 240, 236), outline=VERM, width=2)
        mix(d, 88, y + 16, tag, 22, DIM)
        mix(d, 88, y + 46, field, 34, VERM, mono=False)
        mix(d, 560, y + 38, note, 23, INK, mono=False)
        y += 112

    d.rectangle([64, 946, W - 64, 1024], fill=BOX)
    block(d, 84, 964, "正文写的是方向，表格要的是口径。想看清官方在意什么，翻附件比读正文快。",
          25, 900, INK, mono=False, step=34)

    footer(d, 1044, "来源：广电办发〔2026〕245 号正文全文 + 附件 1《2026 年国际微短剧大赛参赛报名表》PDF 两页\n"
                    "词频口径：网页正文去标签、去空白后逐词计数，本篇发布前复算一次")
    return im, "008_图1_正文零命中与报名表两栏_1080.png"


# ── 图 2：报名表 13 行 15 栏，四层拆开 ──────────────────────
def chart2():
    H = 1580
    im, d = canvas(H)
    header(d, "一张报名表拆成四层：官方想知道的四件事",
           "附件 1 共 13 行 · 前 12 行 15 个待填栏 · 第 13 行为声明与盖章")

    layers = [("身份层", "谁在报｜版权在谁手上", BLUE, 4),
              ("合规层", "有没有号｜在哪播", VERM, 2),
              ("生产层", "多长｜多贵｜是否AI", MONEY, 6),
              ("传播层", "走多远｜拿什么证明", TEAL, 3)]
    bw = (W - 128 - 36) / 4
    for i, (name, sub, color, n) in enumerate(layers):
        x = 64 + i * (bw + 12)
        d.rectangle([x, 200, x + bw, 372], fill=color)
        mix(d, x + 16, 216, name, 30, PAPER, mono=False)
        mix(d, x + 16, 262, "%d 栏" % n, 24, PAPER)
        block(d, x + 16, 306, sub, 19, bw - 30, (238, 232, 222), step=28)

    rows = [
        ("1", "作品名称", "生产", MONEY),
        ("2", "集数×时长（分钟）", "生产", MONEY),
        ("3", "申报单位名称", "身份", BLUE),
        ("4", "主要播出平台", "合规", VERM),
        ("5", "制作成本（万元）", "生产", MONEY, "正文 0 次"),
        ("6", "网络视听节目许可证号或备案号", "合规", VERM, "正文原句"),
        ("7", "作品语种　｜　是否为 AI 作品", "生产", MONEY, "正文 0 次"),
        ("8", "版权持有单位　｜　申报单元", "身份 / 传播", BLUE),
        ("9", "申报单位联系人　｜　联系电话", "身份", BLUE),
        ("10", "作品内容简介（500 字以内）", "生产", MONEY),
        ("11", "国际传播情况（可另附页）", "传播", TEAL, "应附数据证明"),
        ("12", "国际传播效果反馈", "传播", TEAL, "可附相应截图"),
        ("13", "申报单位（个人）声明 + 盖章", "声明", GREY),
    ]
    y = 396
    for r in rows:
        no, field, layer = r[0], r[1], r[2]
        color = r[3]
        flag = r[4] if len(r) > 4 else None
        hot = flag == "正文 0 次"
        d.rectangle([64, y, W - 64, y + 62],
                    fill=(250, 240, 236) if hot else BOX,
                    outline=VERM if hot else LINE, width=2)
        d.rectangle([64, y, 72, y + 62], fill=color)
        mix(d, 88, y + 18, no, 22, DIM)
        mix(d, 148, y + 16, field, 25, VERM if hot else INK, mono=False)
        if flag:
            grade_chip(d, W - 64 - (mixw(d, flag, 21) + 26), y + 11, flag,
                       VERM if hot else TEAL)
        y += 70

    d.rectangle([64, y + 8, W - 64, y + 116], fill=(250, 246, 238), outline=INK, width=2)
    y2 = block(d, 84, y + 22, "第 11 行右栏原文：含海外推广情况、播出国家和地区、播出平台、传播覆盖情况、",
               22, 900, INK, mono=False, step=30)
    block(d, 84, y2, "观看量、观众评价、媒体报道、市场反馈、获奖情况等，应附相应数据证明。",
          22, 900, VERM, mono=False, step=30)

    footer(d, y + 142, "来源：广电总局官网 245 号文附件 1 PDF（2 页），逐栏抄录\n"
                       "「正文 0 次」= 该词在通知正文中出现 0 次（去空白后逐词计数）")
    return im, "008_图2_报名表十三行十五栏_1080.png"


# ── 图 3：同日两份通知对照 ──────────────────────────────────
def chart3():
    H = 1260
    im, d = canvas(H)
    header(d, "同一天下发的两份通知，恰好互为对照",
           "245 国际微短剧大赛 对 244 国际短视频大赛 · 均 11-30 截止")

    cw = 442
    heads = [("245 号文", "国际微短剧大赛", VERM), ("244 号文", "国际短视频大赛", BLUE)]
    rows = [
        ("正文去空白字数", "1,566 字", "2,182 字"),
        ("正文出现「AI」", "0 次", "0 次"),
        ("正文出现「人工智能」", "0 次", "2 次"),
        ("正文要求按《标识办法》标注", "无此句", "有此句"),
        ("报名表「是否为 AI 作品」", "有这一栏", "没有这一栏"),
        ("报名表「制作成本（万元）」", "有这一栏", "没有这一栏"),
        ("报名表「许可证号或备案号」", "有这一栏", "没有这一栏"),
        ("报名表规模", "2 页 15 栏", "3 页，末页二维码"),
        ("作品申报截止", "2026-11-30", "2026-11-30"),
    ]
    hot = {2, 3, 4, 5, 6}

    for i, (no, name, color) in enumerate(heads):
        x = 64 + i * (cw + 36)
        d.rectangle([x, 198, x + cw, 282], fill=color)
        mix(d, x + 20, 212, no, 30, PAPER)
        mix(d, x + 20, 248, name, 24, (240, 234, 224), mono=False)
        for r, (label, a, b) in enumerate(rows):
            val = a if i == 0 else b
            on = r in hot
            ry = 296 + r * 78
            d.rectangle([x, ry, x + cw, ry + 68],
                        fill=(250, 240, 236) if on else BOX,
                        outline=VERM if on else LINE, width=2)
            mix(d, x + 16, ry + 8, label, 20, INK if on else DIM, mono=False)
            mix(d, x + 16, ry + 36, val, 26,
                (VERM if on else color) if (i == 0 or on) else GREY, mono=False)

    y = 296 + len(rows) * 78 + 12
    mix(d, 64, y, "所以：一份在正文讲标注、表格里不问；一份正文一个字不提、表格里问。", 25, INK, mono=False)
    yy = block(d, 64, y + 44, "「AI 生成内容要标识」和「AI 生成内容要被统计」是两条独立的路径。",
               23, 952, VERM, mono=False, step=32)
    yy = block(d, 64, yy, "看到表格有这一栏就写「总局要求 AI 微短剧申报」，是过度解读；"
                          "看到正文没提 AI 就写「总局不管 AI 内容」，同样错。",
               23, 952, VERM, mono=False, step=32)

    footer(d, yy + 16, "来源：广电总局官网公告公示栏 2026-09-30 两条通知正文及各自附件报名表 PDF\n"
                       "词频与栏位由我逐页读取、去空白计数，2026-10-11 复算")
    return im, "008_图3_同日两份通知对照_1080.png"


if __name__ == "__main__":
    for fn in (chart1, chart2, chart3):
        im, name = fn()
        im.save(os.path.join(OUT, name))
        print(name, im.size)
