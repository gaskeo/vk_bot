from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import logging
import sys
from transliterate import translit
import threading
from constants import TOKEN, SQL_FILE_NAME
from events_reactions import *
from checker import Bot
from sql.redis_api import Redis
from ai.main import WordNeuralNetwork
from utils import exception_checker

logging.basicConfig(filename="vk_bot.log", filemode="a",
                    format=f"%(levelname)s\t\t%(asctime)s\t\t%(message)s",
                    level=logging.INFO)

sqlite = Sqlite(SQL_FILE_NAME)

redis = Redis()
nn = WordNeuralNetwork(redis)
DEBUG = False


def main() -> None:
    """
    main cycle of program

    """
    vk_session: VkApi = vk_api.VkApi(
        token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    upload = vk_api.VkUpload(vk_session)
    vk = vk_session.get_api()
    bot = Bot(vk, redis, upload, nn)

    while True:
        for event in longpoll.listen():
            bot.add_event_in_queue(event)
            if threading.active_count() == 1:
                exit()


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            exception_checker()
