from vk_api import bot_longpoll

from my_vk_api import get_admins_in_chat
from constants import MIN_CHAT_PEER_ID

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def accept_connect(self: 'Bot', event: bot_longpoll.VkBotEvent, _, peer_id: int):
    if peer_id < MIN_CHAT_PEER_ID:
        return

    admins: list = get_admins_in_chat(peer_id, self.vk)
    if event.obj.get("user_id", -1) not in admins:
        return

    peer_id2 = event.obj.get("payload", dict()).get("peer_id")
    if not peer_id2:
        return self.send_message("ошибка...", str(peer_id))

    self.redis.connect(str(peer_id), peer_id2)
    self.redis.delete_token(event.obj.get("payload", dict()).get("token"))

    self.send_message("вы подключились", str(peer_id))
    self.send_message("вы подключились", event.obj["payload"]["peer_id"])
