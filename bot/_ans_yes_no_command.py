import random

from utils import send_message


def answer_yes_no(self, _, message, peer_id):
    data = message.strip().rstrip("?").split()
    answer = random.choice(("да", "нет"))
    if len(data) == 1:
        text = answer
    else:
        text = " ".join(data[1:]) + "? - " + answer
    send_message(text, self.vk, peer_id)
