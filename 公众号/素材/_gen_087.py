#!/usr/bin/env python3
"""087《广东 39 个微短剧项目公示：个人报不了》配图与封面。纯本地 Pillow，零扣费。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def project_split():
    im, d = page('39 个项目，分到五个专项', '广东 2026 年第一批拟扶持名单 / 公示 11-05—11-11', '01', 1020)

    put(d, 72, 232, '39', 96, RUST, 'title', 320)
    put(d, 240, 262, '个', 34, INK, 'bold', 340)
    put(d, 300, 262, '微短剧 35', 26, INK, 'bold', 520)
    put(d, 300, 300, '网络动画片 4', 26, INK, 'bold', 520)
    put(d, 610, 250, '名单未披露金额', 18, DIM, 'body', 1008)

    rows = [
        ('微短剧 剧本孵化', 15, RUST),
        ('微短剧 拍摄扶持', 11, GOLD),
        ('微短剧 播出激励', 5, TEAL),
        ('微短剧 推优奖励', 3, GREY),
        ('微短剧 配套扶持', 1, GREY),
        ('网络动画片', 4, TEAL),
    ]
    y = 392
    maxv = 15
    for label, value, color in rows:
        put(d, 72, y + 6, label, 18, INK, 'bold', 360)
        w = int((value / maxv) * 520)
        d.rounded_rectangle((380, y + 8, 380 + max(w, 8), y + 40), radius=6, fill=color)
        put(d, 920, y + 4, str(value), 22, INK, 'bold', 1000)
        y += 74

    d.rounded_rectangle((72, 850, 1008, 910), radius=10, fill=INK)
    put(d, 100, 866, '35 + 4 = 39；微短剧 35 个里，剧本孵化占 15 个。', 19, '#f0c588', 'bold', 986)

    footer(d, 930, [
        '来源：广东省广播电视局 2026-11-05 公示及拟扶持项目名单 PDF。',
        '分项为本号按名单逐条计数；同一项目跨两个专项只各计一次，不推断金额叠加。',
    ])
    return im


def gates():
    im, d = page('四道门，缺一不可', '申报主体 / 阶段 / 时间 / 验收', '02', 1020)

    gates = [
        ('01', '主体', '广东省内注册 + 持《广播电视节目制作经营许可证》', TEAL),
        ('02', '备案', '申报主体须为项目在总局系统的备案立项机构', GOLD),
        ('03', '时间', '2026 两批 4-10、8-10 已截止；下一批未公布', RUST),
        ('04', '验收', '剧本 9 个月交全本；拍摄 12 个月交片并申请发行许可', INK),
    ]
    y = 240
    for num, label, desc, color in gates:
        d.rounded_rectangle((72, y, 1008, y + 120), radius=10, fill=WHITE)
        put(d, 100, y + 22, num, 34, color if color != INK else INK, 'title', 180)
        put(d, 190, y + 20, label, 24, INK, 'bold', 300)
        put(d, 190, y + 62, desc, 16, DIM, 'body', 980)
        y += 136

    d.rounded_rectangle((72, 790, 1008, 900), radius=12, fill=INK)
    put(d, 100, 808, '拿钱后不得把剧本版权、备案立项转给广东省外机构。', 21, '#f0c588', 'bold', 986)
    put(d, 100, 850, '省外团队要在申报前把合作结构设好，不能先拿钱再转包。', 16, '#bdb3a1', 'body', 986)

    footer(d, 922, [
        '来源：粤广电网〔2026〕13 号申报通知（2026-03-13）；广东省广电局 2026-11-05 公示。',
        '四道门为本号按通知要求归纳，不是官方表述。',
    ])
    return im


def cover_087():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 520)

    put(d, 36, 76, '省级扶持 · 公示', 16, GOLD, 'bold', 520)
    put(d, 32, 104, '广东 39 个项目', 40, '#f6efe2', 'title', 520)
    put(d, 32, 154, '个人报不了', 44, '#e07a5f', 'title', 520)
    put(d, 36, 220, '门槛：广东注册 + 制作许可证', 16, '#e8dfcf', 'bold', 540)
    put(d, 36, 252, '且必须是项目备案立项机构', 15, '#bdb3a1', 'body', 540)
    put(d, 36, 288, '两批申报 4-10 / 8-10 已截止', 14, '#bdb3a1', 'body', 540)
    put(d, 36, 330, '名单没有金额', 13, '#8f8576', 'body', 540)

    d.line((560, 70, 560, 330), fill='#4a443b', width=2)

    put(d, 590, 76, '39 个里', 14, GOLD, 'bold', 864)
    put(d, 590, 100, '微短剧 35', 28, '#f6efe2', 'bold', 864)
    put(d, 590, 144, '网络动画 4', 22, '#bdb3a1', 'bold', 864)

    bars = [('剧本孵化', 15), ('拍摄扶持', 11), ('播出激励', 5), ('推优奖励', 3), ('配套扶持', 1)]
    y = 190
    for label, v in bars:
        put(d, 590, y, label, 13, '#e8dfcf', 'body', 700)
        d.rectangle((700, y + 2, 700 + int(v / 15 * 130), y + 11), fill=RUST if label == '剧本孵化' else GREY)
        put(d, 842, y - 2, str(v), 13, '#bdb3a1', 'body', 870)
        y += 26

    put(d, 590, 330, '广州趣丸 AI 项目跨两项', 12, '#8f8576', 'body', 864)

    im.save(OUT / '封面_087_广东扶持_900x383.png')
    print('封面 087 OK', im.size)


if __name__ == '__main__':
    im = project_split()
    im.save(OUT / '087_图1_结构_1080.png')
    print('图1 OK', im.size)
    im = gates()
    im.save(OUT / '087_图2_四门_1080.png')
    print('图2 OK', im.size)
    cover_087()
