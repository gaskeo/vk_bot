from constants import MIN_CHAT_PEER_ID

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import Bot


def create_chat(self: 'Bot', _, message: str, peer_id: int):
    title = message or "нет названия"
    chat_id = self.vk.messages.createChat(title=title)
    link = self.vk.messages.getInviteLink(
        peer_id=MIN_CHAT_PEER_ID + chat_id)

    if link.get("link"):
        self.send_message(link["link"], str(peer_id))
        return

    self.send_message("что-то пошло не так...", str(peer_id))
