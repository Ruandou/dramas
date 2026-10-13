# -*- coding: utf-8 -*-
"""013《厂牌周报01｜快手把完播率换算成钱：50%加权怎么叠，20万上限谁能碰到》正文数据图 6 张
纯本地 Pillow，零扣费（严禁调用任何付费生成 API）。底层工具复用
_gen_charts_006/007/009/011/012（同一套纸底与字体；011 的 line/line_right/para/
note_box/src_foot/cjk_guard/hdr_song 与 012 的 dbl 直接 import，宽度校验与 LINES
登记共享同一套）。
注：Menlo 无中文字形，任何含 CJK 的行一律走 mix()/wrap()，禁止用 MONO 直接画整行，
否则出豆腐块；「数字+汉字」混排（如「20 万元」）同样走 mix。正文图单行文案宽度上限
980px，每条文案打印 OK/OVER 校验并 assert（由 011 的封装代做）。≠ ≈ ≥ ≤ 归 CJK 段
走 Hiragino，— · ÷ × 归 ASCII 段走 Menlo，字体 cmap 已逐字验证有字形。
数据一字不改，全部来自任务「数据真相源」；未披露项原样标注「未披露」。
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


def dashed(d, x0, y, x1, color, dash=12, gap=8, width=2):
    x = x0
    while x < x1:
        d.line([(x, y), (min(x + dash, x1), y)], fill=color, width=width)
        x += dash + gap


# ── 图 1：四项规则卡 ────────────────────────────────────────
def chart1():
    im, d = canvas(TALL)
    hdr_song(d, "快手「好剧、系列剧激励活动」四项规则",
             "2026-09-30 宣布 · 活动期 2026-10-01 至 2026-11-30")

    y = 196
    d.rectangle([64, y, EDGE, y + 96], fill=BOX, outline=LINE, width=2)
    d.rectangle([64, y, 74, y + 96], fill=TEAL)
    line(d, 98, y + 14, "参与范围", 26, TEAL)
    line(d, 98, y + 54, "快手端原生短剧经营者平台上架的分账短剧 · 真人剧与漫剧均可", 24, INK)
    y += 112

    cards = [
        ("+15%", "单剧时长达标", "对应内容消费时长", BLUE),
        ("+15%", "完播率达标", "对应观看完成度", BLUE),
        ("+20%", "第二季起 上一季发布后\n两个月内发新季", "系列剧专项激励", VERM),
    ]
    cw = (EDGE - 64 - 2 * 16) / 3
    ch = 244
    for i, (big, title, sub, color) in enumerate(cards):
        x = 64 + i * (cw + 16)
        d.rectangle([x, y, x + cw, y + ch], fill=(250, 246, 238), outline=color, width=3)
        dbl(d, x + 18, y + 18, big, 52, color)
        yy = y + 96
        for ln in title.split("\n"):
            line(d, x + 18, yy, ln, 23, INK, maxw=int(cw) - 36)
            yy += 32
        line(d, x + 18, y + ch - 44, sub, 21, DIM, maxw=int(cw) - 36)
    y += ch + 20

    # 叠加上限条
    d.rectangle([64, y, EDGE, y + 150], fill=BOX, outline=INK, width=2)
    line(d, 92, y + 18, "叠加规则", 25, INK)
    line(d, 92, y + 60, "15% + 15% + 20%　→　系数可叠加，最高 50%", 30, VERM)
    line(d, 92, y + 106, "系数直接作用于单剧分账金额 · 单剧激励最高 20 万元", 25, INK)
    y += 170

    d.rectangle([64, y, EDGE, y + 108], fill=(250, 240, 236), outline=VERM, width=3)
    d.rectangle([64, y, 76, y + 108], fill=VERM)
    line(d, 100, y + 16, "达标门槛值：未披露", 32, VERM)
    line(d, 100, y + 66, "时长多少算达标、完播率到几个点算达标——五篇公开报道全部空白", 23, INK)
    y += 128

    y = src_foot(d, y, [
        "来源：三篇带完整规则（流媒体网、证券市场周刊、AITOP100，均 2026-10-10）",
        "　　＋两篇消息稿（腾讯新闻、凤凰网，2026-09-30）",
        "五篇口径一致、未见平台官方原文（B 级）；「未披露」为五篇报道的共有空白，本图不补数",
    ])
    return im.crop((0, 0, W, y)), "013_图1_四项规则叠加上限_1080.png"


# ── 图 2：反推曲线（40 万拐点）──────────────────────────────
def chart2():
    im, d = canvas(TALL)
    hdr_song(d, "基础分账 × 系数 = 实际到手：20 万是天花板",
             "本号按公开系数计算（A 级）· 横轴 √ 压缩刻度 · 单位：万元")

    px0, px1 = 190, 950
    py_b, py_t = 640, 270
    ymax = 24  # 万元

    def X(v):  # v 万元；√ 压缩刻度（分段刻度，任务允许），1 万→px0、100 万→px1
        return px0 + (px1 - px0) * ((v ** 0.5) / 10.0)

    def Y(v):
        return py_b - (py_b - py_t) * (v / ymax)

    # 网格与轴
    for v in (5, 10, 15, 20):
        line_right(d, px0 - 14, Y(v) - 13, str(v), 20, DIM)
        d.line([(px0, Y(v)), (px1, Y(v))], fill=LINE, width=1)
    for v in (1, 5, 10, 20, 40, 80, 100):
        d.line([(X(v), py_t - 10), (X(v), py_b)], fill=(232, 226, 214), width=1)
        line_right(d, X(v) + 24, py_b + 12, str(v), 20, DIM)
    d.line([(px0, py_t - 14), (px0, py_b)], fill=INK, width=3)
    d.line([(px0, py_b), (px1 + 10, py_b)], fill=INK, width=3)
    line(d, 64, py_t - 58, "纵轴：实际到手激励（万元）", 22, INK)
    line_right(d, EDGE, py_b + 46, "横轴：基础分账金额（万元，√ 压缩刻度）", 22, INK)

    # 图例（轴标签同行右侧，三个短档名）
    for lx_, col, txt in ((560, VERM, "50% 档"), (700, BLUE, "30% 档"), (840, GREY, "15% 档")):
        d.line([(lx_, py_t - 44), (lx_ + 50, py_t - 44)], fill=col, width=5)
        line(d, lx_ + 62, py_t - 55, txt, 22, col)

    # 20 万天花板
    dashed(d, px0, Y(20), px1, VERM, dash=14, gap=8, width=3)
    line_right(d, EDGE, Y(20) - 36, "20 万元上限（天花板）", 24, VERM)

    # 三条线
    l15 = [(1, 0.15), (10, 1.5)]
    l30 = [(1, 0.3), (10, 3)]
    l50 = [(5, 2.5), (10, 5), (20, 10), (40, 20), (80, 20), (100, 20)]
    for pts, col in ((l15, GREY), (l30, BLUE)):
        d.line([(X(v), Y(w)) for v, w in pts], fill=col, width=4)
    d.line([(X(v), Y(w)) for v, w in l50], fill=VERM, width=5)

    def dot(v, w, col, r=8):
        d.ellipse([X(v) - r, Y(w) - r, X(v) + r, Y(w) + r], fill=col)

    for v, w in l15:
        dot(v, w, GREY, 6)
    for v, w in l30:
        dot(v, w, BLUE, 6)
    for v, w in l50:
        dot(v, w, VERM, 10 if v == 40 else 7)

    # 关键点标注（位置按线走向错开，避免压线；5 万档数值由下方算式框承载，
    # 图上不标——左侧贴纵轴刻度易与刻度数字连读）
    line_right(d, X(10) - 14, Y(5) - 40, "10 万 → 5 万", 21, VERM)
    line(d, X(20) + 16, Y(10) - 10, "20 万 → 10 万", 21, VERM)
    line_right(d, X(40) - 14, Y(20) - 46, "40 万 → 20 万 刚好顶格（拐点）", 24, VERM)
    line_right(d, EDGE, Y(20) + 40, "80 万 → 20 万：有效系数 25%", 22, INK)
    line_right(d, EDGE, Y(20) + 80, "100 万 → 20 万：有效系数 20%", 22, INK)
    line(d, X(10) + 12, Y(1.5) + 4, "15%", 20, GREY)
    line(d, X(10) + 12, Y(3) - 26, "30%", 20, BLUE)

    y = py_b + 86
    y = note_box(d, y, [
        ("算式（A 级，本号按公开系数计算）：实际到手激励 = min(基础分账 × 系数, 20 万元)。", 22, INK, 32),
        ("15% 档：1 万→1,500 元、10 万→1.5 万；30% 档：1 万→3,000 元、10 万→3 万；"
         "50% 档：5 万→2.5 万、10 万→5 万、20 万→10 万、40 万→20 万（顶格拐点）。", 22, INK, 32),
        ("超过 40 万后增量被上限截断：80 万本应 40 万、实给 20 万（有效系数 25%）；100 万只剩 20%。", 22, INK, 32),
        ("「时长达标」「完播率达标」的门槛值未披露——本图只回答「达标之后能拿多少」，不回答「怎么才算达标」。",
         23, VERM, 33),
    ], outline=INK)

    y = src_foot(d, y + 10, [
        "系数与上限：五篇报道口径（B 级）；整张曲线为本号按公开系数计算（A 级），过程可复核",
        "同期背景：快手原生短剧 TOP10 版权方分账 8 月突破 2,000 万元（环比 +53%，四篇均写明）",
        "「7 月约 1,300 万元」仅 AITOP100 一篇明写，属 C 级单源，本图不作依据",
    ])
    return im.crop((0, 0, W, y)), "013_图2_反推曲线四十万拐点_1080.png"


# ── 图 3：60 天排期红线 ─────────────────────────────────────
def chart3():
    im, d = canvas(TALL)
    hdr_song(d, "「两个月内发新季」是一条 60 天的排期红线",
             "系列剧 +20% 加权 · 示例：上一季 2026-10-01 上线")

    x0, x1, axis = 150, 930, 320
    d.rectangle([x0, axis - 26, x1, axis + 26], fill=(250, 240, 236), outline=VERM, width=2)
    d.line([(x0, axis), (x1, axis)], fill=INK, width=3)
    for cx in (x0, x1):
        d.ellipse([cx - 11, axis - 11, cx + 11, axis + 11], fill=INK, outline=PAPER, width=2)
    line(d, (x0 + x1) / 2 - mixw(d, "60 天窗口", 30) / 2, axis - 16 - 40, "60 天窗口", 30, VERM)
    line(d, x0 - 60, axis + 42, "10-01 上一季上线", 22, INK)
    line_right(d, x1 + 70, axis + 42, "11-30 新一季最晚上线", 22, INK)
    line_right(d, x1 + 70, axis + 80, "同日 = 活动期最后一天", 22, VERM)
    d.line([(x1, axis + 30), (x1, axis + 74)], fill=VERM, width=2)

    y = axis + 128
    y = note_box(d, y, [
        ("冲突点（未披露）：", 24, VERM, 34),
        ("上一季若在 10-01 之后上线，60 天窗口会撞穿 11-30 的活动截止线。新季上线要落在活动期内，"
         "还是窗口只要满足 60 天即可？五篇报道都没写——工单里必须加上这一问。", 22, INK, 32),
    ], outline=VERM)
    y += 16

    line(d, 64, y, "三项硬条件（+20% 的参评前提，上线前就能补齐）", 25, INK)
    y += 46
    for i, (t, s) in enumerate((
            ("剧名明确包含季数信息", "第一季 / 第二季写进剧名——立项时没人提醒就漏"),
            ("全季归属同一个端原生分账账号", "最容易踩坑：很多团队第一季和第二季根本不在一个账号"),
            ("新老季完成内容关联", "后台把新季和上一季做关联操作"))):
        d.rectangle([64, y, EDGE, y + 84], fill=BOX, outline=LINE, width=2)
        d.rectangle([64, y, 72, y + 84], fill=BLUE)
        line(d, 92, y + 12, "①②③"[i] + " " + t, 24, INK)
        line(d, 92, y + 50, s, 21, DIM)
        y += 96

    y += 6
    d.rectangle([64, y, EDGE, y + 190], fill=(250, 246, 238), outline=TEAL, width=3)
    line(d, 92, y + 18, "产能验算（本号 standard-86 规格 · 本号计算，A 级）", 24, TEAL)
    line(d, 92, y + 60, "86 集 × 90 秒 ≈ 129 分钟成片", 30, INK)
    line(d, 92, y + 112, "129 ÷ 60 ≈ 每天 2.15 分钟成片", 32, VERM)
    line(d, 92, y + 156, "达不到只有两个选项：砍单季集数，或上一季上线当天就开下一季（边发边做）", 22, INK)
    y += 210

    y = src_foot(d, y, [
        "来源：腾讯新闻、凤凰网（09-30）· 证券市场周刊、AITOP100（10-10）报道口径（B 级）",
        "「60 天」为「上一季上线后两个月内」的折算；",
        "129 ÷ 60 ≈ 2.15 分钟/日为本号按自身 standard-86 规格计算（A 级）",
    ])
    return im.crop((0, 0, W, y)), "013_图3_六十天排期红线_1080.png"


# ── 图 4：两条线索同向 ──────────────────────────────────────
def chart4():
    im, d = canvas(TALL)
    hdr_song(d, "本周两条独立线索，方向一致",
             "一边是平台给续作加权，一边是续作霸榜 · 两者没有交集")

    colw = 400
    lx = 64
    rx = EDGE - colw
    top, colh = 200, 430
    inner_pad = 18

    d.rectangle([lx, top, lx + colw, top + colh], fill=(244, 240, 234), outline=BLUE, width=3)
    d.rectangle([lx, top, lx + colw, top + 56], fill=BLUE)
    line(d, lx + inner_pad, top + 12, "线索一 · 平台侧", 25, PAPER)
    yy = top + 76
    for t, s, c in (
        ("快手：第二季起，上一季发布后两个月内发新季 +20% 激励加权", 23, INK),
        ("系数可叠加最高 50%，作用于分账金额", 22, DIM),
        ("活动期 2026-10-01 至 11-30", 22, DIM)):
        yy = para(d, lx + inner_pad, yy, t, s, c, maxw=colw - inner_pad * 2, mono=True, step=s + 10) + 12
    line(d, lx + inner_pad, top + colh - 60, "给钱的一方主动奖励续作", 23, BLUE)

    d.rectangle([rx, top, rx + colw, top + colh], fill=(250, 240, 236), outline=VERM, width=3)
    d.rectangle([rx, top, rx + colw, top + 56], fill=VERM)
    line(d, rx + inner_pad, top + 12, "线索二 · 渠道侧", 25, PAPER)
    yy = top + 76
    for t, s, c in (
        ("10-07 红果短剧热播榜登顶：《聚宝仙盆之杂灵根才是真 BOSS·第十三季》（3D 漫剧续作）", 23, INK),
        ("原榜首《万妖图录传第十三季》 退居第二", 22, INK),
        ("TOP5 合集热度 3.87 亿（前一日 3.68 亿，+5.3%）", 22, DIM),
        ("榜单头部全是「第十三季」", 23, VERM)):
        yy = para(d, rx + inner_pad, yy, t, s, c, maxw=colw - inner_pad * 2, mono=True, step=s + 10) + 10

    # 中间免责带（居于两栏正中）
    mx = lx + colw
    bcx = (mx + rx) / 2
    d.rectangle([bcx - 52, top, bcx + 52, top + colh], fill=INK)
    ty = top + (colh - (34 * 6 + 40 + 12 * 7)) / 2
    for c in "方向一致≠因果":
        size = 40 if c == "≠" else 34
        col = VERM_L if c == "≠" else PAPER
        d.text((bcx - mixw(d, c, size, mono=False) / 2, ty + size * 0.62), c,
               font=f(HIRA, size, index=2), fill=col, anchor="lm")
        ty += size + 12
    LINES.append(("方向一致≠因果", 34, False))

    y = top + colh + 24
    y = note_box(d, y, [
        ("别把它读成因果：榜单登顶的那批剧拿的是红果的收益，不是快手的加权，两边没有资金往来。", 23, VERM, 34),
        ("能借的判断只有一条：「一季一弃」的做法，在内容和渠道两头同时失去奖励。", 24, INK, 34),
        ("对照（同日另一张榜）：10-07 抖音漫剧日榜 TOP5 合计新增播放 8.4 亿（前一日 8.1 亿，+3.7%）——"
         "头部《路争》《顺路载同事三个月》排名稳固，后三位全是团圆亲情向新剧，并非续作。", 22, DIM, 32),
    ], outline=INK)

    y = src_foot(d, y + 10, [
        "来源：快手激励规则见五篇公开报道（B 级）",
        "榜单据流媒体网《短剧资讯速递》（2026.10.8—10.10 期，2026-10-10 发布，C 级单源）",
        "引用请带「据流媒体网」；「方向一致 ≠ 因果」为本号判断，非媒体报道原文",
    ])
    return im.crop((0, 0, W, y)), "013_图4_两条线索同向_1080.png"


# ── 图 5：本周时间轴 ────────────────────────────────────────
EVENTS = [
    ("10-01", "快手激励活动期开始（至 11-30）", "四项规则生效首日", TEAL),
    ("10-05", "戏曲微短剧《惊梦专线》先导片首发", "第十届中国戏曲文化周闭幕式发布", BLUE),
    ("10-05", "AI 漫剧《李冰父子之逆水封神》上星四川卫视", "四川广播电视台微短剧工作室出品", BLUE),
    ("10-05", "方言短剧《胡基沟那些事》上线", "高价彩礼、大操大办题材，移风易俗向", BLUE),
    ("10-05", "豪门情感短剧《无效娇养》开机", "芒果 TV 等联合出品，魂穿 + 民国女伶", MONEY),
    ("10-06", "乡村微短剧《风雨枣花开》上线", "抖音/红果，青岛本土企业出品", BLUE),
    ("10-06", "都市爱情短剧《致爱丽丝》上线", "红果，追风互娱联合出品", BLUE),
    ("10-06", "竖屏精品短剧《红都雷霆》开机", "北京大视听重点、长征胜利 90 周年片单、咪咕数字传媒联合出品", MONEY),
    ("10-08", "AIGC 微短剧《灯魂之燃青春》上线", "「AIGC + 真人演员」，非遗滚灯题材", BLUE),
    ("10-08", "廉洁文化 AI 微短剧《撑腰》上线", "取材国企招商服务真实场景", BLUE),
    ("10-08", "微短剧《烟雨识归人》开机", "实景拍摄 + AI 视觉还原年代往事双轨叙事", MONEY),
    ("10-13", "广电总局科技司挂出《广播电视收视大数据指标及计算方法》 报批稿公示", "09:00 挂出 · 公示期 10-13 至 10-22", VERM),
]


def chart5():
    im, d = canvas(TALL)
    hdr_song(d, "把本周的事排到日历上：10-01 至 10-13",
             "按日期升序 · 蓝色=上线/首发 · 褐色=开机 · 红色=标准公示")

    y = 198
    spine_x = 162
    for date, title, note, color in EVENTS:
        hot = color == VERM
        h = 118 if hot else 96
        d.rectangle([64, y, EDGE, y + h], fill=(250, 240, 236) if hot else BOX,
                    outline=VERM if hot else LINE, width=3 if hot else 2)
        d.line([(spine_x, y + 14), (spine_x, y + h - 14)], fill=LINE, width=2)
        d.ellipse([spine_x - 9, y + h / 2 - 9, spine_x + 9, y + h / 2 + 9], fill=color, outline=PAPER, width=2)
        line(d, 66, y + h / 2 - 24, date, 24, color)
        tx_x = spine_x + 26
        maxw_t = EDGE - tx_x - 20 - (150 if hot else 0)
        yy = para(d, tx_x, y + 12, title, 23, INK, maxw=maxw_t, step=31)
        para(d, tx_x, yy + 2, note, 20, DIM, maxw=maxw_t, step=27)
        if hot:
            line_right(d, EDGE - 18, y + h - 40, "本号今日另发专稿", 22, VERM)
        y += h + 10

    y += 6
    d.rectangle([64, y, EDGE, y + 132], fill=(250, 246, 238), outline=INK, width=2)
    line(d, 92, y + 12, "给做 AI 剧的人划两处重点：", 23, INK)
    para(d, 92, y + 50, "① 10-05 至 10-08 上星、联制、指导类项目全部用了 AIGC 或「AIGC + 真人」，已是生产工具不是噱头；"
                        "② 抖音漫剧日榜后三位被团圆亲情向新剧占了。", 21, DIM, 900, step=30)
    y += 152

    y = src_foot(d, y, [
        "来源：10-05 至 10-08 条剧目与日期均据流媒体网《短剧资讯速递》",
        "（2026.10.8—10.10 期，2026-10-10 发布，C 级单源）",
        "10-13 条：广电总局官网科技司公示（本号当日核验）；快手活动期见五篇报道（B 级）",
    ])
    return im.crop((0, 0, W, y)), "013_图5_本周时间轴_1080.png"


# ── 图 6：证据分级条 ────────────────────────────────────────
def chart6():
    im, d = canvas(TALL)
    hdr_song(d, "本文每个数字站在哪一档",
             "A=本号自算 · B=多家独立媒体口径一致 · C=单源汇编")

    tiers = [
        ("A 级 · 本号自己算", VERM, [
            "反推表整张：5 万→2.5 万、10 万→5 万、20 万→10 万、40 万→20 万顶格；超 40 万有效系数降至 25%/20%",
            "产能换算：86 集 × 90 秒 ≈ 129 分钟成片，129 ÷ 60 ≈ 2.15 分钟/日",
            "依据：平台公开的系数与上限，过程可复核",
        ]),
        ("B 级 · 多家口径一致，未见平台原文", BLUE, [
            "四项激励规则（时长 +15% / 完播率 +15% / 续作 +20%）与「叠加最高 50%、单剧 20 万元」——三篇带完整规则（流媒体网、证券市场周刊、AITOP100，均 10-10）",
            "活动期 2026-10-01 至 11-30；真人剧与漫剧均可参与",
            "快手原生短剧 TOP10 版权方 8 月分账突破 2,000 万元、较 7 月 +53%——再加两篇消息稿（腾讯新闻、凤凰网 09-30），共四篇",
            "五篇之间无一处矛盾数字；但均未给出时长与完播率的达标门槛值",
        ]),
        ("C 级 · 单一行业媒体汇编或单源", MONEY, [
            "本周全部剧目名称与上线/开机日期（图 5 全列）",
            "10-07 红果热播榜 TOP5 合集热度 3.87 亿（前一日 3.68 亿，+5.3%）",
            "10-07 抖音漫剧日榜 TOP5 新增播放 8.4 亿（前一日 8.1 亿，+3.7%）",
            "「7 月约 1,300 万元」只有 AITOP100 一篇明写，本文不把它当结论用",
            "依据：剧目与榜单均出自流媒体网《短剧资讯速递（2026.10.8—10.10）》（10-10 发布），本号未回一手来源，引用请带「据流媒体网」",
        ]),
    ]
    y = 198
    for name, color, items in tiers:
        pad, ig = 16, 10
        iw = (EDGE - 64) - 24 - pad * 2
        hs = [len(wrap(t, 22, iw, d, True)) * 32 for t in items]
        h = 52 + sum(hs) + ig * (len(items) - 1) + pad + 12
        d.rectangle([64, y, EDGE, y + h], fill=BOX, outline=LINE, width=2)
        d.rectangle([64, y, 74, y + h], fill=color)
        line(d, 64 + 24, y + 14, name, 26, color)
        yy = y + 52 + 6
        for t, hh in zip(items, hs):
            last = "依据" in t
            para(d, 64 + 24 + pad, yy, t, 22, DIM if last else INK, maxw=iw, mono=True, step=32)
            yy += hh + ig
        y += h + 16

    d.rectangle([64, y, EDGE, y + 148], fill=(250, 240, 236), outline=VERM, width=3)
    line(d, 92, y + 14, "明确未知（本文没有答案，只给了问法）", 25, VERM)
    line(d, 92, y + 58, "① 「时长达标」「完播率达标」的门槛值：未披露", 23, INK)
    line(d, 92, y + 98, "② 60 天窗口与 11-30 活动截止的冲突处理规则：未披露", 23, INK)
    y += 168

    line(d, 64, y, "时效：本文信息截至 2026-10-13 14:30 · 活动 11-30 截止", 22, DIM)
    line(d, 64, y + 40, "10-22 是另一件事（收视大数据标准公示期）的截止日", 22, DIM)
    y += 88

    y = src_foot(d, y, [
        "分级为本号对信息来源的标注：A 自算可复核 / B 多家独立报道口径一致 / C 单源汇编未回一手",
        "无法用本文文本核实的项一律列「明确未知」，不补数",
    ])
    return im.crop((0, 0, W, y)), "013_图6_证据分级三档_1080.png"


if __name__ == "__main__":
    for fn in (chart1, chart2, chart3, chart4, chart5, chart6):
        print(fn.__name__)
        im, name = fn()
        im.save(os.path.join(OUT, name))
        print(name, im.size)
    print()
    cjk_guard()
