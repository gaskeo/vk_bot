from constants import MIN_CHAT_PEER_ID


def create_chat(self, _, message, peer_id):
    title = " ".join(message.split()[1:]) if len(message.split()) > 1 else "нет названия"
    chat_id = self.vk.messages.createChat(title=title)
    answer = self.vk.messages.getInviteLink(peer_id=MIN_CHAT_PEER_ID + chat_id)
    if answer.get("link"):
        self.send_message(answer["link"], peer_id)
        return
    self.send_message("что-то пошло не так...", peer_id)


