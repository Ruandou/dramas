# -*- coding: utf-8 -*-
"""016《厂牌周报 02》正文数据图 6 张
纯本地 Pillow，零扣费（严禁调用任何付费生成 API）。底层工具复用
_gen_charts_006/007/009/011/012（同一套纸底与字体；011 的 line/line_right/para/
note_box/src_foot/cjk_guard 与 012 的 dbl 直接 import，宽度校验与 LINES 登记同一套）。
注：Menlo 无中文字形，任何含 CJK 的行一律走 mix()/wrap()，禁止用 MONO 直接画整行；
「≥」「≤」「×」归 CJK 段走 Hiragino，数字带单位如「15 亿」「100%」走 mix。
正文图单行文案宽度上限 980px，每条打印 OK/OVER 校验并 assert。
数据口径：
 · 微信两条线 = 官方文档《微信小程序短剧激励活动 2026年Q4》（腾讯文档，A 级，逐字读取）
 · 上一版对照 = 腾讯广告渠道《2026 Q2 联合发行激励政策》2026-06-17（B 级）
 · 平台格局与各家数字 = 钛媒体 2026-10-15《微信下场，短剧不再只看红果的报价》（B 级）
 · 番茄 IP 竞价 = 流媒体网转述 DataEye（引用抖音集团短剧版权中心手册，C 级）
 数值一字不改。
"""
import os
from PIL import Image, ImageDraw
from _gen_charts_006 import (W, PAPER, INK, DIM, LINE, TRACK, BOX, VERM, VERM_L,
                             BLUE, BLUE_L, GREY, SONG, HIRA, MONO, f, mix, mixw,
                             canvas, header, footer, grade_chip, runs, is_ascii)
from _gen_charts_007 import wrap, block
from _gen_charts_009 import cb, tx, hdr, foot, panel, EDGE, MAXW, MONEY, TEAL, TALL
from _gen_charts_011 import BODY, LINES, line, line_right, para, note_box, src_foot, cjk_guard, hdr_song
from _gen_charts_012 import dbl

OUT = os.path.dirname(os.path.abspath(__file__))
CX = [92, 470, 716, 860, 992]          # 五列表：左起 / 左起 / 右对齐×3
IW = EDGE - 96 - 24                    # 全宽卡内可用宽（左 96 起、右留 24）


def verdict(d, y, text, color, x_right=EDGE - 20, h=36):
    """右侧判定徽标，返回左边 x。"""
    w = mixw(d, text, 20, mono=False) + 24
    d.rectangle([x_right - w, y, x_right, y + h], fill=color)
    line(d, x_right - w + 12, y + (h - 26) / 2, text, 20, PAPER, mono=False)
    return x_right - w


def head_row(d, y, labels, h=58):
    """表头行：labels 为 (x, text, align) 三元组，align 'l' 或 'r'。"""
    d.rectangle([64, y, EDGE, y + h], fill=INK)
    for x, text, al in labels:
        if al == "l":
            line(d, x, y + 14, text, 23, PAPER, mono=False)
        else:
            line_right(d, x, y + 14, text, 23, PAPER, mono=False)
    return y + h


# ── 图 1：微信 Q4 联合发行四档全表 ──────────────────────────
def chart1():
    im, d = canvas(TALL)
    hdr_song(d, "微信「绿泡泡联合发行」四档全表",
             "官方文档《微信小程序短剧激励活动 2026年Q4》· 生效 10-16 至 12-31")

    y = 200
    y = head_row(d, y, [(CX[0], "分档（看剧时长）", "l"), (CX[1], "剧目", "l"),
                        (CX[2], "总分成", "r"), (CX[3], "现金", "r"), (CX[4], "广告金", "r")])

    rows = [
        ("看剧时长 ≥ 10min", "优质新剧", "100%", "90%", "10%", VERM, True),
        ("看剧时长 ≥ 10min", "其它剧目", "85%", "75%", "10%*", DIM, False),
        ("看剧时长 < 10min", "—", "50%", "50%", "—", DIM, False),
        ("非联合发行", "不参与联合发行", "65%", "—", "—", BLUE, False),
    ]
    for i, (a, b, tot, cash, ad, color, hot) in enumerate(rows):
        h = 96 if hot else 76
        d.rectangle([64, y, EDGE, y + h],
                    fill=(250, 240, 236) if hot else (BOX if i % 2 == 0 else (250, 246, 238)),
                    outline=VERM if hot else LINE, width=3 if hot else 2)
        if hot:
            d.rectangle([64, y, 74, y + h], fill=VERM)
        ty = y + (h - 30) / 2
        line(d, CX[0], ty, a, 24, INK if hot else DIM)
        line(d, CX[1], ty, b, 24, color if hot else DIM, mono=False)
        line_right(d, CX[2], ty, tot, 27 if hot else 24, color if hot else INK)
        line_right(d, CX[3], ty, cash, 24, DIM)
        line_right(d, CX[4], ty, ad, 24, DIM)
        y += h + 8

    y += 8
    y = para(d, 64, y, "* 原表「广告金」列第 1、2 行合并显示一个 10%（即 75% 现金 + 10% 广告金 = 85%）；"
                       "「—」为原表格内标注，表示无此项。", 21, DIM, MAXW)
    y += 16

    y = note_box(d, y, [
        ("「优质新剧」定义（原文逐字）：平台每天会从上新时间在 7 日内、变现流水 top5 中，"
         "选取用户看剧时长最高的剧作为优质新剧；在 T 日被选定，可在 T~T+6 日享受更高分成，"
         "每被选中一次，该部短剧最高可享封顶 50 万激励。", 22, INK, 31),
        ("两条附加限制：入选后激励期间人均播放时长仍须 ≥10min，否则按基础激励算；每天只选一部。",
         22, INK, 31),
    ], outline=INK)
    y += 16

    bx = 176
    d.rectangle([64, y, EDGE, y + bx], fill=(250, 246, 238), outline=VERM, width=3)
    d.rectangle([64, y, 76, y + bx], fill=VERM)
    line(d, 100, y + 20, "所以「最高 100%」这句话，真正的问题是：", 23, DIM)
    dbl(d, 100, y + 58, "你是 85%（≥10 分钟）还是 50%（<10 分钟）？", 32, VERM)
    line(d, 100, y + 130, "100% 是「每天一部」的限量名额，不是达标即得。", 22, INK)
    y += bx + 20

    y = src_foot(d, y, [
        "来源：《微信小程序短剧激励活动 2026年Q4》官方文档（正文 2,708 字，本号逐字读取）",
        "四档比例、现金/广告金拆分、优质新剧定义、封顶 50 万均为原文；「*」合并说明为本号核查结论",
    ])
    return im.crop((0, 0, W, y)), "016_图1_微信四档全表_1080.png"


# ── 图 2：Q2 → Q4 逐档对比 ─────────────────────────────────
def chart2():
    im, d = canvas(TALL)
    hdr_song(d, "逐档对着上一版比：四个档位全降",
             "左 Q2（04-01 至 06-30）· 右 Q4（10-16 至 12-31）· Q2 为 B 级")

    cx = [92, 430, 716, 992]
    y = 200
    y = head_row(d, y, [(cx[0], "档位", "l"), (cx[1], "上一版 Q2", "l"),
                        (cx[2], "这一版 Q4", "l"), (cx[3], "变化", "r")])

    rows = [
        ("优质新剧 · ≥10min", "105%", "100%", "-5pp", VERM, False),
        ("基础 · ≥10min", "95%", "85%", "-10pp", VERM, False),
        ("基础 · 3–10min", "85%", "并入 50% 档", "-35pp", VERM, True),
        ("基础 · <3min", "60%", "50%", "-10pp", VERM, False),
        ("非联合发行", "无此档", "65%", "新增", BLUE, False),
        ("优质剧封顶", "真人 50 万 / 动漫 20 万", "统一 50 万", "动漫 +30 万", TEAL, False),
        ("每天优质剧名额", "2 部（真人 + 动漫）", "1 部", "-1 部", VERM, False),
    ]
    for i, (name, q2, q4, dif, color, hot) in enumerate(rows):
        h = 88 if hot else 74
        d.rectangle([64, y, EDGE, y + h],
                    fill=(250, 240, 236) if hot else (BOX if i % 2 == 0 else (250, 246, 238)),
                    outline=color if hot else LINE, width=3 if hot else 2)
        if hot:
            d.rectangle([64, y, 74, y + h], fill=color)
        ty = y + (h - 30) / 2
        line(d, cx[0], ty, name, 24, INK if hot else DIM, mono=False)
        line(d, cx[1], ty, q2, 23, DIM, mono=False)
        line(d, cx[2], ty, q4, 24, color if hot else INK, mono=False)
        line_right(d, cx[3], ty, dif, 24, color)
        y += h + 8

    y += 14
    y = note_box(d, y, [
        ("现金比例同步下调：优质新剧 95% → 90%；≥10min 基础档 85% → 75%；<3min 档 55% → 50%。"
         "上一版 <3min 还有 5% 广告金，这一版 <10min 档广告金为「/」。", 22, INK, 31),
        ("读法：3—10 分钟这一档整档消失，是这次变化最大的一处——上一版拿 85% 的剧，这一版落进 50%，"
         "一档之差 35 个百分点。", 23, VERM, 32),
    ], outline=INK)
    y += 16

    y = para(d, 64, y, "上一版对照来源为腾讯广告渠道发布的《2026 Q2 联合发行激励政策》（2026-06-17），"
                       "页面自述「摘抄自互联网」，本号未取得官方托管页 → 本图整体按 B 级处理。",
             21, DIM, MAXW)
    y += 10

    y = src_foot(d, y + 4, [
        "来源：Q4 为官方文档（A 级）；Q2 为渠道转述（B 级）；两版数字逐格比对为本号自算（A 级）",
        "Q2 表未列「非联合发行」一行——是当时无此口径还是未公开，本号无法确认",
    ])
    return im.crop((0, 0, W, y)), "016_图2_Q2到Q4逐档对比_1080.png"


# ── 图 3：流量主 IAA 四档 ──────────────────────────────────
def chart3():
    im, d = canvas(TALL)
    hdr_song(d, "同一份文档的第二条线：流量主 IAA 四档",
             "门槛是 5 分钟与是否智能托管 · 与联合发行的 10 分钟线是两把尺子")

    y = 200
    y = head_row(d, y, [(CX[0], "分档（人均看剧时长）", "l"), (CX[1], "托管", "l"),
                        (CX[2], "总分成", "r"), (CX[3], "现金", "r"), (CX[4], "广告金", "r")])

    rows = [
        ("人均看剧时长 ≥ 5min", "已托管", "70%", "60%", "10%", VERM, True),
        ("", "未托管", "60%", "60%", "—", DIM, False),
        ("人均看剧时长 < 5min", "已托管", "60%", "50%", "10%", DIM, False),
        ("", "未托管", "50%", "50%", "—", DIM, False),
    ]
    for i, (a, b, tot, cash, ad, color, hot) in enumerate(rows):
        h = 96 if hot else 76
        d.rectangle([64, y, EDGE, y + h],
                    fill=(250, 240, 236) if hot else (BOX if i % 2 == 0 else (250, 246, 238)),
                    outline=VERM if hot else LINE, width=3 if hot else 2)
        if hot:
            d.rectangle([64, y, 74, y + h], fill=VERM)
        ty = y + (h - 30) / 2
        line(d, CX[0], ty, a, 24, INK if hot else DIM)
        line(d, CX[1], ty, b, 24, color if hot else DIM, mono=False)
        line_right(d, CX[2], ty, tot, 27 if hot else 24, color if hot else INK)
        line_right(d, CX[3], ty, cash, 24, DIM)
        line_right(d, CX[4], ty, ad, 24, DIM)
        y += h + 8

    y += 14
    y = note_box(d, y, [
        ("激励对象（原文）：属于「文娱-微短剧」「文娱-互动微短剧」类目、已开通小程序流量主功能、"
         "使用官方播放器的小程序。", 22, INK, 31),
        ("考核口径：过去 7 天（T-8 至 T-2）加当日的人均播放时长，公式 = ∑（单日播放总时长）÷ ∑（单日播放 UV）；"
         "参与前 2 天默认达标。", 22, INK, 31),
        ("违规后果（原文）：平台有权取消所有激励——「也即总分成恢复至 50%」。兜底就是 50%，"
         "与联合发行 <10min 档一致。", 22, VERM, 31),
    ], outline=INK)
    y += 16

    bx = 178
    d.rectangle([64, y, EDGE, y + bx], fill=(250, 246, 238), outline=BLUE, width=3)
    d.rectangle([64, y, 76, y + bx], fill=BLUE)
    line(d, 100, y + 20, "同一个微信，两条线，两把尺子", 26, BLUE)
    line(d, 100, y + 64, "联合发行：门槛 10 分钟 → 过线 85%、没过 50%（100% 是每天一部）", 22, INK, maxw=MAXW - 40)
    line(d, 100, y + 104, "流量主 IAA：门槛 5 分钟 → 过线 60%～70%、没过 50%～60%", 22, INK, maxw=MAXW - 40)
    line(d, 100, y + 142, "人均时长卡在 6～9 分钟的剧：两条路差 10～20 个百分点——差在选路，不在做剧。",
         22, VERM, maxw=MAXW - 40)
    y += bx + 20

    y = src_foot(d, y, [
        "来源：官方文档《微信小程序短剧激励活动 2026年Q4》「优质小程序流量主激励」段（A 级）",
        "四档比例与「/」标注均为原文；「两把尺子」的差额对比为本号归纳",
    ])
    return im.crop((0, 0, W, y)), "016_图3_流量主IAA四档_1080.png"


# ── 图 4：六家平台并排 ─────────────────────────────────────
PLATS = [
    ("微信", "10-16 起「绿泡泡联合发行」四档生效；同一文档另有流量主 IAA 四档",
     "最高 100%（90% 现金 + 10% 广告金）；<10min 落到 50%；不参与联合发行 65%",
     "未公开", VERM, True),
    ("快手", "10-01 至 11-30「好剧、系列剧激励」",
     "时长达标 +15%、完播达标 +15%、续作 60 天内 +20%，可叠加封顶 50%、单剧最高 20 万",
     "未公开", BLUE, False),
    ("红果（抖音系）", "保底扶持加码（2026-05 披露）；不强制全渠道独家",
     "2026 真人短剧保底预算超 15 亿元、部均保底比上年提高约 60%",
     "未公开", BLUE, False),
    ("番茄 IP（抖音版权中心）", "9-11 起「IP 首版合作」竞价；今年新增开放给 AI 漫剧",
     "长网文优选 IP 起拍 8 万元、短故事优选 IP 起拍 3 万元；邀请制",
     "不适用", MONEY, False),
    ("腾讯视频", "横屏短剧继续「保底 + 分账」",
     "新入场优质团队每部不低于 300 万元保底；上半年 43 部分账超百万、腾讯视频占 32 部",
     "最长 3 年", TEAL, True),
    ("爱奇艺", "国内承压，增量在海外",
     "二季度会员收入 40.1 亿元（同比 -2%）；海外微短剧会员收入同比增长超 300%",
     "未公开", GREY, False),
]


def chart4():
    im, d = canvas(TALL)
    hdr_song(d, "六家平台并排：只有一家写了分账周期",
             "2026-10 前后各自的分账、激励与门槛 · 来源等级见文末分级")

    y = 200
    for name, change, nums, cycle, color, hot in PLATS:
        lc = len(wrap(change, 21, IW, d, False))
        ln = len(wrap(nums, 22, IW, d, False))
        h = 20 + 34 + 6 + lc * 27 + 8 + ln * 29 + 20
        d.rectangle([64, y, EDGE, y + h], fill=(250, 240, 236) if hot else (250, 246, 238),
                    outline=color, width=3 if hot else 2)
        d.rectangle([64, y, 74, y + h], fill=color)
        line(d, 96, y + 16, name, 26, color if hot else INK, mono=False)
        cc = VERM if cycle in ("最长 3 年",) else GREY
        verdict(d, y + 14, "分账周期：" + cycle, cc, h=40)
        yy = y + 56
        yy = para(d, 96, yy, change, 21, DIM, maxw=IW) + 8
        para(d, 96, yy, nums, 22, INK, maxw=IW, step=29)
        y += h + 12

    y += 6
    y = para(d, 64, y, "六家里五家对「多久拿到钱」保持沉默——唯一表态的是腾讯视频（最长 3 年）。"
                       "结算周期就是现金流命门，谈的时候直接问，别等合同。", 23, VERM, MAXW)
    y += 10

    y = src_foot(d, y + 4, [
        "来源：微信为官方文档（A 级）；快手为多家一致口径（B 级）",
        "红果/腾讯视频/爱奇艺：钛媒体 10-15（B 级）；番茄 IP：流媒体网转述 DataEye（C 级）",
    ])
    return im.crop((0, 0, W, y)), "016_图4_六家平台并排_1080.png"


# ── 图 5：六家门槛逐条读 ────────────────────────────────────
GATES = [
    ("微信 · 联合发行", "「已加入短剧内容合作计划的剧目」「通过腾讯广告渠道推广该剧目后，产生广告变现收益」"
                        "「推广目标为短剧官方小程序」", "走不通：需计划准入 + 腾讯广告投放账户", VERM),
    ("微信 · 流量主 IAA", "「属于『文娱-微短剧』『文娱-互动微短剧』类目」「已开通小程序流量主功能」"
                          "「使用官方播放器」", "走不通：类目与流量主均为小程序主体侧资质", VERM),
    ("快手", "在「快手端原生短剧经营者平台」上架的分账短剧可参与", "走不通：经营者平台为对公侧准入", BLUE),
    ("红果（抖音系）", "围绕保底合作与系列剧展开（保底预算、部均金额由平台披露口径给出）",
     "走不通：保底合作面向机构/团队", BLUE),
    ("番茄 IP", "「邀请制，暂无申请渠道」；要求制作方「在抖音、红果有爆款基础」",
     "最硬：先有爆款，再谈资格", MONEY),
    ("腾讯视频", "门槛是「新入场的优质团队通过评估」，对应每部不低于 300 万元保底",
     "走不通：优质团队 + 平台评估", TEAL),
]


def chart5():
    im, d = canvas(TALL)
    hdr_song(d, "六家门槛逐条读：个人身份的实际位置",
             "门槛原文取自各来源公开表述 · 「走不通」为本号判断（B 级）")

    y = 200
    for i, (name, gate, why, color) in enumerate(GATES):
        lg = len(wrap(gate, 21, IW, d, False))
        h = 20 + 34 + 6 + lg * 27 + 8 + 30 + 18
        d.rectangle([64, y, EDGE, y + h], fill=(250, 246, 238), outline=LINE, width=2)
        d.rectangle([64, y, 74, y + h], fill=color)
        line(d, 96, y + 16, name, 24, color, mono=False)
        verdict(d, y + 14, "个人：走不通", VERM, h=38)
        yy = y + 56
        yy = para(d, 96, yy, "门槛：" + gate, 21, DIM, maxw=IW) + 8
        para(d, 96, yy, why, 21, INK, maxw=IW, step=28)
        y += h + 12

    y += 6
    y = note_box(d, y, [
        ("六条门槛没有一条能靠「一个人 + 一台电脑」独立满足：前两条要企业主体与对公资质，"
         "后四条要既往成绩与机构身份。", 23, INK, 32),
        ("今天所有平台给出高激励的那条路，都仍然需要「先成为一个主体」或「先有一个爆款」。"
         "对个人，第一步不是选平台，是把主体和第一部作品补齐——这两件都不依赖平台。", 23, VERM, 32),
        ("一条例外：微信「非联合发行 65%」对所有不参与联合发行的剧成立，这条路不需要进任何计划。",
         22, INK, 31),
    ], outline=INK)
    y += 10

    y = src_foot(d, y + 4, [
        "来源：微信门槛为官方原文（A 级）；番茄为流媒体网转述 DataEye（C 级）",
        "其余五家门槛为公开报道口径（B 级）；「个人可参与性」列为本号判断（B 级）",
        "判断依据：门槛原文均为「计划 / 账户 / 主体 / 既往成绩」条件，无一条面向自然人开放",
    ])
    return im.crop((0, 0, W, y)), "016_图5_六家门槛与个人_1080.png"


# ── 图 6：今天能做的三件事 ──────────────────────────────────
STEPS = [
    ("01", "查一个数：你的人均看剧时长", VERM, [
        ("para", "we 分析 → 数据管理 → API 管理 → 收入分析 → 联合发行 → 剧目收入详情，", 21, INK, 29),
        ("para", "按自然日、按剧目拉「播放 UV」「人均播放时长（分钟）」；", 21, INK, 29),
        ("para", "流量主线则看 we 分析 → 经营工具 → 短剧经营。", 21, INK, 29),
        ("para", "目标只有一个：过 10 分钟没有。过了争 85%，没过就是 50%。", 22, VERM, 30),
    ]),
    ("02", "要名单、要口径", BLUE, [
        ("para", "官方原文写着「每日的平台优质剧可咨询行业经理获取」——今天就问三件事：", 21, INK, 29),
        ("para", "① 优质剧名单怎么拿；② 你们的人均时长口径是否含「前 2 天默认达标」；", 21, INK, 29),
        ("para", "③ 非联合发行 65% 与联合发行各档能不能同时申报。", 21, INK, 29),
    ]),
    ("03", "谈判前备三条原文", INK, [
        ("para", "① 65%：你手里「不参与」的官方价，低于它先顶回去；", 21, INK, 29),
        ("para", "② 10 分钟 vs 5 分钟：先算清自己落哪一档、走哪条线；", 21, INK, 29),
        ("para", "③ 分账周期：六家里只有一家公开写了，剩下五家必须逐个问。", 21, INK, 29),
    ]),
]


def chart6():
    im, d = canvas(TALL)
    hdr_song(d, "今天就能做的三件事",
             "顺序不能反：先查时长，再要口径，最后才是谈")

    y = 200
    for num, title, color, items in STEPS:
        lc = sum(len(wrap(t, s, IW - 110, d, False)) for _, t, s, _f, _st in items)
        h = 22 + 34 + 10 + lc * 29 + 22
        d.rectangle([64, y, EDGE, y + h], fill=(250, 246, 238), outline=INK, width=2)
        d.rectangle([64, y, 74, y + h], fill=color)
        dbl(d, 100, y + 24, num, 34, color)
        line(d, 190, y + 22, title, 26, INK, mono=False)
        yy = y + 76
        for _, t, s, fill, st in items:
            yy = para(d, 190, yy, t, s, fill, maxw=IW - 110, step=st) + 2
        y += h + 14

    y += 4
    y = para(d, 64, y, "因为 ① ② 的结果，决定你在 ③ 里能开什么价。", 23, VERM, MAXW)
    y += 8
    y = src_foot(d, y + 4, [
        "路径与原文出处：微信官方文档《微信小程序短剧激励活动 2026年Q4》",
        "本文不构成投资建议；合同条款以合同原文为准、逐字核对",
    ])
    return im.crop((0, 0, W, y)), "016_图6_今天三件事_1080.png"


if __name__ == "__main__":
    for fn in (chart1, chart2, chart3, chart4, chart5, chart6):
        print(fn.__name__)
        im, name = fn()
        im.save(os.path.join(OUT, name))
        print(name, im.size)
    print()
    cjk_guard()