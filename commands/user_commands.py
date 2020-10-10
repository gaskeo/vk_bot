import urllib.request

import vk_api

from io import BytesIO
import os

import random

from .images_tool import create_arabic_meme, create_grain, create_shakal
from utils import send_message
from yandex.yandex_api import get_text_from_json_get_synonyms, get_synonyms
from constants import HELP_TEXT


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
                url = image["photo"]["sizes"][-1]["url"]
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


def help_command(user_id: int, vk: vk_api.vk_api.VkApiMethod):
    """
    command for help
    :param user_id: id of user who need help
    :param vk: vk_api for reply messsage

    """
    send_message(HELP_TEXT, vk, user_id)
