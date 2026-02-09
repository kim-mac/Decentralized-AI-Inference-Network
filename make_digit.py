from PIL import Image, ImageDraw, ImageFont

img = Image.new("L", (28, 28), color=0)  # black background
draw = ImageDraw.Draw(img)

# Draw digit "7"
draw.text((8, 2), "5", fill=255)

img.save("digit5.png")
print("digit.png created")
