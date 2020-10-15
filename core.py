from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import logging

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
        try:
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
        except ValueError as e:
            logging.error(repr(e))
            send_message(f"{repr(e)}", vk, int(CHIEF_ADMIN))


if __name__ == '__main__':
    main()
