from constants import ANSWER_CHANCE, GET_COMMANDS, \
    CHANCES_ONE_ANSWER, HUY_CHANCE, MIN_CHAT_PEER_ID

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot


def get_chance(self: 'Bot', _, message: str, peer_id: int):
    if not peer_id > MIN_CHAT_PEER_ID:
        return self.send_message(
            f"Команда только для бесед", str(peer_id))

    what = GET_COMMANDS.get(
        "" if len(message.split()) < 1 else message.split()[0].lower(),
        ""
    )

    if what == ANSWER_CHANCE:
        chance = self.redis.get_answer_chance(str(peer_id))
    elif what == HUY_CHANCE:
        chance = self.redis.get_huy_chance(str(peer_id))
    else:
        self.send_message(
            "эта команда была выпилена в марте 21 года... помянем",
            str(peer_id))
        return
    self.send_message(f"Шанс {CHANCES_ONE_ANSWER[what]} равен "
                      f"{chance}%", str(peer_id))
