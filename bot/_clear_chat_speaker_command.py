from vk_api import bot_longpoll

from my_vk_api import get_admins_in_chat
from constants import MIN_CHAT_PEER_ID

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def clear_chat_speaker(self: 'Bot', event: bot_longpoll.VkBotMessageEvent, _, peer_id: int):
    if not peer_id > MIN_CHAT_PEER_ID:
        return

    admins = get_admins_in_chat(peer_id, self.vk)

    if event.obj.message.get("from_id", "") not in admins:
        return

    self.redis.clear_chat(str(peer_id))
    self.send_message("слова очищены", str(peer_id))
