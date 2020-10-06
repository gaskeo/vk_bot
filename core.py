import random
import os
from dotenv import load_dotenv
from io import BytesIO

import urllib.request

from sql_api import Sqlite
from yandex_api import get_synonyms, get_text_from_json_get_synonyms
from images_tool import create_shakal, create_grain

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from pyzbar.pyzbar import decode
from PIL import Image

dotenv_path = os.path.join(os.path.dirname(__file__), 'config.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

SQL_FILE_NAME = "db/data.db"

GROUP_ID: str = os.getenv("vk_group_id")
TOKEN: str = os.getenv("vk_group_token")
CHIEF_ADMIN: str = os.getenv("chief_admin")

HELP_TEXT = "Команды:\n" \
            "1. /gs [слово(а)] - подобрать синонимы к слову / словам\n&#4448;Пример: /gs ручка\n" \
            "2. /cyx [текст] - СдеЛатЬ ПосТирОнИЧныЙ тЕКст\n&#4448;" \
            "Пример: /cyx привет можно познакомиться \n" \
            "3. /cs [степень шакала (ширина и длина : степень)][фотография(и)] " \
            "- зашакалить фото\n&#4448;" \
            "Пример: /cs 50 [Фотография]\n" \
            "4. /cg [степень зернистости " \
            "(рандомное число от (исходного - степень) до " \
            "(исходного + степень))][фотография(и)] - " \
            "добавить зернистость на фото"

ADMIN_TEXT = "Команды:\n" \
             "1. /ga - посмотреть список всех админов (Доступно только для 5 уровня)\n" \
             "2. /sa [ссылка/id] [уровень администрирования] " \
             "- установить права админа для пользователя (Доступно только для 5 уровня)" \

sqlite = Sqlite(SQL_FILE_NAME)


def check_command(all_data_message: dict, vk: vk_api.vk_api.VkApiMethod, user_id: int,
                  upload: vk_api.upload.VkUpload):
    """
    main command checker
    :param all_data_message: all data from user's message
    :param vk: vk_api for reply message
    :param user_id: id of user who send a message
    :param upload: object for upload files on vk server

    """
    message: str = all_data_message["text"]
    if message.lower().startswith("/gs"):
        get_synonyms_command(user_id, vk, message)
    elif message.lower().startswith("/sa"):
        set_admin_command(user_id, vk, message)
    elif message.lower().startswith("/cyx"):
        create_yaderniy_xyesos_command(user_id, vk, message)
    elif message.lower().startswith("/cs"):
        create_shakal_command(user_id, vk, message, all_data_message, upload)
    elif message.lower().startswith("/cg"):
        create_grain_command(user_id, vk, message, all_data_message, upload)
    elif message.lower() == "/ga":
        get_all_admins_command(user_id, vk)
    elif message.lower().startswith("/help"):
        help_command(user_id, vk)
    elif message.lower().startswith("/adm"):
        admin_help_command(user_id, vk)
    elif message.lower().startswith("/ia"):
        is_admin_command(user_id, vk, message)
    elif message.lower().startswith("/dqr"):
        decode_qr_code_command(user_id, vk, all_data_message)
    else:
        send_message("Не понял... Список команд: /help", vk, user_id)


def decode_qr_code_command(user_id: int, vk: vk_api.vk_api.VkApiMethod, all_data_message: dict):
    print(all_data_message)
    if all_data_message["attachments"]:
        for qr_code in all_data_message["attachments"]:
            if qr_code["type"] == "photo":
                url = qr_code["photo"]["sizes"][-1]["url"]
                print(qr_code["photo"]["sizes"][-1])
                size = (qr_code["photo"]["sizes"][-1]["width"],
                        qr_code["photo"]["sizes"][-1]["height"])
                qr = urllib.request.urlopen(url).read()
                bytes_qr = BytesIO(qr)
                a = Image.open(bytes_qr)
                b = Image.frombytes(mode="L", size=size, data=a.tobytes())
                data = decode((a.load(), *size))
                print(data)


def get_synonyms_command(user_id: int, vk: vk_api.vk_api.VkApiMethod, message: str):
    """
    get synonyms for words in message
    :param user_id: id of user who need synonyms
    :param vk: vk_api for reply message
    :param message: user's message

    """
    if len(message.split()) >= 2:
        syns = get_syns_refactored(message.split()[1:])
        send_message(syns, vk, user_id)
    else:
        send_message("Ошибка: нет слова", vk, user_id)


def create_yaderniy_xyesos_command(user_id: int, vk: vk_api.vk_api.VkApiMethod, message: str):
    """
    create yAdErNIy xYeSoS from message
    :param user_id: id of user who need yAdErNIy xYeSoS
    :param vk: vk_api for reply message
    :param message: user's message

    """
    if len(message.split()) > 1:
        answer = create_yaderniy_xyesos_2009(" ".join(message.split()[1:]))
        send_message(answer, vk, user_id)


def create_grain_command(user_id: int, vk: vk_api.vk_api.VkApiMethod, message: str,
                         all_data_message: dict, upload: vk_api.upload.VkUpload):
    if all_data_message["attachments"]:
        factor = 50
        if len(message.split()) > 1:
            if message.split()[-1].isdigit():
                factor = int(message.split()[-1])
            else:
                send_message("Степеь должна быть целым числом")
                return
        for image in all_data_message["attachments"]:
            if image["type"] == "photo":
                url = image["photo"]["sizes"][-1]["url"]
                img = urllib.request.urlopen(url).read()
                bytes_img = BytesIO(img)
                name_final_file = create_grain(bytes_img, factor)
                photo = upload.photo_messages(photos=[name_final_file],
                                              peer_id=all_data_message["peer_id"])
                vk_photo_id = \
                    f"photo{photo[0]['owner_id']}_{photo[0]['id']}_{photo[0]['access_key']}"
                send_message("", vk, user_id, vk_photo_id)
                os.remove(name_final_file)
    else:
        send_message("Прикрепи фото", vk, user_id)


def create_shakal_command(user_id: int, vk: vk_api.vk_api.VkApiMethod, message: str,
                          all_data_message: dict, upload: vk_api.upload.VkUpload):
    """
    create shakal photo from message
    :param user_id: id of user who need shakal
    :param vk: vk_api for reply message
    :param message: user's message
    :param all_data_message: all data from user's message
    :param upload: object for upload files on vk server

    """
    if all_data_message["attachments"]:
        factor = 50
        if len(message.split()) > 1:
            if message.split()[-1].isdigit():
                factor = int(message.split()[-1])
        for image in all_data_message["attachments"]:
            if image["type"] == "photo":
                url = image["photo"]["sizes"][-1]["url"]
                img = urllib.request.urlopen(url).read()
                bytes_img = BytesIO(img)
                photo_bytes = create_shakal(bytes_img, factor)
                photo = upload.photo_messages(photos=[photo_bytes],
                                              peer_id=all_data_message["peer_id"])
                vk_photo_id = \
                    f"photo{photo[0]['owner_id']}_{photo[0]['id']}_{photo[0]['access_key']}"
                send_message("", vk, user_id, vk_photo_id)
                os.remove(photo_bytes)
    else:
        send_message("Прикрепи фото", vk, user_id)


def get_all_admins_command(user_id: int, vk: vk_api.vk_api.VkApiMethod):
    """
    command for get all admins from db
    :param user_id: id of user who need admins
    :param vk: vk_api for reply message

    """
    send_message(get_all_admins(user_id), vk, user_id)


def set_admin_command(user_id: int, vk: vk_api.vk_api.VkApiMethod, message: str):
    """
    command for adding or editing admins
    :param user_id: id of user who need adding or editing admins
    :param vk: vk_api for reply message
    :param message: user's message

    """
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


def is_admin_command(user_id: int, vk: vk_api.vk_api.VkApiMethod, message: str):
    """
    checking if user is admin
    :param user_id: id of user who need check another user
    :param vk: vk_api for reply message
    :param message: user's message

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


def help_command(user_id: int, vk: vk_api.vk_api.VkApiMethod):
    """
    command for help
    :param user_id: id of user who need help
    :param vk: vk_api for reply messsage

    """
    send_message(HELP_TEXT, vk, user_id)


def admin_help_command(user_id: int, vk: vk_api.vk_api.VkApiMethod):
    """
    command for send message with admin commands
    :param user_id: id of user who need admin commands
    :param vk: vk_api for reply message

    """
    level: int = sqlite.get_admin(user_id)
    if level > 0:
        send_message(ADMIN_TEXT, vk, user_id)
    else:
        send_message("У вас нет доступа к данной команде", vk, user_id)


def get_syns_refactored(words: list) -> str:
    """
    search synonyms on yandex api and refactor text to message
    :param words: list of words need synonyms
    :return: refactored synonyms for message
    """
    syns = get_text_from_json_get_synonyms(get_synonyms(words))
    if syns:
        syns_refactored = f"Синонимы к слову \"{' '.join(words)}\":\n\n"
        for syn in syns:
            syns_refactored += tuple(syn.keys())[0] + "\n"
            if tuple(syn.values())[0]:
                syns_refactored += f"Подобные слову \"{tuple(syn.keys())[0]}\":\n"
                for unsyn in tuple(syn.values())[0]:
                    syns_refactored += "&#4448;• " + unsyn + "\n"
        return syns_refactored
    else:
        return "Ничего не найдено"


def set_admin(user_id: str, access_level: int, vk: vk_api.vk_api.VkApiMethod) -> str:
    """
    set admin's access for user
    :param user_id: user who need set admin's access for another user
    :param access_level: level of admin's permissions
    :param vk: vk_api for find user's id via url
    :return: answer to message

    """
    user_id: int = get_user_id_via_url(user_id, vk)
    if user_id:
        if str(user_id) != CHIEF_ADMIN:
            answer = sqlite.set_admin(user_id, access_level)
            return answer
        else:
            return "Невозможно поменять уровень администрирования"
    return "Такого пользователя не существует"


def get_user_id_via_url(user_url: str, vk: vk_api.vk_api.VkApiMethod) -> int:
    """
    finding user id via url
    :param user_url: user's url who need id
    :param vk: vk_api for find user's id via url
    :return: user's id or 0 if user not found

    """
    def get_user_screen_name_of_url(url: str) -> str:
        """
        searching screen name in url
        :param url: user's account url
        :return: user's screen name

        """
        if url.startswith("[") and url.endswith("]") and "|" in url:
            url = url[1:url.find("|")]
            return url
        url = url.replace("@", "")
        if url.endswith("/"):
            url = url[:-1]
        while "/" in url:
            url = url[url.rfind("/") + 1:]
        return url

    info = vk.utils.resolveScreenName(screen_name=get_user_screen_name_of_url(user_url))
    if info:
        user_id: int = info["object_id"]
        return user_id
    return 0


def get_all_admins(user_id: int) -> str:
    """
    get all admins and refactor answer
    :param user_id: id of user who need list of admins
    :return: refactored list of admins
    """
    if str(user_id) == CHIEF_ADMIN or sqlite.get_admin(user_id) == 5:
        admins = sqlite.get_all_admins()
        if admins:
            admins_str = f"Всего админов: {len(admins)}\n"
            for (id_temp, access_level_temp) in admins:
                admins_str += f"{'@id'}{id_temp} - {access_level_temp}\n"
            return admins_str
        return "Список пуст"
    return "У вас нет доступа к этой команде"


def create_yaderniy_xyesos_2009(text: str) -> str:
    """
    create yAdErNIy xYeSoS from message
    :param text: text need refactored
    :return: refactored text

    """
    return "".join([symb.lower() if random.choice((0, 1)) else symb.upper() for symb in text])


def send_message(message: str, vk: vk_api.vk_api.VkApiMethod, user_id: int, attachments:
                 str or list = None):
    """
    handler for send message
    :param message: text of message
    :param vk: vk_api for send message
    :param user_id: id of user who receive message 
    :param attachments: attachments in message
    
    """
    vk.messages.send(user_id=user_id,
                     message=message,
                     random_id=random.randint(0, 2 ** 64),
                     attachment=attachments)


def main():
    vk_session = vk_api.VkApi(
        token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    upload = vk_api.VkUpload(vk_session)
    vk = vk_session.get_api()
    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    user_id = event.obj.message['from_id']
                    old = sqlite.check_user_in_db(user_id)
                    if not old:
                        sqlite.add_user(user_id, "")
                        send_message("Ты теперь смешарик! Напиши /help, "
                                     "чтобы узнать список команд", vk, user_id)
                    check_command(event.obj.message, vk, user_id, upload)

                if event.type == VkBotEventType.MESSAGE_ALLOW:
                    user_id = event.obj["user_id"]
                    if sqlite.check_user_in_db(user_id):
                        send_message("Ты снова с нами! Напиши /help, вдруг новые команды появились, "
                                     "а ты не в курсе", vk, user_id)
                    else:
                        sqlite.add_user(user_id, "")
                        send_message("Спасибо, что разрешил сообщения! Напиши /help, "
                                     "чтобы ознакомиться с функциями бота", vk, user_id)
        except Exception as e:
            send_message(str(e), vk, int(CHIEF_ADMIN))


if __name__ == '__main__':
    main()
