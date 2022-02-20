from vk_api import bot_longpoll

from constants import MIN_CHAT_PEER_ID
from my_vk_api import get_admins_in_chat

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def update_chat(self: 'Bot',
                event: bot_longpoll.VkBotMessageEvent, _, peer_id: int):
    if not peer_id > MIN_CHAT_PEER_ID:
        return self.send_message("Команда только для бесед",
                                 str(peer_id))

    admins = get_admins_in_chat(peer_id, self.vk)
    if event.obj.message["from_id"] in admins:
        self.redis.update_chat(str(peer_id))
