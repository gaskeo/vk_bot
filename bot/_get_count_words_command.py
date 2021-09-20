from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Bot


def get_count_words(self: 'Bot', _, __, peer_id: int):
    c = str(self.redis.get_count_words(str(peer_id)))
    if c:
        self.send_message(f"количество слов: {c}", str(peer_id))
