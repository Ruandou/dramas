# -*- coding: utf-8 -*-
"""007《微短剧到底有多少用户？五个数全都真，但没有一个能比》正文数据图 4 张
纯本地 Pillow，零扣费。绘图工具与配色复用 _gen_charts_006.py（同一套纸底/字体）。
注：Menlo 无中文字形、Hiragino 无 ✗✓ 与 U+2212，特殊符号一律避开，否则出豆腐块。
"""
import os
from PIL import Image, ImageDraw
from _gen_charts_006 import (W, PAPER, INK, DIM, LINE, TRACK, BOX, VERM, VERM_L,
                             BLUE, BLUE_L, GREY, SONG, HIRA, MONO, f, mix, mixw,
                             canvas, header, footer, grade_chip, runs, is_ascii)

OUT = os.path.dirname(os.path.abspath(__file__))
MONEY = (110, 102, 90)
STEEL = (84, 118, 152)
TEAL = (44, 96, 96)


def wrap(text, size, maxw, d, mono=True):
    """按像素宽度折行：ASCII 连续段当作一个词（不拆单词），中日韩逐字可断。"""
    toks = []
    for r in runs(text):
        if mono and is_ascii(r):
            toks.append(r)
        else:
            toks.extend(list(r))
    lines, cur = [], ""
    for t in toks:
        trial = cur + t
        if cur and mixw(d, trial, size, mono) > maxw:
            lines.append(cur)
            cur = t
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, text, size, maxw, fill, mono=True, step=None, center_at=None):
    """自动折行绘制，返回下一段起始 y。center_at 给定时按该 x 居中。"""
    step = step or size + 10
    for ln in wrap(text, size, maxw, d, mono):
        xx = x if center_at is None else center_at - mixw(d, ln, size, mono) / 2
        mix(d, xx, y, ln, size, fill, mono=mono)
        y += step
    return y


# ── 图 1：五个数同轴，三样要素全不同 ────────────────────────
def chart1():
    H = 880
    im, d = canvas(H)
    header(d, "五个用户数摆在同一条轴上",
           "机构·口径·时点三样没一样相同 · 横轴按先后等距，不按真实月份比例")

    cols = [
        ("2024-12", "6.62 亿", "网络视听年度报告（媒体转述页）",
         "渗透率｜分母是网民规模｜不少标题把它误标成 CNNIC", BLUE),
        ("2026-02", "7.18 亿", "QuestMobile 官方报告页",
         "月活｜短剧行业｜独立 APP 与小程序合计", VERM),
        ("2026-06", "6.31 亿", "收视中国稿转述 CSM",
         "月活｜微短剧｜媒介接触测量，样本框另一套", MONEY),
        ("2026 上半年", "6 亿", "DataEye 报告（媒体引述）",
         "AI 短剧用户｜只是全类的一个子集", STEEL),
        ("2026-09-17", "超 8 亿", "国新办发布会·总局",
         "用户｜统计范围与时间窗都没给", TEAL),
    ]
    spine = 322
    d.line([(64, spine), (W - 64, spine)], fill=INK, width=2)
    xs = [104 + i * (872 / 4) for i in range(5)]

    for (date, val, org, note, color), cx in zip(cols, xs):
        mix(d, cx - mixw(d, val, 44) / 2, spine - 104, val, 44, color)
        d.ellipse([cx - 12, spine - 12, cx + 12, spine + 12], fill=color, outline=PAPER, width=2)
        mix(d, cx - mixw(d, date, 22) / 2, spine + 26, date, 22, INK)
        y = block(d, cx, spine + 74, org, 21, 196, INK, step=32, center_at=cx)
        block(d, cx, y + 6, note, 19, 196, DIM, step=30, center_at=cx)

    d.rectangle([64, 600, W - 64, 718], fill=BOX)
    mix(d, 84, 616, "五个点连起来会画出一条「先涨、后跌、再暴涨」的折线——", 25, INK, mono=False)
    mix(d, 84, 658, "这条线不存在。差 8,700 万不是用户掉了，是 6.31 与 7.18 用了两把尺子。", 25, VERM, mono=False)

    footer(d, 762, "口径：数值均为各机构页面原句；等距轴仅为排布，不表示时间间隔相等")
    return im, "007_图1_五个数同轴_1080.png"


# ── 图 2：五张身份证 ────────────────────────────────────────
def chart2():
    H = 1320
    im, d = canvas(H)
    header(d, "五张身份证：谁发布、量什么、量到哪月",
           "缺任一格，这个数就只能定性引用，不能进加减乘除")

    rows = [
        ("6.62 亿", "2024-12", "网络视听行业年度报告", "网民中看过微短剧的人（渗透率）",
         "分母＝网民规模 11.09 亿（由使用率 59.7% 反推）", "C 级·仅媒体转述页", BLUE),
        ("7.18 亿", "2026-02", "QuestMobile 官方报告页", "短剧行业月活跃用户",
         "含独立 APP 3.35 亿＋微信小程序 4.27 亿（跨端去重）", "A 级·机构自有页", VERM),
        ("6.31 亿", "2026-06", "收视中国稿引 CSM", "微短剧月活用户（全媒体接触）",
         "电视＋手机＋平板，样本框与 App 监测不同源", "B 级·署名稿转述", MONEY),
        ("6 亿", "2026 上半年", "DataEye 报告（媒体引述）", "AI 短剧用户",
         "全类的一个子集，与「超 8 亿」不是同一分母", "A-/B 级", STEEL),
        ("超 8 亿", "2026-09-17", "国新办发布会·总局", "全国微短剧用户",
         "未给统计范围、未给时间窗、未给分母", "A 级·发布会引语", TEAL),
    ]
    y = 214
    for val, date, org, koujing, note, grade, color in rows:
        d.rectangle([64, y, W - 64, y + 178], fill=BOX, outline=LINE, width=2)
        d.rectangle([64, y, 74, y + 178], fill=color)
        mix(d, 96, y + 20, val, 44, color)
        mix(d, 96, y + 88, date, 22, DIM)
        grade_chip(d, W - 64 - (mixw(d, grade, 21) + 26), y + 16, grade, color)
        yx = 322
        mix(d, yx, y + 20, "机构｜" + org, 23, INK, mono=False)
        mix(d, yx, y + 62, "口径｜" + koujing, 23, INK, mono=False)
        block(d, yx, y + 106, "范围｜" + note, 21, 640, DIM, mono=False, step=32)
        y += 196

    footer(d, y + 6, "来源：QuestMobile 官方报告页 2026-04-08 · 国新办发布会 2026-09-17\n收视中国 2026-07-22 · 人民日报中国城市报 2026-08-10 引 DataEye 报告")
    return im, "007_图2_五张身份证_1080.png"


# ── 图 3：3.35 + 4.27 = 7.62 ≠ 7.18 ─────────────────────────
def chart3():
    H = 1080
    im, d = canvas(H)
    header(d, "3.35 加 4.27 不等于 7.18：那 4,400 万去哪了",
           "同一份 QuestMobile 报告、同一页、同一时点（2026-02）")

    MAXV = 8.6
    x0, x1 = 150, 900

    def X(v):
        return x0 + (x1 - x0) * (v / MAXV)

    ruler = 258
    d.line([(x0, ruler), (x1 + 10, ruler)], fill=INK, width=2)
    for v in range(0, 9):
        d.line([(X(v), ruler - 8), (X(v), ruler + 8)], fill=INK, width=2)
        mix(d, X(v) - mixw(d, str(v), 21) / 2, ruler + 16, str(v), 21, DIM)
    mix(d, X(8) + 16, ruler + 16, "亿", 21, DIM, mono=False)
    for v in range(1, 9):
        d.line([(X(v), ruler + 46), (X(v), 540)], fill=(232, 226, 214), width=1)

    bh = 62
    y = 344
    mix(d, 64, y - 36, "① 分端相加 = 7.62 亿（我算的）", 25, INK, mono=False)
    d.rectangle([x0, y, X(3.35), y + bh], fill=BLUE)
    d.rectangle([X(3.35), y, X(7.62), y + bh], fill=BLUE_L)
    mix(d, x0 + 14, y + 18, "独立 APP 3.35", 23, PAPER)
    mix(d, X(3.35) + 14, y + 18, "微信小程序 4.27", 23, INK)
    mix(d, X(7.62) + 14, y + 18, "7.62", 25, VERM)

    y = 464
    mix(d, 64, y - 36, "② 同页写的行业总数 = 7.18 亿（机构原句）", 25, INK, mono=False)
    d.rectangle([x0, y, X(7.18), y + bh], fill=MONEY)
    mix(d, x0 + 14, y + 18, "短剧行业月活 7.18", 23, PAPER)

    xa, xb = X(7.18), X(7.62)
    for xx in (xa, xb):
        d.line([(xx, 546), (xx, 578)], fill=VERM, width=2)
    d.line([(xa, 570), (xb, 570)], fill=VERM, width=2)
    mix(d, (xa + xb) / 2 - mixw(d, "4,400 万", 25) / 2, 586, "4,400 万", 25, VERM)

    y = block(d, 64, 636, "去向：同一个人在独立 App 和小程序里都被数了一次。机构给的总数去过重，相加的那两个数没去重。",
              23, 952, INK, mono=False, step=34)
    block(d, 64, y + 8, "所以：分端数字永远不能相加——这不是四舍五入的差，是两套计数规则。",
          24, 952, VERM, mono=False, step=34)

    y = 800
    mix(d, 64, y - 34, "③ 同页唯一可做的一道除法（我算的）", 25, INK, mono=False)
    d.rectangle([x0, y, X(3.35), y + bh], fill=TRACK)
    d.rectangle([x0, y, X(3.04), y + bh], fill=VERM)
    mix(d, x0 + 14, y + 18, "红果 3.04", 23, PAPER)
    mix(d, X(3.35) + 16, y + 18, "3.04 ÷ 3.35 = 90.7%", 25, VERM)
    block(d, 64, y + 84, "独立 App 里其余全部平台加起来 3,100 万。前提：红果被计入「独立 APP」这一类；若它在机构分类里另立一栏，这个比不成立。",
          22, 952, DIM, mono=False, step=32)

    footer(d, 986, "来源：QuestMobile 官方报告页《2026 短剧行业洞察报告》（2026-04-08）")
    return im, "007_图3_分端不可相加_1080.png"


# ── 图 4：三件套 + 钱的四类身份 ─────────────────────────────
def chart4():
    H = 1280
    im, d = canvas(H)
    header(d, "引用一个数之前，先补齐这三件套",
           "机构 + 口径 + 时点，缺一样就只做定性引用；钱那套病一模一样")

    chips = [("机构", "谁发布的：总局／QuestMobile／CSM／DataEye／自媒体", BLUE),
             ("口径", "量的是什么：月活？渗透率？子集？播出还是上线？", VERM),
             ("时点", "量到哪个月：2024-12 与 2026-08 差 21 个月", MONEY)]
    bx_w = (W - 128 - 32) / 3
    for i, (t, sub, color) in enumerate(chips):
        x = 64 + i * (bx_w + 16)
        d.rectangle([x, 208, x + bx_w, 384], fill=BOX, outline=color, width=2)
        mix(d, x + 18, 226, "①②③"[i] + " " + t, 30, color)
        block(d, x + 18, 278, sub, 21, bx_w - 36, INK, step=32)

    d.rectangle([64, 412, W - 64, 552], fill=(250, 246, 238), outline=VERM, width=2)
    mix(d, 84, 428, "× 「短剧用户 7 亿多」——三件套全丢，读者无法判断它和另一个数能不能比", 24, INK, mono=False)
    mix(d, 84, 470, "○ 「QuestMobile 监测口径下，截至 2026 年 2 月短剧行业月活 7.18 亿」", 24, VERM, mono=False)
    mix(d, 84, 510, "　　　——机构、口径、时点齐了，这个数才能进句子、进对比", 23, DIM, mono=False)

    mix(d, 64, 592, "钱这套四个数，四种身份（谁都不是「市场规模」这一个意思）", 27, INK, mono=False)
    rows = [("破千亿", "2025 年市场规模", "总局发布会原句", "已发生", VERM),
            ("220 亿元", "AI 剧漫剧，1—5 月", "DataEye 报告·媒体引述", "子集＋5 个月", STEEL),
            ("1,500 / 4,000 亿", "2026 年／未来 5 年", "点众科技陈瑞卿发言", "预测，不是统计", MONEY),
            ("1,210 亿", "2026 上半年真人微短剧", "报道标题，正文没取到", "未取得一手", GREY)]
    y = 648
    for val, scope, who, tag, color in rows:
        d.rectangle([64, y, W - 64, y + 92], fill=BOX, outline=LINE, width=2)
        mix(d, 88, y + 28, val, 30, color)
        mix(d, 452, y + 16, "范围｜" + scope, 23, INK, mono=False)
        mix(d, 452, y + 52, "出处｜" + who, 22, DIM, mono=False)
        grade_chip(d, W - 64 - (mixw(d, tag, 21) + 26), y + 26, tag, color)
        y += 106

    mix(d, 64, y + 8, "写「微短剧市场已达 1,500 亿」＝把一句「或超过」的口头预测当成统计数。", 24, VERM, mono=False)

    footer(d, y + 56, "来源：国新办发布会 2026-09-17 · 人民日报中国城市报 2026-08-10 引 DataEye 报告\n"
                      "36氪报道标题（正文未取到，仅登记不参与计算）")
    return im, "007_图4_三件套与四类身份_1080.png"


if __name__ == "__main__":
    for fn in (chart1, chart2, chart3, chart4):
        im, name = fn()
        im.save(os.path.join(OUT, name))
        print(name, im.size)
