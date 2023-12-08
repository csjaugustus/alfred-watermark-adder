from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import colorsys
import os
import sys

def hex_to_rgba(hex_color, opacity=1.0):
    # Convert the hex code to RGB
    rgb_color = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    # Convert the RGB color to RGBA
    r, g, b = rgb_color
    alpha = 255 * opacity
    if not isinstance(alpha, int):
        alpha = int(alpha)
    rgba_color = (r, g, b, alpha)

    return rgba_color

def new_get_text_size(text, font): # uses bbox instead of textsize, since textsize is deprecated
    temp_canvas = Image.new("RGB", (0, 0))
    draw = ImageDraw.Draw(temp_canvas)

    draw.text((0, 0), text, font=font)
    bbox = draw.textbbox((0, 0), text, font=font)

    x_min, y_min, x_max, y_max = bbox
    tw = x_max - x_min
    th = y_max - y_min
    return tw, th

def add_watermark(img_path):
    image = Image.open(img_path)
    watermarked_image = Image.new(mode='RGBA', size=image.size, color=(0, 0, 0, 0))
    watermarked_image.paste(image, (0, 0))
    if dynamic_font_size:
        fs = int(image.size[1] * font_size_perc)
    else:
        fs = font_size
    font = ImageFont.truetype(font_name, size=fs)

    draw = ImageDraw.Draw(watermarked_image)
    color = hex_to_rgba(hex_color, opacity)

    # pillow sometimes draws texts offscreen, for some reason. to counteract this, we have to add some padding (percentage-based) to the canvas we draw the text on
    text_width, text_height = new_get_text_size(text, font)
    rotated_text = Image.new('RGBA', (int(text_width), int(text_height * (1 + text_canvas_padding))), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(rotated_text)
    text_draw.text((0, 0), text, font=font, fill=color)
    rotated_text = rotated_text.rotate(rotation_angle, expand=1)

    y = -int(y_start_perc * rotated_text.height)
    while y < watermarked_image.height:
        for x in range(0, watermarked_image.width, int(rotated_text.width * (1+x_increment_perc))):
            watermarked_image.alpha_composite(rotated_text, (x, y))
        y += int(y_increment_perc * rotated_text.height)

    new_image_path = os.path.splitext(img_path)[0] + "_watermarked.png"
    watermarked_image.save(new_image_path)

# text = os.environ['text']
opacity = float(os.environ['opacity'])
# hex_color = os.environ['hex_color']
font_size_perc = float(os.environ['font_size_perc'])
rotation_angle = float(os.environ['rotation_angle'])
y_start_perc = float(os.environ['y_start_perc'])
y_increment_perc = float(os.environ['y_increment_perc'])
x_increment_perc = float(os.environ['x_increment_perc'])
text_canvas_padding = float(os.environ['text_canvas_padding'])
dynamic_font_size = int(os.environ['dynamic_font_size'])
font_size = int(os.environ['font_size'])
font_name = os.environ['font']

query = sys.argv[1]
elements = query.split("||")
file_paths = elements[0].strip().split("|")
text = elements[1]
hex_color = elements[2]

for fp in file_paths:
    add_watermark(fp)

print(f"Watermark added for {len(file_paths)} images.")

