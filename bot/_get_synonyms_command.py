from yandex.yandex_api import get_text_from_json_get_synonyms, get_synonyms_yandex


def get_synonyms(self, event, message, peer_id):
    def get_synonyms_refactored(words):
        synonyms = get_text_from_json_get_synonyms(get_synonyms_yandex(words))
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

    text = []
    if len(message.split()) >= 2:
        text = message.split()[1:]
    elif event.obj.message.get("reply_message"):
        text = event.obj.message.get("reply_message").get("text").split() \
            if event.obj.message.get("reply_message").get("text") else ""

    if not text:
        self.send_message("напиши слово после /gs или ответь на сообщение", peer_id=peer_id)
        return
    synonyms_from_api = get_synonyms_refactored(text)
    self.send_message(synonyms_from_api, peer_id=peer_id)
