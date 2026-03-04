from PIL import Image, ImageDraw, ImageFont
img = Image.new('RGB', (256, 256), color=(0, 51, 102))
draw = ImageDraw.Draw(img)
draw.ellipse([50, 50, 206, 206], fill=(0, 64, 128), outline=(255, 255, 255), width=10)
try:
    font = ImageFont.truetype("arial.ttf", 100)
except:
    font = ImageFont.load_default()
draw.text((128, 128), "B", font=font, fill=(255, 255, 255), anchor="mm")
img.save('icon.ico', format='ICO', sizes=[(256,256), (128,128), (64,64), (32,32), (16,16)])
print("✅ Ícone criado")
