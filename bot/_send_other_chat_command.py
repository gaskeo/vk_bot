from utils import send_message


def send_other_chat(self, _, message, peer_id):
    connected_peer_id = self.redis.get_connected_chat(str(peer_id))
    if connected_peer_id:
        message = message.lstrip("/send").strip()
        if message:
            send_message(f"сообщение из другой беседы: {message}", self.vk, int(connected_peer_id))
            send_message("отправлено", self.vk, peer_id)
        else:
            send_message("пустое сообщение", self.vk, peer_id)
    else:
        send_message("вы ни к кому не подключены", self.vk, peer_id)
