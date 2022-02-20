from constants import MIN_CHAT_PEER_ID, CHIEF_ADMIN
from my_vk_api import get_user_name

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Bot


def get_admin(self: 'Bot', _, __, peer_id: int):
    if peer_id > MIN_CHAT_PEER_ID:
        return
    if not (peer_id == int(CHIEF_ADMIN) or
            self.redis.get_admin(peer_id) == 5):
        return

    admins = self.redis.get_all_admins()
    if not admins:
        return self.send_message("Список пуст", str(peer_id))

    admin_out_list = [f"Всего админов: {len(admins)}"]
    for id_temp, access_level_temp in admins.items():
        name = get_user_name(int(id_temp), self.vk)
        admin_out_list.append(
            f"{'@id'}{id_temp} ({name}) - {access_level_temp}")

    self.send_message("\n".join(admin_out_list), str(peer_id))
