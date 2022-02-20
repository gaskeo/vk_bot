from vk_api import bot_longpoll

from constants import MIN_CHAT_PEER_ID
from my_vk_api import get_random_user_from_conversation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def lox_command(self: 'Bot',
                event: bot_longpoll.VkBotMessageEvent,
                __, peer_id: int):
    if not peer_id >= MIN_CHAT_PEER_ID:
        return

    user_id = get_random_user_from_conversation(self.vk, peer_id)
    self.send_message(
        f"вот этот: vk.com/id{user_id}",
        str(peer_id), reply_to=event.obj.message.get("id"))
