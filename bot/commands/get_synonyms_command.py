from yandex_api import get_text_from_json_get_synonyms, \
    get_synonyms_yandex

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot


def get_synonyms(self: 'Bot', _, message: str, peer_id: int):
    def get_synonyms_refactored(words):
        synonyms = \
            get_text_from_json_get_synonyms(get_synonyms_yandex(words))
        if not synonyms:
            return "Ничего не найдено"

        synonyms_refactored = f"Синонимы к слову \"{words}\":\n\n"
        for synonym in synonyms:
            synonyms_refactored += tuple(synonym.keys())[0] + "\n"

            if tuple(synonym.values())[0]:
                synonyms_refactored += \
                    f"Подобные слову \"{tuple(synonym.keys())[0]}\":\n"

                for mini_synonym in tuple(synonym.values())[0]:
                    synonyms_refactored += \
                        "&#4448;• " + mini_synonym + "\n"
        return synonyms_refactored

    if len(message) < 1:
        return self.send_message(
            "напиши слово после /gs или ответь на сообщение",
            str(peer_id))

    synonyms_from_api = get_synonyms_refactored(message)
    self.send_message(synonyms_from_api, str(peer_id))
