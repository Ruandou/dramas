#!/usr/bin/env python3
"""024《报这个微短剧大赛之前》配图与封面（复用 _gen_023 版式与断言）。"""
import _gen_023 as g

g.HEAD = '一人短剧厂牌 / 245 号文'


def figure_one():
    im, d = g.page('两个层级：申报即授权，入围再签', '正文一句，附件 2 四条', '01', 1200)
    d.rounded_rectangle((72, 242, 1008, 560), radius=16, fill=g.WHITE)
    d.rounded_rectangle((72, 242, 1008, 322), radius=16, fill=g.RUST)
    g.put(d, 104, 258, '第一层：所有申报作品', 30, g.WHITE, 'title', 980)
    y = 352
    for line in ['作品一经申报，即视为同意：',
                 '① 参与后续展播　　② 参与译制　　③ 参与海外宣传推广',
                 '④ 授权主办方使用作品宣传片、海报（境内外宣传活动）']:
        y = g.paragraph(d, 104, y, line, width=872, size=25, color=g.INK, leading=38) + 12
    d.rounded_rectangle((72, 586, 1008, 1040), radius=16, fill=g.WHITE)
    d.rounded_rectangle((72, 586, 1008, 666), radius=16, fill=g.TEAL)
    g.put(d, 104, 602, '第二层：入围作品再签附件 2', 30, g.WHITE, 'title', 980)
    y = 696
    for line in ['第一条　已获其他著作权人授权，不与他方权利冲突',
                 '第二条　拥有独立著作权；二年内可在境内外频道 / 网站 / 客户端播完整版或片段',
                 '第三条　内容与权利瑕疵引发的争议，承担全部法律责任',
                 '第四条　作品及作者信息真实有效']:
        y = g.paragraph(d, 104, y, line, width=872, size=24, color=g.INK, leading=36) + 14
    g.footer(d, 1064, [
        'A 级：广电办发〔2026〕245 号通知正文「五、参赛方式」与附件 2 承诺书原文。',
        '红色那层不需要你签字：交了作品就生效。',
    ])
    return im


def figure_two():
    im, d = g.page('44 天，卡人的不是表', '申报材料清单 · 按通知「五、参赛方式」', '02', 1360)
    items = [
        ('报名表（附件 1）', '一页，可当天填完', g.TEAL),
        ('片花', '可剪现有素材', g.TEAL),
        ('官方海报', '有现成物料即可', g.TEAL),
        ('播出证明 / 备案号', '境内须注明许可证号或备案号', g.GOLD),
        ('传播数据反馈', '佐证材料', g.TEAL),
        ('首、中、尾三集完整成片', '不能是片花——最长的关键路径', g.RUST),
        ('剧本单元另交：大纲 + 人物小传', '只走单元五时才需要', g.GOLD),
    ]
    y = 240
    for name, note, color in items:
        d.rounded_rectangle((72, y, 1008, y + 104), radius=12, fill=g.WHITE)
        d.rounded_rectangle((72, y, 80, y + 104), radius=4, fill=color)
        g.put(d, 104, y + 18, name, 27, g.INK, 'bold', 980)
        g.put(d, 104, y + 60, note, 22, g.DIM, right=980)
        y += 120
    d.rounded_rectangle((72, y + 8, 1008, y + 150), radius=14, fill=g.INK)
    g.put(d, 104, y + 32, '截止：2026-11-30 · 邮箱 imtsc2024@vip.qq.com', 25, '#f0c588', 'bold', 980)
    g.put(d, 104, y + 78, '今天 10 月 17 日，还剩 44 天。三集成片要现在开工。', 23, g.WHITE, right=980)
    g.footer(d, y + 190, ['A 级：通知「五、参赛方式」原文；材料清单未含通知之外的要求。'])
    return im


def cover_a():
    from PIL import Image, ImageDraw
    g.TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), g.PAPER)
    d = ImageDraw.Draw(im)
    g.put(d, 33, 28, '一人短剧厂牌', 19, g.DIM, right=900)
    g.put(d, 744, 28, '245 号文', 18, g.DIM, right=875)
    g.center(d, 450, 74, '报名之前', 24, g.TEAL, 'bold', True)
    g.center(d, 450, 114, '先看附件 2', 50, g.INK, 'title', True)
    g.center(d, 450, 188, '你授权出去的是两年', 30, g.RUST, 'title', True)
    g.center(d, 450, 300, '申报即同意展播 · 译制 · 海外宣传', 20, g.DIM, 'body', True)
    for i, (width, color) in enumerate([(200, g.RUST), (146, g.TEAL), (96, g.GOLD)]):
        y = 110 + i * 62
        d.rounded_rectangle((44, y, 44 + width, y + 26), radius=6, fill=color)
    for i, width in enumerate((176, 128, 86)):
        d.rounded_rectangle((856 - width, 116 + i * 62, 856, 138 + i * 62), radius=6, fill='#c2b7a6')
    return im


def cover_b():
    from PIL import Image, ImageDraw
    g.TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), g.INK)
    d = ImageDraw.Draw(im)
    g.put(d, 33, 28, '一人短剧厂牌', 19, '#bdb3a1', right=900)
    g.put(d, 744, 28, '245 号文', 18, '#bdb3a1', right=875)
    g.center(d, 450, 74, '还剩 44 天', 24, '#f0c588', 'bold', True)
    g.center(d, 450, 114, '交了就视为同意', 46, g.WHITE, 'title', True)
    d.line((300, 196, 600, 196), fill='#766657', width=2)
    g.center(d, 450, 218, '两年内可播完整版', 34, '#f0c588', 'title', True)
    g.center(d, 450, 288, '展播 · 译制 · 海外宣传', 21, '#bdb3a1', 'body', True)
    for i, (width, color) in enumerate([(180, '#b55b32'), (124, '#28695e'), (74, '#b9853d')]):
        y = 112 + i * 60
        d.rounded_rectangle((44, y, 44 + width, y + 26), radius=6, fill=color)
    for i, width in enumerate((160, 112, 78)):
        d.rounded_rectangle((856 - width, 118 + i * 60, 856, 140 + i * 60), radius=6, fill='#574e45')
    return im


if __name__ == '__main__':
    for fn, name, tag in [
        (figure_one, '024_图1_申报即授权_1080.png', 'fig1'),
        (figure_two, '024_图2_44天材料清单_1080.png', 'fig2'),
        (cover_a, '封面_024_A_先看附件2_900x383.png', 'coverA'),
        (cover_b, '封面_024_B_交了就视为同意_900x383.png', 'coverB'),
    ]:
        im = fn()
        g.check_glyphs()
        g.save(im, name, tag)
    print('PASS: 字形覆盖、量宽、边界、不重叠、封面安全区')
