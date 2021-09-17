from vk_api import bot_longpoll

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Bot


def generate_speak(self: 'Bot', event: bot_longpoll.VkBotMessageEvent, message: str, peer_id: int):
    word = ""
    if len(message.split()) == 2:
        word = message.split()[1].lower()
    elif event.obj.message.get("reply_message", "").split() == 1:
        word = event.obj.message.get("reply_message")
    answer_message = self.redis.generate_text(str(peer_id), word)
    if answer_message:
        self.send_message(answer_message, str(peer_id), reply_to=event.obj.message.get("id"))
