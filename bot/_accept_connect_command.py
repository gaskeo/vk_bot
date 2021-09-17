from vk_api import bot_longpoll

from constants import MIN_CHAT_PEER_ID
from my_vk_api import get_admins_in_chat

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Bot


def accept_connect(self: 'Bot', event: bot_longpoll.VkBotEvent, _, peer_id: int):
    print(type(event))
    if peer_id > MIN_CHAT_PEER_ID:
        admins = get_admins_in_chat(peer_id, self.vk)
        if event.obj["user_id"] in admins:
            self.redis.connect(str(peer_id), event.obj["payload"]["peer_id"])
            self.redis.delete_token(event.obj["payload"]["token"])
            self.send_message("вы подключились", str(peer_id))
            self.send_message("вы подключились", event.obj["payload"]["peer_id"])
