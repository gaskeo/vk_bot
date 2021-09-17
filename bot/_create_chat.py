from constants import MIN_CHAT_PEER_ID

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Bot


def create_chat(self: 'Bot', _, message: str, peer_id: int):
    title = " ".join(message.split()[1:]) if len(message.split()) > 1 else "нет названия"
    chat_id = self.vk.messages.createChat(title=title)
    answer = self.vk.messages.getInviteLink(peer_id=MIN_CHAT_PEER_ID + chat_id)
    if answer.get("link"):
        self.send_message(answer["link"], str(peer_id))
        return
    self.send_message("что-то пошло не так...", str(peer_id))


