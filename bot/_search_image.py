from requests import get
import random
import string

from PIL import Image
import io

from utils import send_message
from urllib import parse


def search_image(self, event, message, peer_id):
    text = " ".join(message.split()[1:])
    if not text:
        text = event.obj.message.get("reply_message", dict()).get("text", "")
        if not text:
            send_message("напишите текст", self.vk, peer_id, reply_to=event.obj.message.get("id"))
            return
    image = ""
    ex = ""
    images: list = self.image_searcher.find_image(text)
    if not images:
        send_message("ничего не нашлось(\nвозможно лимит на сегодня исчерпан", self.vk, peer_id,
                     reply_to=event.obj.message.get("id"))
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

    self.photo_work(name, peer_id, reply_to=event.obj.message.get("id"))
