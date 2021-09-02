from utils import send_message


def generate_speak(self, _, message, peer_id):
    word = ""
    if len(message.split()) == 2:
        word = message.split()[1].lower()
    answer_message = self.speaker.generate_text(peer_id, word)
    if answer_message:
        send_message(answer_message, self.vk, peer_id)
