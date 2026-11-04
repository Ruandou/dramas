#!/usr/bin/env python3
"""068《AI剧占出海短剧六成》配图与封面。纯本地 Pillow，零扣费。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def budget_dots():
    im, d = page('50 万元，买 1 次还是 15—20 次', 'AI 出海试错预算 / 六翼影视受访口径 / 2026-11-02', '01', 1040)

    put(d, 72, 238, '同样 50 万元，两种下注方式', 26, INK, 'bold', 1008)

    x0, x1 = 190, 980
    per = (x1 - x0) / 20
    for t in (0, 5, 10, 15, 20):
        x = x0 + t * per
        d.line((x, 300, x, 560), fill=LINE, width=1)
        put(d, x - 10, 578, str(t), 18, DIM, 'number', x + 40)

    # 真人：1 次
    put(d, 72, 316, '真人剧', 22, RUST, 'bold', 170)
    xr = x0 + 1 * per
    d.line((xr, 340, xr, 560), fill=RUST, width=3)
    d.ellipse((xr - 10, 330, xr + 10, 350), fill=RUST)
    put(d, xr + 22, 316, '1 次', 24, RUST, 'bold', 330)
    put(d, xr + 22, 356, '市场不买账就归零', 18, DIM, 'body', 470)

    # AI：15—20 次
    put(d, 72, 436, 'AI 短剧', 22, TEAL, 'bold', 170)
    xa0, xa1 = x0 + 15 * per, x0 + 20 * per
    d.line((xa0, 460, xa1, 460), fill=TEAL, width=3)
    for t in range(15, 21):
        x = x0 + t * per
        d.line((x, 460, x, 560), fill=TEAL, width=2)
        d.ellipse((x - 7, 453, x + 7, 467), fill=TEAL)
    put(d, xa0 - 8, 408, '15—20 次', 24, TEAL, 'bold', xa1 + 30)
    put(d, 72, 486, '十几次到二十次试错', 18, DIM, 'body', 300)

    put(d, 840, 600, '可试错次数', 18, DIM, 'body', 1000)

    d.rounded_rectangle((72, 654, 1008, 754), radius=12, fill=INK)
    put(d, 100, 672, '50 万 ÷ 15—20 次 = 2.5 万—3.3 万元 / 次', 27, '#f0c588', 'bold', 986)
    put(d, 100, 716, '这是单次试错预算，不含人力、IP、译制、投流（本号复算）', 18, '#bdb3a1', 'body', 986)

    paragraph(d, 72, 792, '真人剧是一次性下注，失败归零；AI 是把同一笔预算拆成多次小注。对独立团队，先算能试几次，比先问单部成本更低更有用。', 960, 22, INK, 34)

    footer(d, 902, [
        '来源：新湖南《AI剧占全国出海短剧超六成，长沙的出海“大船”怎么造？》（2026-11-02）。',
        '50 万元对比为六翼影视运营负责人盛垄受访口径（单源）；单次预算为本号按 50 万 ÷ 15—20 次复算。',
    ])
    return im


def translation_bars():
    im, d = page('120 分钟字幕：3 天 → 4—5 小时', '马栏山音视频实验室 / 截至 2026-10 / 实验室口径', '02', 1000)

    put(d, 72, 238, '同一部剧，译制时间差多少', 26, INK, 'bold', 1008)

    x0, x1 = 250, 980
    per = (x1 - x0) / 80  # 80 小时刻度
    for t in (0, 24, 48, 72):
        x = x0 + t * per
        d.line((x, 300, x, 548), fill=LINE, width=1)
        put(d, x - 10, 566, f'{t}h', 18, DIM, 'number', x + 40)

    # 人工：至少 72 小时
    put(d, 72, 330, '人工', 22, RUST, 'bold', 230)
    d.rounded_rectangle((x0, 328, x0 + 72 * per, 388), radius=6, fill=RUST)
    put(d, x0 + 72 * per - 150, 344, '至少 72 小时', 22, WHITE, 'bold', x0 + 72 * per - 12)

    # AI：4—5 小时
    put(d, 72, 440, 'AI 译制', 22, TEAL, 'bold', 230)
    d.rounded_rectangle((x0, 438, x0 + 5 * per, 498), radius=6, fill=TEAL)
    put(d, x0 + 5 * per + 18, 450, '4—5 小时', 24, TEAL, 'bold', 760)

    put(d, 72, 600, '以 72 小时计，AI 译制约为人工的 1/14—1/18（本号复算）', 20, INK, 'body', 1008)

    stats = [
        ('14000', '部次', '累计翻译/配音'),
        ('140 万', '分钟', '处理时长'),
        ('40+', '种', '支持语言'),
        ('20+', '家', '服务客户'),
    ]
    cw, gap = 222, 18
    for i, (num, unit, label) in enumerate(stats):
        cx = 72 + i * (cw + gap)
        d.rounded_rectangle((cx, 656, cx + cw, 792), radius=10, fill=WHITE)
        put(d, cx + 18, 672, num, 30, INK, 'bold', cx + cw - 12)
        put(d, cx + 18, 716, unit, 18, DIM, 'body', cx + cw - 12)
        put(d, cx + 18, 748, label, 18, DIM, 'body', cx + cw - 12)

    d.rounded_rectangle((72, 820, 1008, 888), radius=10, fill=INK)
    put(d, 100, 838, '省下的不只是译制费，是先上哪个市场的时间。', 24, '#f0c588', 'bold', 986)

    footer(d, 910, [
        '来源：新湖南（2026-11-02）；马栏山音视频实验室数据经新湖南报道。',
        '120 分钟字幕、3 天、4—5 小时为实验室口径；实际排期还需算人工审校、配音与本地化改编。',
    ])
    return im


def cover_068():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 860)

    put(d, 36, 78, 'AI 出海 · 2026-11-03', 20, GOLD, 'bold', 540)
    put(d, 32, 112, '50 万元', 62, '#f6efe2', 'title', 540)
    put(d, 36, 196, '真人赌 1 次', 34, '#e07a5f', 'bold', 540)
    put(d, 36, 244, 'AI 试 15—20 次', 34, GOLD, 'bold', 540)
    put(d, 36, 312, 'AI 剧占出海短剧超六成', 20, '#bdb3a1', 'body', 540)

    d.line((560, 70, 560, 330), fill='#4a443b', width=2)

    put(d, 590, 96, '同样预算，试错次数', 19, '#c9c0b0', 'bold', 864)

    put(d, 590, 158, '真人', 18, '#bdb3a1', 'body', 650)
    d.ellipse((666, 166, 684, 184), fill=RUST)
    put(d, 694, 158, '1 次', 20, '#f0e8d8', 'bold', 780)

    put(d, 590, 222, 'AI', 18, '#bdb3a1', 'body', 650)
    for i in range(15):
        x = 666 + i * 12
        d.ellipse((x, 230, x + 10, 240), fill=GOLD)
    put(d, 590, 262, '15—20 次', 20, GOLD, 'bold', 780)

    put(d, 590, 310, '爆款率 0.47%：能生成 ≠ 能赚钱', 17, '#e07a5f', 'body', 864)

    im.save(OUT / '封面_068_50万试错_900x383.png')
    print('封面 068 OK', im.size)


if __name__ == '__main__':
    im = budget_dots()
    im.save(OUT / '068_图1_试错次数_1080.png')
    print('图1 OK', im.size)
    im = translation_bars()
    im.save(OUT / '068_图2_译制时间_1080.png')
    print('图2 OK', im.size)
    cover_068()
