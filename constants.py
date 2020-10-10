from dotenv import load_dotenv

import os


dotenv_path = os.path.join(os.path.dirname(__file__), 'config.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

SQL_FILE_NAME: str = os.getenv("db_path")

GROUP_ID: str = os.getenv("vk_group_id")
TOKEN: str = os.getenv("vk_group_token")
CHIEF_ADMIN: str = os.getenv("chief_admin")
Y_TRANSLATE_KEY = os.getenv("yandex_api_key")

with open(os.getenv("help"), encoding="utf-8") as help_text:
    HELP_TEXT = help_text.read()

with open(os.getenv("admin_help"), encoding="utf-8") as help_admin_text:
    ADMIN_TEXT = help_admin_text.read()
