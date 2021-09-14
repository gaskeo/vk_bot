from utils import send_message


def test(self, _, __, peer_id):
    send_message("это тест... ничего интересного", self.vk, peer_id)
