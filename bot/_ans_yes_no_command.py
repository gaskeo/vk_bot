from vk_api import bot_longpoll

import random

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Bot


def answer_yes_no(self: 'Bot', event: bot_longpoll.VkBotMessageEvent, message: str, peer_id: int):
    data = message.strip().rstrip("?").split()[1:]
    if not data:
        data = event.obj.message.get("reply_message", dict()).get("text", "").split()

    answer = random.choice(("да", "нет", "дет"))

    if not data:
        text = answer
    else:
        text = " ".join(data[1:]) + "? - " + answer

    self.send_message(text, str(peer_id), reply_to=event.obj.message.get("id"))
