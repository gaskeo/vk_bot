def get_count_words(self, _, __, peer_id):
    c = str(self.speaker.get_count_words(peer_id))
    if c:
        self.send_message(f"количество слов: {c}", peer_id)
