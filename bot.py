import telebot

import config


class Bot:
    def __init__(self):
        if config.USE_PROXY:
            telebot.apihelper.proxy = {'https': config.PROXY}
        self.tb = telebot.TeleBot(config.TOKEN)

    def send_file(self, file_path, file_name, caption):
        with open(file_path, 'rb') as doc:
            self.tb.send_document(
                config.CHAT_ID, doc,
                caption=caption,
                parse_mode="MarkdownV2",
                reply_to_message_id=config.TOPIC_ID)
