from constants import MIN_CHAT_PEER_ID, ADMIN_TEXT


def admin_help(self, _, __, peer_id):
    if not peer_id > MIN_CHAT_PEER_ID:

        level: int = self.redis.get_admin(str(peer_id))
        if level > 0:
            self.send_message(ADMIN_TEXT, self.vk, peer_id=peer_id)
        else:
            self.send_message("У вас нет доступа к данной команде", peer_id=peer_id)
