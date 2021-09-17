import json

from constants import MIN_CHAT_PEER_ID, HELP_TEXT


def show_help(self, event, message, peer_id):
    if len(message.split()) == 1:
        help_template = None
        if peer_id > MIN_CHAT_PEER_ID:
            help_data = json.loads(HELP_TEXT)["user_help"]["main_conversation"]
            help_text_all = help_data["text"]
            help_keyboard = help_data["keyboard"]
        else:
            help_data = json.loads(HELP_TEXT)["user_help"]["main_user"]
            if event.obj["client_info"].get("carousel", False):
                help_template = help_data["template"]
                help_text_all = help_data["text_template"]
                help_keyboard = help_data["keyboard_template"]
            else:
                help_text_all = help_data["text_no_template"]
                help_keyboard = help_data["keyboard_no_template"]
        help_attachments = help_data["attachments"]
        self.send_message(help_text_all, peer_id=peer_id, attachments=help_attachments,
                          keyboard=help_keyboard, template=help_template)
    else:
        if message.split()[-1] in json.loads(HELP_TEXT)["user_help"]:
            command = message.split()[-1]
            help_data = json.loads(HELP_TEXT)["user_help"][command]
            help_text_command = help_data["text"]
            help_attachments = help_data["attachments"]
            help_keyboard = help_data["keyboard"]
            self.send_message(help_text_command, peer_id=peer_id,
                              attachments=help_attachments, keyboard=help_keyboard)
