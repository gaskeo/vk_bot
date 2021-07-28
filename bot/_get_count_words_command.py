from utils import send_message


def get_count_words(self, _, __, peer_id):
    c = str(self.speaker.get_count_words(peer_id))
    if c:
        send_message(f"количество слов: {c}", self.vk, peer_id)
