#!/usr/bin/env python3
"""081《快手互动掘金》配图与封面。纯本地 Pillow，零扣费。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def guarantee_card():
    """【图 1：S/A+/A 保底与 80 分钟含分支】"""
    im, d = page("S / A+ / A 保底与 80 分钟", "磁力新剧·互动掘金 / 转述口径 / 报名至 12-31", "01", 1040)

    put(d, 72, 236, "永久非独前提下的评级保底（转述）", 20, DIM, "bold", 1008)

    cards = [
        (72, "S", "10 万", RUST, "评级保底上限"),
        (390, "A+", "5 万", GOLD, "评级保底"),
        (708, "A", "3 万", TEAL, "评级保底"),
    ]
    for cx, grade, amount, color, note in cards:
        d.rounded_rectangle((cx, 280, cx + 300, 460), radius=12, fill=WHITE)
        put(d, cx + 24, 298, grade, 22, color, "bold", cx + 280)
        put(d, cx + 24, 340, amount, 52, INK, "title", cx + 280)
        put(d, cx + 24, 416, note, 17, DIM, "body", cx + 280)

    d.rounded_rectangle((72, 492, 1008, 620), radius=12, fill=INK)
    put(d, 102, 512, "硬性形态：含全部分支总物理时长 ≥ 80 分钟", 22, "#f0c588", "bold", 986)
    put(d, 102, 552, "不是单线主线 80 分钟；非线性 + 剧情分支 / 角色切换 / 画面探索", 17, "#bdb3a1", "body", 986)
    put(d, 102, 584, "真人实拍与 AI 形象均可入；保底并非报名即得", 17, "#e8dfcf", "bold", 986)

    rows = [
        (72, "钱怎么谈", "从纯投流 IAA，切到「保底 + 分成」；S 档 10 万是验收后上限"),
        (72, "产能怎么改", "AIGC 可改造成 AI 形象互动片；分支验收细则须向直客核"),
        (72, "独家怎么留", "永久非独可留多渠道二次开发；要独家则保底与资源另谈"),
    ]
    y = 650
    for _, title, desc in rows:
        d.rounded_rectangle((72, y, 1008, y + 78), radius=10, fill=WHITE)
        put(d, 96, y + 14, title, 18, INK, "bold", 980)
        put(d, 96, y + 44, desc, 16, DIM, "body", 980)
        y += 88

    footer(d, 930, [
        "来源：大数跨境 2026-10-30、繁星指数双周报 2026-11-04（行业转述）；未见官网 PDF。",
        "数字与条款以销售协议与平台验收为准；≠ 2026-05 快手大会投资口径。",
    ])
    return im


def cover_081():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, "一人短剧厂牌", 20, "#c9c0b0", "bold", 540)

    put(d, 36, 74, "快手磁力新剧 · 互动掘金", 18, GOLD, "bold", 540)
    put(d, 32, 110, "保底", 28, "#e8dfcf", "bold", 540)
    put(d, 32, 148, "10 / 5 / 3 万", 44, "#f6efe2", "title", 540)
    put(d, 36, 214, "S / A+ / A · 永久非独", 20, "#e07a5f", "bold", 540)
    put(d, 36, 256, "含分支总时长 ≥ 80 分钟", 20, "#e8dfcf", "bold", 540)
    put(d, 36, 300, "报名至 12-31", 22, "#f0c588", "bold", 540)
    put(d, 36, 340, "未见官网 PDF，以协议验收为准", 14, "#8f8576", "body", 540)

    d.line((560, 70, 560, 330), fill="#4a443b", width=2)

    put(d, 590, 74, "评级保底", 14, GOLD, "bold", 864)
    tiers = [("S", "10 万"), ("A+", "5 万"), ("A", "3 万")]
    y = 110
    for g, v in tiers:
        put(d, 590, y, g, 22, "#bdb3a1", "bold", 680)
        put(d, 690, y, v, 24, "#f6efe2", "bold", 864)
        y += 52

    put(d, 590, 280, "AI 形象可入", 16, "#e8dfcf", "bold", 864)
    put(d, 590, 312, "线性竖屏须补分支", 16, "#e07a5f", "bold", 864)
    put(d, 590, 344, "行业转述口径", 13, "#8f8576", "body", 864)

    im.save(OUT / "081_封面.png")
    print("封面 081 OK", im.size)


if __name__ == "__main__":
    im = guarantee_card()
    im.save(OUT / "081_图1_保底与时长_1080.png")
    print("图1 OK", im.size)
    cover_081()
