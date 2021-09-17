import vk_api
import random

from constants import CHIEF_ADMIN


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


def get_user_name(user_id: int, vk: vk_api.vk_api.VkApiMethod) -> str:
    try:
        user = vk.users.get(user_ids=user_id)[0]
        name = user.get("first_name", "Name")
        last_name = user.get("last_name", "Last name")
        return f"{name} {last_name}"
    except IndexError:
        return "'вот тут имя, но вк его не достал'"


def get_admins_in_chat(peer_id, vk) -> list:
    """
    get all admins in chat
    :param peer_id: peer id of chat
    :param vk: vk_api for get admins
    :return: list of admins

    """
    try:
        members = \
            vk.messages.getConversationMembers(
                peer_id=peer_id)["items"]
    except vk_api.exceptions.ApiError:
        return [int(CHIEF_ADMIN)]
    admins = map(lambda y: y["member_id"],
                 tuple(filter(lambda x: x.get("is_admin", False), members)))
    admins = list(admins)

    admins.append(int(CHIEF_ADMIN))
    return admins


def get_random_user_from_conversation(vk: vk_api.vk_api.VkApiMethod, peer_id):
    try:
        members = \
            tuple(filter(lambda u: u["member_id"] > 0,
                         vk.messages.getConversationMembers(peer_id=int(peer_id))["items"]))
        return random.choice(members)['member_id']
    except vk_api.exceptions.ApiError:
        ...
    return -1
