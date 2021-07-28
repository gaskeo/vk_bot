from vk_api import VkApi, VkUpload
from vk_api.bot_longpoll import VkBotEventType

from longpoll import MyVkLongPoll
import threading

import logging
# from checker import Bot
from bot import Bot
from utils import exception_checker, StopEvent

from rds.redis_api import RedisApi
from constants import TOKEN, GROUP_ID, CHIEF_ADMIN, REDIS_PASSWORD, ACCEPTED_PEERS_ON_DEBUG

logging.basicConfig(filename="vk_bot.log", filemode="a",
                    format=f"%(levelname)s\t\t%(asctime)s\t\t%(message)s",
                    level=logging.INFO)


def main() -> None:
    """
    main cycle of program

    """
    for_everyone = False
    vk_session: VkApi = VkApi(
        token=TOKEN)
    long_poll = MyVkLongPoll(vk_session, GROUP_ID)
    upload = VkUpload(vk_session)
    vk = vk_session.get_api()
    rds = RedisApi(password=REDIS_PASSWORD)
    bot = Bot(vk, rds, upload)
    while True:
        for event in long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                peer_id = str(event.obj.message["peer_id"])
            elif event.type == VkBotEventType.MESSAGE_EVENT:
                peer_id = str(event.obj["peer_id"])
            else:
                continue
            if peer_id in ACCEPTED_PEERS_ON_DEBUG or for_everyone:
                bot.add_event_in_queue(event)
            if threading.active_count() == 1:
                exit()


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            exception_checker()
