from vk_api import bot_longpoll

from constants import ANSWER_CHANCE, \
    SET_COMMANDS, \
    HUY_CHANCE, \
    CHANCES_ONE_ANSWER, \
    MIN_CHAT_PEER_ID
from my_vk_api import get_admins_in_chat

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot


def set_chance(self: 'Bot', event: bot_longpoll,
               message: str, peer_id: int):
    if not peer_id > MIN_CHAT_PEER_ID:
        return self.send_message(f"Команда только для бесед",
                                 str(peer_id))

    text = event.obj.message.get("text", "")
    if len(text.split()) != 2:
        return self.send_message("Добавьте шанс (от 0 до 100)",
                                 str(peer_id))

    command = text.split()[0]
    what = SET_COMMANDS.get(command)

    if what not in (ANSWER_CHANCE, HUY_CHANCE):
        return self.send_message(
            "эта команда была выпилена в марте 21 года... помянем",
            str(peer_id))

    admins = get_admins_in_chat(peer_id, self.vk)

    if event.obj.message["from_id"] in admins or \
            not self.redis.get_who_can_change_chances(str(peer_id)):
        chance = message
        if not (chance.isdigit() and 0 <= int(chance) <= 100):
            return self.send_message("Должно быть число от 0 до 100",
                                     str(peer_id))

        if what == ANSWER_CHANCE:
            self.redis.change_answer_chance(str(peer_id), int(chance))
        elif what == HUY_CHANCE:
            self.redis.change_huy_chance(str(peer_id), int(chance))

        self.send_message(
            f"Шанс {CHANCES_ONE_ANSWER.get(what, '...')}"
            f" успешно изменен на {chance}%", str(peer_id))
