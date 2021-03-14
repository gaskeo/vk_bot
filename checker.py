import logging

import threading
from queue import Queue

import time
import datetime
import random
from io import BytesIO
import string
import json
from transliterate import translit

from PIL import Image, ImageDraw, ImageFont, JpegImagePlugin
import cv2

from vk_api.bot_longpoll import VkBotMessageEvent, VkBotEventType
from vk_api import vk_api, upload
import urllib.request

from rds.redis_api import RedisApi
from speaker import Speaker
from yandex.yandex_api import get_synonyms, get_text_from_json_get_synonyms

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
    StopEvent, get_main_pos, generate_huy_word

logger = logging.getLogger("main_logger")
logging.basicConfig(filename="vk_bot.log", filemode="a",
                    format=f"%(levelname)s\t\t%(asctime)s\t\t%(message)s",
                    level=logging.INFO)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


class Bot:
    def __init__(self, vk: vk_api.VkApiMethod,
                 redis: RedisApi,
                 upl: upload.VkUpload,
                 n_threads=8):
        self.redis = redis
        self.vk = vk
        self.upload = upl
        self.events = Queue()
        self.uptime = time.time()
        self.speaker = Speaker(redis)
        self.commands = {
            # commands for all users
            "/": self.redo_command,
            "/help": self.show_help,
            "/gs": self.get_synonyms,  # get synonyms
            "/cp": self.create_postirony,  # create postirony
            "/cs": self.create_shakal,  # create shakal
            "/cg": self.create_grain,  # create grain
            "/ca": self.create_arabfunny,  # create arabfunny
            "/cd": self.create_dab,
            "/ut": self.get_uptime,
            "/a": self.alive,
            # in chats only
            "/gac": self.get_chance,  # get answer chance
            "/ghc": self.get_chance,  # get huy chance
            "/gc": self.get_count_words,
            # "/gsw": self.get_similarity_words,
            "/g": self.generate_speak,
            "/at": self.get_words_after_that,
            "/peer": self.get_peer,
            # for chat admins only
            "/tac": self.toggle_access_chat_settings,  # toggle access
            "/ac": self.set_chance,  # set answer chance
            "/hc": self.set_chance,  # set huy chance
            "/s": self.show_settings,  # settings
            "/clear": self.clear_chat_speaker,
            "/update": self.update_chat,
            "/dt": self.delete_this,
            # "/dsw": self.clear_similarity_words,
            # for bot admins only
            "/adm": self.admin_help,  # help admins
            "/sa": self.set_admin,  # set admin
            "/ga": self.get_admin,  # get admin
            "/ia": self.is_admin,  # is admin
            "/bb": self.bye_bye,  # exit program
            "/th": self.alive_threads,
            # experimental
            "/csg": None,  # create gif shakal
            "/cag": None,  # create gif arabfunny
            # other
            "other": self.send_answer,  # answer on simple message
            # archive
            "/glc": self.archived,  # get ladno chance
            "/gnc": self.archived,  # get nu... chance
            "/lc": self.archived,  # set ladno chance
            "/nc": self.archived,  # set nu... chance
            "/test": self.test
        }
        self.threads = {}
        self.n_threads = n_threads
        self.start()

    @staticmethod
    def logger(event):
        try:
            log = u"{} IN {}: {} | atts: {}".format(event.obj.message["from_id"],
                                                    event.obj.message["peer_id"],
                                                    translit(event.obj.message["text"],
                                                             "ru", reversed=True
                                                             ).encode('unicode-escape'),
                                                    event.obj.message["attachments"]
                                                    )
            logger.info(log)
        except UnicodeEncodeError:
            pass

    def start(self):
        for th in range(self.n_threads):
            event_checker = threading.Thread(target=self.check_event_type)
            event_checker.setName(str(th + 1))
            self.threads[event_checker.name] = 1
            event_checker.start()
            logger.info(f"thread {event_checker.name} started")

    @staticmethod
    def check_stop(event):
        if event == StopEvent:
            logger.info(f"thread {threading.currentThread().name} stopped")
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
            elif message.get("fwd_messages", False):
                message = message.get("fwd_messages")[0]
            else:
                break
        return []

    def check_event_type(self):
        while True:
            try:
                for event in iter(self.events.get, None):
                    self.threads[threading.currentThread().name] = 0
                    self.check_stop(event)
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        self.message_checker(event)
                    self.threads[threading.currentThread().name] = 1
            except Exception:
                exception_checker()

    def message_checker(self, event: VkBotMessageEvent):
        self.logger(event)
        message: str = event.obj.message["text"]
        peer_id = event.obj.message["peer_id"]
        action = event.obj.message.get("action", None)
        if action:
            action_type = action["type"]
            if action_type == "chat_invite_user" and action["member_id"] == -int(GROUP_ID):
                self.redis.add_peer_id(str(peer_id))
                send_message("дайте админку пжпж", self.vk, peer_id)
        if not message:
            return
        if message.startswith(MY_NAMES):
            for name in MY_NAMES:
                message = message.replace(name, '')
        message = message.lstrip().rstrip()

        command = "" if len(message.split()) < 1 else message.split()[0].lower()
        c: callable = self.commands.get(command, self.commands.get("other"))
        c(event, message, peer_id)

    def add_event_in_queue(self, event):
        self.events.put(event)

    # /
    def redo_command(self, event, _, peer_id):
        if event.obj.message.get("reply_message", False):
            message = event.obj.message["reply_message"]
            message["peer_id"] = peer_id
            message["out"] = 0
            message["fwd_messages"] = []
            message["important"] = False
            message["random_id"] = 0
            message["is_hidden"] = False
            raw = {'type': 'message_new',
                   'object': {'message': message},
                   'client_info': {
                       'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link',
                                          'intent_subscribe', 'intent_unsubscribe'],
                       'keyboard': True,
                       'inline_keyboard': True,
                       'carousel': False,
                       'lang_id': 0
                   },
                   'group_id': int(GROUP_ID),
                   }
            e = VkBotMessageEvent(raw)
            self.add_event_in_queue(e)
        else:
            send_message("Ответь на сообщение с командой для ее повтора", self.vk, peer_id)

    # /help
    def show_help(self, event, message, peer_id):
        if len(message.split()) == 1:
            help_template = None
            if peer_id > MIN_CHAT_PEER_ID:
                help_data = json.loads(HELP_TEXT)["user_help"]["main_conversation"]
                help_text_all = help_data["text"]
                help_keyboard = help_data["keyboard"]
            else:
                help_data = json.loads(HELP_TEXT)["user_help"]["main_user"]
                if event.obj["client_info"].get("carousel", False):
                    help_template = help_data["template"]
                    help_text_all = help_data["text_template"]
                    help_keyboard = help_data["keyboard_template"]
                else:
                    help_text_all = help_data["text_no_template"]
                    help_keyboard = help_data["keyboard_no_template"]
            help_attachments = help_data["attachments"]
            send_message(help_text_all, self.vk, peer_id=peer_id, attachments=help_attachments,
                         keyboard=help_keyboard, template=help_template)
        else:
            if message.split()[-1] in json.loads(HELP_TEXT)["user_help"]:
                command = message.split()[-1]
                help_data = json.loads(HELP_TEXT)["user_help"][command]
                help_text_command = help_data["text"]
                help_attachments = help_data["attachments"]
                help_keyboard = help_data["keyboard"]
                send_message(help_text_command, self.vk, peer_id=peer_id,
                             attachments=help_attachments, keyboard=help_keyboard)

    # /gs
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
            send_message(synonyms_from_api, self.vk, peer_id=peer_id)
        else:
            send_message("Ошибка: нет слова", self.vk, peer_id=peer_id)

    # /cp
    def create_postirony(self, event, message, peer_id):
        if len(message.split()) > 1:
            text_p = "".join(
                [(symbol.lower() + (" " if symbol in "*@" else "")) if random.choice((0, 1))
                 else symbol.upper() + (" " if symbol in "*@" else "")
                 for symbol in " ".join(message.split()[1:])])
            send_message(text_p, self.vk, peer_id=peer_id)
        else:
            if event.obj.message.get("reply_message", False):
                message = event.obj.message["reply_message"]["text"]
                if len(message.split()) > 0:
                    text_p = "".join(
                        [(symbol.lower() + (" " if symbol in "*@" else "")) if random.choice((0, 1))
                         else symbol.upper() + (" " if symbol in "*@" else "")
                         for symbol in " ".join(message.split())])
                    send_message(text_p, self.vk, peer_id=peer_id)
                else:
                    send_message("нЕт сЛОв", self.vk, peer_id=peer_id)

    # /cs
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
            for i in range(factor_sh):
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
                url = max(image["photo"]["sizes"], key=lambda x: x["width"])["url"]
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

    # /cg
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
                url = max(image["photo"]["sizes"], key=lambda x: x["width"])["url"]
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

    # ca
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
                url = max(image["photo"]["sizes"], key=lambda x: x["width"])["url"]
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

    def create_dab(self, event, _, peer_id):
        def create_dab_function(image_dab: BytesIO or str) -> str:
            def create_rect():
                def check_compatibility(s: tuple):
                    rw = abs(s[2] - s[0])
                    rh = abs(s[3] - s[1])
                    dr = dab_w / dab_h
                    pr = rw / rh
                    return abs(dr - pr)

                def resize(dw, dh):
                    if dw + start[0] > ds[0]:
                        dh = int((ds[0] / dw) * dh) - coef - coef
                        dw = ds[0] - coef - coef
                    if dh + start[1] > ds[1]:
                        dw = int((ds[1] / dh) * dw) - coef - coef
                        dh = ds[1] - coef - coef
                    return dw, dh

                def distance_to_rangle(s: tuple):
                    return ((s[0] - rangle[0]) ** 2 + (s[1] - rangle[1]) ** 2) ** 0.5

                sizes = {
                    # 0 1
                    # 2 3
                    (0, 0, size[0], y): 3,   # top
                    (0, 0, x, size[1]): 3,  # left
                    (0, y + h, size[0], size[1]): 1,  # bottom
                    (x + w, 0, size[0], size[1]): 2   # right
                }
                r = (w + 60) // 2
                dab: JpegImagePlugin.JpegImageFile = Image.open(second_image)
                dab_w, dab_h = dab.size
                where = min(tuple(sizes.keys()), key=check_compatibility)
                coef = int(abs(where[2] - where[0]) * 0.2)
                start = (where[0] + coef, where[1] + coef)
                angle = sizes[where]
                ds = [abs(where[2] - where[0]), abs(where[3] - where[1])]
                dab_w, dab_h = resize(dab_w, dab_h)
                angles = (
                             (center[0] - r * (2 ** 0.5 / 2), (center[1] - r * (2 ** 0.5 / 2))),
                             (center[0] + r * (2 ** 0.5 / 2), (center[1] - r * (2 ** 0.5 / 2))),
                             (center[0] - r * (2 ** 0.5 / 2), (center[1] + r * (2 ** 0.5 / 2))),
                             (center[0] + r * (2 ** 0.5 / 2), (center[1] + r * (2 ** 0.5 / 2)))
                )
                if angle == 3:
                    rangle = start[0] + dab_w, start[1] + dab_h
                elif angle == 1:
                    rangle = start[0] + dab_w, start[1]
                else:
                    rangle = start[0], start[1] + dab_h
                cangle = min(angles, key=distance_to_rangle)
                dab = dab.resize((dab_w, dab_h))
                image_dab.paste(dab, start)
                draw.rectangle((start, (start[0] + dab_w, start[1] + dab_h)),
                               outline=(255, 0, 0), width=5)
                draw.line((rangle, cangle), width=5, fill=(255, 0, 0))
                image_dab.save(name)

            name = "photos/{}.jpg".format(''.join(
                random.choice(
                    string.ascii_uppercase + string.ascii_lowercase + string.digits
                ) for _ in range(16)))
            with open(name, "wb") as dfn:
                dfn.write(image_dab.getbuffer())
            image_dab = Image.open(image_dab)
            size = image_dab.size
            draw = ImageDraw.Draw(image_dab)
            image_cv2 = cv2.imread(name)
            image_cv2 = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(image_cv2, 1.1, 19)
            if len(faces):
                x, y, w, h = faces[0]
            else:
                w = h = random.randint(int(size[0] * 0.1), int(size[0] * 0.5))
                x, y = random.randint(w, size[0] - w), random.randint(h, size[0] - h)
            draw.ellipse(((x - 30, y - 30), (x + w + 30, y + h + 30)), outline=(255, 0, 0),
                         width=5)
            center = (2 * x + w) // 2, (2 * y + h) // 2
            create_rect()
            return name

        photos = self.find_image(event)
        if len(photos) == 2:
            image, second_image = photos
        elif len(photos) == 1:
            image = photos[0]
            second_image = None
        else:
            send_message("Прикрепи 1 или 2 фото", self.vk, peer_id=peer_id)
            return
        if second_image:
            url = max(second_image["photo"]["sizes"], key=lambda x: x["width"])["url"]
            img = urllib.request.urlopen(url).read()
            second_image = BytesIO(img)
            dab_name = "photos/{}.jpg" \
                .format(''.join(random.choice(string.ascii_uppercase
                                              + string.ascii_lowercase + string.digits)))
            with open(dab_name, "wb") as f:
                f.write(bytes(second_image.getbuffer()))
            second_image = dab_name
        else:
            second_image = "photos/examples/dab.jpg"
        url = max(image["photo"]["sizes"], key=lambda x: x["width"])["url"]
        img = urllib.request.urlopen(url).read()
        bytes_img = BytesIO(img)
        photo_bytes = create_dab_function(bytes_img)
        photo = self.upload.photo_messages(photos=[photo_bytes],
                                           peer_id=peer_id)
        vk_photo_id = \
            f"photo{photo[0]['owner_id']}_{photo[0]['id']}_{photo[0]['access_key']}"
        send_message("", self.vk, peer_id=peer_id, attachments=vk_photo_id)
        os.remove(photo_bytes)
        if second_image != "photos/examples/dab.jpg":
            os.remove(second_image)

    # /ut
    def get_uptime(self, _, __, peer_id):
        send_message("я живу уже "
                     f"{str(datetime.timedelta(seconds=int(time.time() - self.uptime)))}",
                     self.vk, peer_id)

    # /gac /ghc...
    def get_chance(self, _, message, peer_id):
        if peer_id > MIN_CHAT_PEER_ID:
            what = GET_COMMANDS.get(
                "" if len(message.split()) < 1 else message.split()[0].lower(), ""
            )
            if what == ANSWER_CHANCE:
                chance = self.redis.get_answer_chance(str(peer_id))
            elif what == HUY_CHANCE:
                chance = self.redis.get_huy_chance(str(peer_id))
            else:
                send_message("эта команда была выпилена в марте 21 года... помянем",
                             self.vk, peer_id)
                return
            send_message(f"Шанс {CHANCES_ONE_ANSWER[what]} равен "
                         f"{chance}%", self.vk, peer_id=peer_id)
        else:
            send_message(f"Команда только для бесед", self.vk, peer_id=peer_id)

    # /gcw
    def get_count_words(self, _, __, peer_id):
        c = str(self.speaker.get_count_words(peer_id))
        if c:
            send_message(f"количество слов: {c}", self.vk, peer_id)

    # /g
    def generate_speak(self, _, __, peer_id):
        message = self.speaker.generate_text(peer_id)
        if message:
            send_message(message, self.vk, peer_id)

    # /at
    def get_words_after_that(self, event, message, peer_id):
        def send_ans():
            if "///end" in words:
                words.remove("///end")
            if not words:
                send_message("ничего нет", self.vk, peer_id)
                return
            send_message((f"после {message} идет:\n" +
                          "\n".join(("- " + i for i in words))), self.vk, peer_id)

        message = message.replace("/at", "").strip()
        if not message or message == " ":
            if event.obj.message.get("reply_message", False):
                message = event.obj.message["reply_message"]["text"]
                if len(message.split()) > 0:
                    words = list(self.speaker.get_words_after_that(peer_id, message).keys())
                    send_ans()
                    return
        words = list(self.speaker.get_words_after_that(peer_id, message).keys())
        send_ans()

    # /peer
    def get_peer(self, _, __, peer_id):
        send_message(f"peer_id: {str(peer_id)}", self.vk, peer_id)

    # /a
    def alive(self, _, __, peer_id):
        send_message("я не лежу", self.vk, peer_id)

    # /tac
    def toggle_access_chat_settings(self, event, _, peer_id):
        if peer_id > MIN_CHAT_PEER_ID:
            admins = get_admins_in_chat(peer_id, self.vk)
            if event.obj.message["from_id"] in admins:
                who = self.redis.toggle_access_chances(str(peer_id))
                send_message(WHO_CAN_TOGGLE_CHANCES.get(who), self.vk, peer_id=peer_id)
        else:
            send_message("Команда только для бесед", self.vk, peer_id=peer_id)

    # /ac / lc...
    def set_chance(self, event, message, peer_id):
        if peer_id > MIN_CHAT_PEER_ID:
            what = SET_COMMANDS.get(
                "" if len(message.split()) < 1 else message.split()[0].lower(), ""
            )
            if what not in (ANSWER_CHANCE, HUY_CHANCE):
                if what in (LADNO_CHANCE, NU_POLUCHAETSYA_CHANCE):
                    send_message("эта команда была выпилена в марте 21 года... помянем",
                                 self.vk, peer_id)
                return
            if len(message.split()) == 2:
                admins = get_admins_in_chat(peer_id, self.vk)
                if event.obj.message["from_id"] in admins or \
                        not self.redis.get_who_can_change_chances(str(peer_id)):
                    chance = message.split()[1]
                    if chance.isdigit() and 0 <= int(chance) <= 100:
                        if what == ANSWER_CHANCE:
                            self.redis.change_answer_chance(str(peer_id), int(chance))
                        elif what == HUY_CHANCE:
                            self.redis.change_huy_chance(str(peer_id), int(chance))
                        send_message(f"Шанс {CHANCES_ONE_ANSWER.get(what, '...')}"
                                     f" успешно изменен на {chance}%", self.vk, peer_id=peer_id)
                    else:
                        send_message("Должно быть число от 0 до 100", self.vk, peer_id=peer_id)
            else:
                send_message("Добавьте шанс (от 0 до 100)", self.vk, peer_id=peer_id)
        else:
            send_message(f"Команда только для бесед", self.vk, peer_id=peer_id)

    # /s
    def show_settings(self, _, __, peer_id):
        if peer_id > MIN_CHAT_PEER_ID:
            all_chances = {
                HUY_CHANCE: self.redis.get_huy_chance(str(peer_id)),
                ANSWER_CHANCE: self.redis.get_answer_chance(str(peer_id))
            }
            who = self.redis.get_who_can_change_chances(str(peer_id))
            send_message("Настройки беседы:\n{}\n{}".format('\n'.join(
                [f'{CHANCES_ALL_SETTINGS[what]}: '
                 f'{int(chance)}%' for what, chance in
                 tuple(all_chances.items())]), WHO_CAN_TOGGLE_CHANCES.get(who)),
                self.vk, peer_id=peer_id, keyboard=json.loads(KEYBOARDS)["settings_keyboard"]
            )
        else:
            send_message(f"Команда только для бесед", self.vk, peer_id=peer_id)

    # /clear
    def clear_chat_speaker(self, event, _, peer_id):
        if peer_id > MIN_CHAT_PEER_ID:
            admins = get_admins_in_chat(peer_id, self.vk)
            if event.obj.message["from_id"] in admins:
                self.speaker.clear_chat(peer_id)
                send_message("слова очищены", self.vk, peer_id)
            else:
                send_message("чел ты не админ...", self.vk, peer_id)

    # /u
    def update_chat(self, event, _, peer_id):
        if peer_id > MIN_CHAT_PEER_ID:
            admins = get_admins_in_chat(peer_id, self.vk)
            if event.obj.message["from_id"] in admins:
                self.redis.update_chat(str(peer_id))
        else:
            send_message("Команда только для бесед", self.vk, peer_id=peer_id)

    # /dt
    def delete_this(self, event, message, peer_id):
        admins = get_admins_in_chat(peer_id, self.vk)
        if event.obj.message["from_id"] in admins:
            if len(message.split()) > 1:
                self.speaker.delete_words(peer_id, message)
                send_message(f"очищены слова: {message[3:]}", self.vk, peer_id)
            else:
                if event.obj.message.get("reply_message", False):
                    message = event.obj.message["reply_message"]["text"]
                    if len(message.split()) > 0:
                        self.speaker.delete_words(peer_id, message)
                        send_message(f"очищены слова: {message[3:]}", self.vk, peer_id)
                else:
                    send_message("ответь на сообщение или напиши текст после команды",
                                 self.vk, peer_id)
        else:
            send_message("чел ты не админ...", self.vk, peer_id)

    # # /gsw
    # def get_similarity_words(self, _, __, peer_id):
    #     similar_words = self.speaker.get_similar_word(peer_id)
    #     n = len(similar_words)
    #     if similar_words:
    #         similar_words = ' | '.join(tuple(
    #             map(lambda x: ' и '.join(x), similar_words)))
    #         send_message(f"похожие слова (всего: {n}):\n{similar_words[:500]}", self.vk, peer_id)
    #     else:
    #         send_message("нет похожих слов", self.vk, peer_id)

    # /csw
    # def clear_similarity_words(self, event, _, peer_id):
    #     admins = get_admins_in_chat(peer_id, self.vk)
    #     if event.obj.message["from_id"] in admins:
    #         words = self.speaker.clear_similar_word(peer_id)
    #         send_message(f"удалено слов: {len(words)}", self.vk, peer_id)
    #     else:
    #         send_message("чел ты не админ...", self.vk, peer_id)

    # /adm
    def admin_help(self, _, __, peer_id):
        if not peer_id > MIN_CHAT_PEER_ID:

            level: int = self.redis.get_admin(str(peer_id))
            if level > 0:
                send_message(ADMIN_TEXT, self.vk, peer_id=peer_id)
            else:
                send_message("У вас нет доступа к данной команде", self.vk, peer_id=peer_id)

    # /sa
    def set_admin(self, _, message, peer_id):
        def set_admin_function(
                user_url: str,
                admin_access_level: int,
                vk_api_method: vk_api.VkApiMethod
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
                    return self.redis.set_admin(str(user_url), admin_access_level)
                else:
                    return "Невозможно поменять уровень администрирования"
            return "Такого пользователя не существует"

        if not peer_id > MIN_CHAT_PEER_ID:
            if self.redis.get_admin(str(peer_id)) == 5:
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

    # /ga
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

    # /ia
    def is_admin(self, _, message, peer_id):
        if not peer_id > MIN_CHAT_PEER_ID:
            if self.redis.get_admin(str(peer_id)):
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

    # /bb
    def bye_bye(self, _, __, peer_id):
        if not peer_id > MIN_CHAT_PEER_ID:
            if self.redis.get_admin(peer_id) >= 5:
                send_message("Завершаю работу...", self.vk, peer_id=peer_id)
                self.redis.redis.save()
                send_message("Закрыл базу", self.vk, peer_id=peer_id)

                if peer_id != int(CHIEF_ADMIN):
                    send_message(f"Завершаю работу по команде @id{peer_id}", self.vk,
                                 peer_id=int(CHIEF_ADMIN))
                send_message("Завершаю работу всей программы", self.vk, peer_id=peer_id)
                [self.add_event_in_queue(StopEvent) for _ in range(self.n_threads)]
                logging.info(f"exit by {peer_id} | uptime: {int(time.time() - self.uptime)}s")
                logger.info(f"thread {threading.currentThread().name} stopped")
                exit(0)
            else:
                send_message("У вас нет доступа к данной команде", self.vk, peer_id=peer_id)

    # /th
    def alive_threads(self, _, __, peer_id):
        if not peer_id > MIN_CHAT_PEER_ID:
            if self.redis.get_admin(peer_id) >= 5:
                threads = "тред " + \
                          '\nтред '.join((y[0] for y in
                                          tuple(filter(lambda x: x[1] == 1, self.threads.items()))))
                send_message(f"живые треды (из {self.n_threads}):\n{threads}", self.vk, peer_id)

    def send_answer(self, event, message, peer_id):
        if not peer_id > MIN_CHAT_PEER_ID:
            old = self.redis.check_peer_id(str(peer_id))
            if not old:
                self.redis.add_peer_id(str(peer_id))
                send_message("Напиши /help, "
                             "чтобы узнать список команд", self.vk, peer_id=peer_id,
                             keyboard=json.loads(KEYBOARDS)["help_keyboard"])
            else:
                send_message("в лс делаю только "
                             "смешнявки, отвечаю в беседе",
                             self.vk, peer_id)
        else:
            action = event.obj["message"].get("action", 0)
            if action:
                if action["type"] == "chat_invite_user" and \
                        action["member_id"] == -int(GROUP_ID):
                    self.redis.add_peer_id(str(peer_id))
                    send_message("Дайте права админа пожалуйста "
                                 "а то я вас не слышу я глухой",
                                 self.vk, peer_id=peer_id)
            else:
                self.speaker.add_words(peer_id, message)
                what = send_answer(message, chances={
                    ANSWER_CHANCE: self.redis.get_answer_chance(str(peer_id)),
                    HUY_CHANCE: self.redis.get_huy_chance(str(peer_id))
                })
                if what == ANSWER_CHANCE:
                    text = self.speaker.generate_text(peer_id)
                    if text:
                        send_message(text, self.vk, peer_id)
                elif what == HUY_CHANCE:
                    send_message(generate_huy_word(get_main_pos(message)), self.vk, peer_id)

    def archived(self, _, __, peer_id):
        send_message("данная команда была удалена...", self.vk, peer_id)

    def test(self, _, __, ___):
        ...
