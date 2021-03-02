from vk_api.bot_longpoll import VkBotMessageEvent


class MyEvent(VkBotMessageEvent):
    def __init__(self, raw):
        super().__init__(raw)
