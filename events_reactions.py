import vk_api
from vk_api.bot_longpoll import VkBotMessageEvent
import json

from sql.sql_api import Sqlite
from constants import CHIEF_ADMIN, KEYBOARDS, GROUP_ID
from utils import send_message
from checker import check_command


def new_message_reaction(event: VkBotMessageEvent,
                         vk: vk_api.vk_api.VkApiMethod,
                         sqlite: Sqlite, upload: vk_api.upload.VkUpload) -> None:
    """
    handler for new messages
    :param event: VkBotMessageEvent
    :param vk: vk_api for reply message and other
    :param sqlite: Sqlite object
    :param upload: upload object for upload photos and other files on vk

    """
    if event.obj.message["from_id"] == event.obj.message["peer_id"]:
        user_id = event.obj.message['from_id']
        if user_id == int(CHIEF_ADMIN):
            ...
        old = sqlite.check_user_in_db(user_id)
        if not old:
            sqlite.add_user(user_id, "")
            send_message("Напиши /help, "
                         "чтобы узнать список команд", vk, user_id,
                         keyboard=json.loads(KEYBOARDS)["help_keyboard"])
        check_command(event.obj.message, vk, user_id, upload, sqlite)
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
            check_command(event.obj.message, vk, -abs(event.chat_id), upload, sqlite)


def allow_messages_reaction(event: VkBotMessageEvent, vk: vk_api.vk_api.VkApiMethod,
                            sqlite: Sqlite) -> None:
    """
    handler for allow messages
    :param event: VkBotMessageEvent
    :param vk: vk_api for reply message and other
    :param sqlite: Sqlite object

    """
    user_id = event.obj["user_id"]
    if sqlite.check_user_in_db(user_id):
        send_message("/help - помощь", vk, user_id, keyboard=json.loads(KEYBOARDS)["help_keyboard"])
    else:
        sqlite.add_user(user_id, "")
        send_message("/help - помощь", vk, user_id,
                     keyboard=json.loads(KEYBOARDS)["help_keyboard"])
