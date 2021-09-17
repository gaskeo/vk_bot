def send_other_chat(self, event, message, peer_id):
    connected_peer_id = self.redis.get_connected_chat(str(peer_id))
    if connected_peer_id:
        message = message.lstrip("/send").strip()
        if message:
            self.send_message(f"сообщение из другой беседы: {message}", int(connected_peer_id))
            self.send_message("отправлено", peer_id, reply_to=event.obj.message.get("id"))
        else:
            self.send_message("пустое сообщение", peer_id)
    else:
        self.send_message("вы ни к кому не подключены", peer_id)
