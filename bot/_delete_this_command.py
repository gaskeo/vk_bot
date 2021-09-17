from utils import get_admins_in_chat


def delete_this(self, event, message, peer_id):
    admins = get_admins_in_chat(peer_id, self.vk)
    if event.obj.message["from_id"] in admins:
        if len(message.split()) > 1:
            self.speaker.delete_words(peer_id, message)
            self.send_message(f"очищены слова: {message[3:]}", peer_id)
        else:
            if event.obj.message.get("reply_message", False):
                message = event.obj.message["reply_message"]["text"]
                if len(message.split()) > 0:
                    self.speaker.delete_words(peer_id, message)
                    self.send_message(f"очищены слова: {message[3:]}", peer_id)
            else:
                self.send_message("ответь на сообщение или напиши текст после команды", peer_id)
    else:
        self.send_message("чел ты не админ...", peer_id)
