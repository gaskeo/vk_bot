from constants import MIN_CHAT_PEER_ID
from utils import send_message, get_admins_in_chat


def clear_chat_speaker(self, event, _, peer_id):
    if peer_id > MIN_CHAT_PEER_ID:
        admins = get_admins_in_chat(peer_id, self.vk)
        if event.obj.message["from_id"] in admins:
            self.speaker.clear_chat(peer_id)
            send_message("слова очищены", self.vk, peer_id)
        else:
            send_message("чел ты не админ...", self.vk, peer_id)
