import json
import random
import threading
import time
from difflib import SequenceMatcher


class Speaker:
    SIMILAR_COEF = 0.7

    def __init__(self, messages=None):
        self.messages = messages if messages else {}
        self.__flag = True
        with open("history.json") as f:
            self.messages = json.load(f)
        dump = threading.Thread(target=self.create_dump)
        dump.setName("dump")
        dump.start()

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
        peer_id = str(peer_id)
        if self.messages.get(peer_id, -1) == -1:
            self.messages[peer_id] = {"///start": {}, "///end": {}}
        text_formatted = self.format_text(text)
        if not text_formatted:
            return
        for i, j in zip(text_formatted[:-1], text_formatted[1:]):
            if i not in self.messages[peer_id]:
                self.messages[peer_id][i] = {}
            if j not in self.messages[peer_id][i]:
                self.messages[peer_id][i][j] = 1
            else:
                self.messages[peer_id][i][j] += 1

        if text_formatted[-1] not in self.messages[peer_id]:
            self.messages[peer_id][text_formatted[-1]] = {}
        if "///end" in self.messages[peer_id][text_formatted[-1]]:
            self.messages[peer_id][text_formatted[-1]]["///end"] += 1
        else:
            self.messages[peer_id][text_formatted[-1]]["///end"] = 1

    def generate_text(self, peer_id):
        peer_id = str(peer_id)
        if peer_id not in self.messages:
            self.messages[peer_id] = {"///start": {}, "///end": {}}
            return ""
        starts = list(self.messages[peer_id].keys())
        starts.remove("///end")
        starts.remove("///start")
        word = random.choices(starts)[0]
        starts.remove(word)
        sent = [word]
        n_max = random.randint(4, 20)
        n = 0
        while word != "///end":
            if n > n_max:
                break
            word = \
                random.choices(
                    tuple(self.messages[peer_id][word].keys()),
                    weights=tuple(self.messages[peer_id][word].values())
                )[0]
            sent.append(word)
        if sent[-1] == "///end":
            sent.pop(-1)
        return " ".join(sent)

    def create_dump(self):
        while self.__flag:
            with open("history.json", "w") as f:
                json.dump(self.messages, f)
            print("dump written")
            start = time.time()
            while time.time() - start < 300:
                if not self.__flag:
                    print("dump stopped")
                    return
                time.sleep(5)
        print("dump stopped")

    def disable_dump_thread(self):
        self.__flag = False

    def clear_chat(self, peer_id):
        peer_id = str(peer_id)
        if peer_id in self.messages:
            self.messages[peer_id] = {"///start": {}, "///end": {}}

    def get_count_words(self, peer_id):
        peer_id = str(peer_id)
        if peer_id not in self.messages:
            self.messages[peer_id] = {"///start": {}, "///end": {}}
            return 0
        return len(self.messages[peer_id]) - 2

    def get_words_after_that(self, peer_id, word):
        peer_id = str(peer_id)
        if peer_id in self.messages:
            return self.messages[peer_id].get(word, {})

    def delete_words(self, peer_id, text: str):
        peer_id = str(peer_id)
        words = self.format_text(text)
        for word in words:
            if self.messages[peer_id].get(word, False):
                self.messages[peer_id].pop(word)
        for word, word_after in self.messages[peer_id].items():
            for delete_word in words:
                if delete_word in word_after:
                    self.messages[peer_id][word].pop(delete_word)

    def get_similar_word(self, peer_id):
        peer_id = str(peer_id)
        words = []
        for i, word in enumerate(self.messages[peer_id], 1):
            for word_after in tuple(self.messages[peer_id])[i:]:
                if SequenceMatcher(None, word, word_after).ratio() > self.SIMILAR_COEF:
                    words.append((word, word_after))
        return words

    def clear_similar_word(self, peer_id):
        peer_id = str(peer_id)
        words = []
        for i, word in enumerate(self.messages[peer_id], 1):
            for word_after in tuple(self.messages[peer_id])[i:]:
                if SequenceMatcher(None, word, word_after).ratio() > self.SIMILAR_COEF:
                    words.append(word)
        self.delete_words(peer_id, " ".join(words))
        return words
