from PIL import Image
import random
import urllib.request
import os
import string
from io import BytesIO

from utils import send_message, find_image


def create_grain(self, event, message, peer_id):
    def create_grain_function(image_gr: BytesIO or str, factor_sh: int) -> str:
        """
        create grain image from source image
        :param image_gr: bytes of image or file's name
        :param factor_sh: factor of image grain
        :return: name of file in /photos directory
        """
        image_gr = Image.open(image_gr)
        width = image_gr.size[0]
        height = image_gr.size[1]
        pix = image_gr.load()
        for i in range(width):
            for j in range(height):
                random_factor = random.randint(-factor_sh, factor_sh)
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
        name = "photos/{}.jpg" \
            .format(''.join(random.choice(string.ascii_uppercase
                                          + string.ascii_lowercase + string.digits) for _ in
                            range(16)))
        image_gr.save(name)
        return name

    photos = find_image(event)
    if photos:
        factor = 50
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
            name_final_file = create_grain_function(bytes_img, factor)
            photo = self.upload.photo_messages(photos=[name_final_file],
                                               peer_id=peer_id)
            vk_photo_id = \
                f"photo{photo[0]['owner_id']}_{photo[0]['id']}_{photo[0]['access_key']}"
            send_message("", self.vk, peer_id=peer_id, attachments=vk_photo_id)
            os.remove(name_final_file)
    else:
        send_message("Прикрепи фото", self.vk, peer_id=peer_id)
