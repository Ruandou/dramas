"""Draw article 147's original rights comparison with local Pillow only.

Run from any working directory. Refuses to overwrite the output.
"""

from pathlib import Path
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "147_图1_纸质授权对照_1080.png"
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
SIZE = (1080, 1120)
PAPER = "#F2F2EC"
WHITE = "#FCFCF9"
INK = "#132C35"
MUTED = "#486269"
LINE = "#CAD7D3"
PALE = "#E0EAE4"


@lru_cache
def face(size, bold=False):
    return ImageFont.truetype(FONT, size, index=2 if bold else 0)


def main():
    assert not OUTPUT.exists(), f"Output already exists: {OUTPUT}"
    canvas = Image.new("RGB", SIZE, PAPER)
    draw = ImageDraw.Draw(canvas)
    boxes = []
    characters = set()

    def text(x, y, value, size, color=INK, bold=False):
        font = face(size, bold)
        box = draw.textbbox((x, y), value, font=font, anchor="lt")
        assert 55 <= box[0] < box[2] <= 1025, (value, box)
        assert 0 <= box[1] < box[3] <= SIZE[1], (value, box)
        for previous, old_box in boxes:
            overlap = (max(box[0], old_box[0]) < min(box[2], old_box[2])
                       and max(box[1], old_box[1]) < min(box[3], old_box[3]))
            assert not overlap, (previous, value)
        boxes.append((value, box))
        characters.update(value.replace(" ", ""))
        draw.text((x, y), value, font=font, fill=color, anchor="lt")

    text(64, 46, "授权范围对照", 31, MUTED, True)
    text(61, 106, "同一部短剧，两种使用方式", 59, INK, True)
    text(64, 195, "把用途、权利和合同范围逐项对应", 35, MUTED)

    draw.rounded_rectangle((60, 278, 1020, 551), 22, fill=WHITE, outline=LINE, width=2)
    draw.rounded_rectangle((61, 279, 72, 550), 5, fill=MUTED)
    text(98, 308, "网络点播", 49, INK, True)
    text(98, 389, "核对信息网络传播权", 44, INK, True)
    text(98, 476, "合同范围", 31, MUTED)
    text(286, 469, "平台、地区、期限", 41, INK)

    draw.rounded_rectangle((60, 593, 1020, 935), 22, fill=WHITE, outline=LINE, width=2)
    draw.rounded_rectangle((61, 594, 72, 934), 5, fill=MUTED)
    text(98, 625, "印折页并售卖", 49, INK, True)
    text(98, 708, "核对复制权和发行权", 44, INK, True)
    text(98, 796, "合同范围", 31, MUTED)
    text(286, 788, "可用的画面、台词", 41, INK)
    text(286, 851, "印量、销售渠道", 41, INK)

    draw.line((63, 980, 1017, 980), fill=LINE, width=2)
    text(65, 1009, "据《著作权法》第10、26、29条", 30, MUTED)
    text(65, 1061, "具体授权范围看合同", 31, INK, True)

    for index in (0, 2):
        font_file = TTFont(FONT, fontNumber=index, lazy=True)
        cmap = font_file.getBestCmap()
        missing = [char for char in characters if ord(char) not in cmap]
        assert not missing, (index, missing)
        font_file.close()

    with OUTPUT.open("xb") as stream:
        canvas.save(stream, "PNG", optimize=True)
    with Image.open(OUTPUT) as check:
        assert check.size == SIZE and check.mode == "RGB"
        check.verify()
    print(f"PASS: {OUTPUT}; {SIZE[0]}x{SIZE[1]}; glyphs, bounds, overlaps and PNG verified")


if __name__ == "__main__":
    main()
