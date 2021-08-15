from PIL import Image
import random
import urllib.request
import string
from io import BytesIO

from utils import send_message, find_image


def create_shakal(self, event, message, peer_id):
    def create_shakal_function(image_sh: BytesIO or str, factor_sh: int) -> str:
        """
        create shakal image from source image
        :param image_sh: bytes of image or file's name
        :param factor_sh: factor of image grain
        :return: name of file in /photos directory
        """
        name = "photos/{}.jpg" \
            .format(''.join(random.choice(string.ascii_uppercase
                                          + string.ascii_lowercase + string.digits) for _ in
                            range(16)))
        image_sh = Image.open(image_sh)
        start_size = image_sh.size
        for i in range(factor_sh):
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

    photos = find_image(event)
    if photos:
        factor = 5
        if len(message.split()) > 1:
            if message.split()[-1].isdigit():
                factor = int(message.split()[-1])
            else:
                send_message("Степеь должна быть целым числом", self.vk, peer_id=peer_id)
                return
        for image in photos:
            url = max(image["photo"]["sizes"], key=lambda x: x["width"])["url"]
            img = urllib.request.urlopen(url).read()
            bytes_img = BytesIO(img)
            photo_bytes = create_shakal_function(bytes_img, factor)
            self.photo_work(photo_bytes, peer_id)
    else:
        send_message("Прикрепи фото", self.vk, peer_id=peer_id)
