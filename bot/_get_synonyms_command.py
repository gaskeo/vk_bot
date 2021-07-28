from yandex.yandex_api import get_text_from_json_get_synonyms, get_synonyms_yandex
from utils import send_message


def get_synonyms(self, _, message, peer_id):
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

    if len(message.split()) >= 2:
        synonyms_from_api = get_synonyms_refactored(message.split()[1:])
        send_message(synonyms_from_api, self.vk, peer_id=peer_id)
    else:
        send_message("Ошибка: нет слова", self.vk, peer_id=peer_id)

