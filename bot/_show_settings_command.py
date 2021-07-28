import json

from constants import MIN_CHAT_PEER_ID,\
    HUY_CHANCE,\
    ANSWER_CHANCE,\
    CHANCES_ALL_SETTINGS,\
    WHO_CAN_TOGGLE_CHANCES,\
    KEYBOARDS
from utils import send_message


def show_settings(self, _, __, peer_id):
    if peer_id > MIN_CHAT_PEER_ID:
        all_chances = {
            HUY_CHANCE: self.redis.get_huy_chance(str(peer_id)),
            ANSWER_CHANCE: self.redis.get_answer_chance(str(peer_id))
        }
        who = self.redis.get_who_can_change_chances(str(peer_id))
        send_message("Настройки беседы:\n{}\n{}".format('\n'.join(
            [f'{CHANCES_ALL_SETTINGS[what]}: '
             f'{int(chance)}%' for what, chance in
             tuple(all_chances.items())]), WHO_CAN_TOGGLE_CHANCES.get(who)),
            self.vk, peer_id=peer_id, keyboard=json.loads(KEYBOARDS)["settings_keyboard"]
        )
    else:
        send_message(f"Команда только для бесед", self.vk, peer_id=peer_id)
