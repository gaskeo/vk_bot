from vk_api import bot_longpoll

from PIL import Image
import random
import urllib.request
import string
from io import BytesIO

from my_vk_api import find_images

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def create_grain(self: 'Bot', event: bot_longpoll.VkBotMessageEvent, message: str, peer_id: int):
    def create_grain_function() -> str:
        """
        create grain image from source image
        :param image_gr: bytes of image or file's name
        :param factor_sh: factor of image grain
        :return: name of file in /photos directory
        """
        image_gr = Image.open(bytes_img)
        width = image_gr.size[0]
        height = image_gr.size[1]
        pix = image_gr.load()
        for i in range(width):
            for j in range(height):
                random_factor = random.randint(-factor, factor)
                r = min(255, max(0, pix[i, j][0] + random_factor))
                g = min(255, max(0, pix[i, j][1] + random_factor))
                b = min(255, max(0, pix[i, j][2] + random_factor))

                pix[i, j] = r, g, b

        name = "static/photos/{}.jpg" \
            .format(''.join(random.choice(string.ascii_uppercase
                                          + string.ascii_lowercase + string.digits) for _ in
                            range(16)))
        image_gr.save(name)
        return name

    photos = find_images(event)
    if not photos:
        return self.send_message("Прикрепи фото", str(peer_id))

    if not message or not message.isdigit():
        factor = 50
    elif message.isdigit():
        factor = int(message)

    for image in photos:
        url = max(image["photo"]["sizes"], key=lambda x: x["width"])["url"]
        img = urllib.request.urlopen(url).read()
        bytes_img = BytesIO(img)
        name_final_file = create_grain_function()
        self.send_photo(name_final_file, str(peer_id))
