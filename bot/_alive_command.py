from utils import send_message


def alive(self, _, __, peer_id):
    send_message("жив цел", self.vk, peer_id)
