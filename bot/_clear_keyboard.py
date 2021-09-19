from constants import EMPTY_KEYBOARD

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def clear_keyboard(self: 'Bot', _, __, peer_id: int):
    self.send_message("убрал клавиатуру", str(peer_id), keyboard=EMPTY_KEYBOARD)
