import vk_api
import wikipediaapi

import string
import random
import pymorphy2
import json
from loguru import logger
from transliterate import translit
import sys

from constants import CHIEF_ADMIN, HUY_CHANCE, \
    RUSSIAN_SYMBOLS, RUSSIAN_VOWEL, MAIN_POS, ANSWER_CHANCE

wiki_wiki = wikipediaapi.Wikipedia('ar')
wikipediaapi.log.propagate = False

morph = pymorphy2.analyzer.MorphAnalyzer()


def get_user_id_via_url(user_url: str, vk: vk_api.vk_api.VkApiMethod) -> int:
    """
    finding user id via url
    :param user_url: user's url who need id
    :param vk: vk_api for find user's id via url
    :return: user's id or 0 if user not found

    """

    def get_user_screen_name_of_url(url: str) -> str:
        """
        searching screen name in url
        :param url: user's account url
        :return: user's screen name

        """
        if url.startswith("[") and url.endswith("]") and "|" in url:
            url = url[1:url.find("|")]
            return url
        url = url.replace("@", "")
        if url.endswith("/"):
            url = url[:-1]
        while "/" in url:
            url = url[url.rfind("/") + 1:]
        return url

    info = vk.utils.resolveScreenName(screen_name=get_user_screen_name_of_url(user_url))
    if info:
        user_id: int = info["object_id"]
        return user_id
    return 0


def get_user_name(user_id: int, vk: vk_api.vk_api.VkApiMethod) -> str:
    try:
        user = vk.users.get(user_ids=user_id)[0]
        name = user.get("first_name", "Name")
        last_name = user.get("last_name", "Last name")
        return f"{name} {last_name}"
    except IndexError:
        return "'вот тут имя, но вк его не достал'"


def get_only_symbols(text: str) -> str:
    """
    get only latin letters from string
    :param text: string
    :return: string including only latin letters

    """
    final_text = ""
    for i in text:
        if (i.isalpha() and i not in string.ascii_letters) or i == " ":
            final_text += i
    return final_text


def get_random_funny_wiki_page() -> str:
    """
    get random wiki page header from category humor
    :return: random wiki page header

    """
    pages = wiki_wiki.page("Category:فكاهة")
    return random.choice(list(pages.categorymembers.keys()))


def get_main_pos(text) -> dict:
    """
    get dict like {part of speech: [words], ...}
    :param text: ext to work on
    :return: dict like {part of speech: [words], ...}

    """
    text_without_signs = ""
    for symbol in text:
        if symbol.lower() in RUSSIAN_SYMBOLS or symbol == " ":
            text_without_signs += symbol
    words = text_without_signs.split()
    parts = {}
    for word in words:
        parse = morph.parse(word)
        if parse:
            pos = parse[0].tag.POS
            if pos in MAIN_POS:
                if pos in parts:
                    parts[pos].append(word)
                else:
                    parts[pos] = [word]
    return parts


def answer_nu_poluchaetsya_or_not(data: dict) -> str:
    """
    answer nu_poluchaetsya on message
    :param data: dict like {part of speech: [words], ...}
    :return: text like Ну получается... or ""

    """
    part = get_random_part_once(data)
    if part:
        return f"Ну получается {part}."
    return ""


def get_random_part_once(data) -> str:
    """
    get random word of part of speech that find once in dict
    :param data: dict like {part of speech: [words], ...}
    :return: word

    """
    parts_reformed = list(filter(lambda x: len(x[1]) == 1, list(data.items())))
    if parts_reformed:
        return random.choice(parts_reformed)[1][0]
    return ""


def generate_huy_word(data: dict) -> str:
    """
    generator huy word from random word from data
    :param data: dict like {part of speech: [words], ...}
    :return: huy-like word

    """
    word = get_random_part_once(data)
    if word:
        if word.lower().startswith(tuple(RUSSIAN_VOWEL)):
            return "Хуя" + word[1:].lower()
        else:
            if len(word) > 1 and word[1].lower() in RUSSIAN_VOWEL:
                return "Ху" + word[1:].lower()
            return "Ху" + word[2:].lower()
    else:
        return ""


def get_admins_in_chat(peer_id, vk) -> list:
    """
    get all admins in chat
    :param peer_id: peer id of chat
    :param vk: vk_api for get admins
    :return: list of admins

    """
    try:
        members = \
            vk.messages.getConversationMembers(
                peer_id=peer_id)["items"]
    except vk_api.exceptions.ApiError:
        return [int(CHIEF_ADMIN)]
    admins = map(lambda y: y["member_id"],
                 tuple(filter(lambda x: x.get("is_admin", False), members)))
    admins = list(admins)

    admins.append(int(CHIEF_ADMIN))
    return admins


def what_answer(message: str, chances: dict) -> str:
    """
    send answer on non-command message
    :param message: text of message
    :param chances: chances

    """
    if not generate_huy_word(get_main_pos(message)):
        chances[HUY_CHANCE] = 0
    if not chances[HUY_CHANCE] and not chances[ANSWER_CHANCE]:
        return ""
    nc = 100 - chances[HUY_CHANCE] - chances[ANSWER_CHANCE]
    variants = tuple(chances.keys()) + ("Nothing",)
    weights = tuple(chances.values()) + (nc,)
    what = random.choices(variants, weights=weights)[0]
    return what


def exception_checker():
    try:
        type_ex, obj_ex, info = sys.exc_info()
        line = info.tb_lineno
        file = info.tb_frame.f_code.co_filename
        while True:
            info = info.tb_next
            if info:
                line = info.tb_lineno
                file = info.tb_frame.f_code.co_filename
            else:
                break
        logger.error(f"{type_ex} | msg: {translit(str(obj_ex), 'ru', reversed=True)}"
                      f" | file: {file} | line: {line}")
    except Exception:
        pass


def find_image(event):
    message = event.obj.message
    while True:
        if not message:
            return []
        if message.get("attachments", False):
            photos = list(filter(lambda attach: attach["type"] == "photo",
                                 message.get("attachments")))
            if photos:
                return photos
        if message.get("reply_message", False):
            message = message.get("reply_message")
        elif message.get("fwd_messages", False):
            message = message.get("fwd_messages")[0]
        else:
            break
    return []


def get_random_user_from_conversation(vk: vk_api.vk_api.VkApiMethod, peer_id):
    try:
        members = \
            tuple(filter(lambda u: u["member_id"] > 0,
                         vk.messages.getConversationMembers(peer_id=int(peer_id))["items"]))
        return random.choice(members)['member_id']
    except vk_api.exceptions.ApiError as e:
        ...
    return -1




class Nothing:
    ...
