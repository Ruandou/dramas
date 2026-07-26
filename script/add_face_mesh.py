#!/usr/bin/env python3
"""给角色参考图面部叠加 AR 风格三角网格，用于通过 Seedance 真人人脸过滤。

背景：照片级写实人脸参考图会被 ARK 以
InputImageSensitiveContentDetected.PrivacyInformation 拒绝（HTTP 400 不扣费）。
实测在面部叠加网格后可通过过滤，且网格不会被复现到输出视频中，
面部一致性保持（2026-07-26 验证，见 AGENTS.md 相关记忆）。

用法：
  python3 script/add_face_mesh.py --input looks/CHAR-001-L01.png \
      --output looks/CHAR-001-L01-mesh.png --face 789,398,120,165

--face 为 cx,cy,rx,ry（面部椭圆中心与半轴，原图像素坐标），可多次传入（多人脸）。
"""
import argparse
import math
import random

from PIL import Image, ImageDraw

MESH_COLOR = (0, 255, 200, 200)
DOT_COLOR = (0, 255, 220, 230)
ROWS, COLS = 9, 7


def draw_mesh(draw: ImageDraw.ImageDraw, cx: float, cy: float, rx: float, ry: float,
              line_width: int, dot_r: int) -> None:
    """在椭圆区域内画抖动三角网格。"""
    pts = []
    for i in range(ROWS):
        v = -1 + 2 * i / (ROWS - 1)
        half = rx * math.sqrt(max(0.0, 1 - v * v))
        row = []
        for j in range(COLS):
            u = -1 + 2 * j / (COLS - 1)
            x = cx + u * half + random.uniform(-6, 6)
            y = cy + v * ry + random.uniform(-6, 6)
            row.append((x, y))
        pts.append(row)
    for i in range(ROWS):
        for j in range(COLS):
            if j + 1 < COLS:
                draw.line([pts[i][j], pts[i][j + 1]], fill=MESH_COLOR, width=line_width)
            if i + 1 < ROWS:
                draw.line([pts[i][j], pts[i + 1][j]], fill=MESH_COLOR, width=line_width)
            if i + 1 < ROWS and j + 1 < COLS:
                draw.line([pts[i][j], pts[i + 1][j + 1]], fill=MESH_COLOR, width=line_width)
    for row in pts:
        for (x, y) in row:
            draw.ellipse([x - dot_r, y - dot_r, x + dot_r, y + dot_r], fill=DOT_COLOR)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--face", action="append", required=True,
                    help="cx,cy,rx,ry 像素坐标，可多次")
    ap.add_argument("--line-width", type=int, default=3)
    ap.add_argument("--dot-radius", type=int, default=4)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    random.seed(args.seed)
    img = Image.open(args.input).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for spec in args.face:
        cx, cy, rx, ry = (float(x) for x in spec.split(","))
        draw_mesh(d, cx, cy, rx, ry, args.line_width, args.dot_radius)
    out = Image.alpha_composite(img, overlay).convert("RGB")
    out.save(args.output)
    print(f"saved: {args.output} ({img.size[0]}x{img.size[1]}, faces={len(args.face)})")


if __name__ == "__main__":
    main()
