#!/usr/bin/env python
from collections import Counter
import json
import logging
import telebot
from argparse import ArgumentParser
from pymongo import MongoClient
from datetime import datetime, timedelta


def create_bot(api_token, db):
    bot = telebot.TeleBot(api_token)
    with open('README.md') as inp:
        readme_data = inp.read()

    @bot.message_handler(content_types=['sticker'])
    def handle_sticker(msg):
        bot.delete_message(msg.chat.id, msg.message_id)
        db.event.save({
            'type': 'delete_sticker',
            'chat_id': msg.chat.id,
            'chat_username': msg.chat.username,
            'user_id': msg.from_user.id,
            'username': msg.from_user.username,
            'date': datetime.utcnow(),
        })

    @bot.message_handler(commands=['start', 'help'])
    def handle_start_help(msg):
        bot.reply_to(msg, readme_data, parse_mode='Markdown')

    @bot.message_handler(commands=['stat'])
    def handle_stat(msg):
        days = []
        top_today = Counter()
        top_week = Counter()
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        for x in range(7):
            day = today - timedelta(days=x)
            query = {'$and': [
                {'type': 'delete_sticker'},
                {'date': {'$gte': day}},
                {'date': {'$lt': day + timedelta(days=1)}},
            ]}
            num = 0
            for event in db.event.find(query):
                num += 1
                if day == today:
                    top_today[event['chat_username']] += 1
                top_week[event['chat_username']] += 1
            days.insert(0, num)
        ret = ' | '.join([str(x) for x in days])
        ret += '\nTop today: %s' % ', '.join('%s (%d)' % x for x in top_today.most_common(5)) 
        ret += '\nTop week: %s' % ', '.join('%s (%d)' % x for x in top_week.most_common(5)) 
        bot.reply_to(msg, ret)

    return bot



def main():
    parser = ArgumentParser()
    parser.add_argument('--mode')
    opts = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    with open('var/config.json') as inp:
        config = json.load(inp)
    if opts.mode == 'test':
        token = config['test_api_token']
    else:
        token = config['api_token']
    db = MongoClient()['nosticker']
    bot = create_bot(token, db)
    bot.polling()


if __name__ == '__main__':
    main()
