from utils import send_message, get_user_name


def get_top(self, _, __, peer_id):
    users = self.redis.get_all_users_count_messages(peer_id)
    top5 = tuple(sorted(users.items(), key=lambda x: x[1], reverse=True))[:5]
    send = [f"{n}. {get_user_name(int(user), self.vk)} https://vk.com/id{user}: {messages}"
            for n, (user, messages) in enumerate(top5, 1)]
    send_message("Топ 5:\n" + "\n".join(send), self.vk, peer_id)
