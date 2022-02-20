import requests

from constants import SYNONYMS_API_ADDRESS


def get_synonyms_yandex(text, dictionary="ru") -> dict:
    """
    get synonyms from yandex_api api
    :param text: text need synonyms
    :param dictionary: language of text
    :return: dict of synonyms

    """
    params = {
        "dict": dictionary,
        "text": text
    }
    return requests.get(SYNONYMS_API_ADDRESS, params=params).json()


def get_text_from_json_get_synonyms(json, dictionary="ru") -> list:
    """
    refactor object from 'get_synonyms' function
    :param json: source object
    :param dictionary: language of text
    :return: list of synonyms

    """
    all_synonyms = []
    if json[dictionary]["syn"]:
        for word in json[dictionary]["syn"][0]["tr"]:
            main_word = word["text"]
            synonyms = []
            if "syn" in word.keys():
                for syn in word["syn"]:
                    synonyms.append(syn["text"])
            all_synonyms.append({main_word: synonyms})
    return all_synonyms
