#!/usr/bin/env python3
"""023《一个季度 159 张微短剧发行许可》配图与封面。

复用 _gen_023.py 的版式与断言（字形覆盖/量宽/边界/不重叠/封面安全区）。
运行：python3 _gen_023q2.py
"""
import _gen_023 as g

g.HEAD = '一人短剧厂牌 / 发行许可'


def figure_one():
    im, d = g.page('一个季度，367 条许可', 'Q2 通告逐条解析 · 四类与官方计数逐项对上', '01', 1040)
    rows = [
        ('微短剧', 159, g.RUST),
        ('网络动画片', 138, g.GOLD),
        ('网络电影', 45, g.TEAL),
        ('网络剧', 25, g.TEAL),
    ]
    y = 250
    max_w = 700
    for name, n, color in rows:
        w = int(n / 159 * max_w)
        d.rounded_rectangle((72, y, 72 + max(max_w, 10), y + 86), radius=12, fill='#eae2d4')
        d.rounded_rectangle((72, y, 72 + w, y + 86), radius=12, fill=color)
        g.put(d, 96, y + 22, name, 28, g.WHITE, 'bold', 800)
        v = f'{n}'
        vx = 72 + max(max_w, 10) - 46 - d.textlength(v, font=g.font(28, 'number'))
        g.put(d, vx, y + 24, v, 28, g.INK, 'number', 1100)
        g.put(d, vx + d.textlength(v, font=g.font(28, 'number')) + 6, y + 26, '部', 24, g.INK, 'body', 1100)
        y += 106
    d.rounded_rectangle((72, y + 10, 1008, y + 132), radius=14, fill=g.INK)
    g.put(d, 104, y + 32, '合计 367 条', 30, '#f0c588', 'title')
    g.put(d, 104, y + 82, '解析结果按类型计数，与网页正文公布的四类数量完全一致', 23, g.WHITE, right=980)
    g.footer(d, y + 176, [
        'A 级：总局办公厅《关于2026年4月至6月全国国产网络剧片发行许可情况的通告》（2026-07-13）附件 PDF。',
        'B 级：本号 beian.py 解析并自校（四类数量全中才放行）。',
    ])
    return im


def figure_two():
    im, d = g.page('23% 的部数，49% 的集数', '159 部微短剧 · 合计 5,396 集', '02', 1120)
    # 两组对照条
    groups = [
        ('部数', [('≥50 集：37 部', 37, 159, g.RUST), ('其余 122 部', 122, 159, '#c2b7a6')]),
        ('集数', [('≥50 集的 37 部：2,657 集', 2657, 5396, g.RUST), ('其余：2,739 集', 2739, 5396, '#c2b7a6')]),
    ]
    y = 250
    for title, bars in groups:
        g.put(d, 72, y, title, 28, g.INK, 'title')
        y += 48
        total = bars[0][2]
        x = 72
        for label, n, _t, color in bars:
            w = int(n / total * 936)
            d.rounded_rectangle((x, y, x + w, y + 74), radius=8, fill=color)
            txt = f'{round(n / total * 100)}%'
            g.put(d, x + w / 2 - d.textlength(txt, font=g.font(30, 'number')) / 2, y + 18, txt, 30,
                  g.WHITE if color != '#c2b7a6' else g.INK, 'number', x + w)
            x += w
        y += 92
        for label, n, _t, color in bars:
            g.put(d, 72, y, f'{label}', 23, g.INK if color == '#c2b7a6' else g.RUST, 'body')
            y += 34
        y += 40
    d.rounded_rectangle((72, y, 1008, y + 150), radius=14, fill=g.INK)
    g.put(d, 104, y + 24, '中位 24 集，平均 33.9 集', 28, '#f0c588', 'title')
    g.put(d, 104, y + 72, '均值比中位高出约 10 集——被 37 部长剧拉上去的。', 23, g.WHITE, right=980)
    g.put(d, 104, y + 108, '发证分散：159 部来自 152 家申报单位，最多的一家 2 部。', 23, g.WHITE, right=980)
    g.footer(d, y + 194, ['B 级：本号按通告附件清单逐条统计，可复现。'])
    return im


def cover_a():
    g.TEXT_BOXES = []
    from PIL import Image, ImageDraw
    im = Image.new('RGB', (900, 383), g.PAPER)
    d = ImageDraw.Draw(im)
    g.put(d, 33, 28, '一人短剧厂牌', 19, g.DIM, right=900)
    g.put(d, 744, 28, '发行许可', 18, g.DIM, right=875)
    g.center(d, 450, 74, '一个季度', 24, g.TEAL, 'bold', True)
    g.center(d, 450, 112, '159 张微短剧许可', 44, g.INK, 'title', True)
    g.center(d, 450, 184, '23% 的剧拿走 49% 集数', 34, g.RUST, 'title', True)
    g.center(d, 450, 300, '中位 24 集 · 152 家单位', 20, g.DIM, 'body', True)
    for i, (width, color) in enumerate([(200, g.RUST), (146, g.TEAL), (96, g.GOLD)]):
        y = 110 + i * 62
        d.rounded_rectangle((44, y, 44 + width, y + 26), radius=6, fill=color)
    for i, width in enumerate((176, 128, 86)):
        d.rounded_rectangle((856 - width, 116 + i * 62, 856, 138 + i * 62), radius=6, fill='#c2b7a6')
    return im


def cover_b():
    g.TEXT_BOXES = []
    from PIL import Image, ImageDraw
    im = Image.new('RGB', (900, 383), g.INK)
    d = ImageDraw.Draw(im)
    g.put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    g.put(d, 744, 28, '发行许可', 18, '#bdb3a1', right=875)
    g.center(d, 450, 74, '我把 367 条许可逐条数了', 24, '#f0c588', 'bold', True)
    g.center(d, 450, 116, '159 部微短剧', 50, g.WHITE, 'title', True)
    d.line((300, 196, 600, 196), fill='#766657', width=2)
    g.center(d, 450, 218, '中位 24 集', 36, '#f0c588', 'title', True)
    g.center(d, 450, 282, '37 部拿走了 49% 的集数', 22, '#bdb3a1', 'body', True)
    for i, (width, color) in enumerate([(180, '#b55b32'), (124, '#28695e'), (74, '#b9853d')]):
        y = 112 + i * 60
        d.rounded_rectangle((44, y, 44 + width, y + 26), radius=6, fill=color)
    for i, width in enumerate((160, 112, 78)):
        d.rounded_rectangle((856 - width, 118 + i * 60, 856, 140 + i * 60), radius=6, fill='#574e45')
    return im


if __name__ == '__main__':
    for fn, name, tag in [
        (figure_one, '023_图1_四类许可构成_1080.png', 'fig1'),
        (figure_two, '023_图2_部数与集数占比_1080.png', 'fig2'),
        (cover_a, '封面_023_A_159张_900x383.png', 'coverA'),
        (cover_b, '封面_023_B_中位24集_900x383.png', 'coverB'),
    ]:
        im = fn()
        g.check_glyphs()
        g.save(im, name, tag)
    print('PASS: 字形覆盖、量宽、边界、不重叠、封面安全区')
