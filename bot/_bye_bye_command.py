import logging
import time
import threading

from constants import MIN_CHAT_PEER_ID, CHIEF_ADMIN
from utils import send_message, StopEvent


def bye_bye(self, _, __, peer_id):
    if not peer_id > MIN_CHAT_PEER_ID:
        if self.redis.get_admin(peer_id) >= 5:
            send_message("Завершаю работу...", self.vk, peer_id=peer_id)
            self.redis.redis.save()
            send_message("Закрыл базу", self.vk, peer_id=peer_id)

            if peer_id != int(CHIEF_ADMIN):
                send_message(f"Завершаю работу по команде @id{peer_id}", self.vk,
                             peer_id=int(CHIEF_ADMIN))
            send_message("Завершаю работу всей программы", self.vk, peer_id=peer_id)
            [self.add_event_in_queue(StopEvent) for _ in range(self.n_threads)]
            logging.info(f"exit by {peer_id} | uptime: {int(time.time() - self.uptime)}s")
            logging.info(f"thread {threading.currentThread().name} stopped")
            send_message("пока пока...", self.vk, peer_id)
            exit(0)
        else:
            send_message("У вас нет доступа к данной команде", self.vk, peer_id=peer_id)
