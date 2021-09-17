from constants import MIN_CHAT_PEER_ID
from my_vk_api import get_admins_in_chat


def clear_chat_speaker(self, event, _, peer_id):
    if peer_id > MIN_CHAT_PEER_ID:
        admins = get_admins_in_chat(peer_id, self.vk)
        if event.obj.message["from_id"] in admins:
            self.speaker.clear_chat(peer_id)
            self.send_message("слова очищены", peer_id)
        else:
            self.send_message("чел ты не админ...", peer_id)
