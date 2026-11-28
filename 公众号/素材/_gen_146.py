"""Render the mobile registration guide for article 146."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1080, 1120
PAPER = "#F7F3EE"
WHITE = "#FFFDF9"
INK = "#291F2B"
MUTED = "#62565D"
AMBER = "#834117"
AMBER_WASH = "#F6E7D4"
RULE = "#E1D6CA"

HIRAGINO = Path("/System/Library/Fonts/Hiragino Sans GB.ttc")
NOTO = Path("/usr/share/fonts/opentype/noto")
OUTPUT = Path(__file__).with_name("146_图1_报名流程_1080.png")


def font(size, *, bold=False):
    if HIRAGINO.is_file():
        return ImageFont.truetype(str(HIRAGINO), size, index=2 if bold else 0)
    filename = "NotoSansCJK-Bold.ttc" if bold else "NotoSansCJK-Regular.ttc"
    return ImageFont.truetype(str(NOTO / filename), size, index=2)


def draw_step(draw, *, number, top, bottom, title, timing, lines):
    circle_y = top + 60
    draw.ellipse((64, circle_y - 24, 112, circle_y + 24), fill=INK)
    draw.text((88, circle_y), str(number), font=font(27, bold=True), fill=WHITE, anchor="mm")

    draw.rounded_rectangle((144, top, 1016, bottom), radius=25, fill=WHITE, outline=RULE, width=2)
    draw.text((180, circle_y), title, font=font(42, bold=True), fill=INK, anchor="lm")

    timing_font = font(31, bold=True)
    chip_right = 980
    chip_left = chip_right - round(draw.textlength(timing, font=timing_font)) - 42
    draw.rounded_rectangle(
        (chip_left, circle_y - 25, chip_right, circle_y + 25), radius=25, fill=AMBER_WASH
    )
    draw.text(((chip_left + chip_right) // 2, circle_y), timing, font=timing_font, fill=AMBER, anchor="mm")

    body_font = font(37)
    for index, line in enumerate(lines):
        draw.text((180, top + 104 + 47 * index), line, font=body_font, fill=MUTED, anchor="lt")


def main():
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((64, 64, 74, 97), radius=5, fill=AMBER)
    draw.text((91, 81), "爱奇艺跨年晚会", font=font(34, bold=True), fill=AMBER, anchor="lm")
    draw.text((64, 124), "剧情 VCR 报名流程", font=font(68, bold=True), fill=INK, anchor="lt")
    draw.line((64, 224, 1016, 224), fill=RULE, width=2)

    draw.line((88, 324, 88, 780), fill=RULE, width=4)
    draw_step(
        draw, number=1, top=263, bottom=466, title="报名", timing="11月30日截止",
        lines=("100 字以内的构想、过往原创视频", "填写联系方式"),
    )
    draw_step(
        draw, number=2, top=491, bottom=694, title="等审核", timing="报名后 3 个工作日内",
        lines=("入选才会收到通知", "收到通知后 3 日内确认参与"),
    )
    draw_step(
        draw, number=3, top=719, bottom=922, title="入选后制作", timing="3–5 分钟",
        lines=("使用纳逗 Pro 制作", "按官方通知交付"),
    )

    draw.line((64, 972, 1016, 972), fill=RULE, width=2)
    draw.text(
        (64, 1003), "来源　纳逗 Pro 官方征集令（2026-11-13）",
        font=font(28), fill=MUTED, anchor="lt",
    )
    draw.text((64, 1050), "制图　一人短剧厂牌", font=font(28), fill=MUTED, anchor="lt")

    image.save(OUTPUT, optimize=True)


if __name__ == "__main__":
    main()
