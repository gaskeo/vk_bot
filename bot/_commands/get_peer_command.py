from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot


def get_peer(self: 'Bot', _, __, peer_id: int):
    self.send_message(f"peer_id: {str(peer_id)}", str(peer_id))
