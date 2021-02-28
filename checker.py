import logging
import threading
from queue import Queue
import random
from io import BytesIO
import string
import json

from PIL import Image, ImageDraw, ImageFont

import vk_api
from vk_api.bot_longpoll import VkBotMessageEvent, VkBotEventType
import urllib.request

from constants import *
from utils import \
    send_answer, \
    get_random_funny_wiki_page, \
    get_only_symbols, \
    get_admins_in_chat, \
    get_user_name, \
    exception_checker, \
    send_message, \
    get_user_id_via_url, \
    Redis
from yandex.yandex_api import get_synonyms, get_text_from_json_get_synonyms
from ai.main import WordNeuralNetwork

logger = logging.getLogger("main_logger")
logging.basicConfig(filename="vk_bot.log", filemode="a",
                    format=f"%(levelname)s\t\t%(asctime)s\t\t%(message)s",
                    level=logging.INFO)


class StopEvent:
    ...


class Bot:
    def __init__(self, vk: vk_api.vk_api.VkApiMethod,
                 redis: Redis,
                 upload: vk_api.upload.VkUpload,
                 nn: WordNeuralNetwork,
                 n_threads=8):
        self.redis = redis
        self.vk = vk
        self.upload = upload
        self.nn = nn
        self.events = Queue()
        self.commands = {
            # commands for all users
            "/help": self.show_help,
            "/gs": self.get_synonyms,                   # get synonyms
            "/cp": self.create_postirony,               # create postirony
            "/cs": self.create_shakal,                  # create shakal
            "/cg": self.create_grain,                   # create grain
            "/ca": self.create_arabfunny,               # create arabfunny
            # in chats only
            "/gac": self.get_chance,                    # get answer chance
            "/glc": self.get_chance,                    # get ladno chance
            "/ghc": self.get_chance,                    # get huy chance
            "/gnc": self.get_chance,                    # get nu... chance
            # for chat admins only
            "/tac": self.toggle_access_chat_settings,   # toggle access
            "/ac": self.set_chance,                     # set answer chance
            "/lc": self.set_chance,                     # set ladno chance
            "/hc": self.set_chance,                     # set huy chance
            "/nc": self.set_chance,                     # set nu... chance
            "/s": self.show_settings,                   # settings
            # for bot admins only
            "/adm": self.admin_help,                    # help admins
            "/sa": self.set_admin,                      # set admin
            "/ga": self.get_admin,                      # get admin
            "/ia": self.is_admin,                       # is admin
            "/bb": self.bye_bye,                        # exit program
            # experimental
            "/csg": None,                               # create gif shakal
            "/cag": None,                               # create gif arabfunny
            # nn
            "/gaw": self.get_all_words,
            # other
            "other": self.send_answer                   # answer on simple message

        }
        self.threads = []
        self.n_threads = n_threads
        self.start()

    def start(self):
        for th in range(self.n_threads):
            event_checker = threading.Thread(target=self.check_event_type)
            self.threads.append(event_checker)
            event_checker.start()

    @staticmethod
    def check_stop(event):
        if event == StopEvent:
            exit()

    @staticmethod
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
            if message.get("fwd_messages", False):
                message = message.get("fwd_messages")[0]
            else:
                break
        return []

    def check_event_type(self):
        while True:
            try:
                for event in iter(self.events.get, None):
                    self.check_stop(event)
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        self.message_checker(event)
            except Exception:
                exception_checker()

    def message_checker(self, event: VkBotMessageEvent):
        message: str = event.obj.message["text"]
        peer_id = event.obj.message["peer_id"]
        if not message:
            return
        if message.startswith(MY_NAMES):
            for name in MY_NAMES:
                message = message.replace(name, '')
        message = message.lstrip().rstrip()
        command = "" if len(message.split()) < 1 else message.split()[0].lower()
        self.commands.get(command, self.commands.get("other"))(event, message, peer_id)

    def add_event_in_queue(self, event):
        self.events.put(event)

    def show_help(self, _, message, peer_id):
        if len(message.split()) == 1:
            if peer_id > MIN_CHAT_PEER_ID:
                help_data = json.loads(HELP_TEXT)["user_help"]["main_conversation"]
            else:
                help_data = json.loads(HELP_TEXT)["user_help"]["main_user"]
            help_text_all = help_data["text"]
            help_attachments = help_data["attachments"]
            help_keyboard = help_data["keyboard"]
            send_message(help_text_all, self.vk, peer_id=peer_id, attachments=help_attachments,
                         keyboard=help_keyboard)
        else:
            if message.split()[-1] in COMMANDS:
                command = message.split()[-1]
                help_data = json.loads(HELP_TEXT)["user_help"][command]
                help_text_command = help_data["text"]
                help_attachments = help_data["attachments"]
                help_keyboard = help_data["keyboard"]
                send_message(help_text_command, self.vk, peer_id=peer_id,
                             attachments=help_attachments, keyboard=help_keyboard)

    def get_synonyms(self, _, message, peer_id):
        def get_synonyms_refactored(words):
            synonyms = get_text_from_json_get_synonyms(get_synonyms(words))
            if synonyms:
                synonyms_refactored = f"Синонимы к слову \"{' '.join(words)}\":\n\n"
                for synonym in synonyms:
                    synonyms_refactored += tuple(synonym.keys())[0] + "\n"
                    if tuple(synonym.values())[0]:
                        synonyms_refactored += f"Подобные слову \"{tuple(synonym.keys())[0]}\":\n"
                        for mini_synonym in tuple(synonym.values())[0]:
                            synonyms_refactored += "&#4448;• " + mini_synonym + "\n"
                return synonyms_refactored
            else:
                return "Ничего не найдено"
        if len(message.split()) >= 2:
            synonyms_from_api = get_synonyms_refactored(message.split()[1:])
            send_message(synonyms_from_api, self.vk,  peer_id=peer_id)
        else:
            send_message("Ошибка: нет слова", self.vk, peer_id=peer_id)

    def create_postirony(self, _, message, peer_id):
        if len(message.split()) > 1:
            text_p = "".join(
                [symbol.lower() if random.choice((0, 1))
                 else symbol.upper() for symbol in " ".join(message.split()[1:])])
            send_message(text_p, self.vk, peer_id=peer_id)
        else:
            send_message("нЕт сЛОв", self.vk, peer_id=peer_id)

    def create_shakal(self, event, message, peer_id):
        def create_shakal_function(image_sh: BytesIO or str, factor_sh: int) -> str:
            """
            create shakal image from source image
            :param image_sh: bytes of image or file's name
            :param factor_sh: factor of image grain
            :return: name of file in /photos directory

            """
            name = "photos/{}.jpg" \
                .format(''.join(random.choice(string.ascii_uppercase
                                              + string.ascii_lowercase + string.digits) for _ in
                                range(16)))
            image_sh = Image.open(image_sh)
            start_size = image_sh.size
            image_sh.save(name)
            for i in range(factor_sh):
                image_sh = Image.open(name)
                image_sh = image_sh.resize((int(image_sh.size[0] / 1.1),
                                            int(image_sh.size[1] / 1.1)))
                size = image_sh.size
                image_sh.save(name, quality=5)
                if size[0] < 10 or size[1] < 10:
                    break

            image_sh = Image.open(name)
            image_sh = image_sh.resize(start_size)
            image_sh.save(name)
            return name
        photos = self.find_image(event)
        if photos:
            factor = 5
            if len(message.split()) > 1:
                if message.split()[-1].isdigit():
                    factor = int(message.split()[-1])
                else:
                    send_message("Степеь должна быть целым числом", self.vk, peer_id=peer_id)
                    return
            for image in photos:
                url = image["photo"]["sizes"][-1]["url"]
                img = urllib.request.urlopen(url).read()
                bytes_img = BytesIO(img)
                photo_bytes = create_shakal_function(bytes_img, factor)
                photo = self.upload.photo_messages(photos=[photo_bytes],
                                                   peer_id=peer_id)
                vk_photo_id = \
                    f"photo{photo[0]['owner_id']}_{photo[0]['id']}_{photo[0]['access_key']}"
                send_message("", self.vk, peer_id=peer_id, attachments=vk_photo_id)
                os.remove(photo_bytes)
        else:
            send_message("Прикрепи фото", self.vk, peer_id=peer_id)

    def create_grain(self, event, message, peer_id):
        def create_grain_function(image_gr: BytesIO or str, factor_sh: int) -> str:
            """
            create grain image from source image
            :param image_gr: bytes of image or file's name
            :param factor_sh: factor of image grain
            :return: name of file in /photos directory

            """
            image_gr = Image.open(image_gr)
            width = image_gr.size[0]
            height = image_gr.size[1]
            pix = image_gr.load()
            for i in range(width):
                for j in range(height):
                    random_factor = random.randint(-factor_sh, factor_sh)
                    r = pix[i, j][0] + random_factor
                    g = pix[i, j][1] + random_factor
                    b = pix[i, j][2] + random_factor
                    if r < 0:
                        r = 0
                    if g < 0:
                        g = 0
                    if b < 0:
                        b = 0
                    if r > 255:
                        r = 255
                    if g > 255:
                        g = 255
                    if b > 255:
                        b = 255
                    pix[i, j] = r, g, b
            name = "photos/{}.jpg" \
                .format(''.join(random.choice(string.ascii_uppercase
                                              + string.ascii_lowercase + string.digits) for _ in
                                range(16)))
            image_gr.save(name)
            return name

        photos = self.find_image(event)
        if photos:
            factor = 50
            if len(message.split()) > 1:
                if message.split()[-1].isdigit():
                    factor = int(message.split()[-1])
                else:
                    send_message("Степеь должна быть целым числом", self.vk, peer_id=peer_id)
                    return
            for image in photos:
                url = image["photo"]["sizes"][-1]["url"]
                img = urllib.request.urlopen(url).read()
                bytes_img = BytesIO(img)
                name_final_file = create_grain_function(bytes_img, factor)
                photo = self.upload.photo_messages(photos=[name_final_file],
                                                   peer_id=peer_id)
                vk_photo_id = \
                    f"photo{photo[0]['owner_id']}_{photo[0]['id']}_{photo[0]['access_key']}"
                send_message("", self.vk, peer_id=peer_id, attachments=vk_photo_id)
                os.remove(name_final_file)
        else:
            send_message("Прикрепи фото", self.vk, peer_id=peer_id)

    def create_arabfunny(self, event, message, peer_id):
        def create_arabfunny_function(image_ar: BytesIO or str, text_color: str = "black") -> tuple:
            """
            create arabic meme from source image
            :param image_ar: bytes of image or file's name
            :param text_color: english text of text
            :return: tuple like (name of file in /photos directory, text on mem)

            """
            image_ar = Image.open(image_ar)
            draw = ImageDraw.Draw(image_ar)
            text_ar = get_random_funny_wiki_page()
            only_symbols = get_only_symbols(text_ar)[::-1]
            size = image_ar.size[0], image_ar.size[1]
            font_size = size[1] // 6
            font = ImageFont.truetype(f"{FONTS_PATH}{ARABIC_FONT}", font_size,
                                      layout_engine=ImageFont.LAYOUT_BASIC)
            text_size = draw.textsize(only_symbols, font=font)
            x, y = (size[0] - text_size[0]) // 2, (size[1] - int((text_size[1])) - 2)
            while x <= 0 and font_size > 1:
                font_size -= 1
                font = ImageFont.truetype(f"{FONTS_PATH}{ARABIC_FONT}", font_size,
                                          layout_engine=ImageFont.LAYOUT_BASIC)
                text_size = draw.textsize(only_symbols, font=font)
                x = (size[0] - text_size[0]) // 2
            offset = 3
            if text_color not in TEXT_COLORS.keys():
                text_color = "black"
            shadow_color = TEXT_COLORS[text_color]

            for off in range(offset):
                draw.text((x - off, size[1] - int(text_size[1])), only_symbols, font=font,
                          fill=shadow_color)
                draw.text((x + off, size[1] - int(text_size[1])), only_symbols, font=font,
                          fill=shadow_color)
                draw.text((x, size[1] - int(text_size[1]) + off), only_symbols, font=font,
                          fill=shadow_color)
                draw.text((x, size[1] - int(text_size[1]) - off), only_symbols, font=font,
                          fill=shadow_color)
                draw.text(
                    (x - off, size[1] - int(text_size[1]) + off), only_symbols, font=font,
                    fill=shadow_color)
                draw.text(
                    (x + off, size[1] - int(text_size[1]) + off), only_symbols, font=font,
                    fill=shadow_color)
                draw.text(
                    (x - off, size[1] - int(text_size[1]) - off), only_symbols, font=font,
                    fill=shadow_color)
                draw.text(
                    (x + off, size[1] - int(text_size[1]) - off), only_symbols, font=font,
                    fill=shadow_color)
            draw.text(((size[0] - text_size[0]) // 2, (size[1] - int((text_size[1])))),
                      text=only_symbols, font=font, fill=text_color)
            name = "photos/{}.jpg" \
                .format(''.join(random.choice(string.ascii_uppercase
                                              + string.ascii_lowercase + string.digits) for _ in
                                range(16)))
            image_ar.save(name)
            return name, text_ar
        color = 0
        photos = self.find_image(event)
        if photos:
            if len(message.split()) > 1:
                color = message.split()[-1]
            for image in photos:
                url = max(image["photo"]["sizes"], key=lambda x: x["height"])["url"]
                img = urllib.request.urlopen(url).read()
                bytes_img = BytesIO(img)
                name_final_file, text = create_arabfunny_function(bytes_img, color)
                photo = self.upload.photo_messages(photos=[name_final_file],
                                                   peer_id=peer_id)
                vk_photo_id = \
                    f"photo{photo[0]['owner_id']}_{photo[0]['id']}_{photo[0]['access_key']}"
                send_message(text, self.vk, peer_id=peer_id, attachments=vk_photo_id)
                os.remove(name_final_file)
        else:
            send_message("Прикрепи фото", self.vk, peer_id=peer_id)

    def get_chance(self, _, message, peer_id):
        if peer_id > MIN_CHAT_PEER_ID:
            what = GET_COMMANDS.get(
                "" if len(message.split()) < 1 else message.split()[0].lower(), ""
            )
            chance = self.redis.get_chances(peer_id, params={what: True})
            send_message(f"Шанс {CHANCES_ONE_ANSWER[what]} равен "
                         f"{int(chance[what])}%", self.vk, peer_id=peer_id)
        else:
            send_message(f"Команда только для бесед", self.vk, user_id=peer_id)

    def set_chance(self, _, message, peer_id):
        if peer_id > MIN_CHAT_PEER_ID:
            what = SET_COMMANDS.get(
                "" if len(message.split()) < 1 else message.split()[0].lower(), ""
            )
            if len(message.split()) == 2:
                chance = message.split()[1]
                if chance.isdigit() and 0 <= int(chance) <= 100:
                    self.redis.change_chances(peer_id, params={what: int(chance)})
                    send_message(f"Шанс {CHANCES_ONE_ANSWER.get(what, '...')}"
                                 f" успешно изменен на {chance}%", self.vk, peer_id=peer_id)
                else:
                    send_message("Должно быть число от 0 до 100", self.vk, peer_id=peer_id)
            else:
                send_message("Добавьте шанс (от 0 до 100)", self.vk, peer_id=peer_id)
        else:
            send_message(f"Команда только для бесед", self.vk, peer_id=peer_id)

    def show_settings(self, _, __, peer_id):
        if peer_id > MIN_CHAT_PEER_ID:
            all_chances = self.redis.get_chances(peer_id, params={ANSWER_CHANCE: True,
                                                                  LADNO_CHANCE: True,
                                                                  HUY_CHANCE: True,
                                                                  NU_POLUCHAETSYA_CHANCE: True})
            who = self.redis.get_who_can_change_chances(peer_id)
            send_message("Настройки беседы:\n{}\n{}".format('\n'.join(
                [f'{CHANCES_ALL_SETTINGS[what]}: '
                 f'{int(chance)}%' for what, chance in
                 tuple(all_chances.items())]), WHO_CAN_TOGGLE_CHANCES.get(who)),
                self.vk, peer_id=peer_id, keyboard=json.loads(KEYBOARDS)["settings_keyboard"]
            )
        else:
            send_message(f"Команда только для бесед", self.vk, peer_id=peer_id)

    def toggle_access_chat_settings(self, event, _, peer_id):
        if peer_id > MIN_CHAT_PEER_ID:
            admins = get_admins_in_chat(peer_id, self.vk)
            if event.obj.message["from_id"] in admins:
                who = self.redis.toggle_access_chances(peer_id)
                send_message(WHO_CAN_TOGGLE_CHANCES.get(who), self.vk, peer_id=peer_id)
        else:
            send_message("Команда только для бесед", self.vk, peer_id=peer_id)

    def admin_help(self, _, __, peer_id):
        if not peer_id > MIN_CHAT_PEER_ID:
            level: int = self.redis.get_admin(peer_id)
            print(level)
            if level > 0:
                send_message(ADMIN_TEXT, self.vk, peer_id=peer_id)
            else:
                send_message("У вас нет доступа к данной команде", self.vk, peer_id=peer_id)

    def set_admin(self, _, message, peer_id):
        def set_admin_function(
                user_url: str,
                admin_access_level: int,
                vk_api_method: vk_api.vk_api.VkApiMethod
        ) -> str:
            """
            set admin's access for user
            :param user_url: user who need set admin's access for another user
            :param admin_access_level: level of admin's permissions
            :param vk_api_method: vk_api for find user's id via url
            :return: answer to message

            """
            user_url: int = get_user_id_via_url(user_url, vk_api_method)
            if user_url:
                if str(user_url) != CHIEF_ADMIN:
                    return self.redis.set_admin(user_url, admin_access_level)
                else:
                    return "Невозможно поменять уровень администрирования"
            return "Такого пользователя не существует"
        if not peer_id > MIN_CHAT_PEER_ID:
            if self.redis.get_admin(peer_id) == 5:
                if len(message.split()) == 3:
                    new_admin_id, access_level = message.split()[1:]
                    if not access_level.isdigit() or not (1 <= int(access_level) <= 5):
                        send_message("Недопустимый уровень пользователя", self.vk,
                                     peer_id=peer_id)
                        return
                    access_level = int(access_level)
                    answer = set_admin_function(new_admin_id, access_level, self.vk)
                    send_message(answer, self.vk, peer_id=peer_id)
                else:
                    send_message("Неправильный формат команды", self.vk, peer_id=peer_id)
            else:
                send_message("У вас нет прав для этой команды. "
                             "Минимальный уровень администрирования для данной команды: 5",
                             self.vk, peer_id=peer_id)

    def get_admin(self, _, __, peer_id):
        if not peer_id > MIN_CHAT_PEER_ID:
            if peer_id == int(CHIEF_ADMIN) or self.redis.get_admin(peer_id) == 5:
                admins = self.redis.get_all_admins()
                if admins:
                    admins_str = f"Всего админов: {len(admins)}\n"
                    for (id_temp, access_level_temp) in admins:
                        name = get_user_name(int(id_temp), self.vk)
                        admins_str += f"{'@id'}{id_temp} ({name}) - {access_level_temp}\n"
                    send_message(admins_str, self.vk, peer_id=peer_id)
                else:
                    send_message("Список пуст", self.vk, peer_id=peer_id)
            else:
                send_message("У вас нет прав для этой команды", self.vk, peer_id=peer_id)

    def is_admin(self, _, message, peer_id):
        if not peer_id > MIN_CHAT_PEER_ID:
            if self.redis.get_admin(peer_id):
                if len(message.split()) == 2:
                    admin_url = message.split()[-1]
                    admin_id = get_user_id_via_url(admin_url, self.vk)
                    if admin_id:
                        is_admin = self.redis.get_admin(admin_id)
                        if is_admin:
                            name = get_user_name(int(admin_id), self.vk)
                            send_message(f"@id{admin_id} ({name}) - Администратор уровня "
                                         f"{is_admin}",
                                         self.vk, peer_id=peer_id)
                        else:
                            send_message(f"@id{admin_id} - не администратор", self.vk,
                                         peer_id=peer_id)
                    else:
                        send_message("Неправильный id", self.vk, peer_id=peer_id)
                else:
                    send_message("Неправильный формат команды", self.vk, peer_id=peer_id)
            else:
                send_message("У вас нет прав для этой команды", self.vk, peer_id=peer_id)

    def bye_bye(self, _, __, peer_id):
        if not peer_id > MIN_CHAT_PEER_ID:
            if self.redis.get_admin(peer_id) >= 5:
                send_message("Завершаю работу...", self.vk, peer_id=peer_id)
                self.redis.exit_db()
                send_message("Закрыл базу", self.vk, peer_id=peer_id)

                if peer_id != int(CHIEF_ADMIN):
                    send_message(f"Завершаю работу по команде @id{peer_id}", self.vk,
                                 peer_id=int(CHIEF_ADMIN))
                send_message("Завершаю работу всей программы", self.vk, peer_id=peer_id)
                [self.add_event_in_queue(StopEvent) for _ in range(self.n_threads)]
                logging.info(f"exit by {peer_id} | uptime: ")
                exit(0)
            else:
                send_message("У вас нет доступа к данной команде", self.vk, peer_id=peer_id)

    def send_answer(self, event, message, peer_id):
        if not peer_id > MIN_CHAT_PEER_ID:
            old = self.redis.check_peer_id_in_db(peer_id)
            if not old:
                self.redis.add_peer_id(peer_id)
                send_message("Напиши /help, "
                             "чтобы узнать список команд", self.vk, peer_id=peer_id,
                             keyboard=json.loads(KEYBOARDS)["help_keyboard"])
            else:
                send_answer(message, self.vk, peer_id, self.redis)
        else:
            action = event.obj["message"].get("action", 0)
            if action:
                if action["type"] == "chat_invite_user" and \
                        action["member_id"] == -int(GROUP_ID):
                    self.redis.add_peer_id(peer_id)
                    send_message("Дайте права админа пожалуйста "
                                 "а то я вас не слышу я глухой",
                                 self.vk, peer_id=peer_id)
            else:
                old = self.redis.check_peer_id_in_db(peer_id)
                if not old:
                    self.redis.add_peer_id(peer_id)
                    self.redis.add_nn(peer_id)
                self.redis.append_words(peer_id, message.split())
                send_answer(message, self.vk, peer_id, self.redis)

    def get_all_words(self, event, message, peer_id):
        words = self.redis.get_words(peer_id)
        send_message(" ".join(words), self.vk, peer_id=peer_id)

