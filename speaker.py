from rds.redis_api import RedisApi


class Speaker:
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
        self.redis.add_text(str(peer_id), words)

    def generate_text(self, peer_id, word):
        return self.redis.generate_text(str(peer_id), word)

    def clear_chat(self, peer_id):
        self.redis.clear_chat(str(peer_id))

    def get_count_words(self, peer_id):
        return self.redis.get_count_words(str(peer_id))

    def get_words_after_that(self, peer_id, word):
        return self.redis.get_words_after_that(peer_id, word)

    def delete_words(self, peer_id, text: str):
        words = self.format_text(text)
        self.redis.delete_words_from_text(str(peer_id), words)
