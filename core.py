from vk_api import VkApi, VkUpload
from vk_api.bot_longpoll import VkBotEventType

from my_vk_api.longpoll import MyVkLongPoll
import threading

from loguru import logger
from bot import Bot

from rds.redis_api import RedisApi
from constants import TOKEN, GROUP_ID, REDIS_PASSWORD, ACCEPTED_PEERS_ON_DEBUG

for_everyone = 1

if for_everyone:
    logger.remove()

logger.add("vk_bot.log", rotation="10 MB", encoding="utf-8")


def main() -> None:
    """
    main cycle of program

    """
    vk_session: VkApi = VkApi(
        token=TOKEN)
    long_poll = MyVkLongPoll(vk_session, GROUP_ID)
    upload = VkUpload(vk_session)
    vk = vk_session.get_api()
    rds = RedisApi(password=REDIS_PASSWORD)
    if not rds.redis.ping():
        raise ConnectionError
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
    main()

