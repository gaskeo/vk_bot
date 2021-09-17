from constants import MIN_CHAT_PEER_ID

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Bot


def alive_threads(self: 'Bot', _, __, peer_id: int):
    if not peer_id > MIN_CHAT_PEER_ID:
        if self.redis.get_admin(peer_id) >= 5:
            threads = "тред " + \
                      '\nтред '.join((y[0] for y in
                                      tuple(filter(lambda x: x[1] == 1, self.threads.items()))))
            self.send_message(f"живые треды (из {self.n_threads}):\n{threads}", str(peer_id))
