#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一版横版 → 竖版：按宽完整保留，上下同色补边（不裁标题、不糊边）。"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in (
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ):
        p = Path(path)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size, index=0)
            except OSError:
                return ImageFont.truetype(str(p), size, index=1)
    return ImageFont.load_default()


def replace_bottom_tagline(img: Image.Image, text: str) -> Image.Image:
    """仅覆盖底部副标区域，不动主画面。"""
    out = img.convert("RGBA")
    w, h = out.size
    band_h = int(h * 0.14)
    y0 = h - band_h
    overlay = Image.new("RGBA", (w, band_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i in range(band_h):
        a = min(255, int(120 + 135 * (i / band_h)))
        draw.line([(0, i), (w, i)], fill=(0, 0, 0, a))
    out.paste(overlay, (0, y0), overlay)

    draw = ImageDraw.Draw(out)
    size = max(22, w // 28)
    font = load_font(size)
    stroke = max(2, size // 14)
    y = h - band_h // 2
    for dx in range(-stroke, stroke + 1):
        for dy in range(-stroke, stroke + 1):
            if dx or dy:
                draw.text((w // 2 + dx, y + dy), text, font=font, fill=(0, 0, 0, 255), anchor="mm")
    draw.text((w // 2, y), text, font=font, fill=(220, 185, 90, 255), anchor="mm")
    return out.convert("RGB")


def edge_color(img: Image.Image, band: int = 8) -> tuple[int, int, int]:
    w, _ = img.size
    pixels = []
    for y in range(min(band, img.size[1])):
        for x in range(w):
            pixels.append(img.getpixel((x, y))[:3])
    for y in range(max(0, img.size[1] - band), img.size[1]):
        for x in range(w):
            pixels.append(img.getpixel((x, y))[:3])
    r = sum(p[0] for p in pixels) // len(pixels)
    g = sum(p[1] for p in pixels) // len(pixels)
    b = sum(p[2] for p in pixels) // len(pixels)
    return (r, g, b)


def fit_width_pad(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    w, h = img.size
    scale = target_w / w
    new_h = int(h * scale)
    resized = img.resize((target_w, new_h), Image.Resampling.LANCZOS)
    if new_h >= target_h:
        top = (new_h - target_h) // 2
        return resized.crop((0, top, target_w, top + target_h))
    bg = edge_color(resized)
    canvas = Image.new("RGB", (target_w, target_h), bg)
    canvas.paste(resized, (0, (target_h - new_h) // 2))
    return canvas


def export(src: Path, out_png: Path, out_jpg: Path, w: int, h: int, retag: str = "") -> None:
    img = Image.open(src).convert("RGB")
    out = fit_width_pad(img, w, h)
    if retag:
        out = replace_bottom_tagline(out, retag)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    out.save(out_png, "PNG", optimize=True)
    out.save(out_jpg, "JPEG", quality=94, optimize=True)
    print(f"{out_png.name}\t{out.size[0]}x{out.size[1]}\tjpg={out_jpg.stat().st_size//1024}KB")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    covers = root / "assets" / "covers"
    p = argparse.ArgumentParser()
    p.add_argument("--hongguo-src", type=Path, default=covers / "cover_hongguo_v1.png")
    p.add_argument("--douyin-src", type=Path, default=covers / "cover_douyin_v1.png")
    args = p.parse_args()

    export(args.hongguo_src, covers / "红果封面_超雄重生1995.png", covers / "红果封面_超雄重生1995.jpg", 1050, 1500)
    export(args.douyin_src, covers / "抖音封面_超雄重生1995.png", covers / "抖音封面_超雄重生1995.jpg", 1080, 1620, retag="重生1995 · 刑侦逆袭")


if __name__ == "__main__":
    main()
