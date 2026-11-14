# -*- coding: utf-8 -*-
"""099《欧盟数字公平法案》正文两图 + 封面。纯本地 Pillow，零扣费。"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from importlib import import_module

_c = import_module('_gen_charts_006')

OUT = HERE
PAPER, INK, DIM, LINE, BOX = _c.PAPER, _c.INK, _c.DIM, _c.LINE, _c.BOX
RUST, TEAL, GOLD = (174, 66, 44), (40, 105, 94), (185, 133, 61)

SONG, HIRA, MONO = _c.SONG, _c.HIRA, _c.MONO
GLYPHS: dict = {}
BOXES: list = []
ISSUE = '099'
EDITION = '2026-11-13'
W = 1080


def font(size, kind='body'):
    path, index = {'body': (HIRA, 0), 'bold': (HIRA, 2),
                   'title': (SONG, 1), 'number': (MONO, 1)}[kind]
    return _c.f(path, size, index=index)


def put(d, x, y, text, size=28, color=INK, kind='body', right=None):
    ff = font(size, kind)
    width = d.textlength(text, font=ff)
    if right is not None:
        assert x + width <= right + 0.1, (text, x, width, right)
    box = d.textbbox((x, y), text, font=ff, anchor='lt')
    assert box[0] >= 0 and box[2] <= d._image.width and box[3] <= d._image.height, (text, box)
    for other, b in BOXES:
        if min(box[2], b[2]) > max(box[0], b[0]) and min(box[3], b[3]) > max(box[1], b[1]):
            raise AssertionError(f'文本重叠: {text!r} / {other!r}')
    BOXES.append((text, box))
    GLYPHS.setdefault((kind, size), set()).update(text)
    d.text((x, y), text, font=ff, fill=color, anchor='lt')
    return width


def put_right(d, x_right, y, text, size=28, color=INK, kind='body'):
    w = d.textlength(text, font=font(size, kind))
    return put(d, x_right - w, y, text, size, color, kind)


def head(d, title, sub):
    d.rectangle((72, 44, 83, 66), fill=RUST)
    put(d, 100, 44, f'一人短剧厂牌 / 快讯 {ISSUE}', 21, DIM, 'bold')
    put_right(d, W - 72, 44, EDITION, 22, RUST, 'number')
    put(d, 72, 92, title, 44, INK, 'title')
    put(d, 72, 158, sub, 22, DIM)
    return 216


def save(im, name):
    dest = OUT / name
    im.quantize(colors=192, method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.NONE).save(dest, optimize=True)
    print(dest.name, im.size, f'{dest.stat().st_size / 1024:.1f} KB')


def check_glyphs():
    for (kind, size), chars in GLYPHS.items():
        path, index = {'body': (HIRA, 0), 'bold': (HIRA, 2),
                       'title': (SONG, 1), 'number': (MONO, 1)}[kind]
        ff = TTFont(path, fontNumber=index)
        cmap = ff.getBestCmap()
        missing = sorted(c for c in chars if ord(c) not in cmap)
        ff.close()
        assert not missing, (path, index, missing)


def chart1():
    BOXES.clear()
    im = Image.new('RGB', (W, 960), PAPER)
    d = ImageDraw.Draw(im)
    head(d, '金币解锁，两处要改',
         '《数字公平法案》提案第 14 条 / 2026-11-11')

    d.rounded_rectangle((72, 232, 528, 620), radius=16, fill=BOX)
    put(d, 100, 254, '① 标价', 26, TEAL, 'bold')
    put(d, 100, 296, '虚拟币换物品，要标真实货币价值', 18, DIM, right=506)
    put(d, 100, 340, '100 币 = 4.99 欧元', 24, INK, 'bold', right=506)
    put(d, 100, 384, '一集 30 币 ≈ 1.5 欧元', 24, INK, 'bold', right=506)
    put(d, 100, 436, '可标估计值；币种按消费者', 17, DIM, right=506)
    put(d, 100, 466, '第一次买币所用货币', 17, DIM, right=506)
    put(d, 100, 530, '只写「30 coins」不够', 20, RUST, 'bold', right=506)

    d.rounded_rectangle((552, 232, 1008, 620), radius=16, fill=BOX)
    put(d, 580, 254, '② 未成年人', 26, RUST, 'bold')
    put(d, 580, 296, '面向未成年人或被其使用', 18, DIM, right=986)
    put(d, 580, 340, '付费虚拟币默认关闭', 26, RUST, 'bold', right=986)
    put(d, 580, 392, '只能经监护人同意后开启', 20, INK, right=986)
    put(d, 580, 452, '有年龄判断、家长控制的，', 17, DIM, right=986)
    put(d, 580, 482, '先补默认关闭流程', 17, DIM, right=986)
    put(d, 580, 530, '不是加个勾选就行', 20, RUST, 'bold', right=986)

    d.rounded_rectangle((72, 650, 1008, 770), radius=16, fill=(238, 232, 218))
    put(d, 100, 670, '官方没点名微短剧，举例是游戏内购；', 22, INK, 'bold')
    put(d, 100, 708, '但豁免名单只写社交网络、视频分享平台、AI 伴侣和聊天机器人——', 20, INK)
    put(d, 100, 740, '自建金币体系的短剧 App 不在其中。', 20, RUST, 'bold')

    put(d, 72, 900, '数据：欧盟委员会提案 COM(2026) 1100 final 第 14 条；新闻稿 IP/26/2407、问答 QANDA/26/2408。', 17, DIM)

    check_glyphs()
    save(im, '099_图1_金币两处要改_1080.png')


def chart2():
    BOXES.clear()
    im = Image.new('RGB', (W, 990), PAPER)
    d = ImageDraw.Draw(im)
    head(d, '提案走到哪一步',
         'Digital Fairness Act · 尚未生效')

    steps = [('委员会提出提案', '2026-11-11 · COM(2026) 1100 final'),
             ('欧洲议会讨论', '文本可能修改'),
             ('理事会讨论', '两院通过后成为法律'),
             ('生效与适用', '新闻稿未给适用起始日')]
    for i, (main, sub) in enumerate(steps):
        yy = 238 + i * 96
        d.rounded_rectangle((72, yy, 1008, yy + 80), radius=12, fill=BOX if i % 2 == 0 else PAPER,
                            outline=LINE, width=2)
        put(d, 100, yy + 12, f'{i + 1}. {main}', 23, TEAL if i < 3 else RUST, 'bold', right=986)
        put(d, 100, yy + 46, sub, 18, INK, right=986)

    d.rounded_rectangle((72, 650, 1008, 812), radius=16, fill=(238, 232, 218))
    put(d, 100, 668, '第 17 条：四类「成瘾设计」要给关闭开关', 23, INK, 'bold')
    items = ['自动播放 / 无打断连续观看', '与用户操作无关的通知',
             '定时或高频激励（含掉权益）', '模拟人际关系的持续提示']
    for i, t in enumerate(items):
        yy = 712 + i * 26
        put(d, 100, yy, '·', 18, RUST, 'bold')
        put(d, 122, yy, t, 18, INK, right=986)

    put(d, 72, 856, '罚则（CPC 修订提案）：最高全球年营业额 6%；非欧盟公司须指定欧盟法律代表。', 17, DIM)
    put(d, 72, 886, '以上均为提案内容，不是已生效规则。', 17, RUST)

    check_glyphs()
    save(im, '099_图2_提案流程_1080.png')


def cover():
    BOXES.clear()
    C_W, C_H = 900, 383
    im = Image.new('RGB', (C_W, C_H), PAPER)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, DIM, 'bold', C_W - 20)
    put_right(d, C_W - 33, 24, f'{ISSUE} / 快讯', 17, DIM, 'body')

    put(d, 42, 66, '欧盟数字公平法案', 20, DIM, 'bold')
    put(d, 42, 100, '金币买剧', 40, RUST, 'title')
    put(d, 42, 156, '先标真实价格', 40, INK, 'title')
    d.line((42, 226, 380, 226), fill=LINE, width=2)
    put(d, 42, 244, '付费币未成年人默认关闭', 18, INK, 'bold')
    put(d, 42, 276, '提案 11-11 · 尚未生效', 17, DIM)
    put(d, 42, 306, '官方未点名微短剧', 17, DIM)

    d.rounded_rectangle((420, 52, 860, 330), radius=18, fill=(238, 232, 218))
    put(d, 450, 76, '三条要改', 22, DIM, 'bold')
    rows = [('标价', '30 币 ≈ 1.5 欧元', TEAL),
            ('未成年', '付费币默认关闭', RUST),
            ('连播', '给一个明显开关', GOLD)]
    for i, (tag, text, color) in enumerate(rows):
        yy = 128 + i * 66
        put(d, 450, yy + 6, tag, 22, color, 'bold')
        put(d, 530, yy, text, 21, INK, right=830)

    check_glyphs()
    save(im, f'封面_{ISSUE}_{EDITION.replace("-", "")}_900x383.png')


if __name__ == '__main__':
    {'chart1': chart1, 'chart2': chart2, 'cover': cover,
     'all': lambda: (chart1(), chart2(), cover())}[sys.argv[1] if len(sys.argv) > 1 else 'all']()