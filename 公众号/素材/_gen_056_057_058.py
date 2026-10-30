#!/usr/bin/env python3
"""056《100 家版权方、5000 部 IP》/ 057《上党区补贴》/ 058《持械入宋》配图与封面。纯本地 Pillow。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_049 as base

OUT = Path(__file__).resolve().parent
PAPER, WHITE, INK = base.PAPER, base.WHITE, base.INK
DIM, LINE, RUST, TEAL, GOLD, GREY = base.DIM, base.LINE, base.RUST, base.TEAL, base.GOLD, base.GREY
font, put, paragraph, page, footer = base.font, base.put, base.paragraph, base.page, base.footer


def hdash(d, x1, x2, y, fill=LINE, dash=8, gap=6):
    x = x1
    while x < x2:
        d.line((x, y, min(x + dash, x2), y), fill=fill, width=1)
        x += dash + gap


# ---------------- 056 ----------------

def ip_shelf():
    im, d = page('100 家版权方，5000 部非番茄 IP', '抖音集团短剧版权中心 / 2026-10', '01', 1000)

    cards = [
        (72, '合作版权方', '100+', '家小说版权方'),
        (310, '非番茄 IP', '5000+', '部，不含番茄自有'),
        (548, 'IP 体裁', '4 类', '网文 / 短故事 / 电子书 / 影视剧'),
        (786, '平均每家', '50 部', '算术平均，非单家规模'),
    ]
    for cx, label, value, note in cards:
        d.rounded_rectangle((cx, 240, cx + 222, 430), radius=12, fill=WHITE)
        put(d, cx + 20, 258, label, 20, DIM, 'bold', cx + 212)
        put(d, cx + 18, 292, value, 54, INK, 'title', cx + 212)
        if len(note) > 10:
            cut = note.rindex(' / ') if ' / ' in note else len(note)
            put(d, cx + 20, 372, note[:cut], 15, DIM, 'body', cx + 212)
            put(d, cx + 20, 396, note[cut:].strip(' /'), 15, DIM, 'body', cx + 212)
        else:
            put(d, cx + 20, 380, note, 16, DIM, 'body', cx + 212)

    put(d, 72, 456, '点名平台', 20, DIM, 'bold', 1008)
    for i, name in enumerate(('七猫小说', '豆瓣阅读', '17K 小说网')):
        cx = 72 + i * 208
        d.rounded_rectangle((cx, 490, cx + 190, 546), radius=8, fill=INK)
        put(d, cx + 24, 505, name, 22, '#f0c588', 'bold', cx + 186)

    d.rounded_rectangle((72, 584, 1008, 764), radius=12, fill=WHITE)
    put(d, 100, 602, '公告里已经跑出的两个改编案例', 20, DIM, 'bold', 986)
    put(d, 100, 640, '《我都元婴期了，你跟我说开学》', 24, INK, 'bold', 640)
    put(d, 660, 644, '漫剧 ← 看点阅读', 20, RUST, 'bold', 990)
    put(d, 100, 686, '《重生之嫡女归来》', 24, INK, 'bold', 640)
    put(d, 660, 690, '真人短剧 ← 趣阅科技', 20, RUST, 'bold', 990)
    put(d, 100, 728, '公告写的是「改编、分发、收益全链路」，没有披露分成比例。', 19, DIM, 'body', 986)

    d.rounded_rectangle((72, 796, 1008, 902), radius=12, fill=INK)
    put(d, 102, 812, '货架变长了，但拿货方式没变。', 26, '#f0c588', 'bold', 986)
    put(d, 102, 856, '公告邀请的是 IP 版权方入驻，不是制作方自助下单。', 19, '#bdb3a1', 'body', 986)

    footer(d, 904, [
        '来源：短剧黑马 10-27、21 世纪经济报道/羊城派 10-28、网易智能 10-28。',
        '5000÷100=50 为本号算术平均；公告原文未取到，三家报道口径一致。',
    ])
    return im


def priority_list():
    im, d = page('平台优先要什么', '公告的题材清单，与三条通用标准', '02', 900)

    put(d, 72, 236, '01  改编适配性', 19, RUST, 'bold', 1008)
    put(d, 72, 268, '主线清晰、人设鲜明、节奏明快，适合短漫剧改编', 23, INK, 'body', 1008)

    put(d, 72, 326, '02  热门题材', 19, RUST, 'bold', 1008)

    put(d, 72, 364, '男频', 17, DIM, 'bold', 480)
    put(d, 72, 392, '穿越脑洞 · 玄幻修仙 · 都市战神', 22, INK, 'bold', 480)

    put(d, 540, 364, '女频', 17, DIM, 'bold', 1008)
    put(d, 540, 392, '古代权谋 · 种田 · 仙侠团宠', 22, INK, 'bold', 1008)
    put(d, 540, 426, '现代言情 · 家庭伦理', 22, INK, 'bold', 1008)

    d.line((72, 486, 1008, 486), fill=LINE, width=2)

    put(d, 72, 508, '03  热度与潜力', 19, RUST, 'bold', 1008)
    put(d, 72, 540, '有粉丝基础、热度验证或话题潜力', 23, INK, 'body', 1008)

    d.rounded_rectangle((72, 600, 1008, 706), radius=12, fill=INK)
    put(d, 102, 616, '前两组靠改本子和选题能凑，第三组凑不出来。', 24, '#f0c588', 'bold', 986)
    put(d, 102, 656, '原创剧本拿不出在读人数、评分、评论量这层数据。', 18, '#bdb3a1', 'body', 986)

    footer(d, 730, [
        '来源：抖音集团短剧版权中心公告，经短剧黑马 10-27、21 世纪经济报道 10-28 转述。',
        '题材与通用标准为公告口径；分组归纳与「凑不出来」为本号判断。',
    ])
    return im


def four_steps():
    im, d = page('从货架到合同：四步和五个条款', '找 IP 的顺序，与签约前要谈清的五件事', '03', 1120)

    steps = [
        ('01', '确认入口和资质', '在抖音集团短剧创作者中心完成机构入驻与资质审核。界面未登录核实，以平台实际页面为准。'),
        ('02', '按两张清单筛题材', '男频三项、女频五项，先圈一到两个方向，再进池子找。'),
        ('03', '准备三样材料', '改编方案（主线/人设/前 10 集节奏）、集数与成本、既往作品数据。'),
        ('04', '把合同五项谈清楚', '授权范围、期限与地域、是否独家、分成基数、到期后成片处置。'),
    ]
    y = 244
    for num, title, desc in steps:
        put(d, 72, y, num, 22, RUST, 'number', 140)
        put(d, 128, y - 4, title, 25, INK, 'bold', 520)
        paragraph(d, 128, y + 36, desc, width=392, size=18, color=DIM, leading=27)
        y += 168

    d.line((566, 236, 566, 860), fill=LINE, width=2)

    put(d, 600, 240, '合同五项', 24, TEAL, 'bold', 1008)
    terms = [
        ('授权范围', '改编权 / 信息网络传播权 / 转授权'),
        ('期限与地域', '几年、哪些平台、哪些地区'),
        ('是否独家', '独家价与分成通常不同'),
        ('分成基数', '流水还是收入，扣不扣投流'),
        ('到期处置', '成片还在跑，续不续、怎么算钱'),
    ]
    for i, (name, note) in enumerate(terms):
        y2 = 292 + i * 108
        d.rounded_rectangle((600, y2, 1008, y2 + 88), radius=10, fill=WHITE)
        put(d, 620, y2 + 14, name, 22, INK, 'bold', 996)
        put(d, 620, y2 + 50, note, 16, DIM, 'body', 996)

    d.rounded_rectangle((72, 932, 1008, 1040), radius=12, fill=INK)
    put(d, 102, 948, '最容易漏的是第五项：授权到期，成片还在平台上跑。', 23, '#f0c588', 'bold', 986)
    put(d, 102, 988, '合同没写，就是事后补签；补签的价格，通常比开机前贵。', 18, '#bdb3a1', 'body', 986)

    footer(d, 1034, [
        '四步与五项为本号基于公告流程整理的操作建议，非平台官方流程。',
    ])
    return im


def cover_056():
    base.TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, '#bdb3a1', right=420)
    put(d, 33, 60, '抖音短剧版权中心 · 10-28', 18, '#f0c588', 'bold', 470)
    put(d, 28, 96, '5000+', 78, '#efe6d6', 'title', 470)
    put(d, 36, 190, '部非番茄 IP 摆上货架', 24, '#bdb3a1', 'bold', 470)
    put(d, 36, 236, '100 家版权方', 30, '#e0705a', 'bold', 470)
    put(d, 36, 288, '但不是自助下单：版权方先入驻，平台撮合', 17, '#8f8576', 'body', 470)

    d.line((490, 62, 490, 324), fill='#4a443c', width=1)
    put(d, 528, 96, '平台优先的题材', 18, '#bdb3a1', 'body', 880)
    put(d, 528, 132, '男频', 16, '#e0705a', 'bold', 880)
    put(d, 528, 158, '穿越脑洞 / 玄幻修仙 / 都市战神', 17, '#efe6d6', 'body', 880)
    put(d, 528, 200, '女频', 16, '#8fc0b4', 'bold', 880)
    put(d, 528, 226, '古代权谋 / 种田 / 仙侠团宠', 17, '#efe6d6', 'body', 880)
    put(d, 528, 252, '现代言情 / 家庭伦理', 17, '#efe6d6', 'body', 880)
    d.line((528, 292, 868, 292), fill='#4a443c', width=1)
    put(d, 528, 306, '硬标准：有粉丝基础、热度验证', 16, '#f0c588', 'bold', 880)
    return im


# ---------------- 057 ----------------

def subsidy_math():
    im, d = page('四条线乘满 500 万，年度盘子 300 万', '上党区影视扶持政策 / 金额单位：万元', '01', 1030)

    x0, scale = 300, 600 / 500
    rows = [
        ('微短剧', '100 部 × 3 万', 300, RUST, '300'),
        ('电影', '10 部 × 10 万', 100, GREY, '100'),
        ('AI 漫剧', '前 100 部 × 1 万', 100, GOLD, '100'),
    ]
    for i, (name, detail, val, color, label) in enumerate(rows):
        y = 260 + i * 96
        put(d, 72, y + 2, name, 23, INK, 'bold', 292)
        put(d, 72, y + 32, detail, 15, DIM, 'body', 294)
        w = val * scale
        d.rectangle((x0, y, x0 + w, y + 52), fill=color)
        put(d, x0 + w + 14, y + 10, label, 26, INK, 'number', 900)

    y = 556
    put(d, 72, y + 2, '三条合计', 23, INK, 'bold', 292)
    put(d, 72, y + 32, '300 + 100 + 100', 15, DIM, 'body', 294)
    d.rectangle((x0, y, x0 + 500 * scale, y + 52), fill=INK)
    put(d, x0 + 500 * scale + 14, y + 10, '500', 26, RUST, 'bold', 1008)

    fund_x = x0 + 300 * scale
    d.line((fund_x, 236, fund_x, 540), fill=RUST, width=3)
    put(d, fund_x - 42, 226, '300 万', 16, RUST, 'bold', 1008)
    put(d, 72, 632, '虚线位置 = 300 万，正好是微短剧这一条乘满的数；三条合计是它的 1.67 倍。', 19, DIM, 'body', 1008)

    d.rounded_rectangle((72, 690, 1008, 800), radius=12, fill=WHITE)
    put(d, 100, 706, '同样口径下，另外几笔', 20, DIM, 'bold', 986)
    put(d, 100, 742, '剧本版权方 20 万/部 → 15 部就吃满 300 万', 21, INK, 'bold', 986)
    put(d, 100, 776, '产业基金 ≥2000 万是低息融资，不是奖补，不能相加', 18, DIM, 'body', 986)

    d.rounded_rectangle((72, 830, 1008, 930), radius=12, fill=INK)
    put(d, 102, 846, '「最高 3 万」是单价上限，不是预算承诺。', 25, '#f0c588', 'bold', 986)
    put(d, 102, 886, '评审、公示、就高不重复；实际发放按当年预算。', 18, '#bdb3a1', 'body', 986)

    footer(d, 954, [
        '来源：上党区政府长上政函〔2026〕6 号（2026-10-29）所附政策全文。',
        '乘法为本号计算；「不低于 300 万元」为政策原文下限，非当年实际预算。',
    ])
    return im


def six_gates():
    im, d = page('六道门槛，缺一道就报不上', '上党区政策 / 扶持范围与申报条件', '02', 1100)

    gates = [
        ('许可证', '扶持范围第一条：《广播电视节目制作经营许可证》或《网络剧片发行许可证》，二选一。'),
        ('在上党取景', '申报材料第 6 项要取景清单 + 拍摄合同 + 场景照片；擅自变更主要场景，追回资金。'),
        ('先上线', '作品须在申报截止日前完成全部集数上线播出；AI 漫剧单列一遍。'),
        ('申报窗口', '奖补每年集中申报两次，具体时间以当年通知为准。'),
        ('账', '项目总投资专项审计报告，或拍摄制作合同 + 费用打款记录。'),
        ('权属与承诺', '知识产权权属声明、材料真实性承诺书；虚假材料追回并三年禁申。'),
    ]
    y = 244
    for i, (name, desc) in enumerate(gates):
        put(d, 72, y + 2, f'0{i + 1}', 22, RUST, 'number', 146)
        put(d, 140, y - 2, name, 24, INK, 'bold', 1008)
        paragraph(d, 140, y + 34, desc, width=850, size=17, color=DIM, leading=25)
        y += 118

    d.rounded_rectangle((72, 968, 1008, 1018), radius=10, fill=INK)
    put(d, 100, 982, '最实的一条不是注册地，是「在上党取景」。', 21, '#f0c588', 'bold', 986)

    footer(d, 1036, [
        '来源：上党区政府长上政函〔2026〕6 号所附政策全文（2026-10-29）。',
    ])
    return im


def apply_flow():
    im, d = page('申报四步，和四条追回情形', '上党区政策 / 流程与资金回收', '03', 940)

    steps = [
        ('01', '区融媒体中心初审', '材料完整性与真实性'),
        ('02', '专家评审 + 实地核查', '影视、AIGC、文化产业专家'),
        ('03', '公示 5 个工作日', '区政府网站 + 融媒体平台'),
        ('04', '报批拨付', '按程序报批后发放'),
    ]
    for i, (num, title, note) in enumerate(steps):
        cx = 72 + i * 238
        d.rounded_rectangle((cx, 244, cx + 220, 400), radius=10, fill=WHITE)
        put(d, cx + 20, 262, num, 20, RUST, 'number', cx + 210)
        put(d, cx + 20, 296, title, 20, INK, 'bold', cx + 210)
        put(d, cx + 20, 340, note, 15, DIM, 'body', cx + 212)

    put(d, 72, 440, '触发追回的四种情形', 23, RUST, 'bold', 1008)
    items = [
        '提供虚假材料，骗取奖补资金',
        '作品存在知识产权侵权行为',
        '擅自变更主要拍摄场景，未达到上党取景要求',
        '其他违反国家法律法规和财经纪律的行为',
    ]
    y = 490
    for i, text in enumerate(items):
        put(d, 72, y, f'{i + 1}.', 20, RUST, 'number', 120)
        put(d, 112, y - 2, text, 21, INK, 'body', 1008)
        y += 54

    d.rounded_rectangle((72, 736, 1008, 836), radius=12, fill=INK)
    put(d, 102, 752, '追回之外，取消三年内申报上党区财政扶持资金的资格。', 22, '#f0c588', 'bold', 986)
    put(d, 102, 794, '政策解释：区文旅局、区财政局、区融媒体中心。', 18, '#bdb3a1', 'body', 986)

    footer(d, 860, [
        '来源：上党区政府长上政函〔2026〕6 号所附政策全文（2026-10-29）。',
    ])
    return im


def cover_057():
    base.TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, '#bdb3a1', right=420)
    put(d, 33, 60, '上党区 · 10-29 修改版', 18, '#f0c588', 'bold', 470)
    put(d, 28, 96, '3 万', 96, '#efe6d6', 'title', 470)
    put(d, 36, 212, '一部微短剧，限 100 部', 24, '#bdb3a1', 'bold', 470)
    put(d, 36, 256, '先上线，再申报', 30, '#e0705a', 'bold', 470)
    put(d, 36, 306, '钱在拍完之后，不在开机之前', 17, '#8f8576', 'body', 470)

    d.line((490, 62, 490, 324), fill='#4a443c', width=1)
    put(d, 528, 92, '100 部 × 3 万 = 300 万', 19, '#bdb3a1', 'body', 880)
    put(d, 528, 128, '正好等于', 17, '#8f8576', 'body', 880)
    put(d, 528, 154, '年度专项资金下限', 26, '#f0c588', 'bold', 880)
    put(d, 528, 204, '另有电影 10 部 × 10 万', 16, '#efe6d6', 'body', 880)
    put(d, 528, 232, 'AI 漫剧前 100 部 × 1 万', 16, '#efe6d6', 'body', 880)
    put(d, 528, 260, '剧本版权方 20 万 / 部', 16, '#efe6d6', 'body', 880)
    d.line((528, 292, 868, 292), fill='#4a443c', width=1)
    put(d, 528, 304, '六道门槛：许可证 / 上党取景 / 先上线…', 15, '#8fc0b4', 'body', 880)
    return im


# ---------------- 058 ----------------

def three_numbers():
    im, d = page('三个数，三种口径', '《持械入宋》/ 截至 2026-10-28', '01', 980)

    cards = [
        (72, '全网累计播放', '40 亿+', '发布账号「老十一剧场」公布，10-08 口径', RUST),
        (390, '红果收藏', '1098 万', '红果平台可见，截至发稿前', TEAL),
        (708, '红果 AI 剧收藏榜', '第 6 名', '第一季；同榜第 9 季热度 8206 万未采信', GOLD),
    ]
    for cx, label, value, note, color in cards:
        d.rounded_rectangle((cx, 250, cx + 300, 500), radius=12, fill=WHITE)
        put(d, cx + 24, 268, label, 18, DIM, 'bold', cx + 292)
        put(d, cx + 20, 306, value, 58, color, 'title', cx + 292)
        paragraph(d, cx + 24, 406, note, width=252, size=15, color=DIM, leading=23)

    d.line((72, 540, 1008, 540), fill=LINE, width=2)

    put(d, 72, 566, '不能相除，也不能互相印证', 24, INK, 'bold', 1008)
    para = ('40 亿是出品方自述的全网累计，1098 万是单一平台的收藏数，第 6 名是榜单名次。'
            '三个数来自不同平台、不同指标、不同时间点，任何两个相除都得不到有意义的结果。')
    paragraph(d, 72, 610, para, width=936, size=19, color=DIM, leading=32)

    d.rounded_rectangle((72, 720, 1008, 830), radius=12, fill=INK)
    put(d, 102, 736, '但它们指向同一件事：一部 AI 短剧，跑出了长剧的体量。', 23, '#f0c588', 'bold', 986)
    put(d, 102, 778, '靠的不是单集爆，是一季一季往下更。', 19, '#bdb3a1', 'body', 986)

    footer(d, 856, [
        '来源：新榜（36 氪）2026-10-28；新播场（新浪财经转载）2026-09-11。',
        '40 亿为出品方公布口径，非平台披露；三个数不做换算。',
    ])
    return im


def ten_seasons():
    im, d = page('10 季 × 100 集 ≈ 1000 集，摊到每集约 400 万', '集数为推算；播放为全网累计', '02', 1000)

    put(d, 72, 240, '每一格 = 1 季 = 100 集', 20, DIM, 'bold', 1008)
    for i in range(10):
        row, col = divmod(i, 5)
        x = 72 + col * 188
        y = 290 + row * 150
        d.rounded_rectangle((x, y, x + 168, y + 110), radius=10, fill=WHITE)
        put(d, x + 16, y + 14, f'S{i + 1:02d}', 18, RUST, 'number', x + 160)
        put(d, x + 16, y + 44, '100 集', 30, INK, 'title', x + 160)
        put(d, x + 16, y + 84, '1 季', 14, DIM, 'body', x + 160)

    y = 600
    put(d, 72, y, '10 季 × 100 集 = 约 1000 集（本号推算）', 22, INK, 'bold', 1008)
    put(d, 72, y + 44, '40 亿播放 ÷ 1000 集 ≈ 400 万播放/集（平均值，不是单集数据）', 20, DIM, 'body', 1008)

    d.rounded_rectangle((72, 720, 1008, 830), radius=12, fill=INK)
    put(d, 102, 736, '系列化的意思是：不需要每一集都爆。', 25, '#f0c588', 'bold', 986)
    put(d, 102, 778, '整条季播线一直有人看，单集的播放压力就被摊薄了。', 18, '#bdb3a1', 'body', 986)

    footer(d, 856, [
        '「每季 100 集」来自新播场 2026-09-11 报道；10 季为 2026-10-28 报道口径。',
        '1000 集与 400 万/集均为本号按上述两数推算，不是官方数据。',
    ])
    return im


def bets_and_risks():
    im, d = page('三笔账，三个风险', '系列化能省什么，又防不住什么', '03', 800)

    left = [
        ('资产复用', '角色图、场景底图、道具模型跨季复用，第二季不用从零生成。'),
        ('更新速度', '大场面用 AI 生成，季与季之间可以持续供给。'),
        ('季播试错', '一季 100 集独立起量，用一季的成本试，不押全剧。'),
    ]
    right = [
        ('爆款率', '行业破亿率不足 0.5%，万播收益降至 10 元内。'),
        ('同题材分化', '《砚边青梅》3 季仅抖音 3673 万，与 40 亿差两个数量级。'),
        ('翻拍稀释', '《魏家逆子成首辅》已跑出 7 个版本，护城河不是独占。'),
    ]

    put(d, 72, 240, '三笔账', 24, TEAL, 'bold', 480)
    y = 292
    for name, note in left:
        put(d, 72, y, name, 22, INK, 'bold', 480)
        y = paragraph(d, 72, y + 34, note, width=400, size=16, color=DIM, leading=24) + 26

    put(d, 540, 240, '三个风险', 24, RUST, 'bold', 1008)
    y = 292
    for name, note in right:
        put(d, 540, y, name, 22, INK, 'bold', 1008)
        y = paragraph(d, 540, y + 34, note, width=460, size=16, color=DIM, leading=24) + 26

    d.rounded_rectangle((72, 566, 1008, 676), radius=12, fill=INK)
    put(d, 102, 582, '系列化是护城河，不是保险。', 26, '#f0c588', 'bold', 986)
    put(d, 102, 626, '你能连更十季，别人也能拿同一个本子另起一版。', 18, '#bdb3a1', 'body', 986)

    footer(d, 700, [
        '来源：新榜（36 氪）2026-10-28；新播场 2026-09-11。',
        '「三笔账」为本号基于制作流程的判断；「三个风险」中的数字均为报道口径。',
    ])
    return im


def cover_058():
    base.TEXT_BOXES = []
    im = Image.new('RGB', (900, 383), INK)
    d = ImageDraw.Draw(im)
    put(d, 33, 24, '一人短剧厂牌', 18, '#bdb3a1', right=420)
    put(d, 33, 60, 'AI 历史短剧《持械入宋》', 18, '#f0c588', 'bold', 470)
    put(d, 28, 96, '40 亿', 92, '#efe6d6', 'title', 470)
    put(d, 36, 208, '全网累计播放（出品方口径）', 20, '#bdb3a1', 'bold', 470)
    put(d, 36, 252, '10 季', 34, '#e0705a', 'bold', 300)
    put(d, 200, 260, '1098 万收藏', 20, '#efe6d6', 'bold', 470)
    put(d, 36, 310, '摊到 1000 集，每集约 400 万', 17, '#8f8576', 'body', 470)

    d.line((490, 62, 490, 324), fill='#4a443c', width=1)
    put(d, 528, 100, '但它是尾部，不是均值', 18, '#bdb3a1', 'body', 880)
    put(d, 528, 140, '<0.5%', 52, '#e0705a', 'title', 880)
    put(d, 528, 204, '行业破亿率', 16, '#8f8576', 'body', 880)
    put(d, 528, 240, '10 元内 / 万播', 25, '#f0c588', 'bold', 880)
    put(d, 528, 278, '新榜此前报道的行业均值上限', 15, '#8f8576', 'body', 880)
    put(d, 528, 312, '别按 40 亿算自己的收入', 16, '#8fc0b4', 'body', 880)
    return im


if __name__ == '__main__':
    jobs = [
        ('056_图1_货架_1080.png', ip_shelf),
        ('056_图2_优先名单_1080.png', priority_list),
        ('056_图3_四步与合同_1080.png', four_steps),
        ('057_图1_补贴算账_1080.png', subsidy_math),
        ('057_图2_六道门槛_1080.png', six_gates),
        ('057_图3_申报与追回_1080.png', apply_flow),
        ('058_图1_三个口径_1080.png', three_numbers),
        ('058_图2_十季_1080.png', ten_seasons),
        ('058_图3_账与风险_1080.png', bets_and_risks),
        ('封面_056_5000部IP_900x383.png', cover_056),
        ('封面_057_3万一部的条件_900x383.png', cover_057),
        ('封面_058_40亿与10季_900x383.png', cover_058),
    ]
    for name, maker in jobs:
        im = maker()
        base.validate_glyphs()
        base.save_png(im, OUT / name)
    print('done')
