import vk_api
import requests
import wikipediaapi

import string
import random
import pymorphy2
import json

from sql.sql_api import Sqlite
from constants import CHIEF_ADMIN, LADNO_CHANCE, HUY_CHANCE, NU_POLUCHAETSYA_CHANCE

WIKI_API = "https://ru.wikipedia.org/w/api.php"
wiki_wiki = wikipediaapi.Wikipedia('ar')
ALLOWED_SYMBOLS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХКЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхкцчшщъыьэюя"
morph = pymorphy2.analyzer.MorphAnalyzer()
RUSSIAN_VOWEL = "АЕЁИОУЫЭЮЯаеёиоуыэюя"
MAIN_POS = ("NOUN",
            "ADJF", "ADJS", "COMP", "VERB", "INFN", "PRTF", "PRTS", "GRND", "NUMR", "ADVB", "NPRO")


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


def send_message(message: str,
                 vk: vk_api.vk_api.VkApiMethod,
                 user_id: int = None, attachments:
                 str or list = None,
                 keyboard: dict = None):
    """
    handler for send message
    :param message: text of message 
    :param vk: vk_api for send message
    :param user_id: id of user who receive message 
    :param attachments: attachments in message

    """
    if user_id < 0:
        vk.messages.send(chat_id=-user_id,
                         message=message,
                         random_id=random.randint(0, 2 ** 64),
                         attachment=attachments,
                         keyboard=json.dumps(keyboard) if keyboard else None)
    else:
        vk.messages.send(user_id=user_id,
                         message=message,
                         random_id=random.randint(0, 2 ** 64),
                         attachment=attachments,
                         keyboard=json.dumps(keyboard) if keyboard else None)


def get_random_wiki_page() -> str:
    params = {
        "action": "query",
        "format": "json",
        "list": "random",
        "rnlimit": 5,
        "category": "humor",
        "rvprop": "categories"
    }
    pages = requests.get(WIKI_API, params=params).json()["query"]["random"]
    longest_page = max(pages, key=lambda page: page["title"])["title"]
    return longest_page


def get_only_symbols(text: str) -> str:
    final_text = ""
    for i in text:
        if (i.isalpha() and i not in string.ascii_letters) or i == " ":
            final_text += i
    return final_text


def get_random_funny_wiki_page():
    pages = wiki_wiki.page("Category:فكاهة")
    return random.choice(list(pages.categorymembers.keys()))


def get_main_pos(text) -> dict:
    text_without_signs = ""
    for symbol in text:
        if symbol in ALLOWED_SYMBOLS or symbol == " ":
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
    parts_reformed = list(filter(lambda x: len(x[1]) == 1, list(data.items())))
    if len(parts_reformed) == 0:
        return ""
    else:
        return f"Ну получается {random.choice(parts_reformed)[1][0]}."


def generate_huy_word(word: str):
    if word.startswith(tuple(RUSSIAN_VOWEL)):
        return "Хуя" + word[1:].lower()
    else:
        if word[1] in RUSSIAN_VOWEL:
            return "Ху" + word[1:].lower()
        return "Ху" + word[2:].lower()


def answer_or_not(chat_id: int, sqlite: Sqlite):
    answer_chance = sqlite.get_chances(abs(chat_id), {"answer_chance": True})["answer_chance"]
    if answer_chance:
        return random.choices((True, False), weights=(answer_chance, 100 - answer_chance))[0]
    return False


def get_random_answer(chat_id: int, message: str, sqlite: Sqlite = None, weights: dict = None):
    params = {"ladno_chance": True}
    if len(message.split()) == 1 and len(message.split()[0]) >= 2:
        params["huy_chance"] = True
    if answer_nu_poluchaetsya_or_not(get_main_pos(message)):
        params["nu_poluchaetsya_chance"] = True
    if not weights and sqlite:
        weights = sqlite.get_chances(chat_id, params=params)
    if weights.get(HUY_CHANCE, 1) == 0:
        weights.pop(HUY_CHANCE)
    if weights.get(NU_POLUCHAETSYA_CHANCE, 1) == 0:
        weights.pop(NU_POLUCHAETSYA_CHANCE)
    if weights["ladno_chance"] == 0:
        weights.pop("ladno_chance")
    if weights:
        answer = random.choices(tuple(weights.keys()), weights=tuple(weights.values()))
        if answer:
            return answer[0]
    return []


def get_admins_in_chat(peer_id, vk, ):
    members = \
        vk.messages.getConversationMembers(
            peer_id=peer_id, fields='items')["items"]
    admins = map(lambda y: y["member_id"],
                 tuple(filter(lambda x: x.get("is_admin", False), members)))
    admins = list(admins)
    admins.append(int(CHIEF_ADMIN))
    return admins


def send_answer(message: str, vk: vk_api.vk_api.VkApiMethod, user_id: int, sqlite: Sqlite):
    answer = False
    if user_id < 0:
        answer = answer_or_not(user_id, sqlite)
    if (answer and user_id < 0) or user_id > 0:
        if user_id > 0:
            weights = {LADNO_CHANCE: 1, HUY_CHANCE: 100, NU_POLUCHAETSYA_CHANCE: 100}
            sq = None
        else:
            weights = None
            sq = sqlite
        what = get_random_answer(user_id, message, sq, weights=weights)
        if what == "ladno_chance":
            send_message("Ладно.", vk, user_id)
        elif what == "huy_chance":
            send_message(generate_huy_word(message), vk, user_id)
        elif what == "nu_poluchaetsya_chance":
            data = get_main_pos(message)
            answer = answer_nu_poluchaetsya_or_not(data)
            if answer:
                send_message(answer, vk, user_id)