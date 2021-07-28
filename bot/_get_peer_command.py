from utils import send_message


def get_peer(self, _, __, peer_id):
    send_message(f"peer_id: {str(peer_id)}", self.vk, peer_id)