from utils import send_message


def generate_speak(self, event, message, peer_id):
    word = ""
    if len(message.split()) == 2:
        word = message.split()[1].lower()
    elif event.obj.message.get("reply_message", "").split() == 1:
        word = event.obj.message.get("reply_message")
    answer_message = self.speaker.generate_text(peer_id, word)
    if answer_message:
        send_message(answer_message, self.vk, peer_id, reply_to=event.obj.message.get("id"))
