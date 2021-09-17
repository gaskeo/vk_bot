import os


def send_photo(self, photo_bytes, peer_id, second_image=None, text="", **kwargs):
    photo = self.upload.photo_messages(photos=[photo_bytes], peer_id=peer_id)
    vk_photo_id = \
        f"photo{photo[0]['owner_id']}_{photo[0]['id']}_{photo[0]['access_key']}"
    self.send_message(text, peer_id=peer_id, attachments=vk_photo_id, **kwargs)
    os.remove(photo_bytes)
    if second_image and second_image != "photos_examples/dab.png":
        os.remove(second_image)
