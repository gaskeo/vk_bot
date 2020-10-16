from PIL import Image, ImageFont, ImageDraw, ImageSequence
from io import BytesIO

import random
import string

from utils import get_random_funny_wiki_page, get_only_symbols
from constants import FONTS_PATH, ARABIC_FONT

from constants import TEXT_COLORS


def create_grain(image: BytesIO or str, factor: int) -> str:
    """
    create grain image from source image
    :param image: bytes of image or file's name
    :param factor: factor of image grain
    :return: name of file in /photos directory

    """
    image = Image.open(image)
    width = image.size[0]
    height = image.size[1]
    pix = image.load()
    for i in range(width):
        for j in range(height):
            random_factor = random.randint(-factor, factor)
            r = pix[i, j][0] + random_factor
            g = pix[i, j][1] + random_factor
            b = pix[i, j][2] + random_factor
            if r < 0:
                r = 0
            if g < 0:
                g = 0
            if b < 0:
                b = 0
            if r > 255:
                r = 255
            if g > 255:
                g = 255
            if b > 255:
                b = 255
            pix[i, j] = r, g, b
    name = "photos/{}.jpg"\
        .format(''.join(random.choice(string.ascii_uppercase
                                      + string.ascii_lowercase + string.digits) for _ in range(16)))
    image.save(name)
    return name


def create_shakal(image: BytesIO or str, factor: int) -> str:
    """
    create shakal image from source image
    :param image: bytes of image or file's name
    :param factor: factor of image grain
    :return: name of file in /photos directory

    """
    name = "photos/{}.jpg" \
        .format(''.join(random.choice(string.ascii_uppercase
                                      + string.ascii_lowercase + string.digits) for _ in range(16)))
    image = Image.open(image)
    start_size = image.size
    image.save(name)
    for i in range(factor):
        image = Image.open(name)
        image = image.resize((int(image.size[0] / 1.1), int(image.size[1] / 1.1)))
        size = image.size
        image.save(name, quality=5)
        if size[0] < 10 or size[1] < 10:
            break

    image = Image.open(name)
    image = image.resize(start_size)
    image.save(name)
    return name


def create_arabic_meme(image: BytesIO or str, text_color: str = "black") -> tuple:
    """
    create arabic meme from source image
    :param image: bytes of image or file's name
    :param text_color: english text of text
    :return: tuple like (name of file in /photos directory, text on mem)

    """
    image = Image.open(image)
    draw = ImageDraw.Draw(image)
    text = get_random_funny_wiki_page()
    only_symbols = get_only_symbols(text)[::-1]
    size = image.size[0], image.size[1]
    font_size = size[1] // 6
    font = ImageFont.truetype(f"{FONTS_PATH}{ARABIC_FONT}", font_size,
                              layout_engine=ImageFont.LAYOUT_BASIC)
    text_size = draw.textsize(only_symbols, font=font)
    x, y = (size[0] - text_size[0]) // 2, (size[1] - int((text_size[1])) - 2)
    while x <= 0 and font_size > 1:
        font_size -= 1
        font = ImageFont.truetype(f"{FONTS_PATH}{ARABIC_FONT}", font_size,
                                  layout_engine=ImageFont.LAYOUT_BASIC)
        text_size = draw.textsize(only_symbols, font=font)
        x = (size[0] - text_size[0]) // 2
    offset = 3
    if text_color not in TEXT_COLORS.keys():
        text_color = "black"
    shadow_color = TEXT_COLORS[text_color]

    for off in range(offset):
        draw.text((x - off, size[1] - int(text_size[1])), only_symbols, font=font, fill=shadow_color)
        draw.text((x + off, size[1] - int(text_size[1])), only_symbols, font=font, fill=shadow_color)
        draw.text((x, size[1] - int(text_size[1]) + off), only_symbols, font=font, fill=shadow_color)
        draw.text((x, size[1] - int(text_size[1]) - off), only_symbols, font=font, fill=shadow_color)
        draw.text(
            (x - off, size[1] - int(text_size[1]) + off), only_symbols, font=font, fill=shadow_color)
        draw.text(
            (x + off, size[1] - int(text_size[1]) + off), only_symbols, font=font, fill=shadow_color)
        draw.text(
            (x - off, size[1] - int(text_size[1]) - off), only_symbols, font=font, fill=shadow_color)
        draw.text(
            (x + off, size[1] - int(text_size[1]) - off), only_symbols, font=font, fill=shadow_color)
    draw.text(((size[0] - text_size[0]) // 2, (size[1] - int((text_size[1])))),
              text=only_symbols, font=font, fill=text_color)
    name = "photos/{}.jpg" \
        .format(''.join(random.choice(string.ascii_uppercase
                                      + string.ascii_lowercase + string.digits) for _ in range(16)))
    image.save(name)
    return name, text


