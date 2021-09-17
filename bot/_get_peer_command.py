def get_peer(self, _, __, peer_id):
    self.send_message(f"peer_id: {str(peer_id)}", peer_id)
