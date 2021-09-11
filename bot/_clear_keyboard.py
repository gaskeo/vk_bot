from utils import send_message


def clear_keyboard(self, _, __, peer_id):
    empty_keyboard = {
        "one_time": False,
        "buttons": []
    }
    send_message("убрал клавиатуру", self.vk, peer_id, keyboard=empty_keyboard)
