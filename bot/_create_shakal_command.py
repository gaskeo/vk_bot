from vk_api import bot_longpoll

from PIL import Image
import urllib.request
from io import BytesIO

from my_vk_api import find_images

from typing import TYPE_CHECKING

from utils import generate_token

if TYPE_CHECKING:
    from . import Bot


def create_shakal(self: 'Bot', event: bot_longpoll.VkBotMessageEvent,
                  message: str, peer_id: int):
    def create_shakal_function() -> str:
        """
        create shakal image from source image
        :return: name of file in /photos directory
        """
        name = "static/photos/{}.jpg".format(generate_token(16))
        image_sh = Image.open(bytes_img)
        start_size = image_sh.size
        for i in range(factor):
            image_sh = image_sh.resize((int(image_sh.size[0] / 1.1),
                                        int(image_sh.size[1] / 1.1)))
            size = image_sh.size
            image_sh.save(name, quality=5)
            if size[0] < 10 or size[1] < 10:
                break

        image_sh = Image.open(name)
        image_sh = image_sh.resize(start_size)
        image_sh.save(name)
        return name

    photos = find_images(event)
    if not photos:
        return self.send_message("Прикрепи фото", str(peer_id))

    if not message or not message.isdigit():
        factor = 5
    elif message.isdigit():
        factor = int(message)

    for image in photos:
        url = max(image["photo"]["sizes"],
                  key=lambda x: x["width"])["url"]
        img = urllib.request.urlopen(url).read()
        bytes_img = BytesIO(img)
        photo_bytes = create_shakal_function()
        self.send_photo(photo_bytes, str(peer_id))
