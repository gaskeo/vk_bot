from vk_api import bot_longpoll

from constants import MIN_CHAT_PEER_ID, WHO_CAN_TOGGLE_CHANCES
from my_vk_api import get_admins_in_chat

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def toggle_access_chat_settings(self: 'Bot', event: bot_longpoll.VkBotMessageEvent, _, peer_id: int):
    if peer_id > MIN_CHAT_PEER_ID:
        admins = get_admins_in_chat(peer_id, self.vk)
        if event.obj.message["from_id"] in admins:
            who = self.redis.toggle_access_chances(str(peer_id))
            self.send_message(WHO_CAN_TOGGLE_CHANCES.get(who), str(peer_id))
    else:
        self.send_message("Команда только для бесед", str(peer_id))
