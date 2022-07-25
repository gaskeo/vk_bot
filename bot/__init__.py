from loguru import logger

import threading
from queue import Queue

import time

from vk_api.bot_longpoll import VkBotMessageEvent, VkBotEventType
from vk_api import vk_api, upload

from rds.redis_api import RedisApi

from constants import MY_NAMES, GROUP_ID
from .commands import create_commands
from .logging import my_logger, log_stop


def check_stop(event: VkBotMessageEvent):
    return event.type == StopEvent


def stop_thread():
    exit()


class StopEvent(VkBotMessageEvent):
    type = 'stop_event'


def clear_my_names(mess: str) -> str:
    for name in MY_NAMES:
        mess = mess.replace(name, '')
    return mess.strip()


def get_text_from_wall(event: VkBotMessageEvent) -> str:
    mess = event.obj.message
    for attach in mess.get("attachments"):
        if attach.get("type", '') != "wall":
            continue

        if wall_text := get_wall_text(attach):
            return wall_text

        elif copy_history := get_wall_copy_history(attach):
            for post in copy_history:
                if wall_text := post.get("text", ""):
                    return wall_text
    return ''


def get_reply_text(event: VkBotMessageEvent):
    return event.obj.message.get(
        "reply_message", dict()).get("text", "")


def get_wall_text(wall_post: dict) -> str:
    return wall_post.get('wall', dict()).get('text', '')


def get_wall_copy_history(wall_post: dict) -> list:
    return wall_post.get('wall', dict()).get('copy_history', [])


def get_command(text: str) -> str:
    return split_text[0] if len(split_text := text.split()) > 0 else ''


def get_text(event: VkBotMessageEvent):
    text = event.obj.message.get("text", "")

    if text != get_command(text):
        if text.startswith("/"):
            return " ".join(text.split()[1:])
        return text

    elif reply_text := get_reply_text(event):
        return reply_text

    return get_text_from_wall(event)


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

        self.commands = create_commands(Bot)

        self.threads = {}
        self.n_threads = n_threads
        self.start()

    def start(self):
        for th in range(self.n_threads):
            event_checker = threading.Thread(
                target=self.check_event_type)
            event_checker.setName(str(th + 1))
            self.threads[event_checker.name] = 1
            event_checker.start()
            logger.info(f"thread {event_checker.name} started")

    def check_event_type(self):
        while True:
            for event in iter(self.events.get, None):
                self.threads[threading.currentThread().name] = 0
                if check_stop(event):
                    log_stop()
                    stop_thread()

                if event.type in (VkBotEventType.MESSAGE_NEW,
                                  VkBotEventType.MESSAGE_EVENT):
                    self.handle_event(event)
                self.threads[threading.currentThread().name] = 1

    @staticmethod
    def check_invite_me(event: VkBotMessageEvent) -> bool:
        action = event.obj.message.get("action", None)
        if action:
            action_type = action["type"]
            if action_type == "chat_invite_user" \
                    and action["member_id"] == -int(GROUP_ID):
                return True
        return False

    def on_invite(self, event):
        peer_id = event.obj.message["peer_id"]

        self.redis.add_peer_id(str(peer_id))
        self.send_message("дайте админку пжпж", peer_id)
        return

    def on_new_message(self, event: VkBotMessageEvent):
        my_logger(event)
        command = get_command(event.obj.message.get('text', ''))
        message: str = get_text(event)
        if self.check_invite_me(event):
            self.on_invite(event)
            return

        peer_id = event.obj.message["peer_id"]

        message = clear_my_names(message)

        self.add_message(event, message)
        self.get_bot_command(command)(self, event, message, peer_id)

    def on_message_event(self, event: VkBotMessageEvent):
        command = event.obj.payload.get("command", "")
        peer_id = event.obj["peer_id"]
        message = ""
        self.get_bot_command(command)(self, event, message, peer_id)

    def get_bot_command(self, command_name: str):
        return self.commands.get(command_name,
                                 self.commands.get("other"))

    def handle_event(self, event: VkBotMessageEvent):
        if event.type == VkBotEventType.MESSAGE_NEW:
            self.on_new_message(event)

        elif event.type == VkBotEventType.MESSAGE_EVENT:
            self.on_message_event(event)

    def add_event_in_queue(self, event):
        self.events.put(event)

    def add_message(self, event, message):
        if len(message) > 10:
            self.redis.increment_count_messages(
                event.obj.message["peer_id"],
                event.obj.message["from_id"])

    from .send_message import send_message
    from .send_photo import send_photo

    from .commands.redo_command import redo_command
    from .commands.help_command import show_help
    from .commands.get_synonyms_command import get_synonyms
    from .commands.create_postirony_command import create_postirony
    from .commands.create_shakal_command import create_shakal
    from .commands.create_grain_command import create_grain
    from .commands.create_arabfunny_command import create_arabfunny
    from .commands.create_dab_command import create_dab
    from .commands.get_uptime_command import get_uptime
    from .commands.get_chance_command import get_chance
    from .commands.get_count_words_command import get_count_words
    from .commands.generate_speak_command import generate_speak
    from .commands.get_words_after_that_command \
        import get_words_after_that
    from .commands.get_peer_command import get_peer
    from .commands.alive_command import alive
    from .commands.toggle_access_chat_settings_command import \
        toggle_access_chat_settings
    from .commands.set_chance_command import set_chance
    from .commands.show_settings_command import show_settings
    from .commands.clear_chat_speaker_command import clear_chat_speaker
    from .commands.update_chat_command import update_chat
    from .commands.delete_this_command import delete_this
    from .commands.admin_help_command import admin_help
    from .commands.set_admin_command import set_admin
    from .commands.get_admin_command import get_admin
    from .commands.is_admin_command import is_admin
    from .commands.bye_bye_command import bye_bye
    from .commands.alive_threads_command import alive_threads
    from .commands.send_answer_command import send_answer
    from .commands.archived_command import archived
    from .commands.generate_token_command import generate_token
    from .commands.connect_command import connect
    from .commands.accept_connect_command import accept_connect
    from .commands.send_other_chat_command import send_other_chat
    from .commands.disconnect_command import disconnect
    from .commands.test_command import test
    from .commands.ans_yes_no_command import answer_yes_no
    from .commands.lox_command import lox_command
    from .commands.get_my_count import get_my_count
    from .commands.get_top import get_top
    from .commands.send_in_peer import send_in_peer
    from .commands.clear_keyboard import clear_keyboard
    from .commands.search_image import search_image
    from .commands.create_chat import create_chat
    from .commands.get_cat import get_cat
