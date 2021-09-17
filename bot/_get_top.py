from my_vk_api import get_user_name
from constants import MIN_CHAT_PEER_ID

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Bot


def get_top(self: 'Bot', _, __, peer_id: int):
    if peer_id > MIN_CHAT_PEER_ID:
        users = self.redis.get_all_users_count_messages(str(peer_id))
        top5 = tuple(sorted(users.items(), key=lambda x: x[1], reverse=True))[:5]

        send = [f"{n}. {get_user_name(user, self.vk)} vk.com/id{user} : {messages}"
                for n, (user, messages) in enumerate(top5, 1)]

        self.send_message("Топ 5:\n" + "\n".join(send), str(peer_id))
