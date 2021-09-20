from vk_api import bot_longpoll

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Bot


def get_words_after_that(self: 'Bot', event: bot_longpoll.VkBotMessageEvent, message: str, peer_id: int):
    def send_ans():
        if "///end" in words:
            words.remove("///end")
        if not words:
            return self.send_message("ничего нет", str(peer_id))
        self.send_message((f"после {message} идет:\n" +
                           "\n".join(("- " + i for i in words))), str(peer_id), reply_to=event.obj.message.get("id"))

    if len(message) > 0:
        words = list(self.redis.get_words_after_that(str(peer_id), message).keys())
        return send_ans()