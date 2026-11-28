"""Render the original two-person blocking exercise for article 148."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1080, 1360
FRAME_X, FRAME_Y = 288, 226
FRAME_WIDTH, FRAME_HEIGHT = 504, 896
PAPER = "#F5F3E8"
INK = "#17372D"
MUTED = "#50665A"
RULE = "#C8D0BE"
AMBER = "#8A4922"
WALL = "#DCE2CC"
FOREGROUND = "#244737"
FOREGROUND_SLEEVE = "#355B48"
BACKGROUND = "#748564"
BACKGROUND_SLEEVE = "#647754"
SKIN = "#D5B083"
HAIR = "#556749"

HIRAGINO = Path("/System/Library/Fonts/Hiragino Sans GB.ttc")
NOTO = Path("/usr/share/fonts/opentype/noto")
OUTPUT = Path(__file__).with_name("148_图1_双人构图练习_1080.png")


def font(size, *, bold=False):
    if HIRAGINO.is_file():
        return ImageFont.truetype(str(HIRAGINO), size, index=2 if bold else 0)
    filename = "NotoSansCJK-Bold.ttc" if bold else "NotoSansCJK-Regular.ttc"
    return ImageFont.truetype(str(NOTO / filename), size, index=2)


def contour(draw, start, curves, *, fill):
    """Draw a closed silhouette from cubic Bézier anchors."""
    points = [start]
    for control_a, control_b, end in curves:
        for sample in range(1, 17):
            t = sample / 16
            u = 1 - t
            weights = (u**3, 3 * u**2 * t, 3 * u * t**2, t**3)
            anchors = (start, control_a, control_b, end)
            points.append(tuple(sum(w * p[i] for w, p in zip(weights, anchors)) for i in (0, 1)))
        start = end
    draw.polygon(points, fill=fill)


def arm(draw, points, width, color):
    draw.line(points, fill=color, width=width, joint="curve")
    radius = width // 2
    x, y = points[-1]
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def scene():
    image = Image.new("RGB", (FRAME_WIDTH, FRAME_HEIGHT), WALL)
    draw = ImageDraw.Draw(image)

    draw.rectangle((336, 0, 504, 896), fill="#D0D9BD")
    draw.line((336, 0, 336, 896), fill="#C3CFB3", width=2)
    draw.rectangle((0, 728, 504, 896), fill="#CBD3BC")
    draw.line((0, 728, 504, 728), fill="#BCC9AF", width=2)

    # B is slightly smaller and farther from camera, with a left-facing profile.
    contour(
        draw, (333, 307),
        (
            ((352, 293), (394, 292), (419, 312)),
            ((449, 331), (469, 363), (474, 408)),
            ((483, 504), (481, 637), (477, 762)),
            ((471, 817), (465, 861), (459, 897)),
            ((422, 897), (355, 897), (318, 897)),
            ((315, 809), (313, 724), (300, 602)),
            ((291, 518), (293, 425), (296, 367)),
            ((301, 341), (310, 324), (333, 307)),
        ), fill=BACKGROUND,
    )
    contour(
        draw, (347, 314),
        (
            ((349, 292), (345, 278), (325, 268)),
            ((316, 263), (322, 253), (316, 246)),
            ((310, 239), (315, 231), (322, 218)),
            ((325, 212), (325, 190), (332, 179)),
            ((347, 151), (380, 153), (402, 169)),
            ((433, 193), (432, 234), (414, 257)),
            ((399, 274), (402, 297), (414, 313)),
            ((385, 334), (365, 328), (347, 314)),
        ), fill=SKIN,
    )
    contour(
        draw, (323, 212),
        (
            ((319, 183), (336, 155), (359, 150)),
            ((385, 144), (416, 157), (424, 178)),
            ((441, 204), (433, 245), (414, 263)),
            ((406, 261), (399, 245), (395, 220)),
            ((384, 228), (372, 218), (371, 202)),
            ((352, 207), (339, 207), (323, 212)),
        ), fill=HAIR,
    )
    draw.line(((325, 225), (338, 225)), fill=INK, width=3)
    draw.line(((322, 254), (332, 255)), fill=AMBER, width=3)
    arm(draw, [(352, 353), (370, 432), (302, 414)], 42, BACKGROUND_SLEEVE)
    contour(
        draw, (311, 399),
        (
            ((296, 393), (292, 390), (287, 384)),
            ((281, 378), (272, 379), (277, 386)),
            ((280, 391), (285, 395), (286, 398)),
            ((274, 392), (259, 391), (259, 397)),
            ((259, 400), (274, 405), (277, 410)),
            ((268, 407), (261, 408), (263, 413)),
            ((268, 421), (289, 432), (304, 431)),
            ((309, 426), (312, 409), (311, 399)),
        ), fill=SKIN,
    )

    # A stays nearer camera and slightly overlaps the lower-left edge.
    contour(
        draw, (67, 379),
        (
            ((110, 347), (159, 355), (186, 387)),
            ((217, 423), (218, 479), (229, 535)),
            ((242, 633), (240, 739), (254, 897)),
            ((171, 897), (59, 897), (0, 897)),
            ((0, 782), (0, 647), (0, 525)),
            ((0, 462), (20, 412), (67, 379)),
        ), fill=FOREGROUND,
    )
    contour(
        draw, (84, 381),
        (
            ((96, 354), (93, 340), (80, 316)),
            ((60, 282), (75, 242), (105, 220)),
            ((135, 201), (177, 207), (191, 230)),
            ((204, 248), (204, 270), (207, 283)),
            ((210, 296), (226, 303), (216, 310)),
            ((212, 313), (209, 318), (208, 327)),
            ((208, 345), (185, 353), (170, 357)),
            ((167, 364), (174, 378), (187, 388)),
            ((152, 414), (112, 407), (84, 381)),
        ), fill=SKIN,
    )
    contour(
        draw, (91, 344),
        (
            ((72, 332), (58, 303), (59, 278)),
            ((60, 239), (91, 212), (126, 204)),
            ((156, 198), (189, 209), (200, 237)),
            ((183, 246), (168, 256), (160, 277)),
            ((159, 283), (146, 284), (141, 297)),
            ((135, 310), (119, 332), (91, 344)),
        ), fill=FOREGROUND,
    )
    draw.line(((196, 285), (205, 288)), fill=INK, width=3)
    arm(draw, [(109, 446), (148, 494), (208, 427)], 53, FOREGROUND_SLEEVE)
    contour(
        draw, (198, 426),
        (
            ((204, 411), (212, 408), (223, 403)),
            ((228, 400), (239, 397), (241, 402)),
            ((246, 406), (235, 414), (229, 416)),
            ((227, 419), (232, 420), (236, 420)),
            ((245, 421), (245, 429), (240, 432)),
            ((232, 436), (224, 438), (216, 443)),
            ((205, 442), (201, 435), (198, 426)),
        ), fill=SKIN,
    )
    draw.ellipse((229, 429, 247, 447), outline=AMBER, width=5)
    draw.line(((240, 446), (247, 465), (253, 463)), fill=AMBER, width=5, joint="curve")
    draw.line(((243, 456), (249, 454)), fill=AMBER, width=4)

    return image


def annotation(draw, *, letter, title, x, y, color):
    draw.rounded_rectangle((x, y, x + 55, y + 49), radius=12, fill=color)
    draw.text((x + 27, y + 25), letter, font=font(31, bold=True), fill=PAPER, anchor="mm")
    draw.text((x, y + 66), title, font=font(37, bold=True), fill=INK, anchor="lt")


def leader(draw, points, color):
    draw.line(points, fill=PAPER, width=7, joint="curve")
    draw.line(points, fill=color, width=3, joint="curve")
    x, y = points[-1]
    draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=PAPER, outline=color, width=2)


def main():
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)

    draw.text((58, 59), "原创分镜练习示意", font=font(33, bold=True), fill=MUTED, anchor="lt")
    draw.text((56, 121), "双人戏，把反应留在画面里", font=font(68, bold=True), fill=INK, anchor="lt")
    draw.line((58, 205, 1022, 205), fill=RULE, width=2)

    image.paste(scene(), (FRAME_X, FRAME_Y))
    draw.rectangle(
        (FRAME_X, FRAME_Y, FRAME_X + FRAME_WIDTH - 1, FRAME_Y + FRAME_HEIGHT - 1),
        outline=INK, width=3,
    )
    draw.rounded_rectangle((311, 251, 398, 293), radius=8, fill=PAPER)
    draw.text((355, 273), "9:16", font=font(25, bold=True), fill=INK, anchor="mm")

    annotation(draw, letter="A", title="递出钥匙", x=58, y=543, color=INK)
    leader(draw, [(58, 667), (259, 667), (299, 714), (497, 714), (521, 689)], INK)

    annotation(draw, letter="B", title="伸手停住", x=846, y=475, color=AMBER)
    leader(draw, [(1019, 599), (816, 599), (778, 582), (603, 582), (564, 617)], AMBER)

    draw.rounded_rectangle((58, 1161, 1022, 1252), radius=16, fill=INK)
    draw.text(
        (540, 1207), "检查画面里能否同时看到动作和反应", font=font(43, bold=True),
        fill=PAPER, anchor="mm",
    )
    draw.text((58, 1290), "一人短剧厂牌", font=font(31), fill=MUTED, anchor="lt")

    image.save(OUTPUT, optimize=True)


if __name__ == "__main__":
    main()
