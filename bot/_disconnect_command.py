from utils import send_message, get_admins_in_chat


def disconnect(self, event, _, peer_id):
    if event.obj["message"]["from_id"] in get_admins_in_chat(peer_id, self.vk):
        other_peer_id = self.redis.get_connected_chat(str(peer_id))
        if not other_peer_id:
            send_message("вы ни к кому не подключены...", self.vk, peer_id)
            return
        self.redis.disconnect_chats(str(peer_id), other_peer_id)
        send_message("вы отключились", self.vk, peer_id)
        send_message("от вас отключились", self.vk, int(other_peer_id))
        return
    send_message("только админ может это делать", self.vk, peer_id)
