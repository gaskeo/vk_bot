from vk_api import bot_longpoll

from constants import MIN_CHAT_PEER_ID
from my_vk_api import get_admins_in_chat

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Bot


def clear_chat_speaker(self: 'Bot', event: bot_longpoll.VkBotMessageEvent, _, peer_id: int):
    if peer_id > MIN_CHAT_PEER_ID:
        admins = get_admins_in_chat(peer_id, self.vk)
        if event.obj.message["from_id"] in admins:
            self.redis.clear_chat(str(peer_id))
            self.send_message("слова очищены", str(peer_id))
        else:
            self.send_message("чел ты не админ...", str(peer_id))
