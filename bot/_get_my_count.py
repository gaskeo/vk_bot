from vk_api import bot_longpoll

from my_vk_api import get_user_name

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Bot


def get_my_count(self: 'Bot', event: bot_longpoll.VkBotMessageEvent, _, peer_id: int):
    user_id = event.obj.message['from_id']
    count = self.redis.get_count_messages(str(peer_id), str(user_id))
    self.send_message(f"{'@id'}{user_id} ({get_user_name(user_id, self.vk)}): {count}", str(peer_id),
                      reply_to=event.obj.message.get("id"))
