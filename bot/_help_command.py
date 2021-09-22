from vk_api import bot_longpoll

import json

from constants import MIN_CHAT_PEER_ID, HELP_TEXT

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def show_help(self: 'Bot', event: bot_longpoll.VkBotMessageEvent, message: str, peer_id: int):
    if not len(message.split()):
        help_template = None
        if peer_id > MIN_CHAT_PEER_ID:
            help_data = json.loads(HELP_TEXT)["user_help"]["main_conversation"]
            help_text_all = help_data["text"]
            help_keyboard = help_data["keyboard"]
        else:
            help_data = json.loads(HELP_TEXT)["user_help"]["main_user"]
            if event.obj["client_info"].get("carousel", False):
                help_template = help_data["template"]
                help_text_all = help_data["text_template"]
                help_keyboard = help_data["keyboard_template"]
            else:
                help_text_all = help_data["text_no_template"]
                help_keyboard = help_data["keyboard_no_template"]
        help_attachments = help_data["attachments"]
        return self.send_message(help_text_all, str(peer_id), attachments=help_attachments,
                                 keyboard=help_keyboard, template=help_template)

    if message.split()[-1] in json.loads(HELP_TEXT)["user_help"]:
        command = message.split()[-1]
        help_data = json.loads(HELP_TEXT)["user_help"][command]
        help_text_command = help_data["text"]
        help_attachments = help_data["attachments"]
        help_keyboard = help_data["keyboard"]
        self.send_message(help_text_command, str(peer_id),
                          attachments=help_attachments, keyboard=help_keyboard)
