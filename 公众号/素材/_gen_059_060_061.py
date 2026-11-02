#!/usr/bin/env python3
"""059《Q3 发行许可》/ 060《DramaBox 合并》/ 061《即梦折扣》配图与封面。纯本地 Pillow。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def arrow(d, x1, y1, x2, y2, color=GREY):
    d.line((x1, y1, x2, y2), fill=color, width=2)
    if x1 == x2:
        d.polygon([(x2, y2), (x2 - 8, y2 - 12), (x2 + 8, y2 - 12)], fill=color)


# ---------------- 059 ----------------

def q3_scope():
    im, d = page('338 不是下降，是口径变了', '广电总局发行许可 / 2026 Q1—Q3 / 单位：部', '01', 1040)

    put(d, 72, 246, 'Q2 通告（四类）', 24, INK, 'bold', 700)
    put(d, 720, 246, '367 部', 28, RUST, 'bold', 1008)
    x, y, w, h = 72, 292, 936, 58
    segs2 = [(25, GREY, '网络剧 25'), (45, GOLD, '网络电影 45'), (159, RUST, '微短剧 159'), (138, TEAL, '动画 138')]
    cx = x
    for val, color, label in segs2:
        bw = w * val / 367
        d.rectangle((cx, y, cx + bw, y + h), fill=color)
        cx += bw

    put(d, 72, 392, 'Q3 通告（两类）', 24, INK, 'bold', 700)
    put(d, 720, 392, '338 部', 28, RUST, 'bold', 1008)
    x, y, w, h = 72, 438, 936, 58
    segs3 = [(158, RUST, '微短剧 158'), (180, TEAL, '动画 180')]
    cx = x
    for val, color, label in segs3:
        bw = w * val / 338
        d.rectangle((cx, y, cx + bw, y + h), fill=color)
        put(d, cx + 16, y + 14, label, 20, WHITE, 'bold', cx + bw - 10)
        cx += bw

    # Q2 legend
    put(d, 72, 520, 'Q2 四类拆开', 20, DIM, 'bold', 1008)
    for i, (val, color, label) in enumerate(segs2):
        lx = 72 + (i % 4) * 236
        ly = 558
        d.rectangle((lx, ly + 5, lx + 16, ly + 21), fill=color)
        put(d, lx + 26, ly, label, 20, INK, 'body', lx + 230)

    d.line((72, 620, 1008, 620), fill=LINE, width=2)
    put(d, 72, 646, '同口径合计（微短剧 + 动画片）', 22, DIM, 'bold', 1008)

    nums = [('Q1', '269'), ('Q2', '297'), ('Q3', '338')]
    for i, (q, n) in enumerate(nums):
        cx = 100 + i * 300
        put(d, cx, 700, q, 22, DIM, 'bold', cx + 100)
        put(d, cx, 734, n, 64, RUST if q == 'Q3' else INK, 'number', cx + 180)
        if i < 2:
            put(d, cx + 170, 752, '→', 36, GREY, 'body', cx + 240)

    d.rounded_rectangle((72, 850, 1008, 918), radius=12, fill=INK)
    put(d, 100, 866, '338 对 297 多 41 部；对 269 多 69 部。', 24, '#f0c588', 'bold', 986)
    put(d, 100, 898, '把 338 和 367 相减，会得到一个不存在的「减少 29 部」。', 18, '#bdb3a1', 'body', 986)

    footer(d, 940, [
        '来源：广电总局 2026 年 Q1、Q2、Q3 发行许可通告。',
        'Q3 通告只含微短剧、网络动画片；同口径合计为本号复算。',
    ])
    return im


def q3_trend():
    im, d = page('微短剧持平，动画片多了 42 部', 'Q1—Q3 发行许可 / 部数与集数 / 本号按通告复算', '02', 1050)

    # 左：部数
    put(d, 72, 238, '部数', 24, INK, 'bold', 500)
    put(d, 72, 274, '微短剧 / 动画片', 17, DIM, 'body', 500)
    base_y, max_h = 684, 340
    works = [('Q1', 144, 125), ('Q2', 159, 138), ('Q3', 158, 180)]
    for i, (q, micro, anim) in enumerate(works):
        gx = 92 + i * 138
        for j, (val, color) in enumerate([(micro, RUST), (anim, TEAL)]):
            h = max_h * val / 180
            bx = gx + j * 52
            d.rectangle((bx, base_y - h, bx + 40, base_y), fill=color)
            put(d, bx - 4, base_y - h - 30, str(val), 19, INK, 'number', bx + 48)
        put(d, gx, base_y + 12, q, 20, DIM, 'bold', gx + 100)

    # 右：集数
    put(d, 560, 238, '集数', 24, INK, 'bold', 1008)
    put(d, 560, 274, '微短剧 / 动画片', 17, DIM, 'body', 1008)
    eps = [('Q1', 5667, 1229), ('Q2', 5396, 1419), ('Q3', 5369, 1731)]
    for i, (q, micro, anim) in enumerate(eps):
        gx = 580 + i * 138
        for j, (val, color) in enumerate([(micro, RUST), (anim, TEAL)]):
            h = max_h * val / 5667
            bx = gx + j * 52
            d.rectangle((bx, base_y - h, bx + 40, base_y), fill=color)
            put(d, bx - 10, base_y - h - 30, f'{val:,}', 17, INK, 'number', bx + 54)
        put(d, gx, base_y + 12, q, 20, DIM, 'bold', gx + 100)

    for lx, color, label in [(72, RUST, '微短剧'), (190, TEAL, '动画片')]:
        d.rectangle((lx, 730, lx + 16, 746), fill=color)
        put(d, lx + 26, 724, label, 20, INK, 'body', lx + 150)

    d.rounded_rectangle((72, 790, 1008, 884), radius=12, fill=WHITE)
    put(d, 100, 806, '动画片部数占比：46.5% → 46.5% → 53.3%', 21, INK, 'bold', 986)
    put(d, 100, 842, '动画片集数占比：17.8% → 20.8% → 24.4%', 21, DIM, 'body', 986)

    footer(d, 920, [
        '来源：广电总局 2026 年 Q1、Q2、Q3 发行许可通告。',
        '占比与增减为本号按通告部数、集数直接复算。',
    ])
    return im


def q3_genre():
    im, d = page('都市 -24 部，革命 +19 部', 'Q3 对 Q2 微短剧题材变化 / 按部数 / 本号复算', '03', 1120)

    put(d, 72, 236, '题材', 20, DIM, 'bold', 250)
    put(d, 850, 236, '部数变化', 20, DIM, 'bold', 1008)

    rows = [
        ('革命', 19), ('公安', 8), ('传记', 4), ('司法', 2),
        ('传奇', 1), ('农村', 1), ('科幻', 1), ('宫廷', -1),
        ('青少', -1), ('武打', -1), ('其他', -13), ('都市', -24),
    ]
    center = 540
    max_w = 250
    y = 280
    d.line((center, 264, center, 950), fill=LINE, width=2)
    for name, val in rows:
        w = max_w * abs(val) / 24
        color = RUST if val < 0 else TEAL
        if val > 0:
            d.rectangle((center, y + 8, center + w, y + 42), fill=color)
        else:
            d.rectangle((center - w, y + 8, center, y + 42), fill=color)
        put(d, 72, y + 6, name, 23, INK, 'bold', 250)
        text = f'+{val}' if val > 0 else str(val)
        put(d, 850, y + 6, text, 24, color, 'number', 1008)
        y += 56

    put(d, 72, 982, '集数变化：革命 +791、公安 +190、司法 +79；都市 -968、其他 -571。', 20, DIM, 'body', 1008)
    footer(d, 1040, [
        '来源：广电总局 2026 年 Q2、Q3 发行许可通告；题材为通告原始分类。',
        '本图只列部数变化绝对值 ≥1 的题材；增减为本号直接相减。',
    ])
    return im


def cover_059():
    base.TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, '#bdb3a1', right=420)
    put(d, 33, 60, '广电总局 · 2026 Q3', 18, '#f0c588', 'bold', 470)
    put(d, 28, 92, '338', 104, '#efe6d6', 'title', 470)
    put(d, 36, 210, '部 / 7,100 集', 24, '#bdb3a1', 'bold', 470)
    put(d, 36, 252, '微短剧 158 + 动画 180', 20, '#efe6d6', 'body', 470)
    put(d, 36, 300, '不是下降，是只算了两类', 17, '#8f8576', 'body', 470)

    d.line((490, 62, 490, 324), fill='#4a443c', width=1)
    put(d, 528, 96, '同口径三季', 18, '#bdb3a1', 'body', 880)
    put(d, 528, 132, '269 → 297 → 338', 30, '#f0c588', 'bold', 880)
    put(d, 528, 186, 'Q3 对 Q2：+13.8%', 22, '#8fc0b4', 'body', 880)
    put(d, 528, 226, '把 338 和 367 相减', 18, '#efe6d6', 'body', 880)
    put(d, 528, 252, '会得到一个不存在的', 18, '#efe6d6', 'body', 880)
    put(d, 528, 278, '「减少 29 部」', 26, '#e0705a', 'bold', 880)
    put(d, 528, 320, '先看通告标题，再看数字', 15, '#8f8576', 'body', 880)
    return im


# ---------------- 060 ----------------

def merger_ranks():
    im, d = page('两个平台，一组排名', 'Sensor Tower / 2026 Q1 / 短剧 App', '01', 850)

    cards = [
        (72, 258, 'DramaBox · 内购收入', '#1', '第 1 名', RUST),
        (540, 258, 'GoodShort · 内购收入', '#5', '第 5 名', GOLD),
        (72, 458, 'DramaBox · 下载', '#4', '第 4 名', TEAL),
        (540, 458, 'GoodShort · 下载', '#10', '第 10 名', GREY),
    ]
    for cx, cy, label, rank, note, color in cards:
        d.rounded_rectangle((cx, cy, cx + 396, cy + 168), radius=12, fill=WHITE)
        put(d, cx + 24, cy + 18, label, 19, DIM, 'bold', cx + 380)
        put(d, cx + 22, cy + 56, rank, 62, color, 'title', cx + 200)
        put(d, cx + 220, cy + 76, note, 22, INK, 'bold', cx + 380)
        put(d, cx + 24, cy + 132, 'Sensor Tower 2026 Q1', 15, DIM, 'body', cx + 380)

    d.rounded_rectangle((72, 672, 1008, 742), radius=12, fill=INK)
    put(d, 100, 688, '排名是 Q1 的存量，不是 10-31 合并后的表现。', 22, '#f0c588', 'bold', 986)
    put(d, 100, 720, '合并后的用户、收入、下载，公开报道里都没有。', 17, '#bdb3a1', 'body', 986)

    footer(d, 770, [
        '来源：上海证券报 2026-10-31 引 Sensor Tower 2026 Q1 数据。',
        '排名口径为 App 内购收入与下载量，不代表市场份额或利润。',
    ])
    return im


def merger_who():
    im, d = page('谁在台上，什么还没说', '合并后的管理架构 / 截至 2026-10-31', '02', 980)

    # 左：两张来源卡
    d.rounded_rectangle((72, 250, 420, 340), radius=10, fill=WHITE)
    put(d, 96, 266, '点众科技', 24, INK, 'bold', 400)
    put(d, 96, 302, '孵化 DramaBox', 18, DIM, 'body', 400)

    d.rounded_rectangle((72, 370, 420, 460), radius=10, fill=WHITE)
    put(d, 96, 386, '新阅时代', 24, INK, 'bold', 400)
    put(d, 96, 422, '推出 GoodShort', 18, DIM, 'body', 400)

    # 两条来源分别汇入合并框，避免把「点众→新阅」画成上下级
    for sy, gy, lane in [(295, 545, 460), (415, 605, 440)]:
        d.line((420, sy, lane, sy), fill=GREY, width=2)
        d.line((lane, sy, lane, gy), fill=GREY, width=2)
        d.line((lane, gy, 424, gy), fill=GREY, width=2)
        d.polygon([(424, gy), (436, gy - 8), (436, gy + 8)], fill=GREY)

    d.rounded_rectangle((72, 500, 420, 690), radius=10, fill=INK)
    put(d, 96, 518, '战略合并', 26, '#f0c588', 'bold', 400)
    put(d, 96, 560, '董事长', 17, '#bdb3a1', 'body', 400)
    put(d, 166, 556, '陈瑞卿（点众）', 20, '#efe6d6', 'bold', 404)
    put(d, 96, 604, 'CEO', 17, '#bdb3a1', 'body', 400)
    put(d, 166, 600, '胡泽新（GoodShort）', 20, '#efe6d6', 'bold', 404)
    put(d, 96, 646, '点众前 CTO', 16, '#8f8576', 'body', 400)

    # 右：未披露
    put(d, 520, 250, '公开报道里没有的七项', 24, RUST, 'bold', 1008)
    items = ['交易金额', '股权比例', '合并后的法律主体', '两个 App 是否独立运营',
             '内容采购与分账', '创作者/版权方合同', 'AI 生产由谁负责']
    y = 302
    for i, item in enumerate(items):
        put(d, 520, y, f'0{i + 1}', 18, RUST, 'number', 570)
        put(d, 580, y - 2, item, 21, INK, 'body', 1008)
        y += 54

    d.rounded_rectangle((520, 710, 1008, 780), radius=12, fill=WHITE)
    put(d, 544, 726, '官宣的是管理架构，不是交易条款。', 22, INK, 'bold', 986)
    put(d, 544, 758, '谁控股、怎么分账，仍要等文件。', 17, DIM, 'body', 986)

    footer(d, 820, [
        '来源：上海证券报 2026-10-31、腾讯新闻 2026-10-31、界面新闻、澎湃新闻 2026-10-18。',
        '股权比例、交易金额、创作者条款均未披露；本图只列已确认信息。',
    ])
    return im


def merger_checklist():
    im, d = page('供给方先核四件事', '合同里比新闻标题更有用的四个位置', '03', 960)

    rows = [
        ('01', '合同相对方', '签约主体有没有变；变的是品牌、团队，还是法律实体。'),
        ('02', '控制权变更', '合并、控制权变更通常触发通知、重签或终止条款。'),
        ('03', '独家范围', '独家给的是平台、地区，还是全部渠道；合并后是否覆盖另一方。'),
        ('04', '结算与分成', '结算周期、分成基数、扣不扣投流；合并后按哪份合同执行。'),
    ]
    y = 260
    for num, title, desc in rows:
        d.rounded_rectangle((72, y, 1008, y + 120), radius=10, fill=WHITE)
        put(d, 96, y + 18, num, 20, RUST, 'number', 150)
        put(d, 150, y + 14, title, 24, INK, 'bold', 1008)
        paragraph(d, 150, y + 52, desc, width=820, size=18, color=DIM, leading=26)
        y += 140

    d.rounded_rectangle((72, 830, 1008, 894), radius=12, fill=INK)
    put(d, 100, 846, '主体没变，采购规则可能还没变；主体变了，先去谈合同。', 21, '#f0c588', 'bold', 986)

    footer(d, 910, [
        '四件事为本号基于常见合同条款整理的操作建议，不构成法律意见。',
    ])
    return im


def cover_060():
    base.TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, '#bdb3a1', right=420)
    put(d, 33, 60, '出海短剧 · 10-31 官宣', 18, '#f0c588', 'bold', 470)
    put(d, 28, 96, 'DramaBox', 38, '#efe6d6', 'title', 470)
    put(d, 36, 146, '+ GoodShort', 38, '#efe6d6', 'title', 470)
    put(d, 36, 208, '合并了', 30, '#e0705a', 'bold', 470)
    put(d, 36, 252, '金额 / 股权 / 创作者条款', 19, '#bdb3a1', 'body', 470)
    put(d, 36, 278, '都没有披露', 26, '#f0c588', 'bold', 470)
    put(d, 36, 320, '先看合同主体，再看新闻', 15, '#8f8576', 'body', 470)

    d.line((490, 62, 490, 324), fill='#4a443c', width=1)
    put(d, 528, 96, '供给方', 18, '#bdb3a1', 'body', 880)
    put(d, 528, 132, '先别谈涨价', 34, '#f0c588', 'bold', 880)
    put(d, 528, 190, '合同四项', 18, '#8fc0b4', 'bold', 880)
    put(d, 528, 222, '主体 / 控制权变更', 19, '#efe6d6', 'body', 880)
    put(d, 528, 250, '独家范围 / 结算分成', 19, '#efe6d6', 'body', 880)
    put(d, 528, 300, '官宣的是管理架构，不是交易条款', 15, '#8f8576', 'body', 880)
    return im


# ---------------- 061 ----------------

def jimeng_prices():
    im, d = page('三个价格，三种条件', '即梦 Seedance 2.5 720P / 2026-10-30 至 11-05', '01', 850)

    cards = [
        (72, '0.42 元/秒', '活动页标价', '6.2 折，随用随付', RUST),
        (390, '0.378 元/秒', 'CLI 折上 9 折', '0.42 × 0.9，随用随付', TEAL),
        (708, '0.16 元/秒', '超级会员年卡', '¥19,656/年，按积分折算', GOLD),
    ]
    for cx, price, label, note, color in cards:
        d.rounded_rectangle((cx, 260, cx + 300, 520), radius=12, fill=WHITE)
        put(d, cx + 24, 280, label, 19, DIM, 'bold', cx + 290)
        put(d, cx + 20, 318, price, 34, color, 'title', cx + 290)
        paragraph(d, cx + 24, 392, note, width=250, size=17, color=DIM, leading=25)

    put(d, 72, 552, '另有「连续包季低至 0.24 元/秒」，同样是预付档。', 20, INK, 'bold', 1008)

    d.rounded_rectangle((72, 612, 1008, 730), radius=12, fill=INK)
    put(d, 100, 628, '90 秒成片：0.378 × 90 ≈ 34 元', 26, '#f0c588', 'bold', 986)
    put(d, 100, 672, '只含模型生成；重跑 2—3 次，按 70—100 元估。', 18, '#bdb3a1', 'body', 986)
    put(d, 100, 700, '参考图制作、配音、字幕、人工剪辑都不在内。', 16, '#8f8576', 'body', 986)

    footer(d, 760, [
        '来源：即梦 AI 活动页（2026-10-30 至 11-05）。',
        '价格为页面公开口径；年卡按页面标价与积分折算，未计续费差异。',
    ])
    return im


def cover_061():
    base.TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, '#bdb3a1', right=420)
    put(d, 33, 60, '即梦 · 到 11-05', 18, '#f0c588', 'bold', 470)
    put(d, 28, 92, '0.378', 94, '#efe6d6', 'title', 470)
    put(d, 36, 200, '元/秒（CLI 折后）', 24, '#bdb3a1', 'bold', 470)
    put(d, 36, 242, '90 秒 ≈ 34 元', 34, '#e0705a', 'bold', 470)
    put(d, 36, 294, '只含模型生成，不含重跑与人工', 16, '#8f8576', 'body', 470)

    d.line((490, 62, 490, 324), fill='#4a443c', width=1)
    put(d, 528, 92, '页面还写', 18, '#bdb3a1', 'body', 880)
    put(d, 528, 124, '0.16 元/秒', 40, '#f0c588', 'title', 880)
    put(d, 528, 186, '要超级会员年卡', 22, '#efe6d6', 'bold', 880)
    put(d, 528, 226, '先把会员费算进去', 18, '#8fc0b4', 'body', 880)
    put(d, 528, 254, '再比较单价', 18, '#8fc0b4', 'body', 880)
    put(d, 528, 304, '低价不是无门槛', 17, '#e0705a', 'bold', 880)
    return im


if __name__ == '__main__':
    jobs = [
        ('059_图1_口径_1080.png', q3_scope),
        ('059_图2_三季_1080.png', q3_trend),
        ('059_图3_题材_1080.png', q3_genre),
        ('封面_059_338与两类_900x383.png', cover_059),
        ('060_图1_排名_1080.png', merger_ranks),
        ('060_图2_谁在台上_1080.png', merger_who),
        ('060_图3_合同四项_1080.png', merger_checklist),
        ('封面_060_合并未披露_900x383.png', cover_060),
        ('061_图1_三个价格_1080.png', jimeng_prices),
        ('封面_061_0378与门槛_900x383.png', cover_061),
    ]
    for name, maker in jobs:
        im = maker()
        base.validate_glyphs()
        base.save_png(im, OUT / name)
    print('done')
