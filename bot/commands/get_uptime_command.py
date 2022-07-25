import datetime
import time

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot


def get_uptime(self: 'Bot', _, __, peer_id: int):
    uptime = datetime.timedelta(seconds=int(time.time() - self.uptime))
    self.send_message(
        "я живу уже "
        f"{uptime}",
        str(peer_id))
