from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Bot


def clear_keyboard(self: 'Bot', _, __, peer_id: int):
    empty_keyboard = {
        "one_time": False,
        "buttons": []
    }
    self.send_message("убрал клавиатуру", str(peer_id), keyboard=empty_keyboard)
