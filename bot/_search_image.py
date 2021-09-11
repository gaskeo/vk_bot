from requests.models import Response
import random
import string
import re
from utils import send_message

search_in_text = "im0-tub-ru.yandex.net/i"


def search_image(self, _, message, peer_id):
    text = " ".join(message.split()[1:])
    if not text:
        send_message("напишите текст", self.vk, peer_id)
        return

    site_text: str = self.session.get("https://yandex.ru/images/search", params={"text": text, "from": "tabbar"}).text
    site_text = site_text[random.choice([u.start() for u in re.finditer(f"(?={search_in_text})", site_text)]):]
    site_text = site_text[:site_text.find('"')]

    image: Response = self.session.get("https://" + site_text)
    file_format = image.headers["Content-Type"].replace("image/", "")

    name = "photos/{}.{}" \
        .format(''.join(random.choice(string.ascii_uppercase
                                      + string.ascii_lowercase + string.digits) for _ in
                        range(16)), file_format)
    with open(name, "wb") as file:
        file.write(image.content)

    self.photo_work(name, peer_id)



