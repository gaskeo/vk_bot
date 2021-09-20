from vk_api import bot_longpoll

import random

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def answer_yes_no(self: 'Bot', event: bot_longpoll.VkBotMessageEvent, message: str, peer_id: int):
    message = message.rstrip("?")
    answer = random.choice(("да", "нет", "дет"))

    if not message:
        text = answer
    else:
        text = f"{message}? - {answer}"

    self.send_message(text, str(peer_id), reply_to=event.obj.message.get("id"))
