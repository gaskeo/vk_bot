from utils import get_user_name


def get_my_count(self, event, _, peer_id):
    user_id = event.obj.message['from_id']
    count = self.redis.get_count_messages(str(peer_id), str(user_id))
    self.send_message(f"{'@id'}{user_id} ({get_user_name(user_id, self.vk)}): {count}", peer_id,
                      reply_to=event.obj.message.get("id"))
