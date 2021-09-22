from vk_api import vk_api

from constants import MIN_CHAT_PEER_ID, CHIEF_ADMIN
from my_vk_api import get_user_id_via_url

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def set_admin(self: 'Bot', _, message: str, peer_id: int):
    def set_admin_function() -> str:
        """
        set admin's access for user
        :return: answer to message
        """
        user_url: int = get_user_id_via_url(new_admin_id, self.vk)
        if not user_url:
            return "Такого пользователя не существует"

        if str(user_url) != CHIEF_ADMIN:
            return self.redis.set_admin(str(user_url), access_level)
        else:
            return "Невозможно поменять уровень администрирования"

    if peer_id > MIN_CHAT_PEER_ID:
        return

    if self.redis.get_admin(str(peer_id)) != 5:
        return
    if len(message.split()) != 2:
        return self.send_message("Неправильный формат команды", str(peer_id))

    new_admin_id, access_level = message.split()

    if not access_level.isdigit() or not (1 <= int(access_level) <= 5):
        return self.send_message("Недопустимый уровень пользователя",
                                 str(peer_id))

    access_level = int(access_level)
    answer = set_admin_function()
    self.send_message(answer, str(peer_id))
