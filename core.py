from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from constants import *
from commands.user_commands import       \
    create_yaderniy_xyesos_2009_command, \
    create_arabic_funny_command,         \
    create_shakal_command,               \
    create_grain_command,                \
    get_syns,                            \
    help_command
from commands.admin_commands import *


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
    # user commands
    if message.lower().startswith("/gs"):
        get_syns(user_id, vk, message)
    elif message.lower().startswith("/cyx"):
        create_yaderniy_xyesos_2009_command(user_id, vk, message)
    elif message.lower().startswith("/cs"):
        create_shakal_command(user_id, vk, message, all_data_message, upload)
    elif message.lower().startswith("/cg"):
        create_grain_command(user_id, vk, message, all_data_message, upload)
    elif message.lower().startswith("/ca"):
        create_arabic_funny_command(user_id, vk, message, all_data_message, upload)
    elif message.lower().startswith("/help"):
        help_command(user_id, vk)
    # admin commands
    elif message.lower().startswith("/sa"):
        set_admin_command(user_id, vk, message, sqlite)
    elif message.lower() == "/ga":
        get_all_admins_command(user_id, vk, sqlite)
    elif message.lower().startswith("/adm"):
        admin_help_command(user_id, vk, sqlite)
    elif message.lower().startswith("/ia"):
        is_admin_command(user_id, vk, message, sqlite)
    elif message.lower().startswith("/bb"):
        bb_command(user_id, vk, sqlite)
    else:
        if all_data_message:
            print(all_data_message)
        send_message("Не понял... Список команд: /help", vk, user_id)


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
