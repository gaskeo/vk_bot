import logging

import threading
from queue import Queue
import os
from requests import session

import time
from transliterate import translit

from vk_api.bot_longpoll import VkBotMessageEvent, VkBotEventType
from vk_api import vk_api, upload

from rds.redis_api import RedisApi
from speaker import Speaker

from constants import MY_NAMES, GROUP_ID
from utils import send_message, StopEvent

logger = logging.getLogger("main_logger")
logging.basicConfig(filename="vk_bot.log", filemode="a",
                    format=f"%(levelname)s\t\t%(asctime)s\t\t%(message)s",
                    level=logging.INFO)

HEADERS = {
        'user-agent':
            'Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 '
            '(KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; '
            'en-US; scale=2.00; 828x1792; 165586599)'
    }


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
        self.session = session()
        self.session.headers = HEADERS
        self.commands = {
            # commands for all users
            "/": Bot.redo_command,
            "/help": Bot.show_help,
            "/gs": Bot.get_synonyms,  # get synonyms
            "/cp": Bot.create_postirony,  # create postirony
            "/cs": Bot.create_shakal,  # create shakal
            "/cg": Bot.create_grain,  # create grain
            "/ca": Bot.create_arabfunny,  # create arabfunny
            "/cd": Bot.create_dab,
            "/ut": Bot.get_uptime,
            "/a": Bot.alive,
            "/ck": Bot.clear_keyboard,
            "/yesno": Bot.answer_yes_no,
            # in chats only
            "/gac": Bot.get_chance,  # get answer chance
            "/ghc": Bot.get_chance,  # get huy chance
            "/gc": Bot.get_count_words,
            "/si": Bot.search_image,
            # "/gsw": Bot.get_similarity_words,
            "/g": Bot.generate_speak,
            "/at": Bot.get_words_after_that,
            "/peer": Bot.get_peer,
            "/generate": Bot.generate_token,
            "/connect": Bot.connect,
            "/send": Bot.send_other_chat,
            "/lox": Bot.lox_command,
            "/mc": Bot.get_my_count,
            "/gt": Bot.get_top,
            # for chat admins only
            "/tac": Bot.toggle_access_chat_settings,  # toggle access
            "/ac": Bot.set_chance,  # set answer chance
            "/hc": Bot.set_chance,  # set huy chance
            "/s": Bot.show_settings,  # settings
            "/clear": Bot.clear_chat_speaker,
            "/update": Bot.update_chat,
            "/dt": Bot.delete_this,
            "/disconnect": Bot.disconnect,
            "/accept_connect": Bot.accept_connect,
            # "/dsw": Bot.clear_similarity_words,
            # for bot admins only
            "/adm": Bot.admin_help,  # help admins
            "/sa": Bot.set_admin,  # set admin
            "/ga": Bot.get_admin,  # get admin
            "/ia": Bot.is_admin,  # is admin
            "/bb": Bot.bye_bye,  # exit program
            "/th": Bot.alive_threads,
            "/sp": Bot.send_in_peer,
            # experimental
            "/csg": None,  # create gif shakal
            "/cag": None,  # create gif arabfunny
            # other
            "other": Bot.send_answer,  # answer on simple message
            # archive
            "/glc": Bot.archived,  # get ladno chance
            "/gnc": Bot.archived,  # get nu... chance
            "/lc": Bot.archived,  # set ladno chance
            "/nc": Bot.archived,  # set nu... chance
            "/test": Bot.test
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
            for event in iter(self.events.get, None):
                self.threads[threading.currentThread().name] = 0
                self.check_stop(event)
                if event.type in (VkBotEventType.MESSAGE_NEW, VkBotEventType.MESSAGE_EVENT):
                    self.message_checker(event)
                self.threads[threading.currentThread().name] = 1

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

            self.add_message(event, message)

            command = "" if len(message.split()) < 1 else message.split()[0].lower()
        else:
            command = event.obj.payload["command"]
            peer_id = event.obj["peer_id"]
            message = ""
        try:
            c = self.commands.get(command, self.commands.get("other"))
            c(self, event, message, peer_id)
        except Exception as e:
            ...

    def add_event_in_queue(self, event):
        self.events.put(event)

    def photo_work(self, photo_bytes, peer_id, second_image=None):
        photo = self.upload.photo_messages(photos=[photo_bytes], peer_id=peer_id)
        vk_photo_id = \
            f"photo{photo[0]['owner_id']}_{photo[0]['id']}_{photo[0]['access_key']}"
        send_message("", self.vk, peer_id=peer_id, attachments=vk_photo_id)
        os.remove(photo_bytes)
        if second_image and second_image != "photos_examples/dab.png":
            os.remove(second_image)

    def add_message(self, event, message):
        if len(message) > 10:
            self.redis.increment_count_messages(event.obj.message["peer_id"], event.obj.message["from_id"])

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
    from ._ans_yes_no_command import answer_yes_no
    from ._lox_command import lox_command
    from ._get_my_count import get_my_count
    from ._get_top import get_top
    from ._send_in_peer import send_in_peer
    from ._clear_keyboard import clear_keyboard
    from ._search_image import search_image


