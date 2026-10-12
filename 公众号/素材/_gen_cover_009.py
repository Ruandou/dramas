# -*- coding: utf-8 -*-
"""009《官方点名的 12 部微短剧，哪几部是 AI 剧？我逐条查了公开报道》封面两方向
纯本地 Pillow，零扣费。900×383；每条关键文案宽度必须 ≤383（分享卡只保留中间方形区）。
注：Menlo 无中文字形，中英混排行一律走 mix/mix_centered。
"""
import os
from PIL import Image, ImageDraw
from _gen_cover_004 import (W, H, SONG, HIRA, MONO, CARBON, INK, BONE, VERM, DIM, FAINT,
                            BLUE, f, mix, mixw, centered, mix_centered, tracked, safe_zone, OUT)
from _gen_cover_006 import mock

SAFE = 383
TOP = 84
RUST = (214, 96, 78)
TEAL = (74, 138, 132)


def chk(d, text, size, mono=True):
    w = mixw(d, text, size, mono=mono)
    print("   %s %4dpx  %s" % ("OK " if w <= SAFE else "OVER", w, text))
    assert w <= SAFE, (text, w)


def eyebrow(d, tag="政策"):
    d.rectangle([54, 50, 65, 50 + 26], fill=VERM)
    tracked(d, 78, 46, "一人短剧厂牌 · " + tag, f(HIRA, 20), DIM, 3)


# ── A：12 部 / 4 部 ─────────────────────────────────────────
def dir_a():
    im = Image.new("RGB", (W, H), CARBON)
    d = ImageDraw.Draw(im)
    eyebrow(d)
    cx = W / 2
    chk(d, "总局秋季点评会通稿", 20, mono=False)
    chk(d, "12 部", 92)
    chk(d, "我逐条查了", 26, mono=False)
    chk(d, "4 部被媒体写成 AI", 26, mono=False)
    chk(d, "官方没有一部是逐部标注的", 19, mono=False)

    mix_centered(d, cx, TOP, "总局秋季点评会通稿", 20, FAINT)
    mix_centered(d, cx, TOP + 26, "12 部", 92, BONE)
    mix_centered(d, cx, TOP + 148, "我逐条查了", 26, RUST)
    mix_centered(d, cx, TOP + 190, "4 部被媒体写成 AI", 26, BONE)
    d.line([(cx - 150, TOP + 236), (cx + 150, TOP + 236)], fill=(64, 60, 55), width=1)
    mix_centered(d, cx, TOP + 248, "官方没有一部是逐部标注的", 19, FAINT)
    # 两侧装饰（分享卡会裁掉）
    mix(d, 30, 150, "《咕噜比事务所》", 19, (86, 82, 76), mono=False)
    mix(d, 700, 190, "《桃花潭记》", 19, (86, 82, 76), mono=False)
    return im, "封面_009_A_十二部_900x383.png"


# ── B：每集打标识（16 号令第三十四条）──────────────────────
def dir_b():
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    eyebrow(d, "合规")
    cx = W / 2
    chk(d, "《微短剧发展管理办法》第三十四条", 20, mono=False)
    chk(d, "每集", 88)
    chk(d, "明显位置添加提示标识", 28, mono=False)
    chk(d, "义务主体：制作机构和播出单位", 21, mono=False)
    chk(d, "2026-09-01 施行 · 上线后平台是第一责任方", 17, mono=False)

    mix_centered(d, cx, TOP, "《微短剧发展管理办法》第三十四条", 20, FAINT)
    mix_centered(d, cx, TOP + 26, "每集", 88, RUST)
    mix_centered(d, cx, TOP + 142, "明显位置添加提示标识", 28, BONE)
    mix_centered(d, cx, TOP + 186, "义务主体：制作机构和播出单位", 21, BLUE)
    d.line([(cx - 158, TOP + 226), (cx + 158, TOP + 226)], fill=(64, 60, 55), width=1)
    mix_centered(d, cx, TOP + 240, "2026-09-01 施行 · 上线后平台是第一责任方", 17, FAINT)
    return im, "封面_009_B_每集打标识_900x383.png"


if __name__ == "__main__":
    built = []
    for fn in (dir_a, dir_b):
        print(fn.__name__)
        im, name = fn()
        im.save(os.path.join(OUT, name))
        built.append((name, im))
        print(name, im.size)

    pad, gap = 26, 24
    sw = W + 400 + 400 + pad * 4
    sh = (H + 130 + 40) * 2 + pad * 2
    sheet = Image.new("RGB", (sw, sh), (244, 244, 244))
    sd = ImageDraw.Draw(sheet)
    ttl = ["官方点名的 12 部微短剧", "哪几部是 AI 剧？我逐条查了公开报道"]
    yy = pad
    for name, im in built:
        dbg = im.copy()
        safe_zone(ImageDraw.Draw(dbg))
        sd.text((pad, yy), name + "　（细框=分享卡安全区）", font=f(HIRA, 22, index=2), fill=(30, 30, 30))
        sheet.paste(dbg, (pad, yy + 34))
        sheet.paste(mock(im, True, ttl, "10-12"), (pad + W + pad, yy + 34))
        sheet.paste(mock(im, False, ttl, "10-12"), (pad + W + pad + 400 + gap, yy + 34))
        yy += H + 130 + 40
    p = os.path.join(OUT, "对照_009封面两方向.png")
    sheet.save(p)
    print("sheet", p, sheet.size)
