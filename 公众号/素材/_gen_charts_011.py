# -*- coding: utf-8 -*-
"""011《「81 秒」：完播率第一次有了官方公式》正文数据图 3 张
纯本地 Pillow，零扣费。底层工具复用 _gen_charts_006/007/009（同一套纸底与字体）。
注：Menlo 无中文字形，任何含 CJK 的行一律走 mix()/wrap()，禁止直接用 MONO 画整行，
否则出豆腐块。≤ ≥ 归 CJK 段走 Hiragino，× 归 ASCII 段走 Menlo，均已渲染验证。
本文件另加带打印的封装 line()/para()/note_box()/src_foot()：每条文案都打印
mixw() <= 980 的 OK/OVER 校验；末尾 cjk_guard() 再断言含 CJK 的行段不得用 MONO。
"""
import os
from PIL import Image, ImageDraw
from _gen_charts_006 import (W, PAPER, INK, DIM, LINE, TRACK, BOX, VERM, VERM_L,
                             BLUE, BLUE_L, GREY, SONG, HIRA, MONO, f, mix, mixw,
                             canvas, header, footer, grade_chip, runs, is_ascii)
from _gen_charts_007 import wrap, block
from _gen_charts_009 import cb, tx, hdr, foot, panel, EDGE, MAXW, MONEY, TEAL, TALL

OUT = os.path.dirname(os.path.abspath(__file__))
BODY = 980  # 正文图单行文案宽度上限（任务规定）

LINES = []  # (text, size, mono) 全量登记，供 cjk_guard 断言


def _chk(text, size, mono, w, maxw=BODY):
    tag = "OK  " if w <= maxw else "OVER"
    print("   %s %4dpx  %s" % (tag, round(w), text))
    assert w <= maxw, (text, w)


def line(d, x, y, text, size, fill, mono=True, maxw=BODY):
    """单行混排绘制：打印宽度校验 + 边界断言 + 登记。"""
    w = mixw(d, text, size, mono=mono)
    _chk(text, size, mono, w, maxw)
    assert x + w <= EDGE, ("overflow", text)
    LINES.append((text, size, mono))
    return mix(d, x, y, text, size, fill, mono=mono)


def line_right(d, x_right, y, text, size, fill, mono=True):
    w = mixw(d, text, size, mono=mono)
    _chk(text, size, mono, w)
    assert x_right - w >= 64 and x_right <= EDGE, ("right-align", text)
    LINES.append((text, size, mono))
    mix(d, x_right - w, y, text, size, fill, mono=mono)
    return x_right - w


def para(d, x, y, text, size, fill, maxw=MAXW, mono=False, step=None):
    """自动折行绘制，逐折行打印宽度校验。"""
    for ln in wrap(text, size, maxw, d, mono):
        w = mixw(d, ln, size, mono)
        _chk(ln, size, mono, w)
        assert x + w <= EDGE, ("overflow", ln)
    LINES.append((text, size, mono))
    return block(d, x, y, text, size, maxw, fill, mono=mono, step=step)


def note_box(d, y, items, outline=INK, bg=(250, 246, 238), inner=20, pad=18, gap=8):
    """按内容自动算高度的信息框（同 009 panel，但每条折行都打印校验）。"""
    ix = 64 + inner
    iw = (EDGE - 64) - inner * 2
    hs = []
    for text, size, fill, step in items:
        n = len(wrap(text, size, iw, d, False))
        hs.append(n * step)
    total = sum(hs) + gap * (len(items) - 1) + pad * 2
    d.rectangle([64, y, EDGE, y + total], fill=bg, outline=outline, width=2)
    yy = y + pad
    for (text, size, fill, step), h in zip(items, hs):
        para(d, ix, yy, text, size, fill, maxw=iw, step=step)
        yy += h + gap
    return y + total


def src_foot(d, y, lines):
    for ln in lines:
        _chk(ln, 21, False, mixw(d, ln, 21, mono=False))
    LINES.extend((ln, 21, False) for ln in lines)
    return foot(d, y, lines)


def cjk_guard():
    """硬断言：任何含 CJK 的行，其 CJK 段所选字体不得为 MONO（Menlo 无中文字形）。"""
    bad = []
    for text, size, mono in LINES:
        for r in runs(text):
            font_choice = MONO if (mono and is_ascii(r)) else HIRA
            if (not is_ascii(r)) and font_choice == MONO:
                bad.append((text, r))
    assert not bad, bad
    n_cjk = sum(1 for t, _, _ in LINES if any(ord(c) >= 0x2100 for c in t))
    print("cjk_guard: 共登记 %d 条文案（其中 %d 条含 CJK，全部经 mix 分流，无一走 MONO）→ 通过"
          % (len(LINES), n_cjk))


def hdr_song(d, title, kicker):
    """同 009 hdr，但标题按实际绘制字体（Songti 42 Bold）量宽——含大量半角数字的
    标题用 Hiragino 量宽会虚高（009 的 hdr 断言因此误杀图 3 标题）。"""
    tw = d.textlength(title, font=f(SONG, 42, index=1))
    print("   %s %4dpx  %s" % ("OK  " if 98 + tw <= EDGE else "OVER", round(tw), title))
    assert 98 + tw <= EDGE, ("title", title)
    assert 98 + mixw(d, kicker, 25, mono=False) <= EDGE, ("kicker", kicker)
    LINES.append((kicker, 25, False))
    header(d, title, kicker)


# ── 图 1：完播门槛五档表 ────────────────────────────────────
def chart1():
    im, d = canvas(TALL)
    hdr(d, "「完播」的官方门槛：内容越长，要求越松",
        "摘自《广播电视收视大数据指标及计算方法》（报批稿）附录 A 表 A.1")

    y = 196
    d.rectangle([64, y, EDGE, y + 58], fill=INK)
    line(d, 92, y + 14, "内容时长 D_C", 25, PAPER)
    line(d, 500, y + 14, "视为完播的条件", 25, PAPER)
    y += 58
    rows = [
        ("D_C ≤ 5 min", "V_D ≥ D_C × 90%", True),
        ("5 min < D_C ≤ 10 min", "V_D ≥ D_C × 85% + 15 s", False),
        ("10 min < D_C ≤ 45 min", "V_D ≥ D_C × 80% + 45 s", False),
        ("45 min < D_C ≤ 120 min", "V_D ≥ D_C × 75% + 180 s", False),
        ("D_C > 120 min", "V_D ≥ D_C × 70% + 540 s", False),
    ]
    for dur, cond, hot in rows:
        h = 86 if hot else 74
        d.rectangle([64, y, EDGE, y + h], fill=(250, 240, 236) if hot else BOX,
                    outline=VERM if hot else LINE, width=3 if hot else 2)
        d.line([(468, y + 10), (468, y + h - 10)], fill=LINE, width=2)
        line(d, 92, y + (h - 31) / 2, dur, 25, INK if hot else DIM)
        line(d, 500, y + (h - 31) / 2, cond, 25, VERM if hot else DIM)
        if hot:
            chip = "短剧在这一档"
            cw = mixw(d, chip, 21, mono=False) + 26
            grade_chip(d, EDGE - cw - 22, y + (h - 40) / 2, chip, VERM)
            LINES.append((chip, 21, False))
        y += h + 10

    y += 8
    y = para(d, 64, y, "注：D_C 为内容时长，V_D 为收视时长；同一用户多次播放的时长全部计入。",
             21, DIM, MAXW)

    y += 18
    bh = 216
    d.rectangle([64, y, EDGE, y + bh], fill=(250, 246, 238), outline=VERM, width=3)
    d.rectangle([64, y, 76, y + bh], fill=VERM)
    line(d, 100, y + 22, "把第一档单独换算给短剧", 23, DIM)
    line(d, 100, y + 62, "90 秒的剧 → 看到 81 秒才算完播", 36, VERM)
    line(d, 100, y + 134, "81 秒 = 90 × 90%，本图作者计算", 22, INK)
    y += bh + 20

    y = src_foot(d, y, [
        "来源：《广播电视收视大数据指标及计算方法》（报批稿）附录 A 表 A.1（2026-10-13 公示）",
        "「81 秒」为按第一档公式对 90 秒内容的换算，非报批稿原文",
    ])
    return im.crop((0, 0, W, y)), "011_图1_完播门槛五档表_1080.png"


# ── 图 2：21 个指标分布 ─────────────────────────────────────
def chart2():
    im, d = canvas(TALL)
    hdr(d, "报批稿里一共有 21 个指标、21 条编号公式",
        "按第 6 章「指标分类」和第 7 章小节归组（本图作者按目录分组统计）")

    groups = [
        ("宏观统计", 3, BLUE),
        ("内容收视统计", 9, VERM),
        ("供需分析", 2, BLUE),
        ("用户分析", 3, BLUE),
        ("完播分析", 2, TEAL),
        ("广告分析", 2, BLUE),
    ]
    x0, unit, bh = 360, 60, 46
    y = 210
    line(d, 64, y - 34, "指标分组 · 条上数字为该组指标数", 24, INK)
    for name, n, color in groups:
        hot = color in (VERM, TEAL)
        line_right(d, 330, y + 8, name, 24, INK if hot else DIM)
        d.rectangle([x0, y, x0 + n * unit, y + bh], fill=color)
        line(d, x0 + n * unit + 14, y + 8, str(n), 28, color)
        y += bh + 20

    d.line([(64, y + 4), (EDGE, y + 4)], fill=LINE, width=2)
    y += 22
    line(d, 64, y, "合计 21 个指标、21 条编号公式（3 + 9 + 2 + 3 + 2 + 2 = 21）", 24, INK)
    y += 56

    y = note_box(d, y, [
        ("与短剧直接相关：收视时长 VD、平均收视时长 AvVD、忠实度 L、完播用户数 CVU、完播率 CR",
         22, INK, 32),
        ("附录 C：21 个指标里 6 个不适用于点播/回看（总收视率、收视率、收视份额、播出比重、用户集中度、毛评点）",
         22, VERM, 32),
    ], outline=INK)

    y = src_foot(d, y + 10, [
        "来源：《广播电视收视大数据指标及计算方法》（报批稿）第 6、7 章与附录 C",
        "分组计数为本图作者按目录归组统计，非报批稿原文图表",
    ])
    return im.crop((0, 0, W, y)), "011_图2_二十一个指标分布_1080.png"


# ── 图 3：十天异议窗口 ──────────────────────────────────────
def chart3():
    im, d = canvas(TALL)
    hdr_song(d, "公示期只有 10 天：10 月 13 日到 10 月 22 日",
             "来源：广电总局科技司 2026-10-13 09:00 公示通知原文")

    x0, x1, axis = 150, 930, 330
    line(d, (x0 + x1) / 2 - mixw(d, "共 10 天", 30) / 2, 246, "共 10 天", 30, INK)
    d.line([(x0, axis), (x1, axis)], fill=INK, width=3)
    d.rectangle([x0, axis - 26, x1, axis + 26], fill=VERM_L, outline=VERM, width=2)
    line(d, x0 + 20, axis - 15, "异议窗口", 25, VERM)
    for cx in (x0, x1):
        d.ellipse([cx - 11, axis - 11, cx + 11, axis + 11], fill=INK, outline=PAPER, width=2)
    line(d, 64, axis + 42, "10-13 09:00 公示开始", 22, INK)
    line_right(d, EDGE, axis + 42, "10-22 公示截止", 22, INK)

    y = axis + 108
    line(d, 64, y, "提异议必须带的四项（原文要求，逐字）", 25, INK)
    y += 48
    x = 64
    for chip in ("真实姓名", "工作单位", "联系方式", "明确提出异议的事实依据"):
        x = grade_chip(d, x, y, chip, BLUE) + 16
        LINES.append((chip, 21, False))
    assert x <= EDGE, "chips overflow"

    y += 74
    d.rectangle([64, y, EDGE, y + 128], fill=BOX, outline=LINE, width=2)
    line(d, 92, y + 22, "监督邮箱：kjsbzc@nrta.gov.cn", 24, INK)
    line(d, 92, y + 72, "监督电话：（010）86093490；传真：68016436", 24, INK)
    y += 152

    y = src_foot(d, y, [
        "来源：国家广播电视总局官网 · 科技司 2026-10-13 09:00 公示通知",
        "四项要求与监督邮箱、电话、传真均为公示通知原文内容",
    ])
    return im.crop((0, 0, W, y)), "011_图3_十天异议窗口_1080.png"


if __name__ == "__main__":
    for fn in (chart1, chart2, chart3):
        print(fn.__name__)
        im, name = fn()
        im.save(os.path.join(OUT, name))
        print(name, im.size)
    print()
    cjk_guard()
