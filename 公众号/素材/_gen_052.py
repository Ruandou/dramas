#!/usr/bin/env python3
"""052《微短剧扶持查了一圈》配图与封面。纯本地 Pillow。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def center(d, cx, y, text, size, color, kind='bold', right=1016):
    w = d.textlength(text, font=font(size, kind))
    put(d, cx - w / 2, y, text, size, color, kind, right)


def windows():
    im, d = page('三个有日期的窗口，八个滚动的', '2026-10-29 至 12-31 / 申报与签约窗口', '01', 960)
    x0, x1, y = 100, 980, 380
    span = x1 - x0

    def dx(day):
        return x0 + span * day / 63

    d.line((x0, y, x1, y), fill=LINE, width=3)
    for day, label, color in [(0, '10-29', DIM), (20, '11-18', RUST), (63, '12-31', GOLD)]:
        x = dx(day)
        d.line((x, y - 8, x, y + 8), fill=color, width=2)
        center(d, x, y + 18, label, 19, color, 'number', x + 40)

    xb = dx(20)
    d.line((xb, 252, xb, y - 10), fill=RUST, width=3)
    center(d, xb, 214, '11-18 上海截止', 21, RUST, 'bold', xb + 100)

    xa = dx(3)
    d.line((xa, 300, xa, y - 10), fill=TEAL, width=3)
    put(d, xa + 10, 306, '11-01 小说签约开', 19, TEAL, 'bold', 330)

    xc = dx(63)
    d.line((xc, 252, xc, y - 10), fill=GOLD, width=3)
    put(d, xc - 284, 214, '12-31 微信 Q4 与签约截止', 21, GOLD, 'bold', xc)

    cards = [
        (72, '上海专项', '最高 300 万', '企业主体 / 11-18', RUST),
        (394, '微信 Q4', '最高 70% 现金', '小程序主体 / 12-31', TEAL),
        (716, '小说改编', '双方各 5%', '首期 10 部 / 11-01 签', GOLD),
    ]
    for cx, label, value, note, color in cards:
        d.rounded_rectangle((cx, 432, cx + 292, 600), radius=12, fill=WHITE)
        put(d, cx + 22, 450, label, 20, DIM, 'bold', cx + 280)
        put(d, cx + 18, 484, value, 34, color, 'title', cx + 282)
        put(d, cx + 22, 556, note, 18, DIM, 'body', cx + 276)

    put(d, 72, 646, '另外 8 个：滚动或按年度通知，没有公开截止日', 23, INK, 'bold', 1008)
    rows = [
        (72, '深圳', '剧本 100 万 / 制作 200 万'),
        (72 + 468, '抖音保底', '全年 15 亿，部均 +60%'),
        (72, '横琴', '剧本 1 万 / 首拍 20 万'),
        (72 + 468, '红果成长', '单部最高 200 万'),
        (72, '福建', '年 1000 万 / 单部 260 万'),
        (72 + 468, '抖音 IP', '剧本 5 万 / 保底 300 万'),
        (72, '广东', '六档叠加，园区 1000 万'),
        (72 + 468, '红果收稿', 'A- 4 万起 + 分成'),
    ]
    y0 = 692
    for i, (rx, name, amount) in enumerate(rows):
        ry = y0 + (i // 2) * 46
        d.rectangle((rx, ry + 6, rx + 14, ry + 20), fill=TEAL if rx == 72 else GOLD)
        put(d, rx + 26, ry, name, 19, INK, 'bold', rx + 180)
        put(d, rx + 176, ry, amount, 18, DIM, 'body', rx + 452)

    footer(d, 884, [
        '台账截至 2026-10-29；滚动类以各单位最新公告为准。',
        '来源：上海申报指南、微信开放平台、深圳/横琴/福建/广东公开文件、抖音与红果公开信息。',
    ])
    return im


def gate():
    im, d = page('政府端 5 条，条条要企业', '申报主体 / 备案或上线 / 个人能不能申', '02', 1000)

    d.rounded_rectangle((72, 244, 1008, 286), radius=8, fill=INK)
    put(d, 96, 254, '项目', 18, '#efe6d6', 'bold', 280)
    put(d, 300, 254, '申报主体', 18, '#efe6d6', 'bold', 560)
    put(d, 590, 254, '备案或上线', 18, '#efe6d6', 'bold', 790)
    put(d, 826, 254, '个人可申', 18, '#efe6d6', 'bold', 1000)

    rows = [
        ('上海专项', '上海经营单位', '已上线'),
        ('深圳', '深圳企业', '已上线'),
        ('横琴', '合作区企业', '拍摄并完整播放'),
        ('福建', '省内机构', '已上线'),
        ('广东', '省内机构', '已上线'),
    ]
    for i, (name, subject, filing) in enumerate(rows):
        ry = 300 + i * 84
        d.rounded_rectangle((72, ry, 1008, ry + 68), radius=10, fill=WHITE)
        put(d, 96, ry + 20, name, 21, INK, 'bold', 280)
        put(d, 300, ry + 20, subject, 20, INK, 'body', 566)
        put(d, 590, ry + 20, filing, 20, INK, 'body', 796)
        put(d, 826, ry + 20, '不可', 21, RUST, 'bold', 1000)

    d.rounded_rectangle((72, 748, 1008, 856), radius=12, fill=INK)
    put(d, 102, 764, '上海指南原文：申报主体为「上海微短剧经营单位」，不接受个人、个体户。', 20, '#bdb3a1', right=986)
    put(d, 102, 802, '一类微短剧备案，申请人须持《广播电视节目制作经营许可证》。', 22, '#f0c588', 'bold', 986)

    put(d, 72, 878, '三道门叠加：没有主体，没有备案，没有已完成成片。', 22, INK, 'bold', 1008)
    footer(d, 916, [
        '来源：上海 2026 专项申报指南、深圳若干措施、横琴扶持办法、福建/广东公开文件。',
        '「个人可申」按各文件申报对象栏归纳，不是另行解释。',
    ])
    return im


def paths():
    im, d = page('个人能直接拿到钱的两条路', '单价与门槛 / 2026 年 10 月口径', '03', 900)

    d.rounded_rectangle((72, 244, 492, 612), radius=12, fill=WHITE)
    put(d, 96, 264, '一、卖剧本', 22, DIM, 'bold', 470)
    put(d, 92, 300, '2—7 万', 50, INK, 'title', 470)
    put(d, 96, 372, '每部，按评级和平台分档', 19, DIM, 'body', 470)
    lines = ['完稿 + 完整著作权', '集数时长按收稿公告', '入口在平台收稿页']
    for i, line in enumerate(lines):
        put(d, 96, 430 + i * 48, '·', 22, RUST, 'bold', 120)
        put(d, 118, 430 + i * 48, line, 20, INK, 'body', 470)

    d.rounded_rectangle((516, 244, 1008, 612), radius=12, fill=WHITE)
    put(d, 540, 264, '二、卖改编权', 22, DIM, 'bold', 986)
    put(d, 536, 300, '额外 5%', 50, TEAL, 'title', 986)
    put(d, 540, 372, '优先发行前 30 天变现收入', 19, DIM, 'body', 986)
    lines = ['首期 10 部，无公开报名', '签约 11-01 至 12-31', '作者入选即确认意向']
    for i, line in enumerate(lines):
        put(d, 540, 430 + i * 48, '·', 22, TEAL, 'bold', 566)
        put(d, 562, 430 + i * 48, line, 20, INK, 'body', 986)

    d.rounded_rectangle((72, 648, 1008, 744), radius=12, fill=INK)
    put(d, 102, 664, '承制 / 保底：要公司、要许可证、要历史作品。', 21, '#bdb3a1', right=986)
    put(d, 102, 702, '钱最多，个人最短时间进不去。', 25, '#f0c588', 'bold', 986)

    put(d, 72, 772, '政府端 5 条全部要企业，个人不必研究「怎么报」。', 22, INK, 'bold', 1008)
    footer(d, 818, [
        '来源：红果剧本评级与收稿公告、抖音影视 IP 征集、微信公众号小说改编第一期。',
        '2—7 万为公开价目区间；5% 的基数为优先发行前 30 天变现收入。',
    ])
    return im


def cover():
    base.TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, '#bdb3a1', right=430)
    put(d, 33, 58, '扶持与政策 · 2026-10-29', 18, '#f0c588', 'bold', 440)
    put(d, 28, 92, '11 个', 82, '#efe6d6', 'title', 430)
    put(d, 34, 194, '还开着的口子', 24, '#bdb3a1', 'bold', 430)
    put(d, 34, 236, '政府 5 + 平台 6', 30, '#e0705a', 'bold', 450)
    put(d, 34, 288, '5 条政府扶持，条条要企业', 18, '#8f8576', 'body', 450)

    d.line((474, 60, 474, 330), fill='#4a443c', width=1)
    put(d, 508, 66, '个人能拿的 2 条', 20, '#f0c588', 'bold', 880)
    rows = [
        ('卖剧本', '2—7 万/部', '#b9853d'),
        ('卖改编权', '额外 5%', '#28695e'),
    ]
    y = 120
    for name, val, color in rows:
        d.rectangle((508, y + 6, 520, y + 24), fill=color)
        put(d, 532, y - 2, name, 19, '#bdb3a1', 'body', 660)
        put(d, 660, y - 4, val, 22, color, 'bold', 880)
        y += 62
    put(d, 508, 258, '上海 11-18 截止', 20, '#efe6d6', 'bold', 700)
    put(d, 508, 296, '微信两档到 12-31', 20, '#efe6d6', 'bold', 880)
    return im


def main():
    outputs = [
        (windows(), '052_图1_窗口_1080.png'),
        (gate(), '052_图2_政府端门槛_1080.png'),
        (paths(), '052_图3_个人的两条路_1080.png'),
    ]
    for im, name in outputs:
        im.save(OUT / name, optimize=True)
        base.validate_glyphs()
        print(name, im.size, f'{(OUT / name).stat().st_size / 1024:.1f} KB')
    cv = cover()
    cv.save(OUT / '封面_052_11个口子_900x383.png', optimize=True)
    base.validate_glyphs()
    print('封面_052_11个口子_900x383.png', cv.size)
    print('done')


if __name__ == '__main__':
    main()
