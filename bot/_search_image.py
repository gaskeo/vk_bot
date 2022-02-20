from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def search_image(self: 'Bot', __, _, peer_id: int):
    self.send_message(
        "эта команда была выпилена в сентябре 21 года... помянем",
        str(peer_id))
