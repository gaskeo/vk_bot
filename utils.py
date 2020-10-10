import vk_api
import requests

import random


def get_user_id_via_url(user_url: str, vk: vk_api.vk_api.VkApiMethod) -> int:
    """
    finding user id via url
    :param user_url: user's url who need id
    :param vk: vk_api for find user's id via url
    :return: user's id or 0 if user not found

    """

    def get_user_screen_name_of_url(url: str) -> str:
        """
        searching screen name in url
        :param url: user's account url
        :return: user's screen name

        """
        if url.startswith("[") and url.endswith("]") and "|" in url:
            url = url[1:url.find("|")]
            return url
        url = url.replace("@", "")
        if url.endswith("/"):
            url = url[:-1]
        while "/" in url:
            url = url[url.rfind("/") + 1:]
        return url

    info = vk.utils.resolveScreenName(screen_name=get_user_screen_name_of_url(user_url))
    if info:
        user_id: int = info["object_id"]
        return user_id
    return 0


def send_message(message: str, vk: vk_api.vk_api.VkApiMethod, user_id: int, attachments:
                 str or list = None):
    """
    handler for send message
    :param message: text of message 
    :param vk: vk_api for send message
    :param user_id: id of user who receive message 
    :param attachments: attachments in message

    """
    vk.messages.send(user_id=user_id,
                     message=message,
                     random_id=random.randint(0, 2 ** 64),
                     attachment=attachments)


def get_random_wiki_page() -> str:
    request = "https://ar.wikipedia.org/w/api.php?action=query&format=json&list=random&rnlimit=5"
    pages = requests.get(request).json()["query"]["random"]
    longest_page = max(pages, key=lambda page: page["title"])["title"]
    return longest_page


def get_only_symbols(text: str) -> str:
    final_text = ""
    for i in text:
        if i.isalpha() or i == " ":
            final_text += i
    return final_text
