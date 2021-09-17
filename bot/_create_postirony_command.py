from vk_api import bot_longpoll

import random

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Bot


def create_postirony(self: 'Bot', event: bot_longpoll.VkBotMessageEvent, message: str, peer_id: int):
    if len(message.split()) > 1:
        text_p = "".join(
            [(symbol.lower() + (" " if symbol in "*@" else "")) if random.choice((0, 1))
             else symbol.upper() + (" " if symbol in "*@" else "")
             for symbol in " ".join(message.split()[1:])])
        self.send_message(text_p, str(peer_id))
    else:
        if event.obj.message.get("reply_message", False):
            message = event.obj.message["reply_message"]["text"]
            if len(message.split()) > 0:
                text_p = "".join(
                    [(symbol.lower() + (" " if symbol in "*@" else "")) if random.choice((0, 1))
                     else symbol.upper() + (" " if symbol in "*@" else "")
                     for symbol in " ".join(message.split())])
                self.send_message(text_p, str(peer_id))
            else:
                self.send_message("нЕт сЛОв", str(peer_id))
