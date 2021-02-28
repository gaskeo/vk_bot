import vk_api
from vk_api.bot_longpoll import VkBotMessageEvent
import json

from sql.sql_api import Sqlite
from constants import CHIEF_ADMIN, KEYBOARDS, GROUP_ID
from utils import send_message


def new_message_reaction(event: VkBotMessageEvent, bot) -> None:
    """
    handler for new messages
    :param event: VkBotMessageEvent

    """
    bot.message_checker(event)


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
