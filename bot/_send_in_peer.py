from utils import send_message
from constants import MIN_CHAT_PEER_ID


def send_in_peer(self, _, message, peer_id):
    if not peer_id > MIN_CHAT_PEER_ID:
        if self.redis.get_admin(peer_id) >= 5:
            if len(message.split()) < 3:
                send_message('неправильный формат', self.vk, peer_id)
            peer, text = message.split()[1], " ".join(message.split()[2:])
            if self.redis.exist_key(peer):
                send_message(text, self.vk, peer)
            else:
                send_message("нет такой беседы", self.vk, peer_id)
        else:
            send_message("У вас нет доступа к данной команде", self.vk, peer_id=peer_id)