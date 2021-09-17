from constants import MIN_CHAT_PEER_ID

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def send_in_peer(self: 'Bot', _, message: str, peer_id: int):
    if not peer_id > MIN_CHAT_PEER_ID:
        if self.redis.get_admin(peer_id) >= 5:
            if len(message.split()) < 3:
                self.send_message('неправильный формат', str(peer_id))
            peer, text = message.split()[1], " ".join(message.split()[2:])
            if self.redis.exist_key(peer):
                self.send_message(text, peer)
            else:
                self.send_message("нет такой беседы", str(peer_id))
        else:
            self.send_message("У вас нет доступа к данной команде", str(peer_id))
