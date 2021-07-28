from constants import MIN_CHAT_PEER_ID
from utils import get_admins_in_chat, send_message


def accept_connect(self, event, _, peer_id):
    if peer_id > MIN_CHAT_PEER_ID:
        admins = get_admins_in_chat(peer_id, self.vk)
        if event.obj["user_id"] in admins:
            self.redis.connect(peer_id, event.obj["payload"]["peer_id"])
            self.redis.delete_token(event.obj["payload"]["token"])
            send_message("вы подключились", self.vk, peer_id)
            send_message("вы подключились", self.vk, event.obj["payload"]["peer_id"])
