from loguru import logger
import time
import threading

from . import StopEvent
from constants import MIN_CHAT_PEER_ID, CHIEF_ADMIN

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def bye_bye(self: 'Bot', _, __, peer_id: int):
    if peer_id > MIN_CHAT_PEER_ID:
        return

    if self.redis.get_admin(peer_id) < 5:
        return

    self.send_message("Завершаю работу...", str(peer_id))

    self.redis.redis.save()
    self.send_message("Закрыл базу", str(peer_id))

    if peer_id != int(CHIEF_ADMIN):
        self.send_message(f"Завершаю работу по команде @id{peer_id}",
                          str(CHIEF_ADMIN))

    self.send_message("Завершаю работу всей программы", str(peer_id))
    [self.add_event_in_queue(StopEvent) for _ in range(self.n_threads)]

    logger.info(f"exit by {peer_id} | uptime: "
                f"{int(time.time() - self.uptime)}s")
    logger.info(f"thread {threading.currentThread().name} stopped")

    self.send_message("пока пока...", str(peer_id))
    exit(0)
