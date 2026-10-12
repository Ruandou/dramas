# -*- coding: utf-8 -*-
"""009《总局秋季点评会点名 12 部微短剧，我逐条查了哪 4 部是 AI 剧》正文数据图 3 张
纯本地 Pillow，零扣费。底层工具复用 _gen_charts_006/007（同一套纸底与字体）。
注：Menlo 无中文字形、Hiragino 无 ✗✓ 与 U+2212，特殊符号一律避开，否则出豆腐块。
本文件另加三个防溢出封装（hdr / foot / panel）：任何一行超出可读边界即 assert 失败，
高画布绘制后按内容真实高度裁切，避免文字被切或压到页脚。
"""
import os
from PIL import Image, ImageDraw
from _gen_charts_006 import (W, PAPER, INK, DIM, LINE, TRACK, BOX, VERM, VERM_L,
                             BLUE, BLUE_L, GREY, SONG, HIRA, MONO, f, mix, mixw,
                             canvas, header, footer, grade_chip, runs, is_ascii)
from _gen_charts_007 import wrap, block

OUT = os.path.dirname(os.path.abspath(__file__))
MONEY = (110, 102, 90)
TEAL = (44, 96, 96)
EDGE = W - 64          # 右边界
MAXW = 952             # x=64 起的全宽可用宽度
TALL = 2400


def cb(d, x, y, text, size, fill, maxw=MAXW, mono=False, step=None):
    """自动折行绘制，逐行断言不超界。"""
    for ln in wrap(text, size, maxw, d, mono):
        assert x + mixw(d, ln, size, mono) <= EDGE, ("overflow", text[:18], ln)
    return block(d, x, y, text, size, maxw, fill, mono=mono, step=step)


def hdr(d, title, kicker):
    assert 98 + mixw(d, title, 42, mono=False) <= EDGE, ("title", title)
    assert 98 + mixw(d, kicker, 25, mono=False) <= EDGE, ("kicker", kicker)
    header(d, title, kicker)


def tx(d, x, y, text, size, fill, mono=False):
    assert x + mixw(d, text, size, mono=mono) <= EDGE, ("line", text)
    return mix(d, x, y, text, size, fill, mono=mono)


def foot(d, y, lines):
    for ln in lines:
        assert 64 + mixw(d, ln, 21, mono=False) <= EDGE, ("footer", ln)
    footer(d, y, "\n".join(lines))
    return y + 16 + len(lines) * 32 + 24


def panel(d, y, items, x=64, pad=18, inner=20, gap=6, outline=INK, bg=(250, 246, 238)):
    """按内容自动算高度的信息框。items: [(text, size, fill, step), ...]"""
    ix = x + inner
    iw = (EDGE - x) - inner * 2
    hs = []
    for text, size, fill, step in items:
        n = len(wrap(text, size, iw, d, False))
        hs.append(n * step)
    total = sum(hs) + gap * (len(items) - 1) + pad * 2
    d.rectangle([x, y, EDGE, y + total], fill=bg, outline=outline, width=2)
    yy = y + pad
    for (text, size, fill, step), h in zip(items, hs):
        cb(d, ix, yy, text, size, fill, maxw=iw, step=step)
        yy += h + gap
    return y + total


# ── 图 1：两个「1 次」，一个在义务侧、一个在评价侧 ──────────
def chart1():
    im, d = canvas(TALL)
    hdr(d, "两份文件，各出现 1 次「AI」",
        "点评会通稿 390 字（评价）· 16 号令 6,209 字（义务）")

    tx(d, 64, 190, "《2026精品微短剧秋季点评会在京举行》通稿，官网 2026-09-30 21:11", 25, INK)
    bx, bw = 300, 440
    y = 236
    for wd, n in [("AI", 1), ("真人", 1), ("横", 1), ("竖", 1), ("微短剧", 5)]:
        tx(d, 64, y + 4, wd, 27, INK)
        d.rectangle([bx, y + 8, bx + bw, y + 30], fill=TRACK)
        d.rectangle([bx, y + 8, bx + bw * n / 5.0, y + 30], fill=BLUE)
        tx(d, bx + bw + 16, y + 2, "%d 次" % n, 26, INK, mono=True)
        y += 48

    d.line([(64, y + 12), (EDGE, y + 12)], fill=LINE, width=2)
    y += 38
    tx(d, 64, y, "四个词各 1 次，全在同一句里：", 24, DIM)
    y = cb(d, 64, y + 38,
           "「本季度精品微短剧代表作品题材多样、各有特色、辨识度高，充分证明了微短剧容得下"
           "“横”与“竖”、“长”与“短”、“真人”与“AI”。」", 25, VERM, step=36)

    y += 26
    tx(d, 64, y, "《微短剧发展管理办法》全文，第一条至第五十四条，2026-09-01 施行", 25, INK)
    y += 44
    for wd, n in [("AI", 0), ("人工智能", 1), ("真人", 0), ("漫剧", 0), ("横", 0), ("竖", 0)]:
        tx(d, 64, y + 4, wd, 27, INK)
        d.rectangle([bx, y + 8, bx + bw, y + 30], fill=TRACK)
        if n:
            d.rectangle([bx, y + 8, bx + bw / 5.0, y + 30], fill=VERM)
        tx(d, bx + bw + 16, y + 2, "%d 次" % n, 26, VERM if n == 0 else INK, mono=True)
        if n == 1:
            tx(d, bx + bw + 96, y + 6, "→ 第三十四条", 24, VERM)
        y += 48

    y += 16
    y = panel(d, y, [
        ("全文 6,209 字里唯一一句关于 AI 的话是一条义务：使用人工智能技术生成、制作的微短剧，"
         "制作机构和播出单位应当遵守国家有关规定，并依据有关规定在每集明显位置添加提示标识。", 23, INK, 32),
        ("规章把 AI 微短剧当一条标识义务，通稿把 AI 微短剧当一句成绩措辞。", 24, VERM, 34),
    ])

    y = foot(d, y + 10, [
        "来源：广电总局官网 2026-09-30 工作动态通稿页 ＋ art_113_73785（16 号令全文）",
        "口径：剥 script/style 与全部标签、去空白，按起止句截取后逐词计数，导航区不计入",
    ])
    return im.crop((0, 0, W, y)), "009_图1_两个一次_义务与措辞_1080.png"


# ── 图 2：12 部逐条核查的落点 ────────────────────────────────
def chart2():
    im, d = canvas(TALL)
    hdr(d, "通稿点名的 12 部，我逐条查了",
        "公开报道口径 · 查到平台 9 部、查不到 3 部 · 官方未逐部标注")

    cards = [("12 部", "通稿点名", BLUE), ("4 部", "被媒体写成 AI", VERM),
             ("9 部", "查到上线平台", TEAL), ("1 部", "明确写到竖屏", MONEY)]
    cw = (W - 128 - 36) / 4
    for i, (n, sub, color) in enumerate(cards):
        x = 64 + i * (cw + 12)
        d.rectangle([x, 190, x + cw, 300], fill=color)
        tx(d, x + 16, 204, n, 34, PAPER, mono=True)
        block(d, x + 16, 252, sub, 18, cw - 30, (238, 232, 222), mono=False, step=26)

    rows = [
        ("一见·南侨", "爱奇艺上线（福建广电局 05-18）", "无 AI 报道", BLUE),
        ("重案六组:消失的警号", "北京／江苏卫视＋爱奇艺（新华网 09-09）", "无 AI 报道", BLUE),
        ("大唐少年天行传", "腾讯视频 07-24", "无 AI 报道", BLUE),
        ("无名者之光", "红果、抖音 07-23", "无 AI 报道", BLUE),
        ("我的女儿你要向前走", "平台与档期查不到", "无 AI 报道", GREY),
        ("爱在风起燕舞时", "红果、抖音（新浪财经 07-27）", "无 AI 报道", BLUE),
        ("莫欺少女穷", "红果「千部计划」（北京日报 09-15）", "无 AI 报道", BLUE),
        ("雪落无声", "平台查不到；导演自述竖屏", "唯一「竖屏」表述", MONEY),
        ("咕噜比事务所", "湖南卫视＋芒果TV 08-10", "芒果TV AIGC 中心", VERM),
        ("急诊科:开局看见疾病词条", "官方定档只在第三方，不采用", "新华网列为 AI 剧", VERM),
        ("桃花潭记", "央视频、安徽卫视黄金档 08 月", "全 AI 流程", VERM),
        ("北派笔记", "腾讯视频 07 月", "平台称 AI 精品短剧", VERM),
    ]
    y = 324
    for name, plat, ai, color in rows:
        hot = color == VERM
        d.rectangle([64, y, EDGE, y + 74], fill=(250, 240, 236) if hot else BOX,
                    outline=VERM if hot else LINE, width=2)
        d.rectangle([64, y, 72, y + 74], fill=color)
        tx(d, 92, y + 8, "《" + name + "》", 24, INK)
        assert 92 + mixw(d, plat, 20, mono=False) <= EDGE - 260, plat
        tx(d, 92, y + 42, plat, 20, DIM)
        w = mixw(d, ai, 20, mono=False) + 26
        d.rectangle([EDGE - w, y + 22, EDGE, y + 54], fill=color)
        tx(d, EDGE - w + 13, y + 28, ai, 20, PAPER)
        y += 82

    y += 12
    y = panel(d, y, [
        ("一条弃用记录：有稿称《一见·南侨》「腾讯视频首周热度 17673」，我丢了它。"
         "一是与福建广电局的「爱奇艺」口径矛盾；二是同一串 17673 也出现在讲《北派笔记》的稿子里。", 23, INK, 32),
        ("同一个数字挂在两部剧上，通常就是复制粘贴。这种串宁可整条丢掉，也别为凑满 12 行硬写。", 23, VERM, 32),
    ], outline=VERM)

    y = foot(d, y + 10, [
        "来源：12 部片名逐条对应公开报道（福建广电局、新华网、中国日报、北京日报、南方＋等）",
        "分档：右侧标注属「媒体报道归纳」（B 级），不是官方逐部标注；「查不到」＝我未检索到",
    ])
    return im.crop((0, 0, W, y)), "009_图2_十二部逐条核查_1080.png"


# ── 图 3：四句官方话各站在哪一层 ─────────────────────────────
def chart3():
    im, d = canvas(TALL)
    hdr(d, "四句官方话，不是一条线", "义务／统计／要求／措辞 · 没有一处给出可统计定义")

    layers = [
        ("义务", "16 号令第三十四条（2026-09-01 施行）", "每集明显位置添加提示标识",
         "全文 6,209 字：「AI」0 次、「人工智能」1 次", VERM),
        ("统计", "广电办发〔2026〕245 号 附件 1 报名表", "只问「是否为 AI 作品」",
         "正文 1,566 字：「AI」0 次；不问环节与占比", MONEY),
        ("要求", "广电办发〔2026〕244 号 正文", "须按《标识办法》标注",
         "正文「人工智能」2 次；报名表没有这一栏", BLUE),
        ("措辞", "2026-09-30 秋季点评会通稿", "「容得下“真人”与“AI”」",
         "390 字里 1 次；无逐部标注、无名单口径", TEAL),
    ]
    y = 196
    for tag, src, line, note, color in layers:
        d.rectangle([64, y, EDGE, y + 190], fill=BOX, outline=LINE, width=2)
        d.rectangle([64, y, 74, y + 190], fill=color)
        assert 98 + mixw(d, tag, 32, mono=False) + 20 + mixw(d, src, 25, mono=False) <= EDGE, src
        tw = mix(d, 98, y + 18, tag, 32, color, mono=False)
        mix(d, tw + 20, y + 24, src, 25, INK, mono=False)
        tx(d, 98, y + 82, line, 28, INK)
        block(d, 98, y + 134, note, 22, MAXW - 40, DIM, mono=False, step=30)
        y += 206

    y = panel(d, y + 6, [
        ("读法：规章已到「逐集加标识」的颗粒度，申报表格里只是「是或不是」一栏，通稿里是一句成绩。"
         "三份纸都没有回答「哪几个环节用了 AI、AI 占比多少」。", 24, INK, 34),
        ("所以「官方已认定 AI 微短剧」和「官方不管 AI 内容」这两种写法，都超出了这几份文件能给的东西。",
         24, VERM, 34),
    ])

    y = foot(d, y + 10, [
        "来源：广电总局官网 16 号令全文页、09-30 两条通知正文及附件 1、09-30 工作动态通稿页",
        "字数与词频为 2026-10-12 我抓取官网页面后自行计数",
    ])
    return im.crop((0, 0, W, y)), "009_图3_四句官方话四层_1080.png"


if __name__ == "__main__":
    for fn in (chart1, chart2, chart3):
        im, name = fn()
        im.save(os.path.join(OUT, name))
        print(name, im.size)
