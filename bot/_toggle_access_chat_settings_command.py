from constants import MIN_CHAT_PEER_ID, WHO_CAN_TOGGLE_CHANCES
from utils import send_message, get_admins_in_chat


def toggle_access_chat_settings(self, event, _, peer_id):
    if peer_id > MIN_CHAT_PEER_ID:
        admins = get_admins_in_chat(peer_id, self.vk)
        if event.obj.message["from_id"] in admins:
            who = self.redis.toggle_access_chances(str(peer_id))
            send_message(WHO_CAN_TOGGLE_CHANCES.get(who), self.vk, peer_id=peer_id)
    else:
        send_message("Команда только для бесед", self.vk, peer_id=peer_id)
