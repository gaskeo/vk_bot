from constants import MIN_CHAT_PEER_ID
from utils import get_admins_in_chat


def update_chat(self, event, _, peer_id):
    if peer_id > MIN_CHAT_PEER_ID:
        admins = get_admins_in_chat(peer_id, self.vk)
        if event.obj.message["from_id"] in admins:
            self.redis.update_chat(str(peer_id))
    else:
        self.send_message("Команда только для бесед", peer_id=peer_id)
