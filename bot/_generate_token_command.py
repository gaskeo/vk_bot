from secrets import token_hex

from constants import MIN_CHAT_PEER_ID

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Bot


def generate_token(self: 'Bot', _, __, peer_id: int):
    if not peer_id > MIN_CHAT_PEER_ID:
        self.send_message("только для бесед", str(peer_id))
        return
    token = token_hex(24)
    self.redis.add_token(str(peer_id), token)
    self.send_message(f"Введите это в другой беседе:", str(peer_id))
    self.send_message(f"/connect {token}", str(peer_id))
