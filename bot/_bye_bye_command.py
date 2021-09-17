from loguru import logger
import time
import threading

from . import StopEvent

from constants import MIN_CHAT_PEER_ID, CHIEF_ADMIN


def bye_bye(self, _, __, peer_id):
    if not peer_id > MIN_CHAT_PEER_ID:
        if self.redis.get_admin(peer_id) >= 5:
            self.send_message("Завершаю работу...", peer_id=peer_id)
            self.redis.redis.save()
            self.send_message("Закрыл базу", peer_id=peer_id)

            if peer_id != int(CHIEF_ADMIN):
                self.send_message(f"Завершаю работу по команде @id{peer_id}",
                                  peer_id=int(CHIEF_ADMIN))
            self.send_message("Завершаю работу всей программы", peer_id=peer_id)
            [self.add_event_in_queue(StopEvent) for _ in range(self.n_threads)]
            logger.info(f"exit by {peer_id} | uptime: {int(time.time() - self.uptime)}s")
            logger.info(f"thread {threading.currentThread().name} stopped")
            self.send_message("пока пока...", peer_id)
            exit(0)
        else:
            self.send_message("У вас нет доступа к данной команде", peer_id=peer_id)
