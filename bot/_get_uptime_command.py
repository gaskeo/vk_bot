import datetime
import time

from utils import send_message


def get_uptime(self, _, __, peer_id):
    send_message("я живу уже "
                 f"{str(datetime.timedelta(seconds=int(time.time() - self.uptime)))}",
                 self.vk, peer_id)
