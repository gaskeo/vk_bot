import random

from utils import send_message


def create_postirony(self, event, message, peer_id):
    if len(message.split()) > 1:
        text_p = "".join(
            [(symbol.lower() + (" " if symbol in "*@" else "")) if random.choice((0, 1))
             else symbol.upper() + (" " if symbol in "*@" else "")
             for symbol in " ".join(message.split()[1:])])
        send_message(text_p, self.vk, peer_id=peer_id)
    else:
        if event.obj.message.get("reply_message", False):
            message = event.obj.message["reply_message"]["text"]
            if len(message.split()) > 0:
                text_p = "".join(
                    [(symbol.lower() + (" " if symbol in "*@" else "")) if random.choice((0, 1))
                     else symbol.upper() + (" " if symbol in "*@" else "")
                     for symbol in " ".join(message.split())])
                send_message(text_p, self.vk, peer_id=peer_id)
            else:
                send_message("нЕт сЛОв", self.vk, peer_id=peer_id)
