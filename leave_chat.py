#!/usr/bin/env python3
import json
import logging
from argparse import ArgumentParser

from pymongo import MongoClient
from nosticker_bot import create_bot


def main():
    parser = ArgumentParser()
    parser.add_argument('--mode')
    parser.add_argument('chat_id', type=int)
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
    res = bot.leave_chat(opts.chat_id)


if __name__ == '__main__':
    main()
