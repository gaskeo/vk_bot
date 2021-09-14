from utils import send_message, get_user_name


def get_my_count(self, event, _, peer_id):
    user_id = event.obj.message['from_id']
    count = self.redis.get_count_messages(str(peer_id), str(user_id))
    send_message(f"{'@id'}{user_id} ({get_user_name(user_id, self.vk)}): {count}", self.vk, peer_id,
                 reply_to=event.obj.message.get("id"))
