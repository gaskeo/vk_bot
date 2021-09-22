from vk_api.bot_longpoll import VkBotMessageEvent

from constants import GROUP_ID

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def redo_command(self: 'Bot', event: VkBotMessageEvent, _, peer_id: int):
    if not event.obj.message.get("reply_message", False):
        return self.send_message("Ответь на сообщение с командой для ее повтора", str(peer_id))

    message = event.obj.message["reply_message"]
    message["peer_id"] = peer_id
    message["out"] = 0
    message["fwd_messages"] = []
    message["important"] = False
    message["random_id"] = 0
    message["is_hidden"] = False
    message["id"] = event.obj.message.get("id", 0)
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
