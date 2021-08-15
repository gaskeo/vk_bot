from PIL import Image, ImageDraw, ImageFont
import random
import urllib.request
import string
from io import BytesIO

from constants import TEXT_COLORS, FONTS_PATH, ARABIC_FONT
from utils import send_message, get_random_funny_wiki_page, get_only_symbols, find_image


def create_arabfunny(self, event, message, peer_id):
    def create_arabfunny_function(image_ar: BytesIO or str, text_color: str = "black") -> tuple:
        """
        create arabic meme from source image
        :param image_ar: bytes of image or file's name
        :param text_color: english text of text
        :return: tuple like (name of file in /photos directory, text on mem)
        """
        image_ar = Image.open(image_ar)
        draw = ImageDraw.Draw(image_ar)
        text_ar = get_random_funny_wiki_page()
        only_symbols = get_only_symbols(text_ar)[::-1]
        size = image_ar.size[0], image_ar.size[1]
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
            draw.text((x - off, size[1] - int(text_size[1])), only_symbols, font=font,
                      fill=shadow_color)
            draw.text((x + off, size[1] - int(text_size[1])), only_symbols, font=font,
                      fill=shadow_color)
            draw.text((x, size[1] - int(text_size[1]) + off), only_symbols, font=font,
                      fill=shadow_color)
            draw.text((x, size[1] - int(text_size[1]) - off), only_symbols, font=font,
                      fill=shadow_color)
            draw.text(
                (x - off, size[1] - int(text_size[1]) + off), only_symbols, font=font,
                fill=shadow_color)
            draw.text(
                (x + off, size[1] - int(text_size[1]) + off), only_symbols, font=font,
                fill=shadow_color)
            draw.text(
                (x - off, size[1] - int(text_size[1]) - off), only_symbols, font=font,
                fill=shadow_color)
            draw.text(
                (x + off, size[1] - int(text_size[1]) - off), only_symbols, font=font,
                fill=shadow_color)
        draw.text(((size[0] - text_size[0]) // 2, (size[1] - int((text_size[1])))),
                  text=only_symbols, font=font, fill=text_color)
        name = "photos/{}.jpg" \
            .format(''.join(random.choice(string.ascii_uppercase
                                          + string.ascii_lowercase + string.digits) for _ in
                            range(16)))
        image_ar.save(name)
        return name, text_ar

    color = 0
    photos = find_image(event)
    if photos:
        if len(message.split()) > 1:
            color = message.split()[-1]
        for image in photos:
            url = max(image["photo"]["sizes"], key=lambda x: x["width"])["url"]
            img = urllib.request.urlopen(url).read()
            bytes_img = BytesIO(img)
            name_final_file, text = create_arabfunny_function(bytes_img, color)
            self.photo_work(name_final_file, peer_id)
    else:
        send_message("Прикрепи фото", self.vk, peer_id=peer_id)
