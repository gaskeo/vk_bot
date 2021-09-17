from utils import get_admins_in_chat


def disconnect(self, event, _, peer_id):
    if event.obj["message"]["from_id"] in get_admins_in_chat(peer_id, self.vk):
        other_peer_id = self.redis.get_connected_chat(str(peer_id))
        if not other_peer_id:
            self.send_message("вы ни к кому не подключены...", peer_id)
            return
        self.redis.disconnect_chats(str(peer_id), other_peer_id)
        self.send_message("вы отключились", peer_id)
        self.send_message("от вас отключились", other_peer_id)
        return
    self.send_message("только админ может это делать", peer_id)
