from constants import MIN_CHAT_PEER_ID
from utils import get_random_user_from_conversation


def lox_command(self, event, __, peer_id):
    if peer_id >= MIN_CHAT_PEER_ID:
        user_id = get_random_user_from_conversation(self.vk, peer_id)
        self.send_message(f"вот этот: vk.com/id{user_id}", peer_id, reply_to=event.obj.message.get("id"))
