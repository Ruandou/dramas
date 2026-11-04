#!/usr/bin/env python3
"""066《算力账单变信用凭证》/ 067《昆仑万维 2 万美元》配图与封面。纯本地 Pillow。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def bank_four():
    im, d = page('银行看四样，不看厂房', 'AI 短剧企业授信 / 中国证券报 2026-11-03 / 稠州银行 Token 贷 2026-09-23', '01', 1080)

    put(d, 72, 238, '四样材料，决定授信', 26, INK, 'bold', 1008)

    cards = [
        (72, 288, '01', '算力采购合同', '规模 · 单价 · 使用周期', '证明算力投入是真的', TEAL),
        (552, 288, '02', '在手订单', '真实性 · 未来现金流', '证明还款来源', GOLD),
        (72, 486, '03', '词元测算', '单项目 token 成本 · 预期收入', '算清一个项目要烧多少', TEAL),
        (552, 486, '04', '技术与生产', '持续交付 · 成长空间', '判断能不能一直做', GOLD),
    ]
    for cx, cy, num, title, line1, line2, color in cards:
        d.rounded_rectangle((cx, cy, cx + 456, cy + 168), radius=12, fill=WHITE)
        put(d, cx + 24, cy + 18, num, 24, color, 'number', cx + 100)
        put(d, cx + 74, cy + 16, title, 25, INK, 'bold', cx + 440)
        put(d, cx + 24, cy + 64, line1, 20, INK, 'body', cx + 440)
        put(d, cx + 24, cy + 106, line2, 18, DIM, 'body', cx + 440)

    put(d, 72, 694, '放款后，钱的去向是固定的', 22, DIM, 'bold', 1008)
    d.rounded_rectangle((72, 736, 1008, 806), radius=12, fill=INK)
    put(d, 100, 754, '四样对上  →  授信  →  贷款定向支付算力  →  锁定算力、批量交付', 22, '#f0c588', 'bold', 986)

    d.rounded_rectangle((72, 838, 1008, 938), radius=12, fill=WHITE)
    put(d, 100, 858, '算力账单是增信参考，不是抵押物。', 24, RUST, 'bold', 986)
    put(d, 100, 900, '银行不是凭一张账单放款，而是拿它测算项目投入产出。', 19, DIM, 'body', 986)

    footer(d, 958, [
        '来源：中国证券报（2026-11-03）；中国金融新闻网·稠州银行 Token 贷（2026-09-23）。',
        '四样材料为本号据上述报道整理；各地银行授信标准不同。',
    ])
    return im


def money_timeline():
    im, d = page('先付算力，再等回款', 'AI 漫剧算力成本 / 行业受访口径 / 2026-10-28', '02', 1020)

    cards = [
        (72, '一集 AI 漫剧', '17 元 → 80—100 元', '算力成本'),
        (552, '一分钟', '100 元 → 200—300 元', '算力成本'),
    ]
    for cx, title, value, note in cards:
        d.rounded_rectangle((cx, 238, cx + 456, 398), radius=12, fill=WHITE)
        put(d, cx + 24, 258, title, 21, DIM, 'bold', cx + 440)
        put(d, cx + 24, 296, value, 31, INK, 'bold', cx + 440)
        put(d, cx + 24, 348, note, 18, DIM, 'body', cx + 440)

    put(d, 72, 430, '以上为行业受访口径，不是银行报价，也不是平台结算价。', 19, DIM, 'body', 1008)

    put(d, 72, 486, '钱什么时候出去，什么时候回来', 24, INK, 'bold', 1008)
    stages = [
        ('01', '拿到剧本'),
        ('02', '先买算力'),
        ('03', '制作 1—2 个月'),
        ('04', '内容上架'),
        ('05', '回款 40—60 天'),
    ]
    x0, w, gap = 72, 170, 21
    for i, (num, label) in enumerate(stages):
        x = x0 + i * (w + gap)
        color = RUST if i in (1, 4) else TEAL
        d.rounded_rectangle((x, 532, x + w, 650), radius=10, fill=WHITE)
        put(d, x + 12, 548, num, 18, color, 'number', x + w - 8)
        put(d, x + 12, 584, label, 17, INK, 'bold', x + w - 8)
        if i < len(stages) - 1:
            ax = x + w + 3
            d.line((ax, 591, ax + gap - 6, 591), fill=GREY, width=2)
            d.polygon([(ax + gap - 8, 585), (ax + gap - 2, 591), (ax + gap - 8, 597)], fill=GREY)

    put(d, 72, 684, '算力先付、制作一到两个月、回款 40—60 天，三段叠在一起就是垫资缺口。', 20, INK, 'body', 1008)

    d.rounded_rectangle((72, 736, 1008, 852), radius=12, fill=INK)
    put(d, 100, 754, '80 分钟项目：算力 1.6 万—2.4 万元', 24, '#f0c588', 'bold', 986)
    put(d, 100, 796, '同时开三个项目，垫资约 5 万—7 万元（本号按 200—300 元/分钟复算，不含人力、IP、投流）。', 18, '#bdb3a1', 'body', 986)

    footer(d, 878, [
        '来源：每日经济新闻（10-28）；中国证券报（11-03）；中国金融新闻网（09-23）。',
        '算力单价与回款周期为行业受访口径；垫资测算为本号复算。',
    ])
    return im


def cost_compare():
    im, d = page('15—20 万美元 vs 2 万美元', '昆仑万维投资者关系活动 / 单部制作成本 / 2026-11-03', '01', 880)

    cards = [
        (72, '传统海外真人短剧', '15—20 万美元', '单部制作成本', RUST),
        (552, '同等体量 AI 短剧', '< 2 万美元', '公司口径', TEAL),
    ]
    for cx, title, value, note, color in cards:
        d.rounded_rectangle((cx, 244, cx + 456, 438), radius=12, fill=WHITE)
        put(d, cx + 24, 264, title, 21, DIM, 'bold', cx + 440)
        put(d, cx + 24, 306, value, 42, color, 'title', cx + 440)
        put(d, cx + 24, 386, note, 18, DIM, 'body', cx + 440)

    put(d, 72, 478, '按上限 20 万 ÷ 2 万 = 10 倍；按下限 15 万 ÷ 2 万 = 7.5 倍。', 21, INK, 'bold', 1008)

    d.rounded_rectangle((72, 540, 1008, 660), radius=12, fill=INK)
    put(d, 100, 558, '2 万美元是制作成本，不含投流。', 24, '#f0c588', 'bold', 986)
    put(d, 100, 602, '昆仑万维 Q3 销售费用 24.78 亿元，占当季毛利 93.09%。', 19, '#bdb3a1', 'body', 986)

    put(d, 72, 690, '两个数字都是公司自述，不是审计数据，也不是行业平均。', 19, DIM, 'body', 1008)

    footer(d, 730, [
        '来源：东方财富网、观点网、格隆汇、证券时报（2026-11-03）；国际金融报（2026-11-02）。',
        '倍数为本号按上述区间复算；制作成本不含投流、IP 授权与人力。',
    ])
    return im


def cover_066():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 860)

    put(d, 36, 78, 'AI 短剧融资 · 2026-11-03', 20, GOLD, 'bold', 620)
    put(d, 32, 114, '算力账单', 62, '#f6efe2', 'title', 620)
    put(d, 36, 196, '也能当信用凭证', 38, GOLD, 'bold', 620)
    put(d, 36, 258, '贷款先备四样：合同、订单、词元、技术', 21, '#bdb3a1', 'body', 620)
    put(d, 36, 312, '没有厂房，也能谈', 20, '#e07a5f', 'body', 620)

    d.line((650, 70, 650, 330), fill='#4a443b', width=2)
    items = ['算力采购合同', '在手订单', '词元测算', '技术与生产']
    for i, item in enumerate(items):
        yy = 92 + i * 62
        d.line((684, yy + 14, 700, yy + 30), fill=RUST, width=4)
        d.line((700, yy + 30, 718, yy + 2), fill=RUST, width=4)
        put(d, 710, yy, item, 22, '#f0e8d8', 'bold', 894)

    im.save(OUT / '封面_066_算力账单能贷款_900x383.png')
    print('封面 066 OK', im.size)


def cover_067():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 860)

    put(d, 36, 78, '昆仑万维 · 2026-11-03', 20, GOLD, 'bold', 620)
    put(d, 32, 114, '2 万美元', 64, '#f6efe2', 'title', 620)
    put(d, 36, 198, '一部 AI 短剧', 38, GOLD, 'bold', 620)
    put(d, 36, 260, '真人要 15—20 万美元', 22, '#bdb3a1', 'body', 620)
    put(d, 36, 312, '公司口径，不含投流', 20, '#e07a5f', 'body', 620)

    d.line((620, 70, 620, 330), fill='#4a443b', width=2)
    items = ['单部制作成本', '7.5—10 倍差', 'Q3 销售费用 24.78 亿', '占毛利 93.09%']
    for i, item in enumerate(items):
        yy = 92 + i * 62
        d.line((650, yy + 14, 666, yy + 30), fill=RUST, width=4)
        d.line((666, yy + 30, 684, yy + 2), fill=RUST, width=4)
        put(d, 690, yy, item, 19, '#f0e8d8', 'bold', 896)

    im.save(OUT / '封面_067_2万美元_900x383.png')
    print('封面 067 OK', im.size)


if __name__ == '__main__':
    im = bank_four()
    im.save(OUT / '066_图1_银行看四样_1080.png')
    print('图1 OK', im.size)
    im = money_timeline()
    im.save(OUT / '066_图2_先付算力_1080.png')
    print('图2 OK', im.size)
    im = cost_compare()
    im.save(OUT / '067_图1_成本对比_1080.png')
    print('图3 OK', im.size)
    cover_066()
    cover_067()
