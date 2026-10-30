#!/usr/bin/env python3
"""053《没有抵押物，一人短剧公司拿到 30 万贷款》配图与封面。纯本地 Pillow。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def center(d, cx, y, text, size, color, kind='bold', pad=2):
    w = d.textlength(text, font=font(size, kind))
    put(d, cx - w / 2, y, text, size, color, kind, cx + w / 2 + pad)


def timeline():
    im, d = page('钱先出去，交付后 40—60 天才回来', '一人厂牌的现金流 / 从开工到回款', '01', 960)

    d.rounded_rectangle((96, 300, 984, 470), radius=14, fill='#e9e0d1')
    y = 400
    d.line((120, y, 960, y), fill=INK, width=3)
    nodes = [
        (210, '开工', RUST, '算力 / 人力 / IP 先付'),
        (540, '交付', GOLD, '验收 / 上线'),
        (870, '回款', TEAL, '交付后 40—60 天'),
    ]
    for x, label, color, note in nodes:
        d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=color)
        center(d, x, y - 70, label, 28, color, 'bold')
        center(d, x, y + 28, note, 20, INK, 'body')

    put(d, 72, 236, '缺口：制作期 + 40—60 天', 24, INK, 'bold', 600)

    put(d, 72, 528, '这段缺口，就是一人厂牌最容易被拖住的地方。', 30, INK, 'title', 1008)
    paragraph(d, 72, 590,
              '开工时算力、人力、IP 先付；交付后，再等 40—60 天到账。贷款能做的，是接住这段时间差，不改变项目赚不赚钱。',
              936, 24, INK, 40)

    d.rounded_rectangle((72, 700, 1008, 792), radius=12, fill=INK)
    put(d, 102, 716, '先算缺口，再谈额度。', 26, '#f0c588', 'bold', 986)
    put(d, 102, 758, '30 万是贷款，不是收入；它解决时间，不解决亏损。', 19, '#bdb3a1', 'body', 986)

    footer(d, 840, [
        '来源：每经 10-28（回款 40—60 天）；中经 10-25（上海银行案例）。',
        '时间轴为本号示意，制作期按各自排期，不是行业统一值。',
    ])
    return im


def loans():
    im, d = base.page('三种贷款，三种「抵押物」', '2026-10 / 公开报道个案', '02', 1120)

    cards = [
        (250, '上海银行静安支行', '300 万', '创业担保贷',
         '看：上下游合同、应收应付、平台结算',
         '主体：闹海 AI（公司）', RUST),
        (470, '稠州银行', 'Token 贷', '按词元消耗授信（额度未披露）',
         '看：在手订单对应的 Token 消耗',
         '主体：湖州 TikTok 出海短剧企业', TEAL),
        (690, '禾城农商银行', '30 万', 'OPC 信用贷（2026-09）',
         '看：订单、交付、回款、算力支出',
         '主体：嘉兴 AI 短剧一人公司', GOLD),
    ]
    for y, bank, amount, product, detail, subject, color in cards:
        d.rounded_rectangle((72, y, 1008, y + 190), radius=12, fill=WHITE)
        put(d, 96, y + 18, bank, 20, DIM, 'bold', 420)
        put(d, 92, y + 50, amount, 44, color, 'title', 420)
        put(d, 96, y + 120, product, 18, INK, 'bold', 424)
        d.line((440, y + 24, 440, y + 166), fill=LINE, width=2)
        put(d, 470, y + 24, '看什么', 18, DIM, 'bold', 990)
        put(d, 470, y + 56, detail, 19, INK, 'body', 992)
        put(d, 470, y + 100, subject, 19, INK, 'body', 992)

    d.rounded_rectangle((72, 912, 1008, 1004), radius=12, fill=INK)
    put(d, 102, 928, '300 万是公司额度，30 万才是一人公司的参照。', 24, '#f0c588', 'bold', 986)
    put(d, 102, 968, '额度、利率、门槛以银行审批为准，个案不代表普遍可得。', 18, '#bdb3a1', 'body', 986)

    footer(d, 1032, [
        '来源：《中国经营报》10-25；《每日经济新闻》10-28。',
        '三笔均为公开报道个案，不是产品报价；稠州银行贷款额度未披露。',
    ])
    return im


def materials():
    im, d = page('去银行前，先备四样', '银行看的是还款来源，不是「AI」两个字', '03', 1040)

    cards = [
        (72, 250, '01', '合同 / 订单', ['金额、交付内容、结算方式'], RUST),
        (552, 250, '02', '回款流水', ['实际到账，不是后台预估'], GOLD),
        (72, 490, '03', 'Token / 算力账单', ['支出能对应到具体项目'], TEAL),
        (552, 490, '04', '交付验收记录', ['按时交付、复购、退单'], GREY),
    ]
    for x, y, num, title, lines, color in cards:
        d.rounded_rectangle((x, y, x + 456, y + 200), radius=12, fill=WHITE)
        put(d, x + 24, y + 18, num, 20, color, 'number', x + 60)
        put(d, x + 24, y + 52, title, 27, INK, 'bold', x + 440)
        for i, line in enumerate(lines):
            put(d, x + 24, y + 112 + i * 38, line, 19, DIM, 'body', x + 440)

    d.rounded_rectangle((72, 730, 1008, 850), radius=12, fill=INK)
    paragraph(d, 102, 748,
              '最容易被忽略的是第 2 样：银行要「已经到账」，不是「预计分账」。',
              900, 24, '#f0c588', 38, 'bold')
    put(d, 102, 804, '没有回款流水，信用贷只能给小额度。', 19, '#bdb3a1', 'body', 986)

    put(d, 72, 884, '四样攒够 3—6 个月，再谈额度。', 26, INK, 'bold', 1008)

    footer(d, 930, [
        '来源：中经 10-25（上海银行）；每经 10-28（稠州银行 Token 贷）。',
        '「四样材料」「3—6 个月」为本号建议，不是银行统一要求。',
    ])
    return im


def cover():
    base.TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, '#bdb3a1', right=440)
    put(d, 33, 58, '钱与账期 · 2026-10-30', 18, '#f0c588', 'bold', 460)
    put(d, 28, 92, '30 万', 82, '#efe6d6', 'title', 460)
    put(d, 34, 194, '一人公司，没有抵押物', 22, '#bdb3a1', 'bold', 470)
    put(d, 34, 236, '银行看订单，不看房子', 24, '#e0705a', 'bold', 470)
    put(d, 34, 288, '回款 40—60 天', 18, '#8f8576', 'body', 470)

    d.line((490, 62, 490, 324), fill='#4a443c', width=1)
    put(d, 520, 66, '三笔贷款', 20, '#f0c588', 'bold', 880)
    rows = [
        ('上海银行', '300 万', '看合同与应收', RUST),
        ('稠州银行', 'Token 贷', '看在手订单', TEAL),
        ('禾城农商行', '30 万', '看订单与交付', GOLD),
    ]
    y = 120
    for name, val, note, color in rows:
        put(d, 520, y, name, 17, '#bdb3a1', 'body', 700)
        put(d, 700, y - 2, val, 20, color, 'bold', 880)
        put(d, 520, y + 26, note, 15, '#8f8576', 'body', 880)
        y += 60
    put(d, 520, 306, '300 万是公司额度，30 万才是一人参照', 15, '#efe6d6', 'body', 880)
    return im


def main():
    for maker, name in [(timeline, '053_图1_账期_1080.png'),
                        (loans, '053_图2_三种贷款_1080.png'),
                        (materials, '053_图3_四样材料_1080.png')]:
        im = maker()
        base.validate_glyphs()
        base.save_png(im, OUT / name)
    im = cover()
    base.validate_glyphs()
    base.save_png(im, OUT / '封面_053_30万_900x383.png')
    print('done')


if __name__ == '__main__':
    main()
