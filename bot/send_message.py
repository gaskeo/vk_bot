from loguru import logger
import json
import random


def send_message(self, message: str,
                 peer_id: str = None,
                 attachments:
                 str or list = None,
                 keyboard: dict = None,
                 template=None,
                 reply_to=None, **kwargs):
    """
    handler for send message
    :param self: ...
    :param message: text of message 
    :param peer_id: id of peer of chat who receive message 
    :param attachments: attachments in message
    :param keyboard: keyboard in message
    :param template: template in message
    :param reply_to: reply message
    """
    self.vk.messages.send(peer_id=peer_id,
                          message=message,
                          random_id=random.randint(0, 2 ** 64),
                          attachment=attachments,
                          keyboard=json.dumps(
                              keyboard) if keyboard else None,

                          template=json.dumps(
                              template) if template else None,
                          reply_to=reply_to, **kwargs)
    try:
        log = u"ANSWER IN {}: {} | atts: {}".format(
            peer_id, str(message), attachments
        )
        logger.info(log)
    except UnicodeEncodeError:
        pass
