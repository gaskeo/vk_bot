from constants import MIN_CHAT_PEER_ID, ADMIN_TEXT
from utils import send_message


def admin_help(self, _, __, peer_id):
    if not peer_id > MIN_CHAT_PEER_ID:

        level: int = self.redis.get_admin(str(peer_id))
        if level > 0:
            send_message(ADMIN_TEXT, self.vk, peer_id=peer_id)
        else:
            send_message("У вас нет доступа к данной команде", self.vk, peer_id=peer_id)
