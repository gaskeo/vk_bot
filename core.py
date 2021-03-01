import time

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from longpoll import MyVkLongPoll

import logging
from checker import Bot
from utils import exception_checker
import threading
from constants import TOKEN, SQL_FILE_NAME
from events_reactions import *
from sqlitehook import SqliteHook

logging.basicConfig(filename="vk_bot.log", filemode="a",
                    format=f"%(levelname)s\t\t%(asctime)s\t\t%(message)s",
                    level=logging.INFO)


class SqliteStart:
    def __init__(self):
        self.sqlite = None
        self.sqlhook = None

    def get_sql(self):
        return self.sqlite

    def create(self):
        self.sqlite = Sqlite(SQL_FILE_NAME)
        self.sqlhook = SqliteHook(self.sqlite)
        self.check_event_type()

    def get_sqlkook(self):
        return self.sqlhook

    def check_event_type(self):
        self.sqlhook.check_event_type()


def main() -> None:
    """
    main cycle of program

    """
    vk_session: VkApi = vk_api.VkApi(
        token=TOKEN)
    sql = SqliteStart()
    sql_thread = threading.Thread(target=sql.create)
    sql_thread.start()
    while not sql.get_sqlkook():
        pass

    longpoll = MyVkLongPoll(vk_session, GROUP_ID)
    upload = vk_api.VkUpload(vk_session)
    vk = vk_session.get_api()
    bot = Bot(vk, sql.get_sql(), upload, sqlitehook=sql.get_sqlkook())
    while True:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and str(event.obj.message["peer_id"]) in ("2000000002", CHIEF_ADMIN) or 1:
                bot.add_event_in_queue(event)
            if threading.active_count() == 1:
                exit()


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            exception_checker()