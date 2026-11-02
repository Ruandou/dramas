#!/usr/bin/env python3
"""「厂牌榜」周榜（010）三张贴图：热播全勤 / 换血 / 预约与题材。

窗口 2026-10-26—11-01（7 个采样日）。数据来自 data/bangdan.sqlite。
运行：/usr/local/bin/python3 _gen_week.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gen_board as g
from PIL import Image, ImageDraw

ISSUE = '010'
START, END = '2026-10-26', '2026-11-01'
BOOKING_START = '2026-10-26'
W, H = 1080, 1440


def wrap_title(d, title, limit=640):
    return g.fit(d, title, 28, 'bold', limit)


def week_rows(limit=10):
    return g.query(
        "SELECT title, COUNT(DISTINCT edition_date) d, AVG(rank) ar, MIN(rank) br, "
        "AVG(metric_value) av, genre FROM snapshot WHERE board=1 "
        "AND edition_date BETWEEN ? AND ? GROUP BY title "
        "ORDER BY d DESC, ar ASC LIMIT ?", (START, END, limit))


def new_faces(limit=8):
    return g.query(
        "SELECT s.title, MIN(s.rank) br, COUNT(DISTINCT s.edition_date) d, MIN(s.edition_date) f "
        "FROM snapshot s WHERE s.board=1 AND s.edition_date BETWEEN ? AND ? "
        "AND s.title NOT IN (SELECT title FROM snapshot WHERE board=1 AND edition_date < ?) "
        "GROUP BY s.title ORDER BY br ASC LIMIT ?", (START, END, START, limit))


def dropped(limit=5):
    return g.query(
        "SELECT rank, title FROM snapshot WHERE board=1 AND edition_date=? "
        "AND title NOT IN (SELECT title FROM snapshot WHERE board=1 AND edition_date=?) "
        "ORDER BY rank LIMIT ?", (START, END, limit))


def new_face_count():
    return g.query(
        "SELECT COUNT(DISTINCT title) FROM snapshot WHERE board=1 "
        "AND edition_date BETWEEN ? AND ? AND title NOT IN "
        "(SELECT title FROM snapshot WHERE board=1 AND edition_date < ?)",
        (START, END, START))[0][0]


def top10_overlap():
    start = {r[0] for r in g.query(
        "SELECT title FROM snapshot WHERE board=1 AND edition_date=? ORDER BY rank LIMIT 10", (START,))}
    end = {r[0] for r in g.query(
        "SELECT title FROM snapshot WHERE board=1 AND edition_date=? ORDER BY rank LIMIT 10", (END,))}
    return len(start & end)


def new_face_full_count():
    return g.query(
        "SELECT COUNT(*) FROM (SELECT title FROM snapshot WHERE board=1 "
        "AND edition_date BETWEEN ? AND ? AND title NOT IN "
        "(SELECT title FROM snapshot WHERE board=1 AND edition_date < ?) "
        "GROUP BY title HAVING COUNT(DISTINCT edition_date)=7)",
        (START, END, START))[0][0]


def new_face_best_full():
    return g.query(
        "SELECT title, AVG(rank) ar FROM snapshot WHERE board=1 "
        "AND edition_date BETWEEN ? AND ? AND title NOT IN "
        "(SELECT title FROM snapshot WHERE board=1 AND edition_date < ?) "
        "GROUP BY title HAVING COUNT(DISTINCT edition_date)=7 ORDER BY ar LIMIT 1",
        (START, END, START))[0]


def single_day_peak():
    row = g.query(
        "SELECT edition_date, title, metric_value FROM snapshot WHERE board=1 "
        "AND edition_date BETWEEN ? AND ? ORDER BY metric_value DESC LIMIT 1",
        (START, END))[0]
    return row


def full_avg_top():
    return g.query(
        "SELECT title, AVG(metric_value) av FROM snapshot WHERE board=1 "
        "AND edition_date BETWEEN ? AND ? GROUP BY title "
        "HAVING COUNT(DISTINCT edition_date)=7 ORDER BY av DESC LIMIT 1",
        (START, END))[0]


def booking_start_top():
    rows = g.query(
        "SELECT title, metric_value FROM snapshot WHERE board=3 AND edition_date=? "
        "ORDER BY rank LIMIT 1", (BOOKING_START,))
    return rows[0] if rows else None


def daily_champs():
    from datetime import date, timedelta
    out = []
    lo = date.fromisoformat(START)
    for i in range((date.fromisoformat(END) - lo).days + 1):
        d = (lo + timedelta(days=i)).isoformat()
        r = g.query("SELECT title, metric_value FROM snapshot WHERE board=1 "
                    "AND edition_date=? ORDER BY rank LIMIT 1", (d,))[0]
        out.append((d[5:], r[0], r[1]))
    return out


def booking(limit=8):
    return g.query("SELECT rank, title, genre, metric_value FROM snapshot "
                   "WHERE board=3 AND edition_date=? ORDER BY rank LIMIT ?", (END, limit))


def genres(limit=6):
    return g.query("SELECT genre, COUNT(DISTINCT title) n FROM snapshot WHERE board=1 "
                   "AND edition_date BETWEEN ? AND ? GROUP BY genre ORDER BY n DESC LIMIT ?",
                   (START, END, limit))


def page(title, subtitle):
    g.BOXES.clear()
    im = Image.new('RGB', (W, H), g.PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle((72, 44, 83, 66), fill=g.RUST)
    g.put(d, 100, 44, f'一人短剧厂牌 / 厂牌榜 {ISSUE}', 21, g.DIM, 'bold')
    g.put(d, W - 72 - d.textlength(f'{START}—{END}', font=g.font(20, 'number')), 44,
          f'{START}—{END}', 20, g.RUST, 'number')
    g.put(d, 72, 92, title, 46, g.INK, 'title')
    g.put(d, 72, 158, subtitle, 24, g.DIM)
    return im, d


def save(im, name, foot_lines):
    d = ImageDraw.Draw(im)
    y = H - 34 - 32 * len(foot_lines)
    d.line((72, y - 18, W - 72, y - 18), fill=g.LINE, width=2)
    for line in foot_lines:
        g.put(d, 72, y, line, 21, g.DIM)
        y += 32
    dest = g.OUT / name
    im.quantize(colors=192, method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.NONE).save(dest, optimize=True)
    print(name, im.size, f'{dest.stat().st_size / 1024:.1f} KB')


def page1():
    im, d = page('本周热播：和离 7 天 6 冠', '7 个采样日 / 178 部曾上榜 / 41 部全勤 / 按平均名次排序')
    y = 216
    rows = week_rows(10)
    for i, (title, days, ar, br, av, genre) in enumerate(rows, 1):
        g.row_badge(d, y, i, g.RUST if i <= 3 else '#a2988a')
        g.put(d, 124, y + 2, wrap_title(d, title, 560), 28, g.INK, 'bold', 700)
        g.put(d, 710, y + 6, f'{days} 天 · 均 {ar:.1f}', 21, g.DIM, 'body', 900)
        txt = f'{av:.0f}'
        g.put(d, 1008 - d.textlength(txt, font=g.font(28, 'number')), y + 3, txt, 28, g.RUST, 'number')
        if i < len(rows):
            d.line((124, y + 48, W - 72, y + 48), fill='#e6ded0', width=1)
        y += 56

    y += 14
    d.line((72, y + 24, W - 72, y + 24), fill=g.GOLD, width=3)
    g.put(d, 72, y - 8, '本周掉出前 100', 28, g.INK, 'title')
    g.put(d, 340, y, f'{START[5:]} 在榜 / {END[5:]} 不在', 20, g.DIM)
    y += 50
    for rank, title in dropped(5):
        g.row_badge(d, y, rank, '#a2988a')
        g.put(d, 124, y + 2, wrap_title(d, title, 560), 27, g.DIM, 'bold', 700)
        y += 50

    y += 16
    d.rounded_rectangle((72, y, 1008, y + 150), radius=12, fill=g.INK)
    g.put(d, 100, y + 16, '周冠看两把尺子', 21, '#bdb3a1')
    g.put(d, 100, y + 48, '全勤 + 均名 1.3 + 均指数 9,020：和离后我带女儿横扫魔域', 24, '#f0c588', 'bold', 980)
    g.put(d, 100, y + 86, '单日最高 12,068：十八岁太奶奶第五部（11-01 登顶）', 23, '#f0c588', 'bold', 980)
    g.put(d, 100, y + 120, '一个是整周稳，一个是单日冲高。', 20, '#bdb3a1', 'body', 980)

    save(im, f'榜{ISSUE}_贴图1_周榜热播_1080.png', [
        f'口径：7 个采样日（{START[5:]}—{END[5:]}）平均名次与平均指数；指数为第三方转算。',
        '全勤＝7 天均在前 100；「均」为算术平均，不代表平台官方排名。',
    ])


def page2():
    im, d = page('本周换血：前十 8 席换人',
                 f'新面孔 {new_face_count()} 部 / 11-01 前十 8 张 / 新面孔中 {new_face_full_count()} 部全勤')
    y = 216
    g.put(d, 72, y, '每日榜首', 30, g.INK, 'title')
    d.line((72, y + 46, W - 72, y + 46), fill=g.RUST, width=3)
    y += 66
    champs = daily_champs()
    for date, title, value in champs:
        g.put(d, 72, y + 2, date, 22, g.GOLD, 'number')
        g.put(d, 160, y + 1, wrap_title(d, title, 620), 24, g.INK, 'bold', 800)
        txt = f'{value}'
        g.put(d, 1008 - d.textlength(txt, font=g.font(24, 'number')), y + 2, txt, 24, g.RUST, 'number')
        if date != champs[-1][0]:
            d.line((160, y + 40, W - 72, y + 40), fill='#e6ded0', width=1)
        y += 46

    y += 18
    g.put(d, 72, y, '新面孔 TOP8', 30, g.INK, 'title')
    g.put(d, 300, y + 10, '本周首次出现 / 按最高名次', 21, g.DIM)
    d.line((72, y + 46, W - 72, y + 46), fill=g.TEAL, width=3)
    y += 66
    for title, br, days, first in new_faces(8):
        g.row_badge(d, y, br, g.TEAL if br <= 3 else '#a2988a')
        g.put(d, 124, y + 2, wrap_title(d, title, 560), 28, g.INK, 'bold', 700)
        g.put(d, 710, y + 6, f'{days} 天 · {first[5:]} 起', 21, g.DIM, 'body', 990)
        y += 52

    y += 10
    d.rounded_rectangle((72, y, 1008, y + 92), radius=12, fill='#e8f0ec')
    g.put(d, 100, y + 16, f'{START[5:]} 的前十，到 {END[5:]} 只剩 {top10_overlap()} 部。', 24, g.TEAL, 'bold', 980)
    nf, nar = new_face_best_full()
    g.put(d, 100, y + 56, f'新面孔里 {new_face_full_count()} 部 7 天全勤，{nf} 均名 {nar:.1f}。',
          20, g.DIM, 'body', 980)

    save(im, f'榜{ISSUE}_贴图2_周榜换血_1080.png', [
        '新面孔＝本周之前从未进入过热播榜前 100 的剧；不等于新上线。',
        '榜单为第三方转算指数，非平台官方排名，不构成投资参考。',
    ])


def page3():
    im, d = page('预约换棒：第六部 2,046 登顶', '预约看 11-01 / 对比 10-26 与 10-30 / 题材看本周去重')
    y = 216
    g.put(d, 72, y, '预约榜 TOP8', 30, g.INK, 'title')
    g.put(d, 300, y + 10, f'{END[5:]} / 当日预约值', 21, g.DIM)
    d.line((72, y + 46, W - 72, y + 46), fill=g.GOLD, width=3)
    y += 66
    for rank, title, genre, value in booking(8):
        g.row_badge(d, y, rank, g.GOLD if rank <= 3 else '#a2988a')
        g.put(d, 124, y + 2, wrap_title(d, title, 520), 27, g.INK, 'bold', 660)
        g.put(d, 670, y + 6, g.fit(d, genre, 20, 'body', 110), 20, g.DIM, 'body', 800)
        txt = f'{value}'
        g.put(d, 1008 - d.textlength(txt, font=g.font(27, 'number')), y + 3, txt, 27, g.GOLD, 'number')
        y += 54

    y += 14
    g.put(d, 72, y, '本周题材', 30, g.INK, 'title')
    g.put(d, 300, y + 10, '曾上榜去重剧数 / 前 6', 21, g.DIM)
    d.line((72, y + 46, W - 72, y + 46), fill=g.RUST, width=3)
    y += 66
    for i, (genre, n) in enumerate(genres(6), 1):
        g.row_badge(d, y, i, g.RUST if i <= 3 else '#a2988a')
        g.put(d, 124, y + 2, genre, 28, g.INK, 'bold', 740)
        txt = f'{n}'
        g.put(d, 1008 - d.textlength(txt, font=g.font(28, 'number')), y + 3, txt, 28, g.RUST, 'number')
        if i < 6:
            d.line((124, y + 46, W - 72, y + 46), fill='#e6ded0', width=1)
        y += 52

    y += 12
    d.rounded_rectangle((72, y, 1008, y + 122), radius=12, fill='#f7e9e3')
    bs = booking_start_top()[1]
    be = booking(1)[0][3]
    g.put(d, 100, y + 14, f'预约第一换人：{BOOKING_START[5:]} 第五部 {bs:,} → {END[5:]} 第六部 {be:,}。',
          20, g.RUST, 'bold', 980)
    g.put(d, 100, y + 50, f'第五部 10-30 预约 3,421 居首，{END[5:]} 热播 12,068 登顶。',
          20, g.RUST, 'bold', 980)
    g.put(d, 100, y + 86, '都市爱情 29 部占 16.3%；前六合计 120 部，占 67.4%。',
          19, g.DIM, 'body', 980)

    save(im, f'榜{ISSUE}_贴图3_预约与题材_1080.png', [
        f'来源 duanjugongcheng.com/cn/bangdan/{END}，第三方转算指数。',
        f'预约对比用 {BOOKING_START[5:]} 与 {END[5:]}；预约值含义官方未说明，题材按本周曾上榜去重。',
        '本号不做好评榜：11-01 仅 9 分（33 部）与 10 分（67 部）两档。',
    ])


if __name__ == '__main__':
    for fn in (page1, page2, page3):
        fn()
    print('done')
