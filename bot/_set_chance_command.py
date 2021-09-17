from constants import ANSWER_CHANCE,\
    LADNO_CHANCE,\
    SET_COMMANDS,\
    HUY_CHANCE, \
    CHANCES_ONE_ANSWER,\
    NU_POLUCHAETSYA_CHANCE,\
    MIN_CHAT_PEER_ID
from utils import get_admins_in_chat


def set_chance(self, event, message, peer_id):
    if peer_id > MIN_CHAT_PEER_ID:
        what = SET_COMMANDS.get(
            "" if len(message.split()) < 1 else message.split()[0].lower(), ""
        )
        if what not in (ANSWER_CHANCE, HUY_CHANCE):
            if what in (LADNO_CHANCE, NU_POLUCHAETSYA_CHANCE):
                self.send_message("эта команда была выпилена в марте 21 года... помянем", peer_id)
            return
        if len(message.split()) == 2:
            admins = get_admins_in_chat(peer_id, self.vk)
            if event.obj.message["from_id"] in admins or \
                    not self.redis.get_who_can_change_chances(str(peer_id)):
                chance = message.split()[1]
                if chance.isdigit() and 0 <= int(chance) <= 100:
                    if what == ANSWER_CHANCE:
                        self.redis.change_answer_chance(str(peer_id), int(chance))
                    elif what == HUY_CHANCE:
                        self.redis.change_huy_chance(str(peer_id), int(chance))
                    self.send_message(f"Шанс {CHANCES_ONE_ANSWER.get(what, '...')}"
                                 f" успешно изменен на {chance}%", peer_id=peer_id)
                else:
                    self.send_message("Должно быть число от 0 до 100", peer_id=peer_id)
        else:
            self.send_message("Добавьте шанс (от 0 до 100)", peer_id=peer_id)
    else:
        self.send_message(f"Команда только для бесед", peer_id=peer_id)
