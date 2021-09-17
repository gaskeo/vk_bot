

def clear_keyboard(self, _, __, peer_id):
    empty_keyboard = {
        "one_time": False,
        "buttons": []
    }
    self.send_message("убрал клавиатуру", peer_id, keyboard=empty_keyboard)
