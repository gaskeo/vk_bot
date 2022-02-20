from vk_api import bot_longpoll

from PIL import Image, ImageDraw, ImageFont
import urllib.request
from io import BytesIO
from itertools import product

from constants import TEXT_COLORS, FONTS_PATH, ARABIC_FONT
from wiki_api import get_random_funny_wiki_page
from utils import get_only_symbols, generate_token
from my_vk_api import find_images

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def create_arabfunny(self: 'Bot', event: bot_longpoll.VkBotMessageEvent,
                     message: str, peer_id: int):
    def create_arabfunny_function() -> tuple:
        offset = 3

        image_ar = Image.open(bytes_img)
        draw = ImageDraw.Draw(image_ar)

        text_ar = get_random_funny_wiki_page()
        only_symbols = get_only_symbols(text_ar)[::-1]

        size = image_ar.size[0], image_ar.size[1]
        font_size = size[1] // 6

        font = ImageFont.truetype(f"{FONTS_PATH}{ARABIC_FONT}",
                                  font_size,
                                  layout_engine=ImageFont.LAYOUT_BASIC)

        text_size = draw.textsize(only_symbols, font=font)

        x = (size[0] - text_size[0]) // 2

        while x <= 0 and font_size > 1:  # adjust text width for image
            font_size -= 1
            font = ImageFont.truetype(
                f"{FONTS_PATH}{ARABIC_FONT}",
                font_size,
                layout_engine=ImageFont.LAYOUT_BASIC)
            text_size = draw.textsize(only_symbols, font=font)
            x = (size[0] - text_size[0]) // 2

        y = size[1] - int(text_size[1])

        shadow_color = TEXT_COLORS[color]

        for off in range(1, offset):  # draw outline
            for off_x, off_y in product((off, -off, 0), repeat=2):
                draw.text((x + off_x, y + off_y), only_symbols,
                          font=font, fill=shadow_color)

        draw.text(((size[0] - text_size[0]) // 2,
                   (size[1] - int((text_size[1])))),
                  text=only_symbols, font=font, fill=color)

        name = "static/photos/{}.jpg".format(generate_token(16))
        image_ar.save(name)
        return name, text_ar

    photos = find_images(event)
    if not photos:
        self.send_message("Прикрепи фото", str(peer_id))
        return

    color = message
    if color not in TEXT_COLORS.keys():
        color = "black"

    for image in photos:
        url = max(image["photo"]["sizes"], key=lambda x: x["width"])[
            "url"]
        img = urllib.request.urlopen(url).read()
        bytes_img = BytesIO(img)
        name_final_file, text = create_arabfunny_function()
        self.send_photo(photo=name_final_file, peer_id=str(peer_id),
                        text=text)
