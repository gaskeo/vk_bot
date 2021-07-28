from vk_api import vk_api


from constants import MIN_CHAT_PEER_ID, CHIEF_ADMIN
from utils import send_message, get_user_id_via_url


def set_admin(self, _, message, peer_id):
    def set_admin_function(
            user_url: str,
            admin_access_level: int,
            vk_api_method: vk_api.VkApiMethod
    ) -> str:
        """
        set admin's access for user
        :param user_url: user who need set admin's access for another user
        :param admin_access_level: level of admin's permissions
        :param vk_api_method: vk_api for find user's id via url
        :return: answer to message
        """
        user_url: int = get_user_id_via_url(user_url, vk_api_method)
        if user_url:
            if str(user_url) != CHIEF_ADMIN:
                return self.redis.set_admin(str(user_url), admin_access_level)
            else:
                return "Невозможно поменять уровень администрирования"
        return "Такого пользователя не существует"

    if not peer_id > MIN_CHAT_PEER_ID:
        if self.redis.get_admin(str(peer_id)) == 5:
            if len(message.split()) == 3:
                new_admin_id, access_level = message.split()[1:]
                if not access_level.isdigit() or not (1 <= int(access_level) <= 5):
                    send_message("Недопустимый уровень пользователя", self.vk,
                                 peer_id=peer_id)
                    return
                access_level = int(access_level)
                answer = set_admin_function(new_admin_id, access_level, self.vk)
                send_message(answer, self.vk, peer_id=peer_id)
            else:
                send_message("Неправильный формат команды", self.vk, peer_id=peer_id)
        else:
            send_message("У вас нет прав для этой команды. "
                         "Минимальный уровень администрирования для данной команды: 5",
                         self.vk, peer_id=peer_id)
