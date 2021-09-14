import random

from utils import send_message


def answer_yes_no(self, event, message, peer_id):
    data = message.strip().rstrip("?").split()[1:]
    if not data:
        data = event.obj.message.get("reply_message", dict()).get("text", "").split()

    answer = random.choice(("да", "нет", "дет"))

    if not data:
        text = answer
    else:
        text = " ".join(data[1:]) + "? - " + answer

    send_message(text, self.vk, peer_id, reply_to=event.obj.message.get("id"))
