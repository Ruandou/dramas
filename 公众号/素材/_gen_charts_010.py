# -*- coding: utf-8 -*-
"""010《9 月备案公示 296 部里「微短剧」出现 0 次》正文数据图 3 张
纯本地 Pillow，零扣费。防溢出封装（hdr / tx / cb / foot / panel）复用 _gen_charts_009。
注：Menlo 无中文字形、Hiragino 无 ✗✓ 与 U+2212，负号一律用半角 -。
"""
import os
from PIL import Image, ImageDraw
from _gen_charts_006 import (W, PAPER, INK, DIM, LINE, TRACK, BOX, VERM, VERM_L,
                             BLUE, BLUE_L, GREY, SONG, HIRA, MONO, f, mix, mixw,
                             canvas, header, footer, grade_chip)
from _gen_charts_007 import wrap, block
from _gen_charts_009 import cb, tx, hdr, foot, panel, EDGE, MAXW, MONEY, TEAL, TALL

OUT = os.path.dirname(os.path.abspath(__file__))


def tx_right(d, x_right, y, text, size, fill, floor=64, mono=True):
    w = mixw(d, text, size, mono=mono)
    assert x_right - w >= floor, ("right-align", text)
    assert x_right <= EDGE, ("right-align", text)
    mix(d, x_right - w, y, text, size, fill, mono=mono)
    return x_right - w


# ── 图 1：一个月报 0 次、一个季通告 159 部 ──────────────────
def chart1():
    im, d = canvas(TALL)
    hdr(d, "微短剧被记在两条不同的线上", "月度备案公示表 · 季度发行许可通告")

    y = 194
    cols = [
        ("月度备案公示", "2026 年 9 月 · 页面 09-29 10:21", BLUE, [
            ("电视剧", "48 部"),
            ("网络剧合计", "248 部"),
            ("中剧", "53 部"),
            ("短剧集", "12 部"),
            ("季播剧", "6 部"),
            ("互动剧", "1 部"),
            ("网络故事片", "176 部"),
            ("微短剧", "0 个类目"),
        ], "296 行 7 列逐字段数：微短剧 0 次"),
        ("季度发行许可通告", "2026 年 4 至 6 月 · 页面 07-13", VERM, [
            ("国产网络剧片", "367 部 7,436 集"),
            ("网络剧", "25 部 576 集"),
            ("网络电影", "45 部"),
            ("微短剧", "159 部 5,396 集"),
            ("网络动画片", "138 部 1,419 集"),
        ], "通告原句：「颁发发行许可的国产网络剧片」"),
    ]
    cw = (W - 128 - 30) / 2
    for i, (name, sub, color, rows, note) in enumerate(cols):
        x = 64 + i * (cw + 30)
        d.rectangle([x, y, x + cw, y + 78], fill=color)
        tx(d, x + 18, y + 10, name, 30, PAPER)
        tx(d, x + 18, y + 48, sub, 20, (238, 232, 222))
        yy = y + 94
        for label, val in rows:
            hot = label == "微短剧"
            d.rectangle([x, yy, x + cw, yy + 56],
                        fill=(250, 240, 236) if hot else BOX,
                        outline=VERM if hot else LINE, width=2)
            tx(d, x + 18, yy + 14, label, 24, VERM if hot else INK)
            tx_right(d, x + cw - 18, yy + 16, val, 24, VERM if hot else DIM,
                     floor=x + 18 + mixw(d, label, 24) + 16)
            yy += 62
        d.line([(x, yy + 2), (x + cw, yy + 2)], fill=LINE, width=2)
        cb(d, x + 18, yy + 14, note, 21, DIM, maxw=cw - 36)
    y = y + 94 + 8 * 62 + 96

    y = panel(d, y + 14, [
        ("同一时间、同一主管部门体系下的两张表：月报表按长剧体系分类，里面没有微短剧；"
         "微短剧的量只在季度发行许可通告里出现，而它只统计「拿到许可证／批准文件」的那部分。", 24, INK, 34),
    ], outline=INK)

    y = foot(d, y + 10, [
        "来源：官网 09-29 月度备案公示通知及附件 xlsx、〔2026〕5 号季度发行许可通告",
        "两部文件均为 2026-10-12 抓取，附件由本地脚本读取后逐行统计",
    ])
    return im.crop((0, 0, W, y)), "010_图1_月报零次与季通告159部_1080.png"


# ── 图 2：三个月序列 + 微短剧季度平均集数 ────────────────────
def chart2():
    im, d = canvas(TALL)
    hdr(d, "三个月序列在涨，微短剧却在变短", "7／8／9 月备案公示 ＋ 一、二季度发行许可")

    # 左：三个月总盘子与两个类目
    mix(d, 64, 192, "月度备案公示部数", 25, INK, mono=False)
    months = [("7 月", 208), ("8 月", 254), ("9 月", 296)]
    x0, col_w, base = 64, 128, 470
    for i, (m, n) in enumerate(months):
        h = (n - 180) / (300.0 - 180) * 240
        x = x0 + i * (col_w + 18)
        d.rectangle([x, base - h, x + col_w, base], fill=BLUE)
        mix(d, x + col_w / 2 - mixw(d, str(n), 26) / 2, base - h - 36, str(n), 26, INK)
        mix(d, x + col_w / 2 - mixw(d, m, 22, False) / 2, base + 10, m, 22, DIM, mono=False)
    mix(d, 64, base + 46, "三个月净增 88 部（+42.3%）", 22, DIM, mono=False)

    d.line([(520, 210), (520, base + 60)], fill=LINE, width=2)
    tx(d, 560, 192, "两个走向相反的类目", 25, INK)
    series = [("网络故事片", "104 → 143 → 176 部", "占比 50% → 56.3% → 59.5%", TEAL),
              ("短剧集", "18 → 14 → 12 部", "占比 8.7% → 5.5% → 4.1%，唯一连降", VERM),
              ("互动剧", "无 → 无 → 1 部", "7、8 月正文无此类目，9 月首现 1 部 30 集", MONEY)]
    y = 240
    for name, seq, note, color in series:
        tx(d, 560, y, name, 25, INK)
        tx(d, 560, y + 40, seq, 24, color, mono=True)
        tx(d, 560, y + 78, note, 20, DIM)
        y += 118

    y = max(base + 86, y + 14)
    d.line([(64, y), (EDGE, y)], fill=LINE, width=2)
    y += 24
    mix(d, 64, y, "微短剧：季度发行许可通告两期对比（我按部／集各算了一笔除法）", 25, INK, mono=False)
    y += 46
    rows = [("一季度（1—3 月）", "317 部 7,262 集", "微短剧 144 部 5,667 集", "平均 39.4 集/部", BLUE),
            ("二季度（4—6 月）", "367 部 7,436 集", "微短剧 159 部 5,396 集", "平均 33.9 集/部", VERM)]
    for name, total, wdn, avg, color in rows:
        d.rectangle([64, y, EDGE, y + 72], fill=BOX, outline=LINE, width=2)
        d.rectangle([64, y, 72, y + 72], fill=color)
        tx(d, 92, y + 8, name, 24, INK)
        tx(d, 92, y + 40, total, 21, DIM, mono=True)
        tx(d, 420, y + 22, wdn, 24, color, mono=True)
        tx(d, 780, y + 22, avg, 24, color, mono=True)
        y += 82

    y += 6
    y = panel(d, y, [
        ("部数 +10.4%、集数 -4.8%，平均单部集数 39.4 → 33.9，一个季度短了 5.4 集。"
         "官方只给了部和集，「变短」是我算的。", 24, INK, 34),
        ("12 类题材里，司法 6 部 + 公安 10 部 + 国家安全 1 部 = 17 部 510 集，"
         "平均 30.0 集/部——特殊题材并没有被拍成更短的试水内容。", 23, DIM, 32),
    ], outline=INK)

    y = foot(d, y + 10, [
        "来源：官网 07-27／08-31／09-29 三份月度公示；〔2026〕5 号与 1—3 月期发行许可通告",
        "部数、集数为原文；占比、平均集数、增减幅为我自己算（官方未发布这些派生指标）",
    ])
    return im.crop((0, 0, W, y)), "010_图2_三个月序列与季度平均集数_1080.png"


# ── 图 3：三类微短剧各自去了哪张表 ──────────────────────────
def chart3():
    im, d = canvas(TALL)
    hdr(d, "三类微短剧，三种去向", "16 号令第五／十二／十七／二十三／三十三条")

    rows = [
        ("一类", "投资额度较大，或题材涉及政治、军事、外交、国家安全、统战、民族、宗教、司法、公安",
         "备案：备案公示（第十二条）", "许可：发行许可＋许可证定期向社会公告（第十七、二十三条）",
         "公开表里数得到", VERM),
        ("二类", "投资额度相对不大且为一般题材",
         "备案：备案公示可参照适用（第十二条）", "许可：播出前申请内容审核和发行许可，发批准文件",
         "季度通告数得到，公告里没有单独表", MONEY),
        ("三类", "投资额度较低且为一般题材（个人和小组做的量多落这档）",
         "备案：不进备案公示", "播出：由播出单位播前审核并标注节目编号（第十七条）",
         "剧目信息报进线上系统（第三十三条二）", BLUE),
    ]
    y = 196
    for name, who, filing, lic, out, color in rows:
        h = 214
        d.rectangle([64, y, EDGE, y + h], fill=BOX, outline=LINE, width=2)
        d.rectangle([64, y, 76, y + h], fill=color)
        tx(d, 98, y + 14, name, 32, color)
        cb(d, 98 + mixw(d, name, 32) + 22, y + 20, who, 22, INK, maxw=MAXW - 160)
        cb(d, 98, y + 96, filing, 22, DIM, maxw=MAXW - 40)
        cb(d, 98, y + 130, lic, 22, DIM, maxw=MAXW - 40)
        d.rectangle([64, y + h - 40, EDGE, y + h], fill=color)
        tx(d, 84, y + h - 32, out, 22, PAPER)
        y += h + 20

    y = panel(d, y, [
        ("所以：三类微短剧的信息不是被漏掉了，是制度里就没给它一张对公众发布的表。"
         "外部用月报表估赛道规模会漏，用季度通告也只会数到拿到许可证的一、二类。", 24, INK, 34),
        ("想被公开数据数到只有一条路：做成一类或二类、走省局以上备案并拿证。"
         "否则「我做过多少部」这件事，只能靠自己的账。", 24, VERM, 34),
    ], outline=VERM)

    y = foot(d, y + 10, [
        "来源：《微短剧发展管理办法》全文（官网 art_113_73785，09-01 施行）",
        "「个人和小组做的量多落这档」是我的判断，办法原文未写具体投资额档位",
    ])
    return im.crop((0, 0, W, y)), "010_图3_三类微短剧三种去向_1080.png"


if __name__ == "__main__":
    for fn in (chart1, chart2, chart3):
        im, name = fn()
        im.save(os.path.join(OUT, name))
        print(name, im.size)
