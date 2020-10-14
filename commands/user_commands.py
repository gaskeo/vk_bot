import urllib.request

import vk_api

from io import BytesIO
import os

import random
import json

from sql.sql_api import Sqlite
from .images_tool import create_arabic_meme, create_grain, create_shakal
from utils import send_message
from yandex.yandex_api import get_text_from_json_get_synonyms, get_synonyms
from constants import HELP_TEXT, ANSWER_CHANCE, LADNO_CHANCE, HUY_CHANCE, NU_POLUCHAETSYA_CHANCE, \
    COMMANDS, WHO_CAN_TOGGLE_CHANCES

CHANCES_ONE_ANSWER = {
    "answer_chance": "ответа",
    "ladno_chance": "Ладно",
    "huy_chance": "Ху-",
    "nu_poluchaetsya_chance": "Ну получается..."
}

CHANCES_ALL_SETTINGS = {
    "answer_chance": "Шанс ответа",
    "ladno_chance": "Шанс Ладно",
    "huy_chance": "Шанс Ху-",
    "nu_poluchaetsya_chance": "Шанс Ну получается..."
}

SETTINGS_KEYBOARD = {
  "buttons": [
    [
      {
        "action": {
          "type": "text",
          "label": "/lc 0",
          "payload": ""
        },
        "color": "negative"
      },
      {
        "action": {
          "type": "text",
          "label": "/lc 50",
          "payload": ""
        },
        "color": "secondary"
      },
      {
        "action": {
          "type": "text",
          "label": "/lc 100",
          "payload": ""
        },
        "color": "positive"
      }
    ],
    [
      {
        "action": {
          "type": "text",
          "label": "/hc 0",
          "payload": ""
        },
        "color": "negative"
      },
      {
        "action": {
          "type": "text",
          "label": "/hc 50",
          "payload": ""
        },
        "color": "secondary"
      },
      {
        "action": {
          "type": "text",
          "label": "/hc 100",
          "payload": ""
        },
        "color": "positive"
      }
    ],
    [
      {
        "action": {
          "type": "text",
          "label": "/nc 0",
          "payload": ""
        },
        "color": "negative"
      },
      {
        "action": {
          "type": "text",
          "label": "/nc 50",
          "payload": ""
        },
        "color": "secondary"
      },
      {
        "action": {
          "type": "text",
          "label": "/nc 100",
          "payload": ""
        },
        "color": "positive"
      }
    ]
  ],
  "inline": True
}


def create_yaderniy_xyesos_2009_command(
        user_id: int, vk: vk_api.vk_api.VkApiMethod, message: str):
    """
    create yAdErNIy xYeSoS from message
    :param user_id: id of user who need YX2009
    :param vk: vk_api for reply message
    :param message: user's message
    :return: refactored text

    """
    if len(message.split()) > 1:
        text = "".join(
            [symb.lower() if random.choice((0, 1))
             else symb.upper() for symb in " ".join(message.split()[1:])])
        send_message(text, vk, user_id)
    else:
        send_message("нЕт сЛОв", vk, user_id)


def create_arabic_funny_command(user_id: int, vk: vk_api.vk_api.VkApiMethod, message: str,
                                all_data_message: dict, upload: vk_api.upload.VkUpload):
    color = 0
    if all_data_message["attachments"]:
        if len(message.split()) > 1:
            color = message.split()[-1]
        for image in all_data_message["attachments"]:
            if image["type"] == "photo":
                url = max(image["photo"]["sizes"], key=lambda x: x["height"])["url"]
                img = urllib.request.urlopen(url).read()
                bytes_img = BytesIO(img)
                name_final_file, text = create_arabic_meme(bytes_img, color)
                photo = upload.photo_messages(photos=[name_final_file],
                                              peer_id=all_data_message["peer_id"])
                vk_photo_id = \
                    f"photo{photo[0]['owner_id']}_{photo[0]['id']}_{photo[0]['access_key']}"
                send_message(text, vk, user_id, vk_photo_id)
                os.remove(name_final_file)
    else:
        send_message("Прикрепи фото", vk, user_id)


def create_shakal_command(user_id: int, vk: vk_api.vk_api.VkApiMethod, message: str,
                          all_data_message: dict, upload: vk_api.upload.VkUpload):
    """
    create shakal photo from message
    :param user_id: id of user who need shakal
    :param vk: vk_api for reply message
    :param message: user's message
    :param all_data_message: all data from user's message
    :param upload: object for upload files on vk server

    """
    if all_data_message["attachments"]:
        factor = 50
        if len(message.split()) > 1:
            if message.split()[-1].isdigit():
                factor = int(message.split()[-1])
            else:
                send_message("Степеь должна быть целым числом", vk, user_id)
                return
        for image in all_data_message["attachments"]:
            if image["type"] == "photo":
                url = image["photo"]["sizes"][-1]["url"]
                img = urllib.request.urlopen(url).read()
                bytes_img = BytesIO(img)
                photo_bytes = create_shakal(bytes_img, factor)
                photo = upload.photo_messages(photos=[photo_bytes],
                                              peer_id=all_data_message["peer_id"])
                vk_photo_id = \
                    f"photo{photo[0]['owner_id']}_{photo[0]['id']}_{photo[0]['access_key']}"
                send_message("", vk, user_id, vk_photo_id)
                os.remove(photo_bytes)
    else:
        send_message("Прикрепи фото", vk, user_id)


def create_grain_command(user_id: int, vk: vk_api.vk_api.VkApiMethod, message: str,
                         all_data_message: dict, upload: vk_api.upload.VkUpload):
    if all_data_message["attachments"]:
        factor = 50
        if len(message.split()) > 1:
            if message.split()[-1].isdigit():
                factor = int(message.split()[-1])
            else:
                send_message("Степеь должна быть целым числом", vk, user_id)
                return
        for image in all_data_message["attachments"]:
            if image["type"] == "photo":
                url = image["photo"]["sizes"][-1]["url"]
                img = urllib.request.urlopen(url).read()
                bytes_img = BytesIO(img)
                name_final_file = create_grain(bytes_img, factor)
                photo = upload.photo_messages(photos=[name_final_file],
                                              peer_id=all_data_message["peer_id"])
                vk_photo_id = \
                    f"photo{photo[0]['owner_id']}_{photo[0]['id']}_{photo[0]['access_key']}"
                send_message("", vk, user_id, vk_photo_id)
                os.remove(name_final_file)
    else:
        send_message("Прикрепи фото", vk, user_id)


def get_syns(user_id: int, vk: vk_api.vk_api.VkApiMethod, message):
    """
    search synonyms on yandex api and refactor text to message
    :param user_id: id of user who need synonyms
    :param vk: vk_api for reply message
    :param message: user's message
    :param words: list of words need synonyms
    :return: refactored synonyms for message
    """

    def get_syns_refactored(words):
        syns = get_text_from_json_get_synonyms(get_synonyms(words))
        if syns:
            syns_refactored = f"Синонимы к слову \"{' '.join(words)}\":\n\n"
            for syn in syns:
                syns_refactored += tuple(syn.keys())[0] + "\n"
                if tuple(syn.values())[0]:
                    syns_refactored += f"Подобные слову \"{tuple(syn.keys())[0]}\":\n"
                    for unsyn in tuple(syn.values())[0]:
                        syns_refactored += "&#4448;• " + unsyn + "\n"
            return syns_refactored
        else:
            return "Ничего не найдено"

    if len(message.split()) >= 2:
        syns = get_syns_refactored(message.split()[1:])
        send_message(syns, vk, user_id)
    else:
        send_message("Ошибка: нет слова", vk, user_id)


def change_chance_command(chat_id: int,
                          what: str,
                          vk: vk_api.vk_api.VkApiMethod,
                          message: str,
                          sqlite: Sqlite):
    if len(message.split()) == 2:
        chance = message.split()[1]
        if chance.isdigit() and 0 <= int(chance) <= 100:
            sqlite.change_chances(abs(chat_id), params={what: int(chance)})
            send_message(f"Шанс {CHANCES_ONE_ANSWER.get(what, '...')}"
                         f" успешно изменен на {chance}%", vk, -abs(chat_id))
        else:
            send_message("Должно быть число от 0 до 100", vk, -abs(chat_id))
    else:
        send_message("Добавьте шанс (от 0 до 100)", vk, -abs(chat_id))


def get_chance_command(chat_id: int,
                       what: str,
                       vk: vk_api.vk_api.VkApiMethod,
                       sqlite: Sqlite
                       ):
    chance = sqlite.get_chances(abs(chat_id), params={what: True})
    send_message(f"Шанс {CHANCES_ONE_ANSWER[what]} равен "
                 f"{int(chance[what])}%", vk, chat_id)


def show_settings_command(chat_id: int, vk: vk_api.vk_api.VkApiMethod, sqlite: Sqlite):
    all_chances = sqlite.get_chances(abs(chat_id), params={ANSWER_CHANCE: True,
                                                           LADNO_CHANCE: True,
                                                           HUY_CHANCE: True,
                                                           NU_POLUCHAETSYA_CHANCE: True})
    who = sqlite.get_who_can_change_chances(chat_id)
    send_message("Настройки беседы:\n{}\n{}".format('\n'.join(
        [f'{CHANCES_ALL_SETTINGS[what]}: '
         f'{int(chance)}%' for what, chance in
         tuple(all_chances.items())]), WHO_CAN_TOGGLE_CHANCES.get(who)),
        vk, chat_id, keyboard=SETTINGS_KEYBOARD
    )


def help_command(user_id: int, vk: vk_api.vk_api.VkApiMethod, message: str):
    """
    command for help
    :param user_id: id of user who need help
    :param vk: vk_api for reply message
    :param message: text

    """

    if len(message.split()) == 1:
        if user_id > 0:
            help_data = json.loads(HELP_TEXT)["user_help"]["main_user"]
        else:
            help_data = json.loads(HELP_TEXT)["user_help"]["main_conversation"]
        help_text = help_data["text"]
        help_attachments = help_data["attachments"]
        help_keyboard = help_data["keyboard"]
        send_message(help_text, vk, user_id, attachments=help_attachments, keyboard=help_keyboard)
    else:
        if message.split()[-1] in COMMANDS:
            command = message.split()[-1]
            help_data = json.loads(HELP_TEXT)["user_help"][command]
            help_text = help_data["text"]
            help_attachments = help_data["attachments"]
            help_keyboard = help_data["keyboard"]
            send_message(help_text, vk, user_id, attachments=help_attachments,
                         keyboard=help_keyboard)



