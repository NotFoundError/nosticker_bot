#!/usr/bin/env python
import json
import logging
import telebot


def create_bot(api_token):
    bot = telebot.TeleBot(api_token)

    @bot.message_handler(content_types=['sticker'])
    def handle_sticker(msg):
        bot.delete_message(msg.chat.id, msg.message_id)

    @bot.message_handler(commands=['start', 'help'])
    def handle_start_help(msg):
        with open('README.rst') as inp:
            data = inp.read()
        bot.reply_to(msg, data)

    return bot


def main():
    logging.basicConfig(level=logging.DEBUG)
    with open('var/config.json') as inp:
        config = json.load(inp)
    bot = create_bot(config['api_token'])
    bot.polling()


if __name__ == '__main__':
    main()
