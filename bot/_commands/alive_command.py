from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot


def alive(self: 'Bot', _, __, peer_id: int):
    self.send_message("жив цел", str(peer_id))
