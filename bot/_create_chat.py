from constants import MIN_CHAT_PEER_ID
from utils import send_message


def create_chat(self, _, message, peer_id):
    title = " ".join(message.split()[1:]) if len(message.split()) > 1 else "нет названия"
    chat_id = self.vk.messages.createChat(title=title)
    answer = self.vk.messages.getInviteLink(peer_id=MIN_CHAT_PEER_ID + chat_id)
    if answer.get("link"):
        send_message(answer["link"], self.vk, peer_id)
        return
    send_message("что-то пошло не так...", self.vk, peer_id)


