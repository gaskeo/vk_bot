from utils import send_message


def get_my_count(self, event, _, peer_id):
    count = self.redis.get_count_messages(str(peer_id), str(event.obj.message["from_id"]))
    send_message(f"вы написали сообщений: {count}", self.vk, peer_id)
