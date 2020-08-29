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

dotenv_path = os.path.join(os.path.dirname(__file__), 'config.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

SQL_FILE_NAME = "db/data.db"

GROUP_ID = os.getenv("vk_group_id")
TOKEN = os.getenv("vk_group_token")

CHIEF_ADMIN = os.getenv("chief_admin")

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
             "/ga - посмотреть список всех админов (Доступно только для 5 уровня)\n" \
             "/sa [ссылка/id] [уровень администрирования] " \
             "- установить права админа для пользователя (Доступно только для 5 уровня)" \

sqlite = Sqlite(SQL_FILE_NAME)


def check_command(all_data_message, vk: vk_api.vk_api.VkApiMethod, user_id, upload):
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
    else:
        send_message("Ты шо, я не понимаю тебя", vk, user_id)


def get_synonyms_command(user_id, vk, message):
    if len(message.split()) >= 2:
        syns = get_syns_refactored(message.split()[1:])
        send_message(syns, vk, user_id)
    else:
        send_message("Ошибка: нет слова", vk, user_id)


def create_yaderniy_xyesos_command(user_id, vk, message):
    if len(message.split()) > 1:
        answer = create_yaderniy_xyesos_2009(" ".join(message.split()[1:]))
        send_message(answer, vk, user_id)


def create_grain_command(user_id, vk, message, all_data_message, upload):
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
                photo_bytes = create_grain(bytes_img, factor)
                photo = upload.photo_messages(photos=[photo_bytes],
                                              peer_id=all_data_message["peer_id"])
                vk_photo_id = \
                    f"photo{photo[0]['owner_id']}_{photo[0]['id']}_{photo[0]['access_key']}"
                send_message("", vk, user_id, vk_photo_id)
                os.remove(photo_bytes)
    else:
        send_message("Прикрепи фото", vk, user_id)


def create_shakal_command(user_id, vk, message, all_data_message, upload):
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


def get_all_admins_command(user_id, vk):
    send_message(get_all_admins(user_id), vk, user_id)


def set_admin_command(user_id, vk, message):
    if sqlite.get_admin(user_id) == 5:
        if len(message.split()) == 3:
            new_admin_id, access_level = message.split()[1:]
            if not access_level.isdigit() or not (1 <= int(access_level) <= 5):
                send_message("Недопустимый уровень пользователя", vk, user_id)
                return
            answer = set_admin(new_admin_id, access_level, vk)
            send_message(answer, vk, user_id)
        else:
            send_message("Неправильный формат команды", vk, user_id)
    else:
        send_message("У вас нет прав для этой команды. "
                     "Минимальный уровень администрирования для данной команды: 5", vk, user_id)


def help_command(user_id, vk):
    send_message(HELP_TEXT, vk, user_id)


def admin_help_command(user_id, vk):
    level: int = sqlite.get_admin(user_id)
    if level > 0:
        send_message(ADMIN_TEXT, vk, user_id)
    else:
        send_message("У вас нет доступа к данной команде", vk, user_id)


def get_syns_refactored(word):
    syns = get_text_from_json_get_synonyms(get_synonyms(word))
    if syns:
        syns_refactored = f"Синонимы к слову \"{' '.join(word)}\":\n\n"
        for syn in syns:
            syns_refactored += tuple(syn.keys())[0] + "\n"
            if tuple(syn.values())[0]:
                syns_refactored += f"Подобные слову \"{tuple(syn.keys())[0]}\":\n"
                for unsyn in tuple(syn.values())[0]:
                    syns_refactored += "&#4448;• " + unsyn + "\n"
        return syns_refactored
    else:
        return "Ничего не найдено"


def set_admin(user_id, access_level, vk):
    user_id = get_user_id_via_url(user_id, vk)
    if user_id:
        if str(user_id) != CHIEF_ADMIN:
            answer = sqlite.set_admin(user_id, access_level)
            return answer
        else:
            return "Невозможно поменять уровень администрирования"
    return "Такого пользователя не существует"


def get_user_id_via_url(user_url, vk):
    def get_user_screen_name_of_url(url: str):
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
        return info["object_id"]
    return None


def get_all_admins(user_id):
    if str(user_id) == str(CHIEF_ADMIN) or sqlite.get_admin(str(user_id)) == 5:
        admins = sqlite.get_all_admins()
        if admins:
            admins_str = f"Всего админов: {len(admins)}\n"
            for (id_temp, access_level_temp) in admins:
                admins_str += f"{'@id'}{id_temp} - {access_level_temp}\n"
            return admins_str
        return "Список пуст"
    return "У вас нет доступа к этой команде"


def create_yaderniy_xyesos_2009(text: str):
    return "".join([symb.lower() if random.choice((0, 1)) else symb.upper() for symb in text])


def send_message(message, vk, user_id, attachments=None):
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
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message['from_id']
            # messages = [message for message in vk.messages.getHistory
            #    (count=5, user_id=user_id)["items"] if message["from_id"] == user_id][1]
            old = sqlite.check_user_in_db(user_id)
            if not old:
                sqlite.add_user(user_id, "")
                send_message("Ты теперь смешарик", vk, user_id)
            check_command(event.obj.message, vk, user_id, upload)


if __name__ == '__main__':
    main()
