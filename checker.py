import logging
import threading

from constants import *
from commands.user_commands import       \
    create_yaderniy_xyesos_2009_command, \
    create_arabic_funny_command,         \
    create_shakal_command,               \
    create_grain_command,                \
    get_syns,                            \
    help_command,                        \
    toggle_access_chances,               \
    get_chances_distributor,             \
    set_chances_distributor,             \
    settings_command,                    \
    create_arabic_funny_gif_command
from commands.admin_commands import *
from utils import send_answer

logger = logging.getLogger("main_logger")
logging.basicConfig(filename="vk_bot.log", filemode="a",
                    format=f"%(levelname)s\t\t%(asctime)s\t\t%(message)s",
                    level=logging.INFO)


def check_command(all_data_message: dict, vk: vk_api.vk_api.VkApiMethod, user_id: int,
                  upload: vk_api.upload.VkUpload, sqlite) -> None:
    """
    main command checker
    :param all_data_message: all data from user's message
    :param vk: vk_api for reply message
    :param user_id: id of user who send a message
    :param upload: object for upload files on vk server

    """
    message: str = all_data_message["text"]
    if not message:
        return
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
    elif message.lower().startswith("/cag"):
        send_message("жди долго буду обрабатывать", vk, user_id)
        thread = threading.Thread(target=create_arabic_funny_gif_command,
                                  args=(user_id, vk, all_data_message, upload))
        thread.start()
    elif message.lower().startswith("/ca"):
        create_arabic_funny_command(user_id, vk, message, all_data_message, upload)
    elif message.lower().startswith("/tac"):
        toggle_access_chances(all_data_message, vk, user_id, sqlite)
    elif message.lower().startswith(tuple(GET_COMMANDS.keys())):
        get_chances_distributor(user_id, message, vk, sqlite)
    elif message.lower().startswith(tuple(SET_COMMANDS.keys())):
        set_chances_distributor(user_id, message, all_data_message, vk, sqlite)
    elif message.lower().startswith("/s"):
        settings_command(user_id, vk, sqlite)
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
        send_answer(message, vk, user_id, sqlite)