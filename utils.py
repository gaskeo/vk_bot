import string
import random
import pymorphy2

from constants import HUY_CHANCE, \
    RUSSIAN_SYMBOLS, MAIN_POS, ANSWER_CHANCE

from huy_api import generate_huy_word

morph = pymorphy2.analyzer.MorphAnalyzer()


def get_only_symbols(text: str) -> str:
    """
    get only latin letters from string
    :param text: string
    :return: string including only latin letters and spaces

    """
    final_text = ""
    for i in text:
        if (i.isalpha() and i not in string.ascii_letters) or i == " ":
            final_text += i
    return final_text


def get_main_pos(text) -> dict:
    """
    get dict like {part of speech: [words], ...}
    :param text: ext to work on
    :return: dict like {part of speech: [words], ...}

    """
    text_without_signs = ""
    for symbol in text:
        if symbol.lower() in RUSSIAN_SYMBOLS or symbol == " ":
            text_without_signs += symbol
    words = text_without_signs.split()
    parts = {}
    for word in words:
        parse = morph.parse(word)
        if parse:
            pos = parse[0].tag.POS
            if pos in MAIN_POS:
                if pos in parts:
                    parts[pos].append(word)
                else:
                    parts[pos] = [word]
    return parts


def what_answer(message: str, chances: dict) -> str:
    """
    send answer on non-command message
    :param message: text of message
    :param chances: chances

    """
    if not generate_huy_word(get_main_pos(message)):
        chances[HUY_CHANCE] = 0
    if not chances[HUY_CHANCE] and not chances[ANSWER_CHANCE]:
        return ""
    nc = 100 - chances[HUY_CHANCE] - chances[ANSWER_CHANCE]
    variants = tuple(chances.keys()) + ("Nothing",)
    weights = tuple(chances.values()) + (nc,)
    what = random.choices(variants, weights=weights)[0]
    return what


def format_text(text: str) -> list:
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


def generate_token(size: int) -> str:
    all_symbols = string.ascii_uppercase + \
                  string.ascii_lowercase + \
                  string.digits
    return ''.join(random.choice(all_symbols) for _ in range(size))