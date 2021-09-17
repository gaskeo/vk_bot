from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Bot


def archived(self: 'Bot', _, __, peer_id: int):
    self.send_message("данная команда была удалена...", str(peer_id))
