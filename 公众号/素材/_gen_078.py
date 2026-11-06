#!/usr/bin/env python3
"""078《虎鲸文娱上线鲸锐AI：50+ 模型，不卖会员》配图与封面。纯本地 Pillow，零扣费。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def feature_map():
    im, d = page('50+ 模型，装进一个片场', '鲸锐AI 上线 / 虎鲸文娱 2026-11-04', '01', 980)

    d.rounded_rectangle((390, 300, 690, 420), radius=12, fill=INK)
    put(d, 420, 318, '鲸锐AI', 30, '#f6efe2', 'bold', 660)
    put(d, 420, 362, '50+ 模型 / 10+ 自研', 18, '#bdb3a1', 'body', 660)

    boxes = [
        (72, 250, '场景', '场景编辑 / 资产沉淀'),
        (760, 250, '人物表演', '逐镜复现 / 微调'),
        (72, 440, '摄像机', '机位 / 景深 / 运动'),
        (760, 440, '虚拟片场', '场景 / 光影 / 站位'),
        (390, 560, '光影', '9 种质感增强'),
    ]
    for x, y, label, desc in boxes:
        d.rounded_rectangle((x, y, x + 248, y + 100), radius=10, fill=WHITE)
        put(d, x + 20, y + 18, label, 21, INK, 'bold', x + 236)
        put(d, x + 20, y + 58, desc, 15, DIM, 'body', x + 236)

    cards = [
        (72, '35 类工具'),
        (310, '300+ 精控项'),
        (548, '千级节点'),
        (786, '百人协同'),
    ]
    for cx, label in cards:
        d.rounded_rectangle((cx, 700, cx + 222, 780), radius=10, fill=INK)
        put(d, cx + 18, 724, label, 20, '#f0c588', 'bold', cx + 210)

    put(d, 72, 816, '不卖会员、积分即充即用、团队席位不限；公开页面未见 1 积分对应价格。', 18, INK, 'bold', 1008)

    footer(d, 872, [
        '来源：虎鲸文娱 2026-11-04 上线通稿及鲸锐AI 官网公开介绍。',
        '50+/10+/35/300+/千级/百人为官方口径；积分单价未公开，本文不估算单集成本。',
    ])
    return im


def trial_scorecard():
    im, d = page('一场 30 秒的戏，先记四个数', '试用基准 / 同一段提示词，换两个模型各跑一次', '02', 940)

    rows = [
        (72, 252, '生成次数', '同一段提示词跑了几次'),
        (556, 252, '可用镜头', '能进成片的镜头数'),
        (72, 448, '消耗积分', '失败重试算不算'),
        (556, 448, '导出规格', '分辨率 / 帧率 / 水印'),
    ]
    for x, y, label, note in rows:
        d.rounded_rectangle((x, y, x + 452, y + 150), radius=12, fill=WHITE)
        put(d, x + 24, y + 18, label, 22, INK, 'bold', x + 440)
        d.line((x + 24, y + 88, x + 428, y + 88), fill=LINE, width=2)
        put(d, x + 24, y + 108, note, 16, DIM, 'body', x + 440)

    d.rounded_rectangle((72, 650, 1008, 750), radius=12, fill=INK)
    put(d, 102, 672, '四个数记完，再决定要不要把整部剧搬进去。', 22, '#f0c588', 'bold', 986)
    put(d, 102, 714, '注册免费，试错成本是积分；先算一场戏，不算总账。', 17, '#bdb3a1', 'body', 986)

    footer(d, 800, [
        '来源：虎鲸文娱 2026-11-04 上线通稿及鲸锐AI 官网公开介绍。',
        '30%/40—60%/65%/百余部项目为厂商口径，方法未披露；四个数为本号建议的试用记录项。',
    ])
    return im


def cover_078():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 540)

    put(d, 36, 74, 'AI 影视制作平台 · 鲸锐AI', 18, GOLD, 'bold', 540)
    put(d, 32, 108, '50+ 模型', 56, '#f6efe2', 'title', 540)
    put(d, 36, 184, '不卖会员', 26, '#e07a5f', 'bold', 540)
    put(d, 36, 222, '积分即充即用', 24, '#e8dfcf', 'bold', 540)
    put(d, 36, 280, '35 类工具 / 300+ 精控项', 17, '#bdb3a1', 'body', 540)
    put(d, 36, 330, '先拿一场 30 秒的戏试', 15, '#bdb3a1', 'body', 540)

    d.line((560, 70, 560, 330), fill='#4a443b', width=2)

    put(d, 590, 74, '厂商口径', 14, GOLD, 'bold', 864)
    claims = [
        ('30%', '单分钟成本'),
        ('40—60%', '制作时长'),
        ('65%', '超分成本'),
    ]
    y = 120
    for value, label in claims:
        put(d, 590, y, value, 34, '#f6efe2', 'bold', 864)
        put(d, 590, y + 44, label, 14, '#bdb3a1', 'body', 864)
        y += 78

    put(d, 590, 342, '方法未披露，先核基线', 12, '#8f8576', 'body', 864)

    im.save(OUT / '封面_078_鲸锐AI_900x383.png')
    print('封面 078 OK', im.size)


if __name__ == '__main__':
    im = feature_map()
    im.save(OUT / '078_图1_能力_1080.png')
    print('图1 OK', im.size)
    im = trial_scorecard()
    im.save(OUT / '078_图2_试算_1080.png')
    print('图2 OK', im.size)
    cover_078()
