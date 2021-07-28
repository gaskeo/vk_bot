import logging

import threading
from queue import Queue

import time
from transliterate import translit

from vk_api.bot_longpoll import VkBotMessageEvent, VkBotEventType
from vk_api import vk_api, upload

from rds.redis_api import RedisApi
from speaker import Speaker

from constants import MY_NAMES, GROUP_ID
from utils import \
    exception_checker, \
    send_message, \
    StopEvent

logger = logging.getLogger("main_logger")
logging.basicConfig(filename="vk_bot.log", filemode="a",
                    format=f"%(levelname)s\t\t%(asctime)s\t\t%(message)s",
                    level=logging.INFO)


class Bot:
    def __init__(self, vk: vk_api.VkApiMethod,
                 redis: RedisApi,
                 upl: upload.VkUpload,
                 n_threads=8):
        self.redis = redis
        self.vk: vk_api.VkApiMethod = vk
        self.upload = upl
        self.events = Queue()
        self.uptime = time.time()
        self.speaker = Speaker(redis)
        self.commands = {
            # commands for all users
            "/": self.redo_command,
            "/help": self.show_help,
            "/gs": self.get_synonyms,  # get synonyms
            "/cp": self.create_postirony,  # create postirony
            "/cs": self.create_shakal,  # create shakal
            "/cg": self.create_grain,  # create grain
            "/ca": self.create_arabfunny,  # create arabfunny
            "/cd": self.create_dab,
            "/ut": self.get_uptime,
            "/a": self.alive,
            # in chats only
            "/gac": self.get_chance,  # get answer chance
            "/ghc": self.get_chance,  # get huy chance
            "/gc": self.get_count_words,
            # "/gsw": self.get_similarity_words,
            "/g": self.generate_speak,
            "/at": self.get_words_after_that,
            "/peer": self.get_peer,
            "/generate": self.generate_token,
            "/connect": self.connect,
            "/send": self.send_other_chat,
            # for chat admins only
            "/tac": self.toggle_access_chat_settings,  # toggle access
            "/ac": self.set_chance,  # set answer chance
            "/hc": self.set_chance,  # set huy chance
            "/s": self.show_settings,  # settings
            "/clear": self.clear_chat_speaker,
            "/update": self.update_chat,
            "/dt": self.delete_this,
            "/disconnect": self.disconnect,
            "/accept_connect": self.accept_connect,
            # "/dsw": self.clear_similarity_words,
            # for bot admins only
            "/adm": self.admin_help,  # help admins
            "/sa": self.set_admin,  # set admin
            "/ga": self.get_admin,  # get admin
            "/ia": self.is_admin,  # is admin
            "/bb": self.bye_bye,  # exit program
            "/th": self.alive_threads,
            # experimental
            "/csg": None,  # create gif shakal
            "/cag": None,  # create gif arabfunny
            # other
            "other": self.send_answer,  # answer on simple message
            # archive
            "/glc": self.archived,  # get ladno chance
            "/gnc": self.archived,  # get nu... chance
            "/lc": self.archived,  # set ladno chance
            "/nc": self.archived,  # set nu... chance
            "/test": self.test
        }
        self.threads = {}
        self.n_threads = n_threads
        self.start()

    @staticmethod
    def logger(event):
        try:
            log = u"{} IN {}: {} | atts: {}".format(event.obj.message["from_id"],
                                                    event.obj.message["peer_id"],
                                                    translit(event.obj.message["text"],
                                                             "ru", reversed=True
                                                             ).encode('unicode-escape'),
                                                    event.obj.message["attachments"]
                                                    )
            logger.info(log)
        except UnicodeEncodeError:
            pass

    def start(self):
        for th in range(self.n_threads):
            event_checker = threading.Thread(target=self.check_event_type)
            event_checker.setName(str(th + 1))
            self.threads[event_checker.name] = 1
            event_checker.start()
            logger.info(f"thread {event_checker.name} started")

    @staticmethod
    def check_stop(event):
        if event == StopEvent:
            logger.info(f"thread {threading.currentThread().name} stopped")
            exit()

    def check_event_type(self):
        while True:
            try:
                for event in iter(self.events.get, None):
                    self.threads[threading.currentThread().name] = 0
                    self.check_stop(event)
                    if event.type in (VkBotEventType.MESSAGE_NEW, VkBotEventType.MESSAGE_EVENT):
                        self.message_checker(event)
                    self.threads[threading.currentThread().name] = 1
            except Exception:
                exception_checker()

    def message_checker(self, event: VkBotMessageEvent):
        if event.type == VkBotEventType.MESSAGE_NEW:
            self.logger(event)

            message: str = event.obj.message["text"]
            peer_id = event.obj.message["peer_id"]
            action = event.obj.message.get("action", None)
            if action:
                action_type = action["type"]
                if action_type == "chat_invite_user" and action["member_id"] == -int(GROUP_ID):
                    self.redis.add_peer_id(str(peer_id))
                    send_message("дайте админку пжпж", self.vk, peer_id)
            if not message:
                return
            if message.startswith(MY_NAMES):
                for name in MY_NAMES:
                    message = message.replace(name, '')
            message = message.lstrip().rstrip()

            command = "" if len(message.split()) < 1 else message.split()[0].lower()
        else:
            command = event.obj.payload["command"]
            peer_id = event.obj["peer_id"]
            message = ""
        c = self.commands.get(command, self.commands.get("other"))
        c(event, message, peer_id)

    def add_event_in_queue(self, event):
        self.events.put(event)

    from ._redo_command import redo_command
    from ._help_command import show_help
    from ._get_synonyms_command import get_synonyms
    from ._create_postirony_command import create_postirony
    from ._create_shakal_command import create_shakal
    from ._create_grain_command import create_grain
    from ._create_arabfunny_command import create_arabfunny
    from ._create_dab_command import create_dab
    from ._get_uptime_command import get_uptime
    from ._get_chance_command import get_chance
    from ._get_count_words_command import get_count_words
    from ._generate_speak_command import generate_speak
    from ._get_words_after_that_command import get_words_after_that
    from ._get_peer_command import get_peer
    from ._alive_command import alive
    from ._toggle_access_chat_settings_command import toggle_access_chat_settings
    from ._set_chance_command import set_chance
    from ._show_settings_command import show_settings
    from ._clear_chat_speaker_command import clear_chat_speaker
    from ._update_chat_command import update_chat
    from ._delete_this_command import delete_this
    from ._admin_help_command import admin_help
    from ._set_admin_command import set_admin
    from ._get_admin_command import get_admin
    from ._is_admin_command import is_admin
    from ._bye_bye_command import bye_bye
    from ._alive_threads_command import alive_threads
    from ._send_answer_command import send_answer
    from ._archived_command import archived
    from ._generate_token_command import generate_token
    from ._connect_command import connect
    from ._accept_connect_command import accept_connect
    from ._send_other_chat_command import send_other_chat
    from ._disconnect_command import disconnect
    from ._test_command import test



