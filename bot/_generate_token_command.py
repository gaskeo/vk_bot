from secrets import token_hex

from constants import MIN_CHAT_PEER_ID


def generate_token(self, _, __, peer_id):
    if not peer_id > MIN_CHAT_PEER_ID:
        self.send_message("только для бесед", peer_id)
        return
    token = token_hex(24)
    self.redis.add_token(str(peer_id), token)
    self.send_message(f"Введите это в другой беседе:", peer_id)
    self.send_message(f"/connect {token}", peer_id)
