from constants import MIN_CHAT_PEER_ID
from utils import send_message, get_user_name, get_user_id_via_url


def is_admin(self, _, message, peer_id):
    if not peer_id > MIN_CHAT_PEER_ID:
        if self.redis.get_admin(str(peer_id)):
            if len(message.split()) == 2:
                admin_url = message.split()[-1]
                admin_id = get_user_id_via_url(admin_url, self.vk)
                if admin_id:
                    admin = self.redis.get_admin(admin_id)
                    if admin:
                        name = get_user_name(int(admin_id), self.vk)
                        send_message(f"@id{admin_id} ({name}) - Администратор уровня "
                                     f"{admin}",
                                     self.vk, peer_id=peer_id)
                    else:
                        send_message(f"@id{admin_id} - не администратор", self.vk,
                                     peer_id=peer_id)
                else:
                    send_message("Неправильный id", self.vk, peer_id=peer_id)
            else:
                send_message("Неправильный формат команды", self.vk, peer_id=peer_id)
        else:
            send_message("У вас нет прав для этой команды", self.vk, peer_id=peer_id)
