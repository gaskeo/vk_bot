from vk_api import bot_longpoll

from PIL import Image, JpegImagePlugin, ImageDraw
import random
import urllib.request
from io import BytesIO
import cv2

from my_vk_api import find_images

from typing import TYPE_CHECKING

from utils import generate_token

if TYPE_CHECKING:
    from . import Bot

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def create_dab(self: 'Bot',
               event: bot_longpoll.VkBotMessageEvent, _, peer_id: int):
    def create_dab_function(image_dab: BytesIO or str) -> str:
        def create_rect():
            def check_compatibility(s: tuple):
                rw = abs(s[2] - s[0])
                rh = abs(s[3] - s[1])
                dr = dab_w / dab_h
                pr = rw / rh
                return abs(dr - pr)

            def resize(dw, dh):
                if dw + start[0] > ds[0]:
                    dh = int((ds[0] / dw) * dh) - 2 * coefficient
                    dw = ds[0] - 2 * coefficient
                if dh + start[1] > ds[1]:
                    dw = int((ds[1] / dh) * dw) - 2 * coefficient
                    dh = ds[1] - 2 * coefficient
                return dw, dh

            def distance_to_right_corner(s: tuple):
                return ((s[0] - right_corner[0]) ** 2 +
                        (s[1] - right_corner[1]) ** 2) ** 0.5

            sizes = {
                # 0 1
                # 2 3
                (0, 0, size[0], y): 3,  # top
                (0, 0, x, size[1]): 3,  # left
                (0, y + h, size[0], size[1]): 1,  # bottom
                (x + w, 0, size[0], size[1]): 2  # right
            }
            r = (w + 60) // 2
            dab: JpegImagePlugin.JpegImageFile = \
                Image.open(second_image)
            dab_w, dab_h = dab.size
            where = min(tuple(sizes.keys()), key=check_compatibility)
            coefficient = int(abs(where[2] - where[0]) * 0.2)
            start = (where[0] + coefficient, where[1] + coefficient)
            angle = sizes[where]
            ds = [abs(where[2] - where[0]), abs(where[3] - where[1])]
            dab_w, dab_h = resize(dab_w, dab_h)
            corners = (
                (center[0] - r * (2 ** 0.5 / 2),
                 (center[1] - r * (2 ** 0.5 / 2))),

                (center[0] + r * (2 ** 0.5 / 2),
                 (center[1] - r * (2 ** 0.5 / 2))),

                (center[0] - r * (2 ** 0.5 / 2),
                 (center[1] + r * (2 ** 0.5 / 2))),

                (center[0] + r * (2 ** 0.5 / 2),
                 (center[1] + r * (2 ** 0.5 / 2)))
            )
            if angle == 3:
                right_corner = start[0] + dab_w, start[1] + dab_h
            elif angle == 1:
                right_corner = start[0] + dab_w, start[1]
            else:
                right_corner = start[0], start[1] + dab_h
            corner_for_line = min(corners, key=distance_to_right_corner)
            dab = dab.resize((dab_w, dab_h))
            image_dab.paste(dab, start)
            draw.rectangle((start,
                            (start[0] + dab_w, start[1] + dab_h)),
                           outline=(255, 0, 0), width=5)
            draw.line((right_corner, corner_for_line),
                      width=5, fill=(255, 0, 0))
            image_dab.save(name)

        name = "static/photos/{}.jpg".format(generate_token(16))
        with open(name, "wb") as dfn:
            dfn.write(image_dab.getbuffer())
        image_dab = Image.open(image_dab)
        size = image_dab.size
        draw = ImageDraw.Draw(image_dab)
        image_cv2 = cv2.imread(name)
        image_cv2 = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(image_cv2, 1.1, 19)
        if len(faces):
            x, y, w, h = faces[0]
        else:
            w = h = random.randint(int(size[0] * 0.1),
                                   int(size[0] * 0.5))

            x, y = (random.randint(w, size[0] - w),
                    random.randint(h, size[0] - h))
        draw.ellipse(((x - 30, y - 30), (x + w + 30, y + h + 30)),
                     outline=(255, 0, 0),
                     width=5)
        center = (2 * x + w) // 2, (2 * y + h) // 2
        create_rect()
        return name

    photos = find_images(event)
    if len(photos) == 2:
        image, second_image = photos
    elif len(photos) == 1:
        image = photos[0]
        second_image = None
    else:
        self.send_message("Прикрепи 1 или 2 фото", str(peer_id))
        return
    if second_image:
        url = max(second_image["photo"]["sizes"],
                  key=lambda x: x["width"])["url"]

        img = urllib.request.urlopen(url).read()
        second_image = BytesIO(img)
        dab_name = "static/photos/{}.jpg".format(generate_token(16))
        with open(dab_name, "wb") as f:
            f.write(bytes(second_image.getbuffer()))
        second_image = dab_name
    else:
        second_image = "static/photos_examples/dab.png"
    url = max(image["photo"]["sizes"], key=lambda x: x["width"])["url"]
    img = urllib.request.urlopen(url).read()
    bytes_img = BytesIO(img)
    photo_bytes = create_dab_function(bytes_img)
    self.send_photo(photo_bytes, str(peer_id),
                    second_image=second_image)
