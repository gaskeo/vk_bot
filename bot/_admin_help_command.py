from constants import MIN_CHAT_PEER_ID, ADMIN_TEXT

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def admin_help(self: 'Bot', _, __, peer_id: int):
    if peer_id > MIN_CHAT_PEER_ID:
        return

    level: int = self.redis.get_admin(str(peer_id))

    if level > 0:
        self.send_message(ADMIN_TEXT, str(peer_id))
