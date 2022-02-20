from requests import get

from typing import TYPE_CHECKING

from utils import generate_token

if TYPE_CHECKING:
    from . import Bot


def get_cat(self: 'Bot', _, __, peer_id: int):
    data = get("https://api.thecatapi.com/v1/images/search")
    if not data.content:
        return self.send_message("что-то пошло не так", str(peer_id))
    image = get(data.json()[0]["url"]).content
    name = "static/photos/{}.jpg".format(generate_token(16))
    with open(name, "wb") as f:
        f.write(image)
    self.send_photo(name, str(peer_id))
