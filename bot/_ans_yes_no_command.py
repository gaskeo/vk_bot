import random


def answer_yes_no(self, event, message, peer_id):
    data = message.strip().rstrip("?").split()[1:]
    if not data:
        data = event.obj.message.get("reply_message", dict()).get("text", "").split()

    answer = random.choice(("да", "нет", "дет"))

    if not data:
        text = answer
    else:
        text = " ".join(data[1:]) + "? - " + answer

    self.send_message(text, peer_id, reply_to=event.obj.message.get("id"))
