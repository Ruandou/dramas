"""Render the entry requirements graphic for article 149."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1080, 1120
PAPER = "#FAF7F0"
INK = "#222542"
INDIGO = "#383D83"
MUTED = "#575975"
RULE = "#DBD6D2"
LIGHT_CARD = "#EDEEFF"
NIGHT = "#282D52"
PEACH = "#FFD59A"
MILK = "#FBFAFF"
GRAY_LILAC = "#E0E3FA"

HIRAGINO = Path("/System/Library/Fonts/Hiragino Sans GB.ttc")
NOTO = Path("/usr/share/fonts/opentype/noto")
OUTPUT = Path(__file__).with_name("149_图1_参赛集数_1080.png")


def font(size, bold=False):
    if HIRAGINO.is_file():
        return ImageFont.truetype(str(HIRAGINO), size, index=2 if bold else 0)
    filename = "NotoSansCJK-Bold.ttc" if bold else "NotoSansCJK-Regular.ttc"
    return ImageFont.truetype(str(NOTO / filename), size, index=2)


def film_icon(draw, x, y, color, *, series=False, surface):
    if series:
        draw.rounded_rectangle((x + 25, y + 23, x + 119, y + 91), radius=10, outline=color, width=4)
        draw.rounded_rectangle(
            (x + 12, y + 11, x + 106, y + 79), radius=10, fill=surface, outline=color, width=4
        )
    draw.rounded_rectangle((x, y, x + 94, y + 68), radius=10, fill=surface, outline=color, width=4)
    draw.polygon(((x + 38, y + 20), (x + 38, y + 47), (x + 62, y + 34)), fill=color)


def main():
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)

    draw.text((62, 56), "微博 AI 片场", font=font(34, True), fill=INDIGO, anchor="lt")
    draw.text((60, 122), "一集能投，哪些奖要三集", font=font(75, True), fill=INK, anchor="lt")
    draw.line((62, 223, 1018, 223), width=2, fill=RULE)

    draw.rounded_rectangle((62, 266, 1018, 515), radius=25, fill=LIGHT_CARD)
    draw.text((103, 305), "单条投稿", font=font(34, True), fill=INDIGO, anchor="lt")
    draw.text((103, 370), "至少 1 分钟、至少 1080p", font=font(43, True), fill=INK, anchor="lt")
    draw.text((103, 448), "入围奖、赛道人气奖不限集数", font=font(37), fill=MUTED, anchor="lt")
    film_icon(draw, 850, 335, INDIGO, surface=LIGHT_CARD)

    draw.rounded_rectangle((62, 544, 1018, 794), radius=25, fill=NIGHT)
    draw.text((103, 583), "其余终奖", font=font(34, True), fill=PEACH, anchor="lt")
    draw.text((103, 648), "活动期间至少更新 3 集", font=font(43, True), fill=MILK, anchor="lt")
    draw.text((103, 726), "这 3 集须属于同一部作品", font=font(37), fill=GRAY_LILAC, anchor="lt")
    film_icon(draw, 850, 606, PEACH, series=True, surface=NIGHT)

    draw.text((62, 851), "投稿截止  2027 年 1 月 10 日", font=font(35, True), fill=INK, anchor="lt")
    draw.text(
        (62, 911), "须为个人原创，画面全部由 AI 生成。",
        font=font(35), fill=MUTED, anchor="lt",
    )
    draw.line((62, 993, 1018, 993), width=2, fill=RULE)
    draw.text(
        (62, 1036), "来源  微博短剧频道官方规则（2026-11-20）",
        font=font(26), fill=MUTED, anchor="lt",
    )
    draw.text((1018, 1036), "一人短剧厂牌 制图", font=font(26), fill=MUTED, anchor="rt")

    image.save(OUTPUT, optimize=True)


if __name__ == "__main__":
    main()
