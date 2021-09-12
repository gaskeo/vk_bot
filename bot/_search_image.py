from requests import get
import random
import string

from PIL import Image
import io
from transliterate import translit

from utils import send_message
from urllib import parse


def search_image(self, _, message, peer_id):
    text = " ".join(message.split()[1:])
    if not text:
        send_message("напишите текст", self.vk, peer_id)
        return
    link = ""
    image = ""
    ex = ""
    images: list = self.image_searcher.find_image(translit(text, "ru", reversed=True))
    if not images:
        send_message("ничего не нашлось(", self.vk, peer_id)
        return

    total_images = len(images)
    for _ in range(total_images):
        link = random.choice(images)
        images.pop(images.index(link))
        try:
            response = get(link)
        except Exception as e:
            continue
        try:
            Image.open(io.BytesIO(response.content))
        except Exception as e:
            continue

        image = response.content
        link = link
        ex = parse.urlparse(link).path.split(".")[-1]
        if "/" in ex:
            continue
        break
    name = "photos/{}.{}" \
        .format(''.join(random.choice(string.ascii_uppercase
                                      + string.ascii_lowercase + string.digits) for _ in
                        range(16)), ex)
    with open(name, "wb") as file:
        file.write(image)

    self.photo_work(name, peer_id)
