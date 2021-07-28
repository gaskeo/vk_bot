from utils import send_message


def generate_speak(self, _, __, peer_id):
    message = self.speaker.generate_text(peer_id)
    if message:
        send_message(message, self.vk, peer_id)