from constants import MIN_CHAT_PEER_ID
from utils import get_admins_in_chat


def accept_connect(self, event, _, peer_id):
    if peer_id > MIN_CHAT_PEER_ID:
        admins = get_admins_in_chat(peer_id, self.vk)
        if event.obj["user_id"] in admins:
            self.redis.connect(peer_id, event.obj["payload"]["peer_id"])
            self.redis.delete_token(event.obj["payload"]["token"])
            self.send_message("вы подключились", peer_id)
            self.send_message("вы подключились", event.obj["payload"]["peer_id"])
