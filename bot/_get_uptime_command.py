import datetime
import time

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def get_uptime(self: 'Bot', _, __, peer_id: int):
    self.send_message("я живу уже "
                      f"{str(datetime.timedelta(seconds=int(time.time() - self.uptime)))}", str(peer_id))
