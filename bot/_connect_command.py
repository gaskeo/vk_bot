import json

from constants import KEYBOARDS


def connect(self, _, message, peer_id):
    if self.redis.get_connected_chat(str(peer_id)):
        self.send_message("вы уже подключены к другой беседе, для начала админ должен написать /disconnect, "
                          "чтобы отключиться", peer_id)
        return
    data = message.split()
    if len(data) != 2:
        self.send_message("неправильный формат", peer_id)
        return
    token = data[-1]
    connect_peer_id = self.redis.get_peer_id_by_token(token)
    if not connect_peer_id:
        self.send_message("не могу найти такой токен, возможно его уже использовали, попросите сделать новый",
                          peer_id)
    if connect_peer_id == str(peer_id):
        self.send_message("ты че это та же беседа...", peer_id)
        return
    data = self.vk.messages.getConversationsById(peer_ids=str(peer_id)).get("items", [dict()])
    if not data:
        title = "тут должно быть название беседы, но не получилось, странная беседа..."
    else:
        title = data[0].get("chat_settings", {}).get("title")

    keyboard = json.loads(KEYBOARDS)["connect_keyboard"]
    keyboard["buttons"][0][0]["action"]["payload"]["peer_id"] = peer_id
    keyboard["buttons"][0][0]["action"]["payload"]["token"] = token
    extra_text = "(вы уже подключены к другой беседе, по нажатию кнопки эта связь разорвется)" \
        if self.redis.get_connected_chat(connect_peer_id) else ""
    self.send_message(
        f'беседа "{title}" хочет связаться с вами, для подтверждения админы нажмите на кнопочку. '
        f'{extra_text}',
        int(connect_peer_id), keyboard=keyboard
    )

    self.send_message("запрос в другую беседу отправлен", peer_id)
