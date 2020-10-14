from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import logging

from constants import *
from commands.user_commands import       \
    create_yaderniy_xyesos_2009_command, \
    create_arabic_funny_command,         \
    create_shakal_command,               \
    create_grain_command,                \
    get_syns,                            \
    help_command,                        \
    change_chance_command,               \
    get_chance_command,                  \
    show_settings_command
from commands.admin_commands import *
from utils import get_main_pos, answer_nu_poluchaetsya_or_not, \
    answer_or_not, get_random_answer, generate_huy_word, get_admins_in_chat

logger = logging.getLogger("main_logger")
logging.basicConfig(filename="vk_bot.log", filemode="a",
                    format=f"%(levelname)s\t\t%(asctime)s\t\t%(message)s",
                    level=logging.INFO)

sqlite = Sqlite(SQL_FILE_NAME)
MY_NAMES = ("[club198181337|Ну получается ладно]", "[club198181337|@club198181337]")
HELP_KEYBOARD = {"buttons": [
                    [
                        {
                            "action": {
                                "type": "text",
                                "label": "/help",
                                "payload": ""
                            },
                            "color": "positive"
                        }
                    ]
                ]
                }

GET_COMMANDS = {"/gac": ANSWER_CHANCE,
                "/glc": LADNO_CHANCE,
                "/ghc": HUY_CHANCE,
                "/gnc": NU_POLUCHAETSYA_CHANCE}
SET_COMMANDS = {"/ac": ANSWER_CHANCE,
                "/lc": LADNO_CHANCE,
                "/hc": HUY_CHANCE,
                "/nc": NU_POLUCHAETSYA_CHANCE}


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
    log = u"IN {}".format(abs(user_id))
    logging.info(log)
    if message.startswith(MY_NAMES):
        for name in MY_NAMES:
            message = message.replace(name, '')
    message = message.lstrip().rstrip()

    # user commands
    if message.lower().startswith("ладно") and len(message) < 10:
        send_message("Ну получается ладно.", vk, user_id)
        return
    if message.lower().startswith("/gs"):
        get_syns(user_id, vk, message)
    elif message.lower().startswith("/cp"):
        create_yaderniy_xyesos_2009_command(user_id, vk, message)
    elif message.lower().startswith("/cs"):
        create_shakal_command(user_id, vk, message, all_data_message, upload)
    elif message.lower().startswith("/cg"):
        create_grain_command(user_id, vk, message, all_data_message, upload)
    elif message.lower().startswith("/ca"):
        create_arabic_funny_command(user_id, vk, message, all_data_message, upload)
    elif message.lower().startswith("/tac"):
        admins = get_admins_in_chat(all_data_message["peer_id"], vk)
        if all_data_message["from_id"] in admins:
            who = sqlite.toggle_access_chances(user_id)
            send_message(WHO_CAN_TOGGLE_CHANCES.get(who), vk, user_id)
    elif message.lower().startswith(tuple(GET_COMMANDS.keys())):
        if user_id < 0:
            get_chance_command(user_id,
                               GET_COMMANDS.get(message.split()[0], ANSWER_CHANCE), vk, sqlite)
        else:
            send_message("Команда только для бесед", vk, user_id)
    elif message.lower().startswith(tuple(SET_COMMANDS.keys())):
        if user_id < 0:
            who_can_change = sqlite.get_who_can_change_chances(user_id)
            if who_can_change:
                admins = get_admins_in_chat(all_data_message["peer_id"], vk)
                if all_data_message["from_id"] in admins:
                    change_chance_command(user_id,
                                          SET_COMMANDS.get(message.split()[0], "gac"), vk, message,
                                          sqlite)
            else:
                change_chance_command(user_id,
                                      SET_COMMANDS.get(message.split()[0], "gac"), vk, message,
                                      sqlite)

        else:
            send_message("Команда только для бесед", vk, user_id)
    elif message.lower().startswith("/s"):
        if user_id < 0:
            show_settings_command(user_id, vk, sqlite)
        else:
            send_message("Команда только для бесед", vk, user_id)
    elif message.lower().startswith("/help"):
        help_command(user_id, vk, message)
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
    # processing phrases
    else:
        if user_id < 0:
            answer = answer_or_not(user_id, sqlite)
            if answer:
                what = get_random_answer(user_id, message, sqlite)
                if what == "ladno_chance":
                    send_message("Ладно.", vk, user_id)
                elif what == "huy_chance":
                    send_message(generate_huy_word(message), vk, user_id)
                elif what == "nu_poluchaetsya_chance":
                    data = get_main_pos(message)
                    answer = answer_nu_poluchaetsya_or_not(data)
                    if answer:
                        send_message(answer, vk, user_id)
            return
        else:
            what = get_random_answer(0, message, weights=False)
            if what == "ladno_chance":
                send_message("Ладно.", vk, user_id)
            elif what == "huy_chance":
                send_message(generate_huy_word(message), vk, user_id)
            elif what == "nu_poluchaetsya_chance":
                data = get_main_pos(message)
                answer = answer_nu_poluchaetsya_or_not(data)
                if answer:
                    send_message(answer, vk, user_id)


def main():
    vk_session: VkApi = vk_api.VkApi(
        token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    upload = vk_api.VkUpload(vk_session)
    vk = vk_session.get_api()
    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    if event.obj.message["from_id"] == event.obj.message["peer_id"]:
                        user_id = event.obj.message['from_id']
                        if user_id == int(CHIEF_ADMIN):
                            ...
                        old = sqlite.check_user_in_db(user_id)
                        if not old:
                            sqlite.add_user(user_id, "")
                            send_message("Ты теперь смешарик! Напиши /help, "
                                         "чтобы узнать список команд", vk, user_id,
                                         keyboard=HELP_KEYBOARD)
                        check_command(event.obj.message, vk, user_id, upload)
                    else:
                        action = event.obj["message"].get("action", 0)
                        if action:
                            if action["type"] == "chat_invite_user" and \
                                    action["member_id"] == -int(GROUP_ID):
                                sqlite.add_chat(event.chat_id)
                                send_message("Дайте права админа пожалуйста "
                                             "а то я вас не слышу я глухой",
                                             vk, -abs(event.chat_id))
                        else:
                            old = sqlite.check_chat_in_db(event.chat_id)
                            if not old:
                                sqlite.add_chat(event.chat_id)
                            check_command(event.obj.message, vk, -abs(event.chat_id), upload)

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
            logging.error(repr(e))
            send_message(f"{repr(e)}\n{e}", vk, int(CHIEF_ADMIN))


if __name__ == '__main__':
    main()
