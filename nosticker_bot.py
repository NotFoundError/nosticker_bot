#!/usr/bin/env python
from collections import Counter
import json
import logging
import telebot
from argparse import ArgumentParser
from pymongo import MongoClient
from datetime import datetime, timedelta

HELP = """*No Sticker Bot Help*

This simple telegram bot was created to solve only one task - to delete FUCKINGLY annoying stickers. Since you add bot to the group and allow it to delete sticker messages it starts deleting any sticker posted to the group.

*Usage*

1. Add [@nosticker_bot](https://t.me/nosticker_bot) to your group.
2. Go to group settings / users list / promote user to admin
3. Enable only one item: Delete messages
4. Click SAVE button
5. Enjoy!

*Commands*

/help - display this help message
/stat - display simple statistics about number of deleted stickers

*Open Source*

The source code is available at [github.com/lorien/nosticker_bot](https://github.com/lorien/nosticker_bot)
You can contact author of the bot at @madspectator

*My other projects*

Check out my [@daysandbox_bot](https://t.me/daysandbox_bot) - simple bot that removes LOT of spam.
"""

def create_bot(api_token, db):
    bot = telebot.TeleBot(api_token)

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

    #@bot.message_handler(content_types=['document'])
    #def handle_document(msg):
    #    if msg.document.mime_type == 'video/mp4':
    #        bot.delete_message(msg.chat.id, msg.message_id)
    #        db.event.save({
    #            'type': 'delete_document',
    #            'chat_id': msg.chat.id,
    #            'chat_username': msg.chat.username,
    #            'user_id': msg.from_user.id,
    #            'username': msg.from_user.username,
    #            'date': datetime.utcnow(),
    #            'document': {
    #                'file_id': msg.document.file_id,
    #                'file_name': msg.document.file_name,
    #                'mime_type': msg.document.mime_type,
    #                'file_size': msg.document.file_size,
    #                'thumb': msg.document.thumb.__dict__ if msg.document.thumb else None,
    #            },
    #        })


    @bot.message_handler(commands=['start', 'help'])
    def handle_start_help(msg):
        if msg.chat.type != 'private':
            return
        bot.reply_to(msg, HELP, parse_mode='Markdown')

    #@bot.message_handler(commands=['stat'])
    #def handle_stat(msg):
    #    if msg.chat.type != 'private':
    #        return
    #    days = []
    #    top_today = Counter()
    #    top_week = Counter()
    #    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    #    for x in range(7):
    #        day = today - timedelta(days=x)
    #        query = {'$and': [
    #            {'type': 'delete_sticker'},
    #            {'date': {'$gte': day}},
    #            {'date': {'$lt': day + timedelta(days=1)}},
    #        ]}
    #        num = 0
    #        for event in db.event.find(query):
    #            num += 1
    #            if day == today:
    #                top_today[event['chat_username']] += 1
    #            top_week[event['chat_username']] += 1
    #        days.insert(0, num)
    #    ret = 'Recent 7 days: %s' % ' | '.join([str(x) for x in days])
    #    ret += '\nTop today: %s' % ', '.join('%s (%d)' % x for x in top_today.most_common(5)) 
    #    ret += '\nTop week: %s' % ', '.join('%s (%d)' % x for x in top_week.most_common(5)) 
    #    bot.reply_to(msg, ret)

    @bot.message_handler(commands=['stat'])
    def handle_stat(msg):
        if msg.chat.type != 'private':
            return
        days = []
        top_today = Counter()
        top_ystd = Counter()
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
                key  = (
                    '@%s' % event['chat_username'] if event['chat_username']
                    else '#%d' % event['chat_id']
                )
                if day == today:
                    top_today[key] += 1
                if day == (today - timedelta(days=1)):
                    top_ystd[key] += 1
                top_week[key] += 1
            days.insert(0, num)
        ret = 'Recent 7 days: %s' % ' | '.join([str(x) for x in days])
        ret += '\n\nTop today:\n%s' % '\n'.join('  %s (%d)' % x for x in top_today.most_common())
        ret += '\n\nTop yesterday:\n%s' % '\n'.join('  %s (%d)' % x for x in top_ystd.most_common())
        ret += '\n\nTop 10 week:\n%s' % '\n'.join('  %s (%d)' % x for x in top_week.most_common(10))
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
