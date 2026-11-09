#!/usr/bin/env python3
"""088《微短剧专项治理启动：换名重发被点名》配图与封面。纯本地 Pillow，零扣费。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def scope():
    im, d = page('两个月治理，管两端', '总局 11-06 部署 / 治理期 11-01 至 12 月底', '01', 1020)

    d.line((110, 268, 970, 268), fill=LINE, width=4)
    d.line((110, 268, 300, 268), fill=RUST, width=4)
    for x, label, sub, color in [
        (110, '11-01', '治理开始', RUST),
        (300, '11-06', '官网发布通知', INK),
        (970, '12 月底', '治理结束', TEAL),
    ]:
        d.ellipse((x - 8, 260, x + 8, 276), fill=color)
        lx = min(max(x - 30, 72), 920)
        put(d, lx, 226, label, 20, color, 'bold', 1008)
        sx = min(max(x - 40, 72), 860)
        put(d, sx, 292, sub, 15, DIM, 'body', 1008)

    d.rounded_rectangle((72, 352, 1008, 618), radius=12, fill=WHITE)
    put(d, 100, 374, '内容创作方面', 26, RUST, 'bold', 980)
    put(d, 100, 420, '五类低俗不良内容', 16, DIM, 'body', 980)

    chips1 = [('儿童类不良', 132), ('软色情擦边', 132), ('极端对立', 110), ('拜金主义', 110)]
    x = 100
    for label, w in chips1:
        d.rounded_rectangle((x, 450, x + w, 492), radius=8, outline=RUST, width=2)
        put(d, x + 16, 460, label, 20, INK, 'bold', x + w - 8)
        x += w + 22
    d.rounded_rectangle((100, 506, 386, 548), radius=8, outline=RUST, width=2)
    put(d, 116, 516, '严重违背家庭伦理道德', 20, INK, 'bold', 378)

    put(d, 420, 508, '两条合规：特殊题材备案审核；“盗脸”“偷声”', 18, TEAL, 'bold', 992)
    put(d, 420, 540, 'AI 人脸、声音须有授权记录', 14, DIM, 'body', 992)

    d.rounded_rectangle((72, 640, 1008, 846), radius=12, fill=WHITE)
    put(d, 100, 662, '传播推广方面', 26, TEAL, 'bold', 980)
    rows = [
        ('片名、宣推素材、弹幕评论、引流片段中的低俗内容', RUST),
        ('同一剧集换片名、换主角姓名，改头换面反复播出', RUST),
        ('首页首屏首推与重点榜单同质化，提升算法多样性', INK),
    ]
    y = 708
    for text, color in rows:
        d.ellipse((102, y + 8, 112, y + 18), fill=color)
        put(d, 128, y, text, 18, INK, 'body', 992)
        y += 42

    d.rounded_rectangle((72, 866, 1008, 940), radius=10, fill=INK)
    put(d, 100, 880, '执法基数：今年以来累计下架 7.5 万部', 21, '#f0c588', 'bold', 986)
    put(d, 100, 912, '处置违规账号 1500 余个（总局披露累计数，非本轮成果）', 14, '#bdb3a1', 'body', 986)

    footer(d, 952, [
        '来源：广电总局官网 2026-11-06 19:47 通知（网络视听节目管理司）。',
    ])
    return im


def checks():
    im, d = page('四个自查动作', '在制项目对照 / 窗口期至 12 月底', '02', 1020)

    items = [
        ('01', '剧本', '对照五类内容清单过一遍；儿童题材、擦边桥段重点看', RUST),
        ('02', '宣推', '片名、海报、切片、引流片段按正片标准审，不豁免', GOLD),
        ('03', '重发', '停掉换片名、换主角名的重发；旧剧重推走备案审核', TEAL),
        ('04', '授权', 'AI 人脸、声音授权记录补齐；特殊题材备案审核确认', INK),
    ]
    y = 240
    for num, label, desc, color in items:
        d.rounded_rectangle((72, y, 1008, y + 128), radius=10, fill=WHITE)
        put(d, 100, y + 24, num, 34, color, 'title', 180)
        put(d, 190, y + 22, label, 24, INK, 'bold', 300)
        put(d, 190, y + 66, desc, 16, DIM, 'body', 986)
        y += 144

    d.rounded_rectangle((72, 818, 1008, 918), radius=12, fill=INK)
    put(d, 100, 834, '治理压实平台主体责任，标准传导到上传环节。', 21, '#f0c588', 'bold', 986)
    put(d, 100, 876, '两个月窗口，对在制项目是自查期；上架前对清单，比下架划算。', 15, '#bdb3a1', 'body', 986)

    footer(d, 934, [
        '来源：广电总局 2026-11-06 通知；四动作按通知归纳，非官方表述。',
        '“跟风题材首推机会变少”为本号对算法多样性要求的推断。',
    ])
    return im


def cover_088():
    base.TEXT_BOXES = []
    W, H = 900, 383
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((36, 34, 48, 56), fill=RUST)
    put(d, 62, 32, '一人短剧厂牌', 20, '#c9c0b0', 'bold', 520)

    put(d, 36, 76, '总局专项治理 · 两个月', 16, GOLD, 'bold', 520)
    put(d, 32, 104, '换名重发', 44, '#f6efe2', 'title', 520)
    put(d, 32, 158, '被明确点名', 40, '#e07a5f', 'title', 520)
    put(d, 36, 224, '片名 · 宣推 · 弹幕 · 引流同查', 16, '#e8dfcf', 'bold', 540)
    put(d, 36, 256, '创作端五类内容 + 盗脸偷声', 15, '#bdb3a1', 'body', 540)
    put(d, 36, 292, '治理期 11-01 至 12 月底', 14, '#bdb3a1', 'body', 540)
    put(d, 36, 330, 'AI 微短剧是直接对象', 13, '#8f8576', 'body', 540)

    d.line((560, 70, 560, 330), fill='#4a443b', width=2)

    put(d, 590, 76, '执法基数 · 今年以来累计', 14, GOLD, 'bold', 870)
    put(d, 590, 104, '7.5 万部', 34, '#f6efe2', 'title', 870)
    put(d, 590, 152, '违规微短剧下架', 15, '#bdb3a1', 'body', 870)
    put(d, 590, 190, '1500 余个', 26, '#e07a5f', 'title', 870)
    put(d, 590, 230, '违规账号处置', 15, '#bdb3a1', 'body', 870)
    put(d, 590, 274, '非本轮两个月成果', 13, '#8f8576', 'body', 870)
    put(d, 590, 330, '来源：总局官网 11-06', 12, '#8f8576', 'body', 870)

    im.save(OUT / '封面_088_专项治理_900x383.png')
    print('封面 088 OK', im.size)


if __name__ == '__main__':
    im = scope()
    im.save(OUT / '088_图1_两端_1080.png')
    print('图1 OK', im.size)
    im = checks()
    im.save(OUT / '088_图2_自查_1080.png')
    print('图2 OK', im.size)
    cover_088()