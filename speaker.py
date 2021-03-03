import json
import random
import threading
import time


class Speaker:
    def __init__(self, messages=None):
        self.messages = messages if messages else {}
        self.flag = True
        with open("history.json") as f:
            self.messages = json.load(f)
        dump = threading.Thread(target=self.create_dump)
        dump.setName("dump")
        dump.start()

    def add_words(self, peer_id, text):
        peer_id = str(peer_id)
        if self.messages.get(peer_id, -1) == -1:
            self.messages[peer_id] = {"///start": {}, "///end": {}}
        text = text.lower()
        text_formatted = ""
        for s in text:
            if s.isalpha():
                text_formatted += s
            elif s in " \n\t":
                text_formatted += " "
        text_formatted = text_formatted.split()
        if text_formatted[0] in self.messages[peer_id]["///start"]:
            self.messages[peer_id]["///start"][text_formatted[0]] += 1
        else:
            self.messages[peer_id]["///start"][text_formatted[0]] = 1
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
        word = random.choices(tuple(self.messages[peer_id]["///start"].keys()))[0]
        sent = [word]
        while word != "///end":
            word = \
                random.choices(
                    tuple(self.messages[peer_id][word].keys()),
                    weights=tuple(self.messages[peer_id][word].values())
                )[0]
            sent.append(word)
        return " ".join(sent[:-1])

    def create_dump(self):
        while self.flag:
            with open("history.json", "w") as f:
                json.dump(self.messages, f)
            print("dump written")
            time.sleep(30)
        print("dump stopped")

    def disable_dump_thread(self):
        self.flag = False

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
