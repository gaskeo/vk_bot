import vk_api
import wikipediaapi

import string
import random
import pymorphy2
import json
import logging
from transliterate import translit
import sys

from sql.sql_api import Sqlite
from constants import CHIEF_ADMIN, LADNO_CHANCE, HUY_CHANCE, NU_POLUCHAETSYA_CHANCE, \
    RUSSIAN_SYMBOLS, RUSSIAN_VOWEL, MAIN_POS, MIN_CHAT_PEER_ID, ANSWER_CHANCE

wiki_wiki = wikipediaapi.Wikipedia('ar')
wikipediaapi.log.propagate = False

morph = pymorphy2.analyzer.MorphAnalyzer()

logger = logging.getLogger("main_logger")
logging.basicConfig(filename="vk_bot.log", filemode="a",
                    format=f"%(levelname)s\t\t%(asctime)s\t\t%(message)s",
                    level=logging.INFO)


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
    user = vk.users.get(user_ids=user_id)[0]
    name = user.get("first_name", "Name")
    last_name = user.get("last_name", "Last name")
    return f"{name} {last_name}"


def send_message(message: str,
                 vk: vk_api.vk_api.VkApiMethod,
                 peer_id: int = None,
                 attachments:
                 str or list = None,
                 keyboard: dict = None,
                 template=None):
    """
    handler for send message
    :param message: text of message 
    :param vk: vk_api for send message
    :param peer_id: id of peer of chat who receive message 
    :param attachments: attachments in message
    :param keyboard: keyboard in message
    :param template: template in message
    """
    vk.messages.send(peer_id=peer_id,
                     message=message,
                     random_id=random.randint(0, 2 ** 64),
                     attachment=attachments,
                     keyboard=json.dumps(keyboard) if keyboard else None,
                     template=json.dumps(template) if template else None)
    try:
        log = u"ANSWER IN {}: {} | atts: {}".format(
            peer_id, translit(str(message), 'ru', reversed=True), attachments
        )
        logger.info(log)
    except UnicodeEncodeError:
        pass


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


def answer_or_not(chat_id: int, sqlite) -> bool:
    """
    choose answer on message or not
    :param chat_id: id of chat for get weights
    :param sqlite: Sqlite object from sql_api
    :return: True if answer else False

    """
    answer_chance = sqlite(Sqlite.get_chances, (chat_id,),
                           {"params": {"answer_chance": True}})["answer_chance"]
    if answer_chance:
        return random.choices((True, False), weights=(answer_chance, 100 - answer_chance))[0]
    return False


def get_random_answer(chat_id: int, message: str, sqlite=None, weights: dict = None) \
        -> str:
    """
    get random answer template name
    :param chat_id: id of chat for get weights
    :param message:
    :param sqlite: Sqlite object from sql_api
    :param weights: weights of answers. if refer, sqlite don't need
    :return: random answer or "" if can't answer
    """
    params = {LADNO_CHANCE: True}
    if generate_huy_word(get_main_pos(message)):
        params[HUY_CHANCE] = True
    else:
        params[HUY_CHANCE] = False
    if answer_nu_poluchaetsya_or_not(get_main_pos(message)):
        params[NU_POLUCHAETSYA_CHANCE] = True
    else:
        params[NU_POLUCHAETSYA_CHANCE] = False
    if not weights and sqlite:
        weights = sqlite(Sqlite.get_chances, (chat_id,), {"params": params})
    if weights.get(HUY_CHANCE, 1) == 0 or not params[HUY_CHANCE]:
        if weights.get(HUY_CHANCE, 1) == 0:
            weights.pop(HUY_CHANCE)
    if weights.get(NU_POLUCHAETSYA_CHANCE, 1) == 0 or not params[NU_POLUCHAETSYA_CHANCE]:
        if weights.get(NU_POLUCHAETSYA_CHANCE, 1) == 0:
            weights.pop(NU_POLUCHAETSYA_CHANCE)
    if weights.get(LADNO_CHANCE, 1) == 0 or not params[LADNO_CHANCE]:
        if weights.get(LADNO_CHANCE, 1) == 0:
            weights.pop(LADNO_CHANCE)
    if weights:
        answer = random.choices(tuple(weights.keys()), weights=tuple(weights.values()))
        if answer:
            return answer[0]
    return ""


def get_admins_in_chat(peer_id, vk) -> list:
    """
    get all admins in chat
    :param peer_id: peer id of chat
    :param vk: vk_api for get admins
    :return: list of admins

    """
    members = \
        vk.messages.getConversationMembers(
            peer_id=peer_id)["items"]
    admins = map(lambda y: y["member_id"],
                 tuple(filter(lambda x: x.get("is_admin", False), members)))
    admins = list(admins)

    admins.append(int(CHIEF_ADMIN))
    return admins


def send_answer(message: str, chances: dict) -> str:
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
        logging.error(f"{type_ex} | msg: {translit(str(obj_ex), 'ru', reversed=True)}"
                      f" | file: {file} | line: {line}")
    except Exception:
        pass


class StopEvent:
    ...


class Nothing:
    ...
