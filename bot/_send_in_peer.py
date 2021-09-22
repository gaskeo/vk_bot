from constants import MIN_CHAT_PEER_ID

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def send_in_peer(self: 'Bot', _, message: str, peer_id: int):
    if peer_id > MIN_CHAT_PEER_ID:
        return

    if self.redis.get_admin(peer_id) < 5:
        return

    if len(message.split()) < 2:
        return self.send_message('неправильный формат', str(peer_id))

    peer, text = message.split()[0], " ".join(message.split()[1:])

    if self.redis.exist_key(peer):
        return self.send_message(text, peer)
    return self.send_message("нет такой беседы", str(peer_id))
