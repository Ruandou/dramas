#!/usr/bin/env python3
"""批量为 looks 生成面部网格变体：
1. 白底定妆图 → 顶部非白区域即头部，估算面部椭圆 (cx,cy,rx,ry)
2. 调用 script/add_face_mesh.py 生成 -mesh.png
豁免：CHAR-GRP-12-L01（背影，但背影有后脑无脸——豁免）、CHAR-GRP-16-L01（剪影）
"""
import os, subprocess, sys, json
from PIL import Image

LOOKS = "assets/looks"
SCRIPT = "/Users/lei/Movies/demo1/script/add_face_mesh.py"
EXEMPT = {"CHAR-GRP-12-L01", "CHAR-GRP-16-L01"}

def estimate_face(path):
    img = Image.open(path).convert("L")
    w, h = img.size
    small = img.resize((w // 4, h // 4))
    sw, sh = small.size
    px = small.load()
    TH = 235  # 背景近白
    rows = []
    for y in range(sh):
        xs = [x for x in range(sw) if px[x, y] < TH]
        rows.append(xs)
    ys = [y for y, xs in enumerate(rows) if len(xs) >= 3]
    if not ys:
        return None
    y0, y1 = min(ys), max(ys)
    H = y1 - y0
    band0, band1 = y0, min(sh - 1, y0 + int(0.13 * H))
    xs_all, widths = [], []
    for y in range(band0, band1 + 1):
        xs = rows[y]
        if xs:
            xs_all += xs
            widths.append(max(xs) - min(xs))
    if not xs_all:
        return None
    cx = sum(xs_all) / len(xs_all) * 4
    cy = (band0 + (band1 - band0) * 0.78) * 4  # 面部低于头顶（含发髓/帽）
    head_w = (sorted(widths)[len(widths) // 2]) * 4
    rx = max(60, head_w * 0.42)
    ry = rx * 1.45
    return cx, cy, rx, ry

def main():
    ids = sys.argv[1:] or sorted(
        f[:-4] for f in os.listdir(LOOKS)
        if f.endswith(".png") and f.startswith("CHAR-") and "-mesh" not in f
    )
    report = {}
    for i in ids:
        if i in EXEMPT:
            report[i] = "exempt"
            continue
        src = f"{LOOKS}/{i}.png"
        dst = f"{LOOKS}/{i}-mesh.png"
        est = estimate_face(src)
        if not est:
            report[i] = "ESTIMATE_FAIL"
            continue
        cx, cy, rx, ry = est
        r = subprocess.run(
            ["python3", SCRIPT, "--input", src, "--output", dst,
             "--face", f"{cx:.0f},{cy:.0f},{rx:.0f},{ry:.0f}"],
            capture_output=True, text=True)
        report[i] = f"ok {cx:.0f},{cy:.0f},{rx:.0f},{ry:.0f}" if r.returncode == 0 else f"FAIL {r.stderr[-120:]}"
    print(json.dumps(report, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
