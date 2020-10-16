from PIL import Image, ImageFont, ImageDraw, ImageSequence
from io import BytesIO
import string

from utils import get_random_funny_wiki_page, get_only_symbols
import random

from constants import TEXT_COLORS, ARABIC_FONT, FONTS_PATH


def create_arabic_meme_gif(gif: BytesIO or str) -> tuple:
    """
    create arabic meme from source image
    :param gif: bytes of gif or file's name
    :return: tuple like (name of file in /photos directory, text on mem)

    """
    text = get_random_funny_wiki_page()
    image = Image.open(gif)
    only_symbols = get_only_symbols(text)[::-1]
    size = image.size[0], image.size[1]
    font_size = size[1] // 6
    font = ImageFont.truetype(f"{FONTS_PATH}{ARABIC_FONT}", font_size,
                              layout_engine=ImageFont.LAYOUT_BASIC)
    frame0 = ImageSequence.Iterator(image)[0]
    draw = ImageDraw.Draw(frame0)
    text_size = draw.textsize(only_symbols, font=font)
    x, y = (size[0] - text_size[0]) // 2, (size[1] - int((text_size[1])) - 2)
    while x <= 0 and font_size > 1:
        font_size -= 1
        font = ImageFont.truetype(f"{FONTS_PATH}{ARABIC_FONT}", font_size,
                                  layout_engine=ImageFont.LAYOUT_BASIC)
        text_size = draw.textsize(only_symbols, font=font)
        x = (size[0] - text_size[0]) // 2
    frames = []
    del draw
    offset = 3
    for frame in ImageSequence.Iterator(image):
        frame = frame.convert('RGB')
        draw = ImageDraw.Draw(frame)
        x_d = random.randint(0, size[0] - text_size[0])
        y_d = random.randint(0, size[1] - text_size[1])
        text_color = random.choice(tuple(TEXT_COLORS.keys()))
        shadow_color = random.choice(tuple(TEXT_COLORS.values()))
        for off in range(offset):
            draw.text((x_d - off, y_d), only_symbols, font=font,
                      fill=shadow_color)
            draw.text((x_d + off, y_d), only_symbols, font=font,
                      fill=shadow_color)
            draw.text((x_d, y_d + off), only_symbols, font=font,
                      fill=shadow_color)
            draw.text((x_d, y_d - off), only_symbols, font=font,
                      fill=shadow_color)
            draw.text(
                (x_d - off, y_d + off), only_symbols, font=font,
                fill=shadow_color)
            draw.text(
                (x_d + off, y_d + off), only_symbols, font=font,
                fill=shadow_color)
            draw.text(
                (x_d - off, y_d - off), only_symbols, font=font,
                fill=shadow_color)
            draw.text(
                (x_d + off, y_d - off), only_symbols, font=font,
                fill=shadow_color)
        draw.text((x_d, y_d),
                  text=only_symbols, font=font, fill=text_color)
        b = BytesIO()
        frame.save(b, format="GIF")
        frame = Image.open(b)

        frames.append(frame)
    name = "photos/{}.gif" \
        .format(''.join(random.choice(string.ascii_uppercase
                                      + string.ascii_lowercase + string.digits) for _ in range(16)))
    frames[0].save(name, save_all=True, append_images=frames[1:])

    return name, text

