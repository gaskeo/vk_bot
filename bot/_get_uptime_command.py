import datetime
import time


def get_uptime(self, _, __, peer_id):
    self.send_message("я живу уже "
                      f"{str(datetime.timedelta(seconds=int(time.time() - self.uptime)))}", peer_id)
