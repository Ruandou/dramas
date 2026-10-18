#!/usr/bin/env python3
"""027《拆开微信 Q4 分账》配图与封面（复用 _gen_023 版式与断言）。"""
import _gen_023 as g
from PIL import Image, ImageDraw


def page(title, subtitle, number, height, head):
    g.HEAD = head
    return g.page(title, subtitle, number, height)


def fig_027():
    im, d = page('三档分账，两条通道', '2026 Q4 · 10-16 至 12-31 · 77 天', '01', 1260, '一人短剧厂牌 / 微信分账')
    rows = [
        ('优质新剧：90% 现金 + 10% 广告金', '上新 7 日内 · 当日流水前五 · 五部里时长最高 · 随后 7 天', g.RUST),
        ('普通剧目：75% 现金 + 10% 广告金', '人均播放时长 10 分钟及以上', g.GOLD),
        ('普通剧目：50% 现金', '人均播放时长不到 10 分钟', g.TEAL),
    ]
    y = 240
    for name, note, color in rows:
        d.rounded_rectangle((72, y, 1008, y + 118), radius=12, fill=g.WHITE)
        d.rounded_rectangle((72, y, 80, y + 118), radius=4, fill=color)
        g.put(d, 104, y + 20, name, 27, g.INK, 'bold', 980)
        g.put(d, 104, y + 66, note, 22, g.DIM, right=980)
        y += 134
    d.rounded_rectangle((72, y + 10, 1008, y + 190), radius=14, fill=g.INK)
    g.put(d, 104, y + 32, '另一条通道：IAA 小程序', 24, '#f0c588', 'bold', 980)
    g.put(d, 104, y + 74, '最高 70% 现金激励', 30, g.WHITE, 'title', 980)
    g.put(d, 104, y + 126, '文娱-微短剧/互动微短剧 · 流量主 · 官方播放器', 21, '#bdb3a1', right=980)
    d.rounded_rectangle((72, y + 214, 1008, y + 318), radius=14, fill='#e9e3d8')
    g.put(d, 104, y + 234, '10 分钟约等于 90 秒 × 7 集', 27, g.RUST, 'bold', 980)
    g.put(d, 104, y + 278, '但人均是平均数：不是让一个人看 7 集，是让足够多的人看很多集。', 20, g.INK, right=980)
    g.footer(d, y + 350, [
        'B 级：微信官方口径经新京报（2026-10-16）与流媒体网（2026-10-12）转述；官方活动页为 JS 渲染，未逐字抓取。',
        '100% = 90% 现金 + 10% 广告金配赠，不是 100% 现金。',
    ])
    return im


def cover():
    g.TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), g.INK)
    d = ImageDraw.Draw(im)
    sub = '#bdb3a1'
    g.put(d, 33, 28, '一人短剧厂牌', 19, sub, right=900)
    g.put(d, 744, 28, '微信分账', 18, sub, right=875)
    g.center(d, 450, 80, '最高 100%', 54, '#f0c588', 'title', True)
    g.center(d, 450, 176, '只给 7 天', 50, g.WHITE, 'title', True)
    g.center(d, 450, 300, '微信 Q4 分账：每天只给一部', 19, sub, 'body', True)
    for i, (width, color) in enumerate([(200, g.RUST), (146, g.TEAL), (96, g.GOLD)]):
        yy = 110 + i * 62
        d.rounded_rectangle((44, yy, 44 + width, yy + 26), radius=6, fill=color)
    for i, width in enumerate((176, 128, 86)):
        d.rounded_rectangle((856 - width, 116 + i * 62, 856, 138 + i * 62), radius=6, fill='#574e45')
    return im


if __name__ == '__main__':
    for fn, name, tag in [
        (fig_027, '027_图1_三档分账_1080.png', 'fig27'),
    ]:
        im = fn()
        g.check_glyphs()
        g.save(im, name, tag)
    im = cover()
    g.check_glyphs()
    g.save(im, '封面_027_A_最高100只给7天_900x383.png', 'cover27')
    print('PASS: 断言全过')
