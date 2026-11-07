#!/usr/bin/env python3
"""082《10月一类备案159部》配图与封面。纯本地 Pillow，零扣费。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def structure_card():
    """【图 1：10月一类备案结构与小团队对照】"""
    im, d = page("10月一类备案：159 部结构", "广电总局网络视听司 2026-10-30 公示 / 转载核对", "01", 1120)

    put(d, 72, 236, "总量回落正常：9月 224 → 10月 159（-65）", 20, DIM, "bold", 1008)

    cards = [
        (72, "传奇", "54 部", "33.96%", RUST),
        (390, "都市", "37 部", "23.27%", GOLD),
        (708, "司法", "15 部", "9.43% · 第三", TEAL),
    ]
    for cx, name, n, pct, color in cards:
        d.rounded_rectangle((cx, 280, cx + 300, 470), radius=12, fill=WHITE)
        put(d, cx + 24, 298, name, 22, color, "bold", cx + 280)
        put(d, cx + 24, 340, n, 44, INK, "title", cx + 280)
        put(d, cx + 24, 416, pct, 18, DIM, "bold", cx + 280)

    d.rounded_rectangle((72, 500, 1008, 620), radius=12, fill=INK)
    put(d, 102, 520, "对一人公司：司法/公安/革命 = 特殊题材一类路径", 22, "#f0c588", "bold", 986)
    put(d, 102, 560, "持证制作机构 → 备案公示 → 成片发行许可；别按三类平台自审赌", 17, "#e8dfcf", "bold", 986)

    rows = [
        ("主体分散", "159 部 / 134 家，均 1.19；厦门七奥最高 6 部"),
        ("司法占坑", "曲江影视一次报 5 部司法；有牌照机构在批量占坑"),
        ("续集拆号", "带季数 8 部；《司命》拆三部各占号，部数≠可播剧"),
        ("你的动作", "立项加「分类预判」列；碰特殊题材先核制作许可证"),
    ]
    y = 650
    for title, desc in rows:
        d.rounded_rectangle((72, y, 1008, y + 78), radius=10, fill=WHITE)
        put(d, 96, y + 14, title, 18, INK, "bold", 980)
        put(d, 96, y + 44, desc, 16, DIM, "body", 980)
        y += 88

    footer(d, 1000, [
        "来源：广电总局网络视听节目管理司 2026-10-30 公示（万众编剧网转载 11-02）；",
        "9月 224 /《司命》等见澎湃号·湃客 11-04。未见总局官网同页原文，不标原创。",
    ])
    return im


def cover_082():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, "一人短剧厂牌", 20, "#c9c0b0", "bold", 540)

    put(d, 36, 74, "一类备案 · 10 月公示", 18, GOLD, "bold", 540)
    put(d, 32, 110, "159 部", 52, "#f6efe2", "title", 540)
    put(d, 36, 180, "比 9 月少 65 部", 22, "#e8dfcf", "bold", 540)
    put(d, 36, 230, "司法升至第三题材", 24, "#e07a5f", "bold", 540)
    put(d, 36, 280, "15 部 · 9.43%", 22, "#f0c588", "bold", 540)
    put(d, 36, 330, "特殊题材须一类路径", 16, "#8f8576", "body", 540)

    d.line((560, 70, 560, 330), fill="#4a443b", width=2)

    put(d, 590, 74, "题材结构", 14, GOLD, "bold", 864)
    tiers = [("传奇", "54"), ("都市", "37"), ("司法", "15"), ("革命", "11")]
    y = 110
    for g, v in tiers:
        put(d, 590, y, g, 20, "#bdb3a1", "bold", 700)
        put(d, 740, y, v, 22, "#f6efe2", "bold", 864)
        y += 44

    put(d, 590, 310, "134 家 · 均 1.19", 16, "#e8dfcf", "bold", 864)
    put(d, 590, 342, "转载核对 · 不标原创", 13, "#8f8576", "body", 864)

    im.save(OUT / "082_封面.png")
    print("封面 082 OK", im.size)


if __name__ == "__main__":
    im = structure_card()
    im.save(OUT / "082_图1_结构对照_1080.png")
    print("图1 OK", im.size)
    cover_082()
