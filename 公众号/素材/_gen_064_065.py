#!/usr/bin/env python3
"""064《可灵 198 亿》/ 065《11-05 微短剧论坛》配图与封面。纯本地 Pillow。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def kling_money():
    im, d = page('198.02 亿到账，缺口 6.45 亿', '可灵 AI 增资交割 / 快手公告 2026-10-30 / 单位：亿元', '01', 1120)

    # 计划 vs 实到
    put(d, 72, 240, '原定上限 204.47 亿', 22, DIM, 'bold', 700)
    put(d, 720, 240, '实到 198.02 亿', 22, INK, 'bold', 1008)

    x0, span, top, bot = 72, 936, 282, 342
    paid = span * 198.02 / 204.47
    d.rectangle((x0, top, x0 + paid, bot), fill=TEAL)
    d.rectangle((x0 + paid, top, x0 + span, bot), fill=RUST)
    put(d, x0 + 16, top + 16, '已缴 198.02', 21, WHITE, 'bold', x0 + paid - 8)
    put(d, 892, bot + 8, '未缴 6.45', 15, RUST, 'bold', 1008)

    # 两笔缺口
    cards = [
        (72, 380, 456, 'BFI MIDCO', '8000 万美元 ≈ 5.45 亿元', '认购义务整体终止'),
        (552, 380, 456, '达康兰五', '剩余 1 亿元未缴', '7.8 亿元份额已转让'),
    ]
    for cx, cy, cw, name, amount, note in cards:
        d.rounded_rectangle((cx, cy, cx + cw, cy + 150), radius=12, fill=WHITE)
        put(d, cx + 24, cy + 16, name, 21, DIM, 'bold', cx + cw - 12)
        put(d, cx + 22, cy + 54, amount, 26, RUST, 'bold', cx + cw - 12)
        put(d, cx + 24, cy + 100, note, 18, INK, 'body', cx + cw - 12)

    # 股权
    put(d, 72, 572, '交割后谁说了算', 26, INK, 'bold', 1008)
    rows = [
        ('Lucky Labs（快手）', '66.68% 股权 / 52.45% 表决权', TEAL),
        ('盖坤', '3.02% 股权 / 23.72% 表决权', GOLD),
        ('上海国方数科', '1.38% 股权', GREY),
        ('国家人工智能产业投资基金', '1.15% 股权', GREY),
        ('沐曦数智', '0.08% 股权', GREY),
    ]
    for i, (name, stake, color) in enumerate(rows):
        ry = 620 + i * 58
        d.rounded_rectangle((72, ry, 1008, ry + 46), radius=8, fill=WHITE)
        put(d, 94, ry + 12, name, 19, INK, 'bold', 470)
        put(d, 500, ry + 12, stake, 19, color if color != GREY else DIM, 'body', 990)

    d.rounded_rectangle((72, 924, 1008, 1004), radius=12, fill=INK)
    put(d, 100, 940, '少的是 6.45 亿，不是融资失败。', 23, '#f0c588', 'bold', 986)
    put(d, 100, 972, '两家中东资方未按期缴款，其余全部到账。', 17, '#bdb3a1', 'body', 986)

    footer(d, 1018, [
        '来源：快手公告（2026-10-30），经科创板日报、每日经济新闻、凤凰网核对。',
        '股权与表决权为公告披露口径；金额四舍五入。',
    ])
    return im


def kling_price():
    im, d = page('融资不等于降价', '可灵 198 亿 / 对 API 用户，先看三件事 / 2026-11-03', '02', 1120)

    put(d, 72, 240, '为什么不能把 198 亿当成降价通知', 25, INK, 'bold', 1008)
    reasons = [
        ('01', '股权融资，不是补贴', '投资方要回报，钱先变成算力和收入。'),
        ('02', '2031 年 IPO 对赌', '未上市可按年化 8% 单利回购，指向做收入。'),
        ('03', 'GPU 厂商只持股 0.08%', '沐曦未确认算力合作，不能推导算力便宜。'),
    ]
    for i, (num, title, note) in enumerate(reasons):
        ry = 296 + i * 132
        d.rounded_rectangle((72, ry, 1008, ry + 112), radius=12, fill=WHITE)
        put(d, 96, ry + 20, num, 30, RUST, 'number', 160)
        put(d, 170, ry + 18, title, 24, INK, 'bold', 980)
        put(d, 170, ry + 62, note, 19, DIM, 'body', 980)

    put(d, 72, 710, '真要判断价格，看这三项', 24, INK, 'bold', 1008)
    checks = [
        (72, 758, 300, '公开价目表', '基础价 / 批量价 / 会员折扣'),
        (390, 758, 300, '配额与并发', '扩容量比直接降价更常见'),
        (708, 758, 300, '企业合同门槛', '年框 / 预付 / 最低消费'),
    ]
    for cx, cy, cw, title, note in checks:
        d.rounded_rectangle((cx, cy, cx + cw, cy + 138), radius=12, fill=WHITE)
        put(d, cx + 22, cy + 18, title, 21, TEAL, 'bold', cx + cw - 12)
        y = paragraph(d, cx + 22, cy + 58, note, width=cw - 44, size=18, color=DIM, leading=28)
        assert y <= cy + 136, (title, y)

    d.rounded_rectangle((72, 922, 1008, 1002), radius=12, fill=INK)
    put(d, 100, 938, '融资是公司的事，价格是合同的事。', 23, '#f0c588', 'bold', 986)
    put(d, 100, 970, '别因为一条融资新闻，去签更长的预付合同。', 17, '#bdb3a1', 'body', 986)

    footer(d, 1016, [
        '来源：快手公告（2026-10-30）；IPO 时间表为媒体口径，公司未确认。',
        '三项观察与采购建议为本号判断，不构成采购建议。',
    ])
    return im


def forum_known():
    im, d = page('11-05 微短剧论坛：知道什么，不知道什么', '2026 中国广播电视精品创作大会 / 北京会议中心 / 11-05', '01', 1000)

    put(d, 72, 238, '已知', 26, TEAL, 'bold', 500)
    known = [
        ('时间', '11 月 5 日'),
        ('地点', '北京会议中心'),
        ('主办', '广电总局网络视听司、北京市广电局'),
        ('承办', '中国网络视听协会、红果短剧、《网络视听》'),
        ('发布', '精品项目、扶持计划、标杆案例'),
        ('对话', '品质共建 / 全民价值共创 / 全球故事共讲'),
    ]
    for i, (k, v) in enumerate(known):
        ry = 288 + i * 78
        d.rounded_rectangle((72, ry, 546, ry + 64), radius=10, fill=WHITE)
        put(d, 92, ry + 12, k, 18, DIM, 'bold', 150)
        put(d, 154, ry + 12, v, 18, INK, 'body', 538)

    put(d, 560, 238, '未知', 26, RUST, 'bold', 1008)
    unknown = [('嘉宾名单', '谁来'), ('议程时间', '几点开始'), ('报名方式', '能不能去'), ('直播入口', '在哪看')]
    for i, (k, v) in enumerate(unknown):
        ry = 288 + i * 98
        d.rounded_rectangle((560, ry, 1008, ry + 82), radius=10, fill=WHITE)
        put(d, 582, ry + 14, '×', 24, RUST, 'bold', 620)
        put(d, 620, ry + 12, k, 21, INK, 'bold', 996)
        put(d, 620, ry + 46, v, 17, DIM, 'body', 996)

    d.rounded_rectangle((72, 790, 1008, 884), radius=12, fill=INK)
    put(d, 100, 808, '比论坛本身更有用的，是两份名单', 23, '#f0c588', 'bold', 986)
    put(d, 100, 846, '精品项目名单、扶持计划细则；报名和直播等公布再定行程。', 18, '#bdb3a1', 'body', 986)

    footer(d, 906, [
        '来源：央广网（2026-10-30）、光明网（2026-10-29）论坛通稿。',
        '议程、嘉宾、报名与直播信息截至 11-02 未公布。',
    ])
    return im


def cover_kling():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 860)
    put(d, 36, 78, '可灵 · 2026-10-30 公告', 20, GOLD, 'bold', 860)
    put(d, 32, 114, '198 亿到账', 60, '#f6efe2', 'title', 620)
    put(d, 36, 196, '不是降价通知', 38, GOLD, 'bold', 620)
    put(d, 36, 258, '先看价目表、配额、合同门槛', 21, '#bdb3a1', 'body', 620)
    put(d, 36, 312, '融资是公司的事，价格是合同的事', 20, '#e07a5f', 'body', 620)

    d.line((650, 70, 650, 330), fill='#4a443b', width=2)
    items = ['实到 198.02 亿', '缺口 6.45 亿', '快手仍控 66.68%', '2031 IPO 对赌']
    for i, item in enumerate(items):
        yy = 92 + i * 62
        d.line((684, yy + 14, 700, yy + 30), fill=RUST, width=4)
        d.line((700, yy + 30, 718, yy + 2), fill=RUST, width=4)
        put(d, 710, yy, item, 20, '#f0e8d8', 'bold', 896)
    im.save(OUT / '封面_064_198亿不是降价_900x383.png')
    print('封面 064 OK', im.size)


def cover_forum():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 860)
    put(d, 36, 78, '2026 中国广播电视精品创作大会', 20, GOLD, 'bold', 860)
    put(d, 32, 116, '11-05 微短剧论坛', 44, '#f6efe2', 'title', 860)
    put(d, 36, 182, '北京会议中心', 30, GOLD, 'bold', 860)
    put(d, 36, 236, '会发布：精品项目 / 扶持计划 / 标杆案例', 21, '#e8dfcf', 'body', 860)
    put(d, 36, 292, '嘉宾、议程、报名、直播：未公布', 22, '#e07a5f', 'bold', 860)
    im.save(OUT / '封面_065_1105论坛_900x383.png')
    print('封面 065 OK', im.size)


if __name__ == '__main__':
    for name, fn in [
        ('064_图1_资金构成_1080.png', kling_money),
        ('064_图2_三件事_1080.png', kling_price),
        ('065_图1_已知未知_1080.png', forum_known),
    ]:
        im = fn()
        im.save(OUT / name)
        print(name, im.size)
    cover_kling()
    cover_forum()
