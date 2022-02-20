import threading

from constants import MIN_CHAT_PEER_ID, ENTER

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def alive_threads(self: 'Bot', _, __, peer_id: int):
    if peer_id > MIN_CHAT_PEER_ID \
            or not self.redis.get_admin(peer_id) >= 5:
        return

    check_lines = []

    for thread in self.threads.items():
        if thread[1] == 1:
            check_lines.append(f"тред {thread[0]} жив")
        elif thread[0] == threading.currentThread().name:
            check_lines.append(f"тред {thread[0]} жив (это я)")
        elif thread[1] == 0:
            check_lines.append(f"тред {thread[0]} умер или работает...")

    self.send_message(f"живые треды (из {self.n_threads}):\n"
                      f"{ENTER.join(check_lines)}", str(peer_id))
