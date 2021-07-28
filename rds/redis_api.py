import random

import redis
from constants import CHIEF_ADMIN, MIN_CHAT_PEER_ID, ANSWER_CHANCE, LADNO_CHANCE, HUY_CHANCE, \
    NU_POLUCHAETSYA_CHANCE, \
    WHO_CAN_TOGGLE_CHANCES_TEXT, ADMIN_LEVELS, ADMINS_ONLY, ALL, STOP_WORDS


class RedisApi:
    # users --> peer_id -> level (hash) (int)
    #       `-> peer_id -> level
    # peer_id --> xy_chance -> chance;
    #         `-> tac -> who (hash) (int)
    # peer_id:word --> word_after -> chance (hash) (int)
    #              `-> word_after -> chance
    # peer_id:_all_ -> all_words (set)
    # peer_id:_start_ -> all_starts (set)
    # tokens --> token -> peer_id
    #        `-> token -> peer_id
    # connects --> peer_id1 -> peer_id2
    #          `-> peer_id2 -> peer_id1

    # get user             +
    # add user             +
    # get huy chance       +
    # set huy chance       +
    # get tac              +
    # set tac              +
    # set admin            +
    # get admin            +
    # add word
    # delete word
    # get word
    # get word's chance
    # get words after another word
    def __init__(self, host=None, password=None):
        self.redis = redis.Redis(password=password, host=host)
        self.chances = {ANSWER_CHANCE: 30, LADNO_CHANCE: 30, HUY_CHANCE: 30,
                        NU_POLUCHAETSYA_CHANCE: 30, WHO_CAN_TOGGLE_CHANCES_TEXT: 1}

    @staticmethod
    def decode_bytes(bytes_text: bytes):
        return bytes_text.decode("utf-8")

    def check_and_add_peer_id(self, peer_id: str):
        if not self.check_peer_id(peer_id):
            self.add_peer_id(peer_id)

    def add_peer_id(self, peer_id: str):
        if int(peer_id) > MIN_CHAT_PEER_ID:
            self.redis.hset(peer_id, HUY_CHANCE, 30)  # huy chance
            self.redis.hset(peer_id, WHO_CAN_TOGGLE_CHANCES_TEXT, ADMINS_ONLY)
            self.redis.hset(peer_id, ANSWER_CHANCE, 30)  # huy chance

        else:
            self.redis.hset(ADMIN_LEVELS, peer_id, 0)   # admin level: 0 - not admin

    def check_peer_id(self, peer_id: str):
        if int(peer_id) > MIN_CHAT_PEER_ID:
            return True if self.redis.hget(peer_id, HUY_CHANCE) else False
        else:
            return True if self.redis.hget(ADMIN_LEVELS, peer_id) else False

    def get_huy_chance(self, peer_id: str):
        self.check_and_add_peer_id(peer_id)
        if int(peer_id) > MIN_CHAT_PEER_ID:
            return int(self.redis.hget(peer_id, HUY_CHANCE))
        return -1

    def get_answer_chance(self, peer_id):
        self.check_and_add_peer_id(peer_id)
        if int(peer_id) > MIN_CHAT_PEER_ID:
            return int(self.redis.hget(peer_id, ANSWER_CHANCE))
        return -1

    def change_huy_chance(self, peer_id: str, chance: int):
        self.check_and_add_peer_id(peer_id)
        if int(peer_id) > MIN_CHAT_PEER_ID:
            self.redis.hset(peer_id, HUY_CHANCE, chance)

    def change_answer_chance(self, peer_id: str, chance: int):
        self.check_and_add_peer_id(peer_id)
        if int(peer_id) > MIN_CHAT_PEER_ID:
            self.redis.hset(peer_id, ANSWER_CHANCE, chance)

    def get_who_can_change_chances(self, peer_id):
        self.check_and_add_peer_id(peer_id)
        if int(peer_id) > MIN_CHAT_PEER_ID:
            who = self.redis.hget(peer_id, WHO_CAN_TOGGLE_CHANCES_TEXT)
            return int(who)

    def toggle_access_chances(self, peer_id: str):
        self.check_and_add_peer_id(peer_id)
        if int(peer_id) > MIN_CHAT_PEER_ID:
            who = 1 - int(self.redis.hget(peer_id, WHO_CAN_TOGGLE_CHANCES_TEXT))
            self.redis.hset(peer_id, WHO_CAN_TOGGLE_CHANCES_TEXT, who)
            return who

    def set_admin(self, peer_id, level):
        self.check_and_add_peer_id(peer_id)
        if 0 <= level <= 5:
            self.redis.hset(ADMIN_LEVELS, peer_id, level)
            return f"Для @id{peer_id} поставлен уровень доступа {level}"

    def get_admin(self, peer_id):
        self.check_and_add_peer_id(peer_id)
        return int(self.redis.hget(ADMIN_LEVELS, peer_id))

    def get_all_admins(self):
        levels = self.redis.hgetall(ADMIN_LEVELS)
        if levels:
            return dict(filter(lambda y: y[1] > 0,
                               map(lambda x: (int(x[0]), int(x[1])), levels.items())))

    def add_text(self, peer_id: str, text: iter):
        if int(peer_id) <= MIN_CHAT_PEER_ID:
            return
        self.check_and_add_peer_id(peer_id)
        if not text:
            return
        elif len(text) == 1:
            if text[0] not in STOP_WORDS:
                self.redis.sadd(f"{peer_id}:_start_", text[0])
                self.redis.sadd(f"{peer_id}:_all_", text[0])
                self.redis.hset(f"{peer_id}:{text[0]}", "///end", 1)
            return
        for word, word_after in zip(text[:-1], text[1:]):
            if word in STOP_WORDS:
                continue
            has_word_after = self.redis.hget(f"{peer_id}:{word}", word_after)
            if not has_word_after:
                self.redis.hset(f"{peer_id}:{word}", word_after, 1)
            else:
                self.redis.hincrby(f"{peer_id}:{word}", word_after)
            self.redis.sadd(f"{peer_id}:_all_", word)
        if text[0] not in STOP_WORDS:
            self.redis.sadd(f"{peer_id}:_start_", text[0])
        if text[-1] not in STOP_WORDS:
            self.redis.sadd(f"{peer_id}:_all_", text[-1])
            self.redis.hset(f"{peer_id}:{text[-1]}", "///end", 1)

    def generate_text(self, peer_id: str):
        if int(peer_id) <= MIN_CHAT_PEER_ID:
            return
        self.check_and_add_peer_id(peer_id)
        word = self.redis.srandmember(f"{peer_id}:_start_")
        if not word:
            return ""
        start = self.decode_bytes(word)
        sent = [start]
        n_max = random.randint(4, 20)
        n = 0
        while start != "///end":
            if n > n_max:
                break
            words = tuple(map(lambda x:
                              (self.decode_bytes(x[0]), int(x[1])),
                              self.redis.hgetall(f"{peer_id}:{start}").items()))
            start = random.choices(tuple(map(lambda x: x[0], words)),
                                   weights=tuple(map(lambda x: x[1], words)))[0]
            sent.append(start)
        if sent[-1] == "///end":
            sent.pop(-1)
        return " ".join(sent)

    def clear_chat(self, peer_id: str):
        words = tuple(map(self.decode_bytes, self.redis.smembers(f"{peer_id}:_all_")))
        for word in words:
            self.redis.delete(f"{peer_id}:{word}")
        self.redis.delete(f"{peer_id}:_all_")

    def get_count_words(self, peer_id: str):
        return self.redis.scard(f"{peer_id}:_all_")

    def get_words_after_that(self, peer_id: str, word):
        words = dict(map(lambda x: (self.decode_bytes(x[0]), int(x[1])),
                     self.redis.hgetall(f"{peer_id}:{word}").items()))
        if words.get("///end"):
            words.pop("///end")
        return words

    def delete_words_from_text(self, peer_id: str, words: iter):
        for word in words:
            self.redis.delete(f"{peer_id}:{word}")
        self.redis.srem(f"{peer_id}:_all_", *words)
        for i in tuple(map(self.decode_bytes, self.redis.smembers(f"{peer_id}:_all_"))):
            self.redis.hdel(f"{peer_id}:{i}", *words)

    def update_chat(self, peer_id: str):
        self.change_answer_chance(peer_id, 30)
        self.change_huy_chance(peer_id, 30)
        if self.get_who_can_change_chances(peer_id) == ALL:
            self.toggle_access_chances(peer_id)

    def add_token(self, peer_id: str, token: str):
        self.redis.hset("tokens", token, peer_id)

    def get_peer_id_by_token(self, token: str):
        peer_id = self.redis.hget("tokens", token)
        if peer_id:
            return peer_id.decode("UTF-8")
        return None

    def connect(self, peer_id1: str, peer_id2: str):
        self.redis.hset("connects", peer_id1, peer_id2)
        self.redis.hset("connects", peer_id2, peer_id1)

    def get_connected_chat(self, peer_id: str):
        peer_id = self.redis.hget("connects", peer_id)
        if peer_id:
            return peer_id.decode("UTF-8")
        return None

    def disconnect_chats(self, peer_id1: str, peer_id2: str):
        self.redis.hdel("connects", peer_id1, peer_id2)
