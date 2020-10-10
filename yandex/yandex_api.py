import requests

SYNONYMS_API_ADDRESS = "https://dictionary.yandex.net/dicservice.json/lookupMultiple"


def get_synonyms(text, dict="ru") -> dict:
    """
    get synonyms from yandex api
    :param text: text need synonyms
    :param dict: language of text
    :return: dict of synonyms

    """
    params = {
        "dict": dict,
        "text": text
    }
    return requests.get(SYNONYMS_API_ADDRESS, params=params).json()


def get_text_from_json_get_synonyms(json, dict="ru") -> list:
    """
    refactor object from 'get_synonyms' function
    :param json: source object
    :param dict: language of text
    :return: list of synonyms

    """
    all_syn = []
    if json[dict]["syn"]:
        for word in json[dict]["syn"][0]["tr"]:
            main_word = word["text"]
            syns = []
            if "syn" in word.keys():
                for syn in word["syn"]:
                    syns.append(syn["text"])
            all_syn.append({main_word: syns})
    return all_syn

