from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def test(self: 'Bot', _, __, peer_id: int):
    self.send_message("это тест... ничего интересного", str(peer_id))
