import random

from my_vk_api import delete_user_mentions

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot


def create_postirony(self: 'Bot', _, message: str, peer_id: int):
    if len(message) < 1:
        return self.send_message("нЕт сЛОв", str(peer_id))

    message = delete_user_mentions(message)

    answer = "".join(
        [symbol.lower() if random.choice((0, 1))
         else symbol.upper()
         for symbol in message])

    return self.send_message(answer, str(peer_id)) if answer else ...
