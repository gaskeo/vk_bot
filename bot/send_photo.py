import os

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from . import Bot


def send_photo(self: 'Bot',
               photo_bytes: Any,
               peer_id: str = None,
               second_image: Any = None,
               text: str = "", **kwargs):
    photo = self.upload.photo_messages(photos=[photo_bytes], peer_id=int(peer_id))
    vk_photo_id = \
        f"photo{photo[0]['owner_id']}_{photo[0]['id']}_{photo[0]['access_key']}"
    self.send_message(text, peer_id=peer_id, attachments=vk_photo_id, **kwargs)
    os.remove(photo_bytes)
    if second_image and second_image != "photos_examples/dab.png":
        os.remove(second_image)
