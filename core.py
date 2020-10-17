from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import logging
import sys

from constants import TOKEN, SQL_FILE_NAME
from events_reactions import *

logging.basicConfig(filename="vk_bot.log", filemode="a",
                    format=f"%(levelname)s\t\t%(asctime)s\t\t%(message)s",
                    level=logging.INFO)

sqlite = Sqlite(SQL_FILE_NAME)


def main() -> None:
    """
    main cycle of program

    """
    vk_session: VkApi = vk_api.VkApi(
        token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    upload = vk_api.VkUpload(vk_session)
    vk = vk_session.get_api()
    while True:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                log = u"{} IN {}".format(event.obj.message["from_id"],
                                         event.chat_id or event.obj.message["from_id"])
                logging.info(log)
                new_message_reaction(event, vk, sqlite, upload)
            if event.type == VkBotEventType.MESSAGE_ALLOW:
                allow_messages_reaction(event, vk, sqlite)
            if event.type == VkBotEventType.MESSAGE_REPLY:
                log = u"ANSWER ON {}".format(event.obj["peer_id"])
                logging.info(log)


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            try:
                type_ex, obj_ex, info = sys.exc_info()
                file = info.tb_frame.f_code.co_filename
                line = info.tb_lineno
                logging.error(f"{type_ex} | msg: {obj_ex} | line: {file} | line: {line}")
            except Exception:
                pass
