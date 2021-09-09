from constants import MIN_CHAT_PEER_ID
from utils import send_message, get_random_user_from_conversation


def lox_command(self, _, __, peer_id):
    if peer_id >= MIN_CHAT_PEER_ID:
        user_id = get_random_user_from_conversation(self.vk, peer_id)
        send_message(f"вот этот: vk.com/id{user_id}", self.vk, peer_id)





