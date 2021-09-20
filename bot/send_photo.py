import os

from typing import TYPE_CHECKING, Any

import vk_api.exceptions

if TYPE_CHECKING:
    from . import Bot


def send_photo(self: 'Bot',
               photo: Any,
               peer_id: str = None,
               second_image: Any = None,
               text: str = "", **kwargs):
    try:
        photo_returned = self.upload.photo_messages(photos=[photo], peer_id=int(peer_id))
    except vk_api.exceptions.ApiError as e:
        os.remove(photo)
        if second_image and second_image != "static/photos_examples/dab.png":
            os.remove(second_image)

        return self.send_message("у меня не получилось отправить картинку, возможно у меня нет прав", peer_id)

    vk_photo_id = \
        f"photo{photo_returned[0]['owner_id']}_{photo_returned[0]['id']}_{photo_returned[0]['access_key']}"
    self.send_message(text, peer_id=peer_id, attachments=vk_photo_id, **kwargs)
    os.remove(photo)
    if second_image and second_image != "static/photos_examples/dab.png":
        os.remove(second_image)
