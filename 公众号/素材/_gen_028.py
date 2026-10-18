#!/usr/bin/env python3
"""028《88 集变 125 集》配图与封面（复用 _gen_023 版式与断言）。"""
import _gen_023 as g
from PIL import Image, ImageDraw


def page(title, subtitle, number, height, head):
    g.HEAD = head
    return g.page(title, subtitle, number, height)


def fig_timeline():
    im, d = page('四天时间线：谁在什么时候说了什么', '2026-10-15 晚 至 10-19 · 北京日报 / 贝壳财经', '01', 1180, '一人短剧厂牌 / 版权链')
    rows = [
        ('10-15 晚', '用户发现《好一个乖女孩》在绿泡泡', '点开发现是红果的《好一个乖乖女》，集数与主演署名都变了', g.RUST),
        ('10-16', '贝壳财经检索：页面「已下架」', '但该剧仍出现在绿泡泡的搜索结果里', g.GOLD),
        ('10-16', '出品方：与红果签的是独家', '「哪敢一剧两卖」；抖音版权中心称全权独家、未授权', g.TEAL),
        ('10-16 中午', '该剧在绿泡泡搜不到', '据后续检索，此前已无法搜索到', g.GOLD),
        ('10-18 核查', '腾讯仍无公开回应', '争议没有司法结论；本文不对是否侵权下判断', g.DIM),
    ]
    y = 240
    for date, head, note, color in rows:
        d.rounded_rectangle((72, y, 1008, y + 138), radius=14, fill=g.WHITE)
        d.rounded_rectangle((72, y, 80, y + 138), radius=4, fill=color)
        g.put(d, 104, y + 24, date, 24, color, 'bold', 980)
        g.put(d, 286, y + 22, head, 28, g.INK, 'bold', 980)
        g.put(d, 286, y + 74, note, 21, g.DIM, right=980)
        y += 158
    g.footer(d, y + 18, [
        'B 级：北京日报/长安街知事（2026-10-16）、贝壳财经（2026-10-16）报道；腾讯未回应截至 10-18 核查。',
        '时间线只写报道能对上时点的动作；上传主体、是否同一版本均未证实。',
    ])
    return im


def fig_fields():
    im, d = page('五个字段：改了什么，没改什么', '同一部剧，两个平台', '02', 1180, '一人短剧厂牌 / 版权链')
    rows = [
        ('剧名', '好一个乖乖女', '好一个乖女孩'),
        ('集数', '88 集', '125 集（+42%）'),
        ('主演署名', '柯淳、余茵', '周书容、刘忠正'),
        ('平台', '红果', '绿泡泡'),
        ('热度', '—', '352.3 万（页面显示）'),
    ]
    d.rounded_rectangle((72, 240, 1008, 300), radius=12, fill=g.INK)
    g.put(d, 104, 256, '字段', 23, g.WHITE, 'bold', 320)
    g.put(d, 360, 256, '红果', 23, g.WHITE, 'bold', 650)
    g.put(d, 700, 256, '绿泡泡', 23, g.WHITE, 'bold', 980)
    y = 300
    for i, (k, a, b) in enumerate(rows):
        fill = g.WHITE if i % 2 == 0 else '#ece5d8'
        d.rounded_rectangle((72, y, 1008, y + 112), radius=10, fill=fill)
        g.put(d, 104, y + 22, k, 25, g.DIM, 'bold', 320)
        g.put(d, 360, y + 20, a, 25, g.INK, right=660)
        g.put(d, 700, y + 20, b, 25, g.RUST, 'bold', 980)
        y += 112
    d.rounded_rectangle((72, y + 24, 1008, y + 150), radius=14, fill=g.INK)
    g.put(d, 104, y + 46, '报道称：内容「只做了拆集」', 27, '#f0c588', 'bold', 980)
    g.put(d, 104, y + 96, '改名、拆集、换署名，改变的是包装，不是作品的表达。', 21, g.WHITE, right=980)
    g.footer(d, y + 184, [
        'B 级：北京日报/长安街知事（2026-10-16）报道；页面热度 352.3 万口径不明，不能当播放量。',
        '+42% =（125-88）÷88，本号自算。',
    ])
    return im


def fig_chain():
    im, d = page('授权链：三个节点，三处可能断', '平台说「第三方提供」，不等于权利链干净', '03', 1040, '一人短剧厂牌 / 版权链')
    boxes = [
        (72, 250, 320, 400, g.TEAL, '版权方 / 出品方', '于今无量'),
        (392, 250, 640, 400, g.GOLD, '原平台', '红果（独家）'),
        (712, 250, 1008, 400, g.RUST, '新平台', '绿泡泡（第三方提供）'),
    ]
    for x1, y1, x2, y2, color, head, note in boxes:
        d.rounded_rectangle((x1, y1, x2, y2), radius=14, fill=g.WHITE)
        d.rounded_rectangle((x1, y1, x2, y1 + 14), radius=7, fill=color)
        g.put(d, x1 + 24, y1 + 44, head, 25, color, 'bold', x2 - 10)
        g.put(d, x1 + 24, y1 + 92, note, 24, g.INK, right=x2 - 10)
    for x1, x2 in [(320, 392), (640, 712)]:
        d.line((x1 + 8, 316, x2 - 8, 316), fill=g.DIM, width=4)
        d.polygon([(x2 - 8, 316), (x2 - 22, 308), (x2 - 22, 324)], fill=g.DIM)
    g.put(d, 330, 276, '独家', 19, g.DIM, right=384)
    g.put(d, 650, 276, '授权？', 19, g.RUST, 'bold', 712)
    d.rounded_rectangle((72, 460, 1008, 650), radius=14, fill=g.INK)
    g.put(d, 104, 484, '断点一：谁授权给绿泡泡？', 25, '#f0c588', 'bold', 980)
    g.put(d, 104, 524, '报道里出品方否认授权；上传主体未公布。', 21, g.WHITE, right=980)
    g.put(d, 104, 568, '断点二：授权是否覆盖改名、拆集、换署名？', 25, '#f0c588', 'bold', 980)
    g.put(d, 104, 608, '合同未公开，外界看不到权利范围。', 21, g.WHITE, right=980)
    d.rounded_rectangle((72, 686, 1008, 824), radius=14, fill='#e9e3d8')
    g.put(d, 104, 708, '断点三：平台接到通知后多久下架？', 25, g.RUST, 'bold', 980)
    g.put(d, 104, 754, '10-16 中午已搜不到；平台责任以司法认定为准。', 21, g.INK, right=980)
    g.footer(d, 858, [
        '示意图：角色与箭头为本号据报道重绘，非平台官方流程图。',
        '是否侵权、谁承担责任，本文不下结论。',
    ])
    return im


def fig_contract():
    im, d = page('签约前，逐条对照这 5 句', '少一句，出事时就少一条依据', '04', 1260, '一人短剧厂牌 / 合同清单')
    rows = [
        ('01', '权利清单', '信息网络传播权、改编权、汇编权、剪辑/拆集权，逐项勾，不写「相关权利」。'),
        ('02', '平台范围与独家', '写平台名：绿泡泡、红果、抖音、快手；独家期限、到期下架。'),
        ('03', '转授权', '能否再授权给第三方内容提供方？要不要书面同意？收益怎么分？'),
        ('04', '署名', '剧名、主演、片头片尾、海报；任何修改需书面同意，换名换署名算违约。'),
        ('05', '违约与下架', '通知发给谁、多少小时内下架、违约金、维权费用谁承担。'),
    ]
    y = 240
    for num, head, note in rows:
        d.rounded_rectangle((72, y, 1008, y + 156), radius=14, fill=g.WHITE)
        g.put(d, 104, y + 30, num, 30, g.RUST, 'number', 180)
        g.put(d, 200, y + 26, head, 29, g.INK, 'bold', 980)
        g.paragraph(d, 200, y + 78, note, width=776, size=21, color=g.DIM, leading=30)
        y += 176
    g.footer(d, y + 10, [
        '本清单是合同检查项，不是法律意见；具体条款请由执业律师按项目审阅。',
        '优先把「平台名 + 权利项 + 下架时限」写死，这三项最容易在争议里说不清。',
    ])
    return im


def fig_steps():
    im, d = page('发现被「换皮」，先做这 4 步', '顺序不能反：先固定证据，再通知', '05', 1080, '一人短剧厂牌 / 维权动作')
    rows = [
        ('1', '取证', '录屏，不要只截图：URL、账号、时间、播放页一起录；重要项目做公证或可信时间戳。'),
        ('2', '对照', '剧名、集数、主演署名、关键剧情、片头片尾，做一张对照表。'),
        ('3', '双向通知', '同时通知原平台（权利方）与上架平台，要求下架并保留回执。'),
        ('4', '追溯', '查上传主体与第三方提供方；若是被授权方转授权，回头翻合同第三句。'),
    ]
    y = 240
    for num, head, note in rows:
        d.rounded_rectangle((72, y, 1008, y + 150), radius=14, fill=g.WHITE)
        d.ellipse((104, y + 36, 176, y + 108), fill=g.INK)
        g.put(d, 122, y + 50, num, 32, g.WHITE, 'number', 168)
        g.put(d, 208, y + 26, head, 30, g.RUST, 'bold', 980)
        g.paragraph(d, 208, y + 78, note, width=768, size=21, color=g.DIM, leading=30)
        y += 170
    g.footer(d, y + 10, [
        '取证优先于投诉：没有可用证据，通知很容易被「未发现」挡回来。',
        '本文只给动作顺序，不构成法律意见。',
    ])
    return im


def fig_evidence():
    im, d = page('证据分级：哪些能当事实', 'B 级媒体报道 / C 级单源 / 未验证', '06', 1120, '一人短剧厂牌 / 证据边界')
    blocks = [
        (g.TEAL, 'B 级｜媒体报道', [
            '北京日报/长安街知事、贝壳财经（2026-10-16）：发现过程、88→125 集、主演署名、回应。',
            '腾讯未回应：截至 10-18 核查，公开报道中未见。',
        ]),
        (g.GOLD, 'C 级｜历史数据 / 单源', [
            '50 亿播放（公开资料，2026-07）、7 天分账 400 万（2025-02 报道）。',
            '红果日活近 2 亿、月活约 3.68 亿（媒体引述，未取财报口径）。',
        ]),
        (g.RUST, '未验证｜不能当结论', [
            '上传主体是谁、是否同一版本、是否构成侵权。',
            '绿泡泡当前检索状态：本文未再复核。',
        ]),
    ]
    y = 240
    for color, head, lines in blocks:
        d.rounded_rectangle((72, y, 1008, y + 236), radius=14, fill=g.WHITE)
        d.rounded_rectangle((72, y, 80, y + 236), radius=4, fill=color)
        g.put(d, 104, y + 22, head, 28, color, 'bold', 980)
        yy = y + 70
        for line in lines:
            yy = g.paragraph(d, 104, yy, line, width=872, size=21, color=g.INK, leading=30) + 10
        y += 258
    g.footer(d, y + 6, [
        '分级只描述本号能核到的证据强度，不代表事件真假。',
        '下判断之前，先看这句话是「谁说的」、有没有第二个独立来源。',
    ])
    return im


def cover_a():
    g.TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), g.INK)
    d = ImageDraw.Draw(im)
    sub = '#bdb3a1'
    g.put(d, 33, 28, '一人短剧厂牌', 19, sub, right=900)
    g.put(d, 744, 28, '版权链', 18, sub, right=875)
    g.center(d, 450, 78, '88 集 → 125 集', 52, '#f0c588', 'title', True)
    g.center(d, 450, 164, '爆款剧被「换皮」', 42, g.WHITE, 'title', True)
    g.center(d, 450, 300, '改名拆集上绿泡泡 · 合同缺哪几句', 19, sub, 'body', True)
    for i, (width, color) in enumerate([(200, g.RUST), (146, g.TEAL), (96, g.GOLD)]):
        yy = 110 + i * 62
        d.rounded_rectangle((44, yy, 44 + width, yy + 26), radius=6, fill=color)
    for i, width in enumerate((176, 128, 86)):
        d.rounded_rectangle((856 - width, 116 + i * 62, 856, 138 + i * 62), radius=6, fill='#574e45')
    return im


def cover_b():
    g.TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), g.PAPER)
    d = ImageDraw.Draw(im)
    g.put(d, 33, 28, '一人短剧厂牌', 19, g.DIM, right=900)
    g.put(d, 744, 28, '合同清单', 18, g.DIM, right=875)
    g.center(d, 450, 72, '签约前', 24, g.TEAL, 'bold', True)
    g.center(d, 450, 108, '先写死这 5 句', 48, g.INK, 'title', True)
    d.line((300, 192, 600, 192), fill=g.LINE, width=2)
    g.center(d, 450, 214, '平台范围 · 转授权 · 署名', 26, g.RUST, 'bold', True)
    g.center(d, 450, 262, '少一句，出事时就少一条依据', 20, g.DIM, 'body', True)
    g.center(d, 450, 310, '88 集变 125 集的教训', 19, g.DIM, 'body', True)
    for i, (width, color) in enumerate([(180, g.RUST), (124, g.TEAL), (74, g.GOLD)]):
        y = 112 + i * 60
        d.rounded_rectangle((44, y, 44 + width, y + 26), radius=6, fill=color)
    for i, width in enumerate((160, 112, 78)):
        d.rounded_rectangle((856 - width, 118 + i * 60, 856, 140 + i * 60), radius=6, fill='#c2b7a6')
    return im


if __name__ == '__main__':
    for fn, name, tag in [
        (fig_timeline, '028_图1_四天时间线_1080.png', 'fig1'),
        (fig_fields, '028_图2_五个字段对照_1080.png', 'fig2'),
        (fig_chain, '028_图3_授权链断点_1080.png', 'fig3'),
        (fig_contract, '028_图4_合同五句清单_1080.png', 'fig4'),
        (fig_steps, '028_图5_四步取证_1080.png', 'fig5'),
        (fig_evidence, '028_图6_证据分级_1080.png', 'fig6'),
    ]:
        im = fn()
        g.check_glyphs()
        g.save(im, name, tag)
    for fn, name, tag in [
        (cover_a, '封面_028_A_88集变125集_900x383.png', 'coverA'),
        (cover_b, '封面_028_B_合同五句_900x383.png', 'coverB'),
    ]:
        im = fn()
        g.check_glyphs()
        g.save(im, name, tag)
    print('PASS: 断言全过')
