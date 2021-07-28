from vk_api.bot_longpoll import VkBotMessageEvent, VkBotEventType
from utils import send_message


def redo_command(self, event, _, peer_id):
    if event.obj.message.get("reply_message", False):
        message = event.obj.message["reply_message"]
        message["peer_id"] = peer_id
        message["out"] = 0
        message["fwd_messages"] = []
        message["important"] = False
        message["random_id"] = 0
        message["is_hidden"] = False
        raw = {'type': 'message_new',
               'object': {'message': message},
               'client_info': {
                   'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link',
                                      'intent_subscribe', 'intent_unsubscribe'],
                   'keyboard': True,
                   'inline_keyboard': True,
                   'carousel': False,
                   'lang_id': 0
               },
               'group_id': int(GROUP_ID),
               }
        e = VkBotMessageEvent(raw)
        self.add_event_in_queue(e)
    else:
        send_message("Ответь на сообщение с командой для ее повтора", self.vk, peer_id)