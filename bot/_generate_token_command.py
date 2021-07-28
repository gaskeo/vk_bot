from secrets import token_hex

from constants import MIN_CHAT_PEER_ID
from utils import send_message


def generate_token(self, _, __, peer_id):
    if not peer_id > MIN_CHAT_PEER_ID:
        send_message("только для бесед", self.vk, peer_id)
        return
    token = token_hex(24)
    self.redis.add_token(str(peer_id), token)
    send_message(f"Введите это в другой беседе:", self.vk, peer_id)
    send_message(f"/connect {token}", self.vk, peer_id)
