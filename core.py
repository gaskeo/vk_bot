from vk_api import VkApi, VkUpload
from vk_api.bot_longpoll import VkBotEventType

from longpoll import MyVkLongPoll
import threading
import time

import logging
from checker import Bot
from utils import exception_checker, StopEvent

from sql.sqlstart import SqliteStart
from constants import TOKEN, GROUP_ID, CHIEF_ADMIN

logging.basicConfig(filename="vk_bot.log", filemode="a",
                    format=f"%(levelname)s\t\t%(asctime)s\t\t%(message)s",
                    level=logging.INFO)


def main() -> None:
    """
    main cycle of program

    """
    FOR_EVERYONE = True
    vk_session: VkApi = VkApi(
        token=TOKEN)
    sql = SqliteStart()
    sql_thread = threading.Thread(target=sql.create)
    sql_thread.setName("sql")
    sql_thread.start()
    while not sql.get_sqlkook():
        time.sleep(0.1)

    longpoll = MyVkLongPoll(vk_session, GROUP_ID)
    upload = VkUpload(vk_session)
    vk = vk_session.get_api()
    bot = Bot(vk, sql.get_sql(), upload, sqlitehook=sql.get_sqlkook())
    while True:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and \
                    str(event.obj.message["peer_id"]) in ("2000000002", "2000000003", "2000000005", CHIEF_ADMIN)\
                    or FOR_EVERYONE:
                bot.add_event_in_queue(event)
            if threading.active_count() == 2:
                sql.get_sqlkook().add_in_q(StopEvent)
                exit()


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            exception_checker()