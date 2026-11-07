#!/usr/bin/env python3
"""083《AI 微短剧新倡议：换脸克隆声音，先授权》配图与封面。纯本地 Pillow，零扣费。"""
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def auth_chain():
    im, d = page('一条能回放的授权链', 'AI 微短剧“融像”“融声” / 两协会倡议 2026-11-05', '01', 1020)

    steps = [
        ('01', '素材入场', '人脸、人声、姓名、外部形象', RUST),
        ('02', '告知与同意', '充分告知；人脸人声单独同意', TEAL),
        ('03', '凭证留存', '书面或可验证电子；写清范围', GOLD),
        ('04', '生成留痕', '模型版本、原始素材、操作日志', RUST),
        ('05', '标识与核验', '显式+隐式标识；平台可核验', TEAL),
    ]
    y = 246
    for num, title, desc, color in steps:
        d.rounded_rectangle((72, y, 660, y + 92), radius=10, fill=WHITE)
        d.rounded_rectangle((72, y, 86, y + 92), radius=4, fill=color)
        put(d, 102, y + 14, num, 15, color, 'number', 150)
        put(d, 150, y + 12, title, 24, INK, 'bold', 644)
        put(d, 150, y + 56, desc, 15, DIM, 'body', 644)
        y += 100

    d.rounded_rectangle((690, 246, 1008, 746), radius=12, fill=WHITE)
    put(d, 714, 266, '授权台账，至少写清', 20, INK, 'bold', 992)
    d.line((714, 304, 984, 304), fill=LINE, width=2)
    rows = [
        ('授权人', '身份信息'),
        ('素材', '脸、声、姓名、形象'),
        ('用途', '商用、改编、平台、地域'),
        ('期限', '起止、撤回条件'),
        ('凭证', '签名、时间戳、存档位置'),
    ]
    y = 322
    for label, value in rows:
        put(d, 714, y, label, 15, DIM, 'bold', 992)
        put(d, 714, y + 24, value, 14, INK, 'body', 992)
        y += 80

    d.rounded_rectangle((72, 786, 1008, 894), radius=12, fill=INK)
    put(d, 102, 804, '同意 ≠ 单独同意；口头/聊天记录不够稳；“AI 自动生成”不是免责牌。', 20, '#f0c588', 'bold', 986)
    put(d, 102, 846, '倡议不是法规，但会成平台审核参照；先留证据，再谈成本。', 16, '#bdb3a1', 'body', 986)

    footer(d, 922, [
        '来源：中国网络视听节目服务协会 2026-11-05 倡议书全文；广电总局 2026-11-05 论坛通稿。',
        '授权台账字段为本号按倡议第一、二条整理；具体授权文本以法务意见为准。',
    ])
    return im


def verify_grid():
    im, d = page('平台核验，会看哪些证据', '倡议书第四条 / 六个考察因素', '02', 980)

    cards = [
        ('E1', '可识别性', '观众能否认出特定自然人'),
        ('E2', '素材来源与生成过程', '原始素材、模型、操作记录'),
        ('E3', '许可与使用范围', '用途、平台、期限、地域'),
        ('E4', '传播范围', '投放平台、分发规模'),
        ('E5', '技术检测结果', '比对 / 鉴定报告'),
        ('E6', '原始文件与操作日志', '能倒查、能复现'),
    ]
    for i, (num, label, note) in enumerate(cards):
        row, col = divmod(i, 2)
        x = 72 + col * 476
        y = 246 + row * 168
        d.rounded_rectangle((x, y, x + 460, y + 150), radius=10, fill=WHITE)
        put(d, x + 22, y + 16, num, 14, GREY, 'number', x + 440)
        put(d, x + 22, y + 42, label, 23, INK, 'bold', x + 440)
        put(d, x + 22, y + 86, note, 16, DIM, 'body', x + 440)
        d.line((x + 22, y + 122, x + 438, y + 122), fill=LINE, width=2)

    d.rounded_rectangle((72, 760, 1008, 870), radius=12, fill=INK)
    put(d, 102, 778, '不能只凭局部相似下结论；', 24, '#f0c588', 'bold', 986)
    put(d, 102, 820, '“算法自动生成”“偶然撞脸”“无主观故意”也不能当然免责。', 17, '#bdb3a1', 'body', 986)

    footer(d, 900, [
        '来源：中国网络视听节目服务协会 2026-11-05 倡议书第四条。',
        '六个因素为原文列举；核验顺序与权重由平台/机构自行确定，本文不作推断。',
    ])
    return im


def cover_083():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 520)

    put(d, 36, 80, 'AI 微短剧 · 人格权益', 17, GOLD, 'bold', 520)
    put(d, 32, 112, '换脸克隆声音', 38, '#f6efe2', 'title', 520)
    put(d, 32, 166, '先授权', 56, '#e07a5f', 'title', 520)
    put(d, 36, 244, '两协会发布“融像”“融声”倡议', 18, '#e8dfcf', 'bold', 520)
    put(d, 36, 284, '单独同意 / 可验证凭证 / 生成留痕', 15, '#bdb3a1', 'body', 520)
    put(d, 36, 330, '不是法规，但会成平台审核参照', 13, '#8f8576', 'body', 520)

    d.line((548, 70, 548, 330), fill='#4a443b', width=2)

    d.rounded_rectangle((568, 70, 852, 318), radius=12, fill='#f6efe2')
    put(d, 590, 90, '素材使用授权', 18, INK, 'bold', 838)
    checks = ['单独同意', '授权范围', '生成日志']
    y = 136
    for label in checks:
        d.rounded_rectangle((590, y, 606, y + 16), radius=3, fill=RUST)
        d.line((593, y + 8, 598, y + 13), fill='#f6efe2', width=2)
        d.line((598, y + 13, 604, y + 4), fill='#f6efe2', width=2)
        put(d, 620, y - 3, label, 15, INK, 'bold', 838)
        y += 42

    for i in range(24):
        x = 590 + i * 10
        h = 10 + 12 * abs(math.sin(i / 2.3))
        d.line((x, 296 - h / 2, x, 296 + h / 2), fill=TEAL, width=2)

    d.ellipse((748, 216, 832, 300), fill=RUST)
    stamp = '授权'
    sw = d.textlength(stamp, font=font(17, 'bold'))
    put(d, 790 - sw / 2, 246, stamp, 17, WHITE, 'bold', 838)

    im.save(OUT / '封面_083_AI授权_900x383.png')
    print('封面 083 OK', im.size)


if __name__ == '__main__':
    im = auth_chain()
    im.save(OUT / '083_图1_授权链_1080.png')
    print('图1 OK', im.size)
    im = verify_grid()
    im.save(OUT / '083_图2_核验_1080.png')
    print('图2 OK', im.size)
    cover_083()
