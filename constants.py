from dotenv import load_dotenv
from sys import platform

import os


dotenv_path = os.path.join(os.path.dirname(__file__), 'config.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

SQL_FILE_NAME: str = os.getenv("db_path")

GROUP_ID: str = os.getenv("vk_group_id")
TOKEN: str = os.getenv("vk_group_token")
CHIEF_ADMIN: str = os.getenv("chief_admin")

if platform in ("linux", "linux2"):
    FONTS_PATH: str = os.getenv("font_linux")
elif platform == "win32":
    FONTS_PATH: str = os.getenv("font_windows")
ARABIC_FONT: str = os.getenv("arabic_font")

Y_TRANSLATE_KEY = os.getenv("yandex_api_key")

with open(os.getenv("help"), encoding="utf-8") as help_text:
    HELP_TEXT = help_text.read()

with open(os.getenv("admin_help"), encoding="utf-8") as help_admin_text:
    ADMIN_TEXT = help_admin_text.read()

ANSWER_CHANCE = "answer_chance"
LADNO_CHANCE = "ladno_chance"
HUY_CHANCE = "huy_chance"
NU_POLUCHAETSYA_CHANCE = "nu_poluchaetsya_chance"
COMMANDS = ("gs", "cp", "cs", "cg", "ca", "lc", "glc", "s", "tac", "ac", "gac", "hc", "ghc", "nc", "gnc")
ADMIN_COMMANDS = ("sa", "ga", "ia", "/bb")
WHO_CAN_TOGGLE_CHANCES = {
    0: "Менять настройки могут все пользователи",
    1: "Менять настройки могут только админы"
}