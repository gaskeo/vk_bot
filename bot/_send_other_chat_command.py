from vk_api import bot_longpoll

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def send_other_chat(self: 'Bot', event: bot_longpoll.VkBotMessageEvent, message: str, peer_id: int):
    connected_peer_id = self.redis.get_connected_chat(str(peer_id))
    if connected_peer_id:
        message = message.lstrip("/send").strip()
        if message:
            self.send_message(f"сообщение из другой беседы: {message}", str(connected_peer_id))
            self.send_message("отправлено", str(peer_id), reply_to=event.obj.message.get("id"))
        else:
            self.send_message("пустое сообщение", str(peer_id))
    else:
        self.send_message("вы ни к кому не подключены", str(peer_id))
