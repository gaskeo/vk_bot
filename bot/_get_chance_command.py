from constants import ANSWER_CHANCE, GET_COMMANDS, CHANCES_ONE_ANSWER, HUY_CHANCE, MIN_CHAT_PEER_ID


def get_chance(self, _, message, peer_id):
    if peer_id > MIN_CHAT_PEER_ID:
        what = GET_COMMANDS.get(
            "" if len(message.split()) < 1 else message.split()[0].lower(), ""
        )
        if what == ANSWER_CHANCE:
            chance = self.redis.get_answer_chance(str(peer_id))
        elif what == HUY_CHANCE:
            chance = self.redis.get_huy_chance(str(peer_id))
        else:
            self.send_message("эта команда была выпилена в марте 21 года... помянем", peer_id)
            return
        self.send_message(f"Шанс {CHANCES_ONE_ANSWER[what]} равен "
                          f"{chance}%", peer_id=peer_id)
    else:
        self.send_message(f"Команда только для бесед", peer_id=peer_id)
