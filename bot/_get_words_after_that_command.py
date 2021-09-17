def get_words_after_that(self, event, message, peer_id):
    def send_ans():
        if "///end" in words:
            words.remove("///end")
        if not words:
            self.send_message("ничего нет", peer_id)
            return
        self.send_message((f"после {message} идет:\n" +
                           "\n".join(("- " + i for i in words))), peer_id, reply_to=event.obj.message.get("id"))

    message = message.replace("/at", "").strip()
    if not message or message == " ":
        if event.obj.message.get("reply_message", False):
            message = event.obj.message["reply_message"]["text"]
            if len(message.split()) > 0:
                words = list(self.speaker.get_words_after_that(peer_id, message).keys())
                send_ans()
                return
    words = list(self.speaker.get_words_after_that(peer_id, message).keys())
    send_ans()
