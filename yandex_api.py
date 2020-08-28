import requests

API_ADDRESS = "https://dictionary.yandex.net/dicservice.json/lookupMultiple"


def get_synonyms(text, dict="ru"):

    params = {
        "dict": dict,
        "text": text
    }
    return requests.get(API_ADDRESS, params=params).json()


def get_text_from_json_get_synonyms(json, dict="ru"):
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
    else:
        return None

