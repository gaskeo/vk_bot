from constants import MIN_CHAT_PEER_ID
from utils import send_message


def alive_threads(self, _, __, peer_id):
    if not peer_id > MIN_CHAT_PEER_ID:
        if self.redis.get_admin(peer_id) >= 5:
            threads = "тред " + \
                      '\nтред '.join((y[0] for y in
                                      tuple(filter(lambda x: x[1] == 1, self.threads.items()))))
            send_message(f"живые треды (из {self.n_threads}):\n{threads}", self.vk, peer_id)
