from vk_api import bot_longpoll

from my_vk_api import get_admins_in_chat

from utils import format_text

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Bot


def delete_this(self: 'Bot', event: bot_longpoll.VkBotMessageEvent, message: str, peer_id: int):
    admins = get_admins_in_chat(peer_id, self.vk)
    if event.obj.message["from_id"] in admins:
        if len(message.split()) > 1:
            words = format_text(message)
            self.redis.delete_words_from_text(str(peer_id), words)

            self.send_message(f"очищены слова: {' '.join(message.split()[1:])}", str(peer_id))
        else:
            if event.obj.message.get("reply_message", False):
                message = event.obj.message["reply_message"]["text"]
                if len(message.split()) > 0:
                    words = format_text(message)
                    self.redis.delete_words_from_text(str(peer_id), words)

                    self.send_message(f"очищены слова: {message}", str(peer_id))
            else:
                self.send_message("ответь на сообщение или напиши текст после команды", str(peer_id))
    else:
        self.send_message("чел ты не админ...", str(peer_id))
