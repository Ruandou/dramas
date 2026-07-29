"""生成「雪盐镇」简体字形参考图（右起横排，金字黑底），供 Seedream image_urls 锁字形。"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 900
img = Image.new("RGB", (W, H), (12, 10, 8))
d = ImageDraw.Draw(img)

font = None
for path, idx in [("/System/Library/Fonts/Supplemental/Songti.ttc", 0),
                  ("/System/Library/Fonts/STHeiti Medium.ttc", 0)]:
    try:
        font = ImageFont.truetype(path, 420, index=idx)
        break
    except OSError:
        continue
assert font, "no CJK font"

# 右起横排：雪 盐 镇 → 绘制顺序从右往左
chars = ["雪", "盐", "镇"]
xs = [W - 480, W // 2 - 210, 60]
for ch, x in zip(chars, xs):
    d.text((x, H // 2), ch, font=font, fill=(212, 175, 55), anchor="lm")

out = "assets/looks/text_ref_雪盐镇.png"
img.save(out)
print("saved", out)
