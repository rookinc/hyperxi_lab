from PIL import Image, ImageDraw, ImageFont

W, H = 1400, 800
img = Image.new("RGB", (W, H), (235, 250, 235))
draw = ImageDraw.Draw(img)

draw.rectangle([0, 0, W, H * 0.65], fill=(210, 240, 255))
draw.rectangle([0, H * 0.65, W, H], fill=(140, 205, 120))

draw.ellipse([1050, 60, 1180, 190], fill=(255, 220, 90), outline=(255, 200, 40), width=4)

for x, y in [(180, 120), (360, 90), (760, 150)]:
    draw.ellipse([x, y, x + 90, y + 55], fill="white")
    draw.ellipse([x + 35, y - 20, x + 125, y + 45], fill="white")
    draw.ellipse([x + 80, y, x + 170, y + 55], fill="white")

flower_centers = [(180, 620), (320, 690), (520, 640), (760, 700), (980, 650), (1160, 705)]
petal_colors = [(255, 160, 180), (255, 220, 120), (180, 160, 255), (255, 170, 120), (170, 220, 255), (255, 190, 220)]

for (cx, cy), color in zip(flower_centers, petal_colors):
    draw.line([cx, cy, cx, cy - 65], fill=(60, 140, 60), width=6)
    draw.ellipse([cx - 22, cy - 40, cx + 2, cy - 22], fill=(70, 160, 70))
    draw.ellipse([cx - 2, cy - 28, cx + 22, cy - 10], fill=(70, 160, 70))
    r = 16
    offsets = [(-22, 0), (22, 0), (0, -22), (0, 22), (-16, -16), (16, -16), (-16, 16), (16, 16)]
    for ox, oy in offsets:
        draw.ellipse([cx + ox - r, cy - 65 + oy - r, cx + ox + r, cy - 65 + oy + r], fill=color)
    draw.ellipse([cx - 12, cy - 77, cx + 12, cy - 53], fill=(255, 210, 70))

box = [170, 245, 1230, 425]
draw.rounded_rectangle(box, radius=28, fill=(255, 255, 255), outline=(130, 190, 130), width=5)

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 92)
    subfont = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)
except:
    font = ImageFont.load_default()
    subfont = ImageFont.load_default()

title = "Hello, World!"
subtitle = "Spring PNG Generator"

tw = draw.textbbox((0, 0), title, font=font)
sw = draw.textbbox((0, 0), subtitle, font=subfont)

title_x = (W - (tw[2] - tw[0])) / 2
subtitle_x = (W - (sw[2] - sw[0])) / 2

draw.text((title_x, 275), title, fill=(70, 120, 70), font=font)
draw.text((subtitle_x, 375), subtitle, fill=(110, 110, 110), font=subfont)

img.save("hello_world_spring.png")
print("saved hello_world_spring.png")
