# -*- coding: utf-8 -*-
"""012《只有 8 个粉丝的号，文章怎么会有 777 个人读？》正文数据图 3 张
纯本地 Pillow，零扣费（严禁调用任何付费生成 API）。底层工具复用
_gen_charts_006/007/009/011（同一套纸底与字体；011 的 line/para/note_box/
src_foot/cjk_guard 直接 import，宽度校验与 LINES 登记共享同一套）。
注：Menlo 无中文字形，任何含 CJK 的行一律走 mix()/wrap()，禁止用 MONO 直接画整行，
否则出豆腐块；数字+汉字混排（如「777 人」）同样走 mix。正文图单行文案宽度上限
980px，每条文案打印 OK/OVER 校验并 assert（由 011 的封装代做）。
数据全部来自本号后台（查询时间 2026-10-13 12:0x，「最近 30 天」窗口），数值不得改动。
"""
import os
from PIL import Image, ImageDraw
from _gen_charts_006 import (W, PAPER, INK, DIM, LINE, TRACK, BOX, VERM, VERM_L,
                             BLUE, BLUE_L, GREY, SONG, HIRA, MONO, f, mix, mixw,
                             canvas, header, footer, grade_chip, runs, is_ascii)
from _gen_charts_007 import wrap, block
from _gen_charts_009 import cb, tx, hdr, foot, panel, EDGE, MAXW, MONEY, TEAL, TALL
from _gen_charts_011 import BODY, LINES, line, line_right, para, note_box, src_foot, cjk_guard, hdr_song

OUT = os.path.dirname(os.path.abspath(__file__))


def dbl(d, x, y, text, size, fill):
    """大字用 Hiragino W6（index=2）直接量宽并绘制——Menlo Bold 数字与汉字基线不齐，
    大字混排（如「关注 8 人」）统一走本函数。"""
    w = 0
    for r in runs(text):
        w += d.textlength(r, font=f(HIRA, size, index=2))
    tag = "OK  " if w <= BODY else "OVER"
    print("   %s %4dpx  %s" % (tag, round(w), text))
    assert w <= BODY, (text, w)
    assert x + w <= EDGE, ("dbl overflow", text)
    LINES.append((text, size, False))
    xx = x
    for r in runs(text):
        d.text((xx, y + size * 0.62), r, font=f(HIRA, size, index=2), fill=fill, anchor="lm")
        xx += d.textlength(r, font=f(HIRA, size, index=2))
    return xx


# ── 图 1：777 个阅读人数的渠道构成 ──────────────────────────
def chart1():
    im, d = canvas(TALL)
    hdr_song(d, "777 个读者是从哪些渠道来的",
             "12 篇逐篇拉总 · 最近 30 天 · 查询于 2026-10-13 12:0x")

    chans = [("推荐", 710, "91.4%", VERM),
             ("搜一搜", 43, "5.5%", BLUE),
             ("公众号消息", 11, "1.4%", BLUE),
             ("公众号主页", 11, "1.4%", BLUE),
             ("其它", 10, "1.3%", GREY),
             ("聊天会话", 4, "0.5%", GREY)]
    x0, track_w = 380, 340
    y = 206
    line(d, 64, y - 30, "六条渠道 · 按阅读人数降序（条上数字：人数 · 占 777 的比例）", 22, INK)
    for name, n, pct, color in chans:
        line_right(d, x0 - 20, y + 7, name, 24, INK if color != GREY else DIM)
        d.rectangle([x0, y, x0 + track_w, y + 40], fill=TRACK)
        bw = max(round(track_w * n / 710), 4)
        d.rectangle([x0, y, x0 + bw, y + 40], fill=color)
        line(d, x0 + bw + 16, y + 5, "%d 人 · %s" % (n, pct), 24, color)
        y += 40 + 16

    y += 6
    y = para(d, 64, y, "六条渠道数字相加 = 789，大于阅读人数合计 777：同一人可被多个渠道重复计入，"
                       "渠道数不能直接相加当人数用。", 22, VERM, MAXW)
    y += 16

    line(d, 64, y, "先看两个数：关注 8 人，读过 777 人", 30, INK)
    y += 54

    # 并排两组：账号级看板 vs 12 篇逐篇拉总
    bx_w, gap = 466, 20
    lx, rx = 64, 64 + bx_w + gap
    pad, ig = 16, 8
    big_h = 48
    l_items = [("最近 30 天阅读总人数 811", 22), ("流量来源：推荐占 89.8%", 22)]
    r_items = [("渠道六条相加 789 > 777", 22), ("推荐 710 人 · 占 91.4%", 22)]
    inner = bx_w - pad * 2

    def box_h(items):
        hh = 0
        for t, s in items:
            hh += len(wrap(t, s, inner, d, False)) * (s + 10)
        return 30 + big_h + ig + hh + ig + 20 + pad * 2

    bh = max(box_h(l_items), box_h(r_items))
    for bx, tag, big, items, color in (
            (lx, "账号级看板", "关注 8 人", l_items, BLUE),
            (rx, "12 篇逐篇拉总", "阅读 777 人", r_items, VERM)):
        d.rectangle([bx, y, bx + bx_w, y + bh], fill=(250, 246, 238), outline=color, width=3)
        d.rectangle([bx, y, bx + 8, y + bh], fill=color)
        LINES.append((tag, 22, False))
        line(d, bx + pad + 8, y + pad, tag, 22, color)
        dbl(d, bx + pad + 8, y + pad + 34, big, 36, INK)
        yy = y + pad + 34 + big_h + ig
        for t, s in items:
            yy = para(d, bx + pad + 8, yy, t, s, DIM, maxw=inner) + ig
    y += bh + 16

    y = note_box(d, y, [
        ("811 是账号级看板汇总，777 是 12 篇逐篇相加，两者聚合规则不同，不互相校验。", 23, INK, 33),
    ], outline=INK)

    y = src_foot(d, y + 10, [
        "来源：本号公众号后台（查询时间 2026-10-13 12:0x，窗口「最近 30 天」）",
        "百分比以 777 为分母，由本图作者计算；六条渠道与 811、89.8% 为后台原始读数",
    ])
    return im.crop((0, 0, W, y)), "012_图1_七百七十七人从哪来_1080.png"


# ── 图 2：完读率与阅读人数不同向 ────────────────────────────
DATA = [
    ("国庆扶持", 124, 21.0, 38),
    ("43万部微短剧", 103, 19.4, 40),
    ("「98.7%」瓶颈", 103, 28.2, 65),
    ("16号令54条", 102, 17.6, 34),
    ("9部剧本出局", 102, 32.4, 58),
    ("Seedance对比", 65, 26.2, 39),
    ("报名表问AI", 35, 14.3, 38),
    ("五个数", 19, 26.3, 14),
    ("三角网格", 25, 40.0, 55),
    ("90秒账单", 6, 0.0, 0),
    ("009重发", 54, 13.0, 46),
    ("010重发", 64, 10.9, 25),
]


def chart2():
    im, d = canvas(TALL)
    hdr_song(d, "完读率与阅读人数：12 个点",
             "12 篇逐条后台读数 · 最近 30 天 · 查询于 2026-10-13 12:0x")

    px0, px1, uv_max = 170, 980, 130
    py_b, py_t, cr_max = 520, 230, 42
    sx = (px1 - px0) / uv_max
    sy = (py_b - py_t) / cr_max

    for v in (10, 20, 30, 40):
        yy = py_b - v * sy
        d.line([(px0, yy), (px1, yy)], fill=LINE, width=1)
        line_right(d, px0 - 14, yy - 14, "%d%%" % v, 20, DIM)
    for v in (0, 30, 60, 90, 120):
        xx = px0 + v * sx
        d.line([(xx, py_t - 14), (xx, py_b)], fill=LINE, width=1)
        line_right(d, xx + 24, py_b + 10, str(v), 20, DIM)
    d.line([(px0, py_t - 14), (px0, py_b)], fill=INK, width=3)
    d.line([(px0, py_b), (px1 + 10, py_b)], fill=INK, width=3)
    line(d, 64, py_t - 56, "纵轴：完读率 %", 22, INK)
    line_right(d, EDGE, py_b + 44, "横轴：阅读人数（人）", 22, INK)

    # 标签只放简称（数值由网格线 + 下方数据表承载），右侧密集簇逐个错位防压字
    LBL = {
        "国庆扶持":      ("right", -14, -11, INK, None),
        "43万部微短剧":  ("right", -16, -6, DIM, None),
        "「98.7%」瓶颈": ("right", -16, -7, DIM, None),
        "16号令54条":    ("left", 14, -4, DIM, None),
        "9部剧本出局":   ("left", 14, -11, VERM, None),
        "Seedance对比":  ("left", 14, 11, DIM, None),
        "报名表问AI":    ("left", 14, -11, DIM, None),
        "五个数":        ("left", 14, -11, DIM, None),
        "三角网格":      ("left", 14, -11, VERM, "三角网格 25人·40.0%"),
        "90秒账单":      ("left", 14, -44, GREY, "90秒账单 6人·0.0%（样本 6 人，无统计意义）"),
        "009重发":       ("right", -14, 14, DIM, None),
        "010重发":       ("left", 14, -9, DIM, None),
    }
    for name, uv, cr, dur in DATA:
        cx, cy = px0 + uv * sx, py_b - cr * sy
        hot = name in ("三角网格", "90秒账单")
        if name == "90秒账单":
            d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=PAPER, outline=GREY, width=3)
        else:
            col = VERM if hot else INK
            r = 10 if hot else 8
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        side, dx, dy, col, over = LBL[name]
        txt = over if over else name
        if side == "left":
            line(d, cx + dx, cy + dy, txt, 19, col)
        else:
            line_right(d, cx + dx, cy + dy, txt, 19, col)

    y = py_b + 100
    y = note_box(d, y, [
        ("完读率最高的一篇《三角网格》40.0%，只有 25 人读；它不是这篇写得最好，是读的人太少，比例失真。",
         22, INK, 32),
        ("两篇都是 102 人的稿子（《9部剧本出局》《16号令54条》），完读率差 14.7 个百分点（32.4% 对 17.6%）。",
         22, INK, 32),
        ("《90秒账单》只有 6 人读过：完读率 0.0%、平均时长 0 秒，样本 6 人无统计意义，图中画成灰色空心点。",
         22, DIM, 32),
        ("12 个点看不出方向。本图不画趋势线，也不给相关性结论。", 23, VERM, 33),
    ], outline=INK)
    y += 16

    # 逐条数据表（含平均时长，散点标签放不下的字段在此补齐）
    line(d, 64, y, "12 篇原始数据（标题简称 · 阅读人数 · 完读率 · 平均时长）", 24, INK)
    y += 44
    d.rectangle([64, y, EDGE, y + 52], fill=INK)
    line(d, 92, y + 12, "篇目", 23, PAPER, mono=False)
    line_right(d, 520, y + 12, "阅读人数", 23, PAPER, mono=False)
    line_right(d, 730, y + 12, "完读率", 23, PAPER, mono=False)
    line_right(d, EDGE - 30, y + 12, "平均时长", 23, PAPER, mono=False)
    y += 52
    for i, (name, uv, cr, dur) in enumerate(DATA):
        hot = name == "90秒账单"
        if i % 2 == 0 and not hot:
            d.rectangle([64, y, EDGE, y + 50], fill=BOX)
        if hot:
            d.rectangle([64, y, EDGE, y + 50], fill=(250, 240, 236), outline=VERM, width=2)
        line(d, 92, y + 11, name, 22, VERM if hot else INK, mono=False)
        line_right(d, 520, y + 11, "%d" % uv, 22, INK)
        line_right(d, 730, y + 11, "%.1f%%" % cr, 22, INK)
        line_right(d, EDGE - 30, y + 11, "%ds" % dur, 22, INK)
        y += 50

    y = para(d, 64, y + 6, "注：《90秒账单》一行红框标注：样本 6 人，完读率与平均时长无统计意义。",
             21, DIM, MAXW)

    y = src_foot(d, y + 8, [
        "来源：后台逐篇「内容分析」页（查询时间 2026-10-13 12:0x，窗口「最近 30 天」）",
        "完读率与平均时长为后台原始读数，本图仅呈现散点与原始值，不含任何趋势判断",
    ])
    return im.crop((0, 0, W, y)), "012_图2_完读率与阅读人数不同向_1080.png"


# ── 图 3：五步自拉配方 ──────────────────────────────────────
def step_card(d, y, num, title, items, color=INK, accent=VERM):
    """步骤卡：左侧色条 + 「第N步 · 标题」+ 内容行。items: [(kind, text, size, fill, step, maxw, mono)]
    kind='para' 折行 / kind='raw' 单行（含 URL 手拆行）。按内容算高度。"""
    pad, ig = 14, 6
    inner_x = 64 + 20 + pad
    iw = EDGE - inner_x - pad
    h_title = 42
    hs = []
    for it in items:
        kind, text, size, fill, step = it[0], it[1], it[2], it[3], it[4]
        if kind == "raw":
            hs.append(len(text) * step)  # text 为手拆好的多行 URL，行数已知
        else:
            n = len(wrap(text, size, iw, d, it[5] if len(it) > 5 else False))
            hs.append(n * step)
    total = pad + h_title + ig + sum(hs) + ig * (len(items) - 1) + pad
    d.rectangle([64, y, EDGE, y + total], fill=BOX, outline=LINE, width=2)
    d.rectangle([64, y, 64 + 12, y + total], fill=accent)
    LINES.append(("第%s步 · %s" % (num, title), 25, False))
    assert 64 + 20 + mixw(d, "第%s步 · %s" % (num, title), 25, mono=False) <= EDGE
    line(d, inner_x, y + pad, "第%s步" % num, 26, accent)
    after = mix(d, inner_x, y + pad, "第%s步" % num, 26, accent)
    LINES.append((title, 24, False))
    line(d, after + 16, y + pad + 2, title, 24, INK, mono=False)
    yy = y + pad + h_title
    for it in items:
        kind, text, size, fill, step = it[0], it[1], it[2], it[3], it[4]
        mono = it[5] if len(it) > 5 else False
        if kind == "raw":
            for ln in text:
                line(d, inner_x, yy, ln, size, fill, mono=True)
                LINES.append((ln, size, True))
                yy += step
        else:
            yy = para(d, inner_x, yy, text, size, fill, maxw=iw, mono=mono, step=step) + ig
    return y + total


def chart3():
    im, d = canvas(TALL)
    hdr_song(d, "五步自拉配方：自己把数拉一遍",
             "作者实操路径 · 尖括号内全是占位符 · 勿写真实 token")

    y = 196
    y = step_card(d, y, "一", "账号级", [
        ("para", "数据分析 → 内容分析 → 数据时间选「最近 30 天」→ 读「流量来源」六条柱", 23, INK, 33),
        ("para", "推荐占比 ≥80%，即按「推荐驱动型」做后续决策", 23, VERM, 33),
    ]) + 14

    y = step_card(d, y, "二", "单篇分析页直链（把 URL 拼出来直接打开）", [
        ("raw", ["/misc/appmsganalysis?action=detailpage",
                 "&msgid=<msgID>_1&publish_date=<YYYY-MM-DD>",
                 "&type=int&pageVersion=1",
                 "&token=<你的后台token>"], 23, INK, 36),
    ]) + 10

    y = note_box(d, y, [
        ("三个坑：", 23, VERM, 33),
        ("① publish_date 必须等于真实发表日——填错不报错，静默返回全 0", 22, INK, 32),
        ("② 当天发的稿一定全 0（数据 T+1）", 22, INK, 32),
        ("③ read_num 是阅读次数，read_uv 才是阅读人数", 22, INK, 32),
    ], outline=VERM) + 14

    y = step_card(d, y, "三", "渠道数字代号", [
        ("para", "9999 = 全部（聚合行，勿与渠道相加）", 23, INK, 33),
        ("para", "0 = 公众号消息　4 = 公众号主页　5 = 其它", 23, INK, 33),
        ("para", "6 = 推荐　7 = 搜一搜", 23, VERM, 33),
        ("para", "1 / 2 = 聊天会话 / 朋友圈（本号 12 篇几乎没出现，未验证）", 22, DIM, 32),
    ]) + 14

    y = step_card(d, y, "四", "自建表头四列", [
        ("para", "发表日 / 阅读人数 / 推荐占比 / 搜一搜占比", 24, INK, 34),
        ("para", "建议再加两列：完读率、平均时长", 23, VERM, 33),
    ]) + 14

    y = step_card(d, y, "五", "自查开关", [
        ("para", "disable_recommend：0 = 推荐开着，1 = 被关", 23, INK, 33),
        ("para", "本号 12 篇查出来全是 0", 23, TEAL, 33),
    ]) + 14

    y = src_foot(d, y, [
        "来源：本号公众号后台实操路径（2026-10-13 实测）",
        "URL 中 msgID、publish_date、token 均为占位符；本配方为作者自用流程，非平台官方文档",
    ])
    return im.crop((0, 0, W, y)), "012_图3_五步自拉配方_1080.png"


if __name__ == "__main__":
    for fn in (chart1, chart2, chart3):
        print(fn.__name__)
        im, name = fn()
        im.save(os.path.join(OUT, name))
        print(name, im.size)
    print()
    cjk_guard()
