import json
import random
import threading
import time
from difflib import SequenceMatcher
from rds.redis_api import RedisApi


class Speaker:
    SIMILAR_COEF = 0.8

    def __init__(self, redis: RedisApi):
        self.nearest_words = {}
        self.redis = redis

    @staticmethod
    def format_text(text):
        text = text.lower()
        text_formatted = ""
        for s in text:
            if s.isalpha() or s.isdigit():
                text_formatted += s
            elif str(s.encode('unicode-escape')).startswith("b'\\\\U"):
                text_formatted += f" {s} "
            elif s in " \n\t":
                text_formatted += " "
        return text_formatted.split()

    def add_words(self, peer_id, text: str):
        words = self.format_text(text)
        if self.nearest_words.get(str(peer_id), False):
            print(self.nearest_words[str(peer_id)])
            w, t = self.nearest_words[str(peer_id)]
            if time.time() - t < 20:
                words.insert(0, w)
        self.nearest_words[str(peer_id)] = (words[-1], time.time())
        print(words)
        self.redis.add_text(str(peer_id), words)

    def generate_text(self, peer_id):
        return self.redis.generate_text(str(peer_id))

    def clear_chat(self, peer_id):
        self.redis.clear_chat(str(peer_id))

    def get_count_words(self, peer_id):
        return self.redis.get_count_words(str(peer_id))

    def get_words_after_that(self, peer_id, word):
        return self.redis.get_words_after_that(peer_id, word)

    def delete_words(self, peer_id, text: str):
        words = self.format_text(text)
        self.redis.delete_words_from_text(str(peer_id), words)

    # future
    # def get_similar_word(self, peer_id):
    #     peer_id = str(peer_id)
    #     words = []
    #     for i, word in enumerate(dict(self.messages[peer_id]), 1):
    #         for word_after in tuple(self.messages[peer_id])[i:]:
    #             if SequenceMatcher(None, word, word_after).ratio() > self.SIMILAR_COEF:
    #                 words.append((word, word_after))
    #     return words
    #
    # def clear_similar_word(self, peer_id):
    #     peer_id = str(peer_id)
    #     words = []
    #     for i, word in enumerate(self.messages[peer_id], 1):
    #         for word_after in tuple(self.messages[peer_id])[i:]:
    #             if SequenceMatcher(None, word, word_after).ratio() > self.SIMILAR_COEF:
    #                 words.append(word)
    #     self.delete_words(peer_id, " ".join(words))
    #     return words
