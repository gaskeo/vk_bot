from dotenv import load_dotenv
from sys import platform

import os

dotenv_path = os.path.join(os.path.dirname(__file__), 'config.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

GROUP_ID: str = os.getenv("vk_group_id")
TOKEN: str = os.getenv("vk_group_token")
CHIEF_ADMIN: str = os.getenv("chief_admin")

REDIS_PASSWORD: str = os.getenv("redis_pass")

if platform in ("linux", "linux2"):
    FONTS_PATH: str = os.getenv("font_linux")
elif platform == "win32":
    FONTS_PATH: str = os.getenv("font_windows")
ARABIC_FONT: str = os.getenv("arabic_font")

with open(os.getenv("help"), encoding="utf-8") as help_text:
    HELP_TEXT = help_text.read()

with open(os.getenv("admin_help"), encoding="utf-8") as help_admin_text:
    ADMIN_TEXT = help_admin_text.read()

with open(os.getenv("keyboards"), encoding="utf-8") as keyboards:
    KEYBOARDS = keyboards.read()

IMAGE_START_PARAMS = {
    "key": os.getenv("google-key"),
    "cx": os.getenv("google-cx")
}

ANSWER_CHANCE = "answer_chance"
LADNO_CHANCE = "ladno_chance"
HUY_CHANCE = "huy_chance"
NU_POLUCHAETSYA_CHANCE = "nu_poluchaetsya_chance"

WHO_CAN_TOGGLE_CHANCES = {
    0: "Менять настройки могут все пользователи",
    1: "Менять настройки могут только админы"
}

GET_COMMANDS = {"/gac": ANSWER_CHANCE,
                "/glc": LADNO_CHANCE,
                "/ghc": HUY_CHANCE,
                "/gnc": NU_POLUCHAETSYA_CHANCE}

SET_COMMANDS = {"/ac": ANSWER_CHANCE,
                "/lc": LADNO_CHANCE,
                "/hc": HUY_CHANCE,
                "/nc": NU_POLUCHAETSYA_CHANCE}

# Заменить xxxxxxxxx на id группы
MY_NAMES = ("[clubxxxxxxxxx|group_name]",
            "[clubxxxxxxxxx|@clubxxxxxxxxx]")

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

RUSSIAN_SYMBOLS = "абвгдеёжзийклмнопрстуфхкцчшщъыьэюя"
RUSSIAN_VOWEL = "аеёиоуыэюя"
MAIN_POS = ("NOUN",
            "ADJF", "ADJS", "COMP", "VERB", "INFN", "PRTF",
            "PRTS", "GRND", "NUMR", "ADVB", "NPRO")

SYNONYMS_API_ADDRESS = \
    "https://dictionary.yandex.net/dicservice.json/lookupMultiple"

TEXT_COLORS = {
    "black": "white",
    "blue": "white",
    "green": "white",
    "orange": "black",
    "purple": "black",
    "red": "white",
    "white": "black",
    "yellow": "black"
}

MIN_CHAT_PEER_ID = 2000000000

ADMIN_LEVELS = "admin_levels"
WHO_CAN_TOGGLE_CHANCES_TEXT = "who_can"
ADMINS_ONLY = 1
ALL = 0

ACCEPTED_PEERS_ON_DEBUG = (CHIEF_ADMIN, )
STOP_WORDS = "_start_", "_all_"

ENTER = "\n"

EMPTY_KEYBOARD = {
    "one_time": False,
    "buttons": []
}
