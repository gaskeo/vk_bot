from vk_api import bot_longpoll

from my_vk_api import get_admins_in_chat

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def disconnect(self: 'Bot', event: bot_longpoll.VkBotMessageEvent,
               _, peer_id: int):
    if event.obj.message.get("from_id", -1) \
            not in get_admins_in_chat(peer_id, self.vk):
        return

    other_peer_id = self.redis.get_connected_chat(str(peer_id))
    if not other_peer_id:
        return self.send_message("вы ни к кому не подключены...",
                                 str(peer_id))

    self.redis.disconnect_chats(str(peer_id), other_peer_id)

    self.send_message("вы отключились", str(peer_id))
    self.send_message("от вас отключились", other_peer_id)
