import redis
from constants import *

ADMIN_LEVELS = "admin_levels"
WHO_CAN_TOGGLE_CHANCES_TEXT = "who_can_change_chances"


class Redis:
    def __init__(self):
        self.redis = redis.Redis()
        self.chances = {ANSWER_CHANCE: 30, LADNO_CHANCE: 30, HUY_CHANCE: 30,
                        NU_POLUCHAETSYA_CHANCE: 30, WHO_CAN_TOGGLE_CHANCES_TEXT: 1}

    @staticmethod
    def decode_bytes(bytes_text: bytes):
        return bytes_text.decode("utf-8")

    def add_peer_id(self, peer_id):
        if peer_id > MIN_CHAT_PEER_ID:
            for chance, value in self.chances.items():
                self.redis.hset(chance, peer_id, value)
        else:
            self.redis.hset(ADMIN_LEVELS, peer_id, 0)

    def check_peer_id_in_db(self, peer_id):
        if peer_id > MIN_CHAT_PEER_ID:
            return True if self.redis.hget(ANSWER_CHANCE, peer_id) else False
        else:
            return True if self.redis.hget(ADMIN_LEVELS, peer_id) else False

    def get_chances(self, peer_id, params: dict):
        if not self.check_peer_id_in_db(peer_id):
            self.add_peer_id(peer_id)

        if peer_id > MIN_CHAT_PEER_ID:
            chances = {}
            for param, value in params.items():
                if param in self.chances and value:
                    chances[param] = int(self.redis.hget(param, peer_id))
            return chances
        return {}

    def change_chances(self, peer_id, params: dict):
        if not self.check_peer_id_in_db(peer_id):
            self.add_peer_id(peer_id)

        if peer_id > MIN_CHAT_PEER_ID:
            for param, value in params.items():
                if param in self.chances and 0 <= value <= 100:
                    self.redis.hset(param, peer_id, value)

    def get_who_can_change_chances(self, peer_id):
        if not self.check_peer_id_in_db(peer_id):
            self.add_peer_id(peer_id)

        if peer_id > MIN_CHAT_PEER_ID:
            who = self.redis.hget(WHO_CAN_TOGGLE_CHANCES_TEXT, peer_id)
            return int(who) if who else None

    def toggle_access_chances(self, peer_id):
        if not self.check_peer_id_in_db(peer_id):
            self.add_peer_id(peer_id)

        who = 1 - int(self.redis.hget(WHO_CAN_TOGGLE_CHANCES_TEXT, peer_id))
        self.redis.hset(WHO_CAN_TOGGLE_CHANCES_TEXT, peer_id, who)
        return who

    def set_admin(self, peer_id, level):
        if not self.check_peer_id_in_db(peer_id):
            self.add_peer_id(peer_id)

        if 0 <= level <= 5:
            self.redis.hset(ADMIN_LEVELS, peer_id, level)

    def get_admin(self, peer_id):
        if not self.check_peer_id_in_db(peer_id):
            self.add_peer_id(peer_id)

        return int(self.redis.hget(ADMIN_LEVELS, peer_id))

    def get_all_admins(self):
        levels = self.redis.hgetall(ADMIN_LEVELS)
        if levels:
            return dict(
                filter(
                    lambda y: y[1] > 0,
                    map(
                        lambda x: (int(x[0]), int(x[1])), levels.items()
                    )
                )
            )

    def add_nn(self, peer_id):
        self.redis.hset("words", peer_id, "")
        self.redis.hset("first_weights", peer_id, "_".join([",".join(["0" for _ in range(25)])
                                                            for __ in range(3000)]))
        self.redis.hset("second_weights", peer_id, "_".join([",".join(["0" for _ in range(3000)])
                                                             for __ in range(25)]))

    def check_nn_in_redis(self, peer_id):
        if self.redis.hget("words", peer_id) is not None:
            return True
        return False

    def get_nn(self, peer_id):
        if not self.check_nn_in_redis(peer_id):
            self.add_nn(peer_id)
        data = {}

        words = self.redis.hget("words", peer_id)
        words = words.decode("utf-8")
        words = words.split("___")
        data["words"] = words

        first_weights = self.redis.hget("first_weights", peer_id).decode("utf-8")
        first_weights = first_weights.split("_")
        first_weights = [list(map(float, i.split(","))) for i in first_weights]
        data["first_weights"] = first_weights

        second_weights = self.redis.hget("second_weights", peer_id).decode("utf-8")
        second_weights = second_weights.split("_")
        second_weights = [list(map(float, i.split(","))) for i in second_weights]
        data["second_weights"] = second_weights

        return data

    def get_words(self, peer_id):
        if not self.check_nn_in_redis(peer_id):
            self.add_nn(peer_id)
        words = self.redis.hget("words", peer_id)
        words = words.decode("utf-8")
        words = words.split("___")
        return words

    def append_words(self, peer_id, words: list):
        if not self.check_nn_in_redis(peer_id):
            self.add_nn(peer_id)
        old_words = self.redis.hget("words", peer_id).decode("utf-8")
        old_words_formatted = old_words.split("___")
        words_formatted = []
        for word in words:
            if word.lower() not in old_words_formatted:
                words_formatted.append(word)

        if 3000 - len(old_words_formatted) >= len(words_formatted):
            self.redis.hset("words", peer_id, "___".join((old_words, "___".join(words_formatted))))

    def exit_db(self):
        self.redis.close()


