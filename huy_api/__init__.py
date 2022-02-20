import random

from constants import RUSSIAN_VOWEL


def generate_huy_word(data: dict) -> str:
    """
    generator huy word from random word from data
    :param data: dict like {part of speech: [words], ...}
    :return: huy-like word

    """

    def get_random_part_once(words: dict) -> str:
        """
        get random word of part of speech that find once in dict
        :param words: dict like {part of speech: [words], ...}
        :return: word

        """
        parts_reformed = list(filter(lambda x: len(x[1]) == 1,
                                     list(words.items())))
        if parts_reformed:
            return random.choice(parts_reformed)[1][0]
        return ""

    word = get_random_part_once(data)
    if word:
        if word.lower().startswith(tuple(RUSSIAN_VOWEL)):
            return "Хуя" + word[1:].lower()
        else:
            if len(word) > 1 and word[1].lower() in RUSSIAN_VOWEL:
                return "Ху" + word[1:].lower()
            return "Ху" + word[2:].lower()
    else:
        return ""
