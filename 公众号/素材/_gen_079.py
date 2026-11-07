#!/usr/bin/env python3
"""079《上海微短剧经费至 11-18》配图与封面。纯本地 Pillow，零扣费。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def tiers_table():
    """【图 1：谁能报 / 上限 / 硬条件】"""
    im, d = page("谁能报 / 上限 / 硬条件", "上海 2026 微短剧专项经费 / 指南 2026-10-21", "01", 1180)

    d.rounded_rectangle((72, 236, 1008, 310), radius=10, fill=INK)
    put(d, 96, 250, "300 万是评审上限，不是报名保底", 24, "#f0c588", "bold", 986)
    put(d, 96, 284, "精品档（含 AI）须持上海市发行许可证或节目登记备案号", 17, "#bdb3a1", "body", 986)

    d.rounded_rectangle((72, 334, 1008, 378), radius=8, fill="#e8dfcf")
    put(d, 90, 346, "档位", 17, INK, "bold", 280)
    put(d, 300, 346, "评审上限", 17, INK, "bold", 500)
    put(d, 520, 346, "硬条件摘要", 17, INK, "bold", 990)

    rows = [
        ("精品含 AI", "最高 300 万", "沪发行许可证/备案号；平台首播", RUST),
        ("出口创作", "最高 50 万", "出口/出海相关创作扶持", TEAL),
        ("厂牌扶持", "最高 200 万", "入驻优质厂牌；产能等 3 项及以上", GOLD),
        ("品质东方·微剧场", "每部 1 万", "该栏目首播精品 AI；同单位≤3", GREY),
        ("数字/IP 库", "各≤50 万", "按指南对应材料与建设内容", GREY),
        ("复合型人才培训", "单课最高 20 万", "按参训规模分档；办学许可另核", GREY),
        ("五个一批", "5 万免申即享", "入选即可，不走常规申报", TEAL),
    ]
    y = 390
    for name, cap, cond, color in rows:
        d.rounded_rectangle((72, y, 1008, y + 70), radius=10, fill=WHITE)
        d.rectangle((72, y + 12, 80, y + 58), fill=color)
        put(d, 96, y + 12, name, 18, INK, "bold", 290)
        put(d, 300, y + 12, cap, 18, color, "bold", 510)
        put(d, 520, y + 12, cond, 16, DIM, "body", 990)
        y += 78

    put(d, 72, 950, "宣传上海城市形象者，精品档评审上限可再加 50%——仍须过评审。", 18, INK, "bold", 1008)
    put(d, 72, 986, "项目完成窗口：2025-10-16 至 2026-10-15；须在沪经营主体。", 17, DIM, "body", 1008)

    footer(d, 1030, [
        "来源：上海市文旅局《2026年度上海市微短剧发展专项经费项目申报指南》（2026-10-21）。",
        "额度均为「最高」评审上限，非保底；表内硬条件为本号按指南摘要，以原文为准。",
    ])
    return im


def checklist():
    """【图 2：先核主体与许可证，再填表】"""
    im, d = page("先核主体与许可证，再填表", "一人公司动作清单 / 线上至 11-18 · 纸质 11-19—20", "02", 1080)

    steps = [
        ("01", "核主体", "营业执照经营地在上海；经营范围覆盖微短剧相关", RUST),
        ("02", "核证", "广电制作经营许可证；精品档再核沪发行许可证/备案号", TEAL),
        ("03", "核日期", "项目落在 2025-10-16 至 2026-10-15", GOLD),
        ("04", "核档位", "精品/出口/厂牌对号入座；别一部剧顶互斥口径", GREY),
        ("05", "再填表", "先约审计与信用报告，再排线上与纸质递交", INK),
    ]
    y = 246
    for num, title, desc, color in steps:
        d.rounded_rectangle((72, y, 1008, y + 96), radius=12, fill=WHITE)
        d.rounded_rectangle((96, y + 22, 168, y + 74), radius=8, fill=color)
        put(d, 112, y + 34, num, 24, WHITE, "bold", 160)
        put(d, 196, y + 20, title, 24, INK, "bold", 980)
        put(d, 196, y + 56, desc, 17, DIM, "body", 980)
        y += 110

    d.rounded_rectangle((72, 810, 1008, 920), radius=12, fill=INK)
    put(d, 102, 828, "两个截止日分开倒排", 22, "#f0c588", "bold", 986)
    put(d, 102, 866, "11-18 前交齐线上；11-19—20 只做现场递交，不接受邮寄。", 18, "#bdb3a1", "body", 986)
    put(d, 102, 896, "线上过了不等于线下能补证。", 18, "#e8dfcf", "bold", 986)

    footer(d, 952, [
        "来源：上海市文旅局申报指南（2026-10-21）；动作清单为本号整理（C）。",
        "资格与受理口径以文旅局原文及现场答复为准；本文不代办申报。",
    ])
    return im


def cover_079():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, "一人短剧厂牌", 20, "#c9c0b0", "bold", 540)

    put(d, 36, 74, "上海 2026 微短剧专项经费", 18, GOLD, "bold", 540)
    put(d, 32, 108, "至 11-18", 56, "#f6efe2", "title", 540)
    put(d, 36, 184, "线上截止", 22, "#e07a5f", "bold", 540)
    put(d, 36, 222, "纸质 11-19—20 现场交", 20, "#e8dfcf", "bold", 540)
    put(d, 36, 268, "300 万是评审上限", 22, "#f0c588", "bold", 540)
    put(d, 36, 308, "不是报名保底", 20, "#bdb3a1", "body", 540)
    put(d, 36, 342, "须在沪经营 · 精品绑过审证号", 15, "#8f8576", "body", 540)

    d.line((560, 70, 560, 330), fill="#4a443b", width=2)

    put(d, 590, 74, "主要档位上限", 14, GOLD, "bold", 864)
    rows = [
        ("精品含 AI", "300 万"),
        ("厂牌", "200 万"),
        ("出口", "50 万"),
        ("五个一批", "5 万免申"),
    ]
    y = 110
    for label, val in rows:
        put(d, 590, y, label, 16, "#bdb3a1", "body", 740)
        put(d, 750, y, val, 18, "#f6efe2", "bold", 864)
        y += 48

    put(d, 590, 320, "完成窗 2025-10-16—2026-10-15", 13, "#8f8576", "body", 864)
    put(d, 590, 346, "指南 2026-10-21 发布", 13, "#8f8576", "body", 864)

    im.save(OUT / "079_封面.png")
    print("封面 079 OK", im.size)


if __name__ == "__main__":
    im = tiers_table()
    im.save(OUT / "079_图1_档位上限_1080.png")
    print("图1 OK", im.size)
    im = checklist()
    im.save(OUT / "079_图2_动作清单_1080.png")
    print("图2 OK", im.size)
    cover_079()
