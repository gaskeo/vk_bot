import random
import os
from dotenv import load_dotenv

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

dotenv_path = os.path.join(os.path.dirname(__file__), 'config.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

GROUP_ID = os.getenv("vk_group_id")
TOKEN = os.getenv("vk_group_token")


def main():
    vk_session = vk_api.VkApi(
        token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            text = event.obj.message['text']
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message='hello world',
                             random_id=random.randint(0, 2 ** 64))


if __name__ == '__main__':
    main()
