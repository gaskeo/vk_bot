from utils import send_message


def archived(self, _, __, peer_id):
    send_message("данная команда была удалена...", self.vk, peer_id)