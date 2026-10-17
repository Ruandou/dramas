#!/usr/bin/env python3
"""025/026 配图与封面（复用 _gen_023 版式与断言）。"""
import _gen_023 as g
from PIL import Image, ImageDraw


def page(title, subtitle, number, height, head):
    g.HEAD = head
    return g.page(title, subtitle, number, height)


def fig_025():
    im, d = page('五档支持，两条时限', '沪文旅规〔2026〕1 号 · 逐条摘原文', '01', 1260, '一人短剧厂牌 / 上海政策')
    rows = [
        ('智能体项目', '研发投入 20%，最高 1000 万', g.RUST),
        ('优秀微短剧（含 AI）', '最高 300 万；城市形象类 +50%', g.RUST),
        ('优质厂牌', '一次性最高 200 万', g.GOLD),
        ('出海发行', '最高 50 万', g.GOLD),
        ('剧本（国家级入选）', '一次性 5 万', g.TEAL),
    ]
    y = 240
    for name, note, color in rows:
        d.rounded_rectangle((72, y, 1008, y + 118), radius=12, fill=g.WHITE)
        d.rounded_rectangle((72, y, 80, y + 118), radius=4, fill=color)
        g.put(d, 104, y + 20, name, 28, g.INK, 'bold', 980)
        g.put(d, 104, y + 66, note, 23, color if color != g.TEAL else g.INK, 'body', 980)
        y += 134
    d.rounded_rectangle((72, y + 10, 1008, y + 160), radius=14, fill=g.INK)
    g.put(d, 104, y + 34, '备案时限：规划 2 个工作日 / 上线 5 个工作日', 25, '#f0c588', 'bold', 980)
    g.put(d, 104, y + 82, '原文：工作日随报随审。另：算力租用、模型 API、语料采购均在支持范围（未写比例）。', 21, g.WHITE, right=980)
    g.footer(d, y + 200, [
        'A 级：沪文旅规〔2026〕1 号附件原文（签发 2026-05-20，施行即印发之日）。',
        '「10-15 挂网」是全文首次公开，不是新政。',
    ])
    return im


def fig_026():
    im, d = page('五类问题，三类撞上短剧桥段', '「清朗·整治短视频虚假人设乱象」· 2026-09-30 起两个月', '01', 1360, '一人短剧厂牌 / 清朗行动')
    items = [
        ('① 假扮弱势群体', '摆拍送外卖、假扮农户助农、假扮病残', '低', g.TEAL),
        ('② 虚构职业资质', '冒充医生律师教师、绕过资质认证', '中', g.GOLD),
        ('③ 利用 AI 仿冒人物', 'AI 合成音视频假冒公众人物、影子账号', '高', g.RUST),
        ('④ 鼓吹奢靡迷信', '点名「AI 霸总」「养生大师」诱骗老年人', '高', g.RUST),
        ('⑤ 编造冲突剧情', '家暴、辍学、绑架、地域矮化', '高', g.RUST),
    ]
    y = 240
    for name, note, level, color in items:
        d.rounded_rectangle((72, y, 1008, y + 132), radius=12, fill=g.WHITE)
        d.rounded_rectangle((72, y, 80, y + 132), radius=4, fill=color)
        g.put(d, 104, y + 20, name, 27, g.INK, 'bold', 800)
        g.put(d, 104, y + 68, note, 22, g.DIM, right=940)
        d.rounded_rectangle((920, y + 22, 984, y + 58), radius=8, fill=color)
        g.put(d, 934, y + 28, level, 22, g.WHITE, 'bold', 984)
        y += 150
    d.rounded_rectangle((72, y + 8, 1008, y + 190), radius=14, fill=g.INK)
    g.put(d, 104, y + 30, '原文：不得借标签规避治理', 26, '#f0c588', 'bold', 980)
    g.put(d, 104, y + 76, '「不得借已标注虚构演绎、AI生成、营销、转载、个人观点等内容标签', 21, g.WHITE, right=980)
    g.put(d, 104, y + 112, '及无不良导向声明规避网络生态治理相关要求」', 21, g.WHITE, right=980)
    g.put(d, 104, y + 150, '标识是义务，不是免责。', 23, '#f0c588', 'bold', 980)
    g.footer(d, y + 230, ['A 级：中央网信办专项行动通知原文（2026-09-30）。风险等级为本号按原文与短剧桥段的重叠度自评。'])
    return im


def cover(title_lines, foot, tag, dark=False):
    g.TEXT_BOXES = []
    bg = g.INK if dark else g.PAPER
    im = Image.new('RGB', (900, 383), bg)
    d = ImageDraw.Draw(im)
    sub = '#bdb3a1' if dark else g.DIM
    g.put(d, 33, 28, '一人短剧厂牌', 19, sub, right=900)
    g.put(d, 744, 28, tag, 18, sub, right=875)
    y = 70
    for i, (text, size, color, kind) in enumerate(title_lines):
        g.center(d, 450, y, text, size, color, kind, True)
        y += int(size * 1.45)
    g.center(d, 450, 300, foot, 19, sub, 'body', True)
    for i, (width, color) in enumerate([(200, g.RUST), (146, g.TEAL), (96, g.GOLD)]):
        yy = 110 + i * 62
        d.rounded_rectangle((44, yy, 44 + width, yy + 26), radius=6, fill=color)
    for i, width in enumerate((176, 128, 86)):
        d.rounded_rectangle((856 - width, 116 + i * 62, 856, 138 + i * 62), radius=6,
                            fill='#574e45' if dark else '#c2b7a6')
    return im


if __name__ == '__main__':
    for fn, name, tag in [
        (fig_025, '025_图1_五档支持_1080.png', 'fig25'),
        (fig_026, '026_图1_五类问题_1080.png', 'fig26'),
    ]:
        im = fn()
        g.check_glyphs()
        g.save(im, name, tag)
    for fn, name, tag, args in [
        (cover, '封面_025_A_最高300万_900x383.png', 'cover25a',
         ([('上海给 AI 微短剧', 42, g.INK, 'title'), ('最高 300 万', 52, g.RUST, 'title')], '这份文件 5 月就生效了', '上海政策', False)),
        (cover, '封面_026_A_标了也不免责_900x383.png', 'cover26a',
         ([('标了「AI生成」', 44, g.WHITE, 'title'), ('也不免责', 52, '#f0c588', 'title')], '网信办把话写死了', '清朗行动', True)),
    ]:
        im = fn(*args)
        g.check_glyphs()
        g.save(im, name, tag)
    print('PASS: 断言全过')
