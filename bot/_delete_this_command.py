from utils import send_message, get_admins_in_chat


def delete_this(self, event, message, peer_id):
    admins = get_admins_in_chat(peer_id, self.vk)
    if event.obj.message["from_id"] in admins:
        if len(message.split()) > 1:
            self.speaker.delete_words(peer_id, message)
            send_message(f"очищены слова: {message[3:]}", self.vk, peer_id)
        else:
            if event.obj.message.get("reply_message", False):
                message = event.obj.message["reply_message"]["text"]
                if len(message.split()) > 0:
                    self.speaker.delete_words(peer_id, message)
                    send_message(f"очищены слова: {message[3:]}", self.vk, peer_id)
            else:
                send_message("ответь на сообщение или напиши текст после команды",
                             self.vk, peer_id)
    else:
        send_message("чел ты не админ...", self.vk, peer_id)
