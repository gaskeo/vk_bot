import vk_api

from sql.sql_api import Sqlite
from constants import ADMIN_TEXT, CHIEF_ADMIN
from utils import send_message, get_user_id_via_url


def admin_help_command(user_id: int, vk: vk_api.vk_api.VkApiMethod, sqlite: Sqlite):
    """
    command for send message with admin commands
    :param user_id: id of user who need admin commands
    :param vk: vk_api for reply message
    :param sqlite: class for search admin in db

    """
    level: int = sqlite.get_admin(user_id)
    if level > 0:
        send_message(ADMIN_TEXT, vk, user_id)
    else:
        send_message("У вас нет доступа к данной команде", vk, user_id)


def get_all_admins_command(user_id: int, vk: vk_api.vk_api.VkApiMethod, sqlite: Sqlite) -> str:
    """
    get all admins and refactor answer
    :param user_id: id of user who need list of admins
    :param vk: vk_api for reply message
    :param sqlite: class for search admin in db
    :return: refactored list of admins
    """
    if str(user_id) == CHIEF_ADMIN or sqlite.get_admin(user_id) == 5:
        admins = sqlite.get_all_admins()
        if admins:
            admins_str = f"Всего админов: {len(admins)}\n"
            for (id_temp, access_level_temp) in admins:
                admins_str += f"{'@id'}{id_temp} - {access_level_temp}\n"
            send_message(admins_str, vk, user_id)
        return "Список пуст"
    return "У вас нет доступа к этой команде"


def is_admin_command(user_id: int, vk: vk_api.vk_api.VkApiMethod, message: str, sqlite: Sqlite):
    """
    checking if user is admin
    :param user_id: id of user who need check another user
    :param vk: vk_api for reply message
    :param message: user's message
    :param sqlite: class for search admin in db

    """
    if sqlite.get_admin(user_id):
        if len(message.split()) == 2:
            admin_url = message.split()[-1]
            admin_id = get_user_id_via_url(admin_url, vk)
            if admin_id:
                is_admin = sqlite.get_admin(admin_id)
                if is_admin:
                    send_message(f"@id{admin_id} - Администратор уровня {is_admin}", vk, user_id)
                else:
                    send_message(f"@id{admin_id} - не администратор", vk, user_id)
            else:
                send_message("Неправильный id", vk, user_id)
        else:
            send_message("Неправильный формат команды", vk, user_id)
    else:
        send_message("У вас нет прав для этой команды")


def set_admin_command(user_id: int, vk: vk_api.vk_api.VkApiMethod, message: str, sqlite: Sqlite):
    """
    command for adding or editing admins
    :param user_id: id of user who need adding or editing admins
    :param vk: vk_api for reply message
    :param message: user's message
    :param sqlite: class for search admin in db

    """

    def set_admin(
            user_url: str,
            admin_access_level: int,
            vk_api_method: vk_api.vk_api.VkApiMethod
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
                return sqlite.set_admin(user_url, admin_access_level)
            else:
                return "Невозможно поменять уровень администрирования"
        return "Такого пользователя не существует"

    if sqlite.get_admin(user_id) == 5:
        if len(message.split()) == 3:
            new_admin_id, access_level = message.split()[1:]
            if not access_level.isdigit() or not (1 <= int(access_level) <= 5):
                send_message("Недопустимый уровень пользователя", vk, user_id)
                return
            access_level = int(access_level)
            answer = set_admin(new_admin_id, access_level, vk)
            send_message(answer, vk, user_id)
        else:
            send_message("Неправильный формат команды", vk, user_id)
    else:
        send_message("У вас нет прав для этой команды. "
                     "Минимальный уровень администрирования для данной команды: 5", vk, user_id)
        
        
def bb_command(user_id: int, vk: vk_api.vk_api.VkApiMethod, sqlite: Sqlite):
    """
    command for stop program
    :param user_id: id of user who need stop program
    :param vk: vk_api for reply message
    :param sqlite: class for search admin in db
    """
    if sqlite.get_admin(user_id) >= 5:
        send_message("Завершаю работу...", vk, user_id)
        sqlite.exit_db()
        send_message("Закрыл базу", vk, user_id)

        if user_id != int(CHIEF_ADMIN):
            send_message(f"Завершаю работу по команде @id{user_id}", vk, int(CHIEF_ADMIN))
        send_message("Завершаю работу всей программы", vk, user_id)
        exit(0)
