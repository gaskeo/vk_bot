import vk_api
import requests
import wikipediaapi

import string
import random
import pymorphy2

from sql.sql_api import Sqlite

WIKI_API = "https://ru.wikipedia.org/w/api.php"
wiki_wiki = wikipediaapi.Wikipedia('ar')
ALLOWED_SYMBOLS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХКЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхкцчшщъыьэюя"
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


def send_message(message: str,
                 vk: vk_api.vk_api.VkApiMethod,
                 user_id: int = None, attachments:
                 str or list = None):
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
                         attachment=attachments)
    else:
        vk.messages.send(user_id=user_id,
                         message=message,
                         random_id=random.randint(0, 2 ** 64),
                         attachment=attachments)


def send_ladno(vk: vk_api.vk_api.VkApiMethod,
               chat_id: int, sqlite: Sqlite):
    chance = sqlite.get_ladno_chance(chat_id)
    ladno = random.choices((1, 0), weights=(chance, 1 - chance))
    if ladno[0]:
        send_message("Ладно.", vk, -abs(chat_id))


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


def get_adjectives_and_count_other_pos(text) -> dict:
    text_without_signs = ""
    for symbol in text:
        if symbol in ALLOWED_SYMBOLS or symbol == " ":
            text_without_signs += symbol
    words = text_without_signs.split()
    adjectives = []
    other = []
    for word in words:
        parse = morph.parse(word)
        if parse:
            if parse[0].tag.POS == "ADJF":
                adjectives.append(parse[0].word)
            else:
                other.append(parse[0].word)
    return {"adjectives": adjectives,
            "other": other
            }


def answer_nu_poluchaetsya_or_not(data: dict) -> str:
    if len(data["adjectives"]) == 1 and len(data["other"]) < 5:
        if "не" in data["other"]:
            ne = "не "
        else:
            ne = ""
        return f"Ну получается {ne}{data['adjectives'][0]}."
    return ""
