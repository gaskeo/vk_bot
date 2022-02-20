import json

from constants import MIN_CHAT_PEER_ID, \
    HUY_CHANCE, \
    ANSWER_CHANCE, \
    CHANCES_ALL_SETTINGS, \
    WHO_CAN_TOGGLE_CHANCES, \
    KEYBOARDS

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def show_settings(self: 'Bot', _, __, peer_id: int):
    if not peer_id > MIN_CHAT_PEER_ID:
        return self.send_message(f"Команда только для бесед",
                                 str(peer_id))

    all_chances = {
        HUY_CHANCE: self.redis.get_huy_chance(str(peer_id)),
        ANSWER_CHANCE: self.redis.get_answer_chance(str(peer_id))
    }

    who = self.redis.get_who_can_change_chances(str(peer_id))

    self.send_message("Настройки беседы:\n{}\n{}".format('\n'.join(
        [f'{CHANCES_ALL_SETTINGS[what]}: '
         f'{int(chance)}%' for what, chance in
         tuple(all_chances.items())]), WHO_CAN_TOGGLE_CHANCES.get(who)),
        str(peer_id),
        keyboard=json.loads(KEYBOARDS)["settings_keyboard"]
    )
