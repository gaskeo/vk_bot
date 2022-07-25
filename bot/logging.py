import threading
from loguru import logger

from vk_api.bot_longpoll import VkBotMessageEvent


def log_stop():
    logger.info(
        f"thread {threading.currentThread().name} stopped")


def my_logger(event: VkBotMessageEvent):
    try:
        log = u"{} IN {}: {} | atts: {}".format(
            event.obj.message["from_id"],
            event.obj.message["peer_id"],
            event.obj.message["text"],
            event.obj.message["attachments"]
        )
        logger.info(log)
    except UnicodeEncodeError:
        pass
