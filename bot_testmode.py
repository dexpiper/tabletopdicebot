"""
Used to run the bot in longpolling mode locally.
SQLite in-memory database is in use.
"""

import os
import logging

import telebot
from flask import Flask

import models


botlogger = logging.getLogger('botlogger')


TOKEN = os.environ.get('TOKEN')
URL = os.environ.get('URL')
DATABASE_URL = os.environ.get('DATABASE_URL')

if not TOKEN:
    botlogger.warning('TOKEN should be defined as system var')
if not URL:
    botlogger.warning('URL should be defined as system var')

# connecting to database

creds, host_and_database = DATABASE_URL[11:].split('@')
host_and_port, database = host_and_database.split('/')
host, port = host_and_port.split(':')
user, password = creds.split(':')

models.db.bind(provider='postgres', user=user, password=password,
               host=host, port=port, database=database)
models.db.generate_mapping(create_tables=True)
# set_sql_debug(True)

botlogger.info('Starting database...')
import models  # noqa E402

# Setting bot
bot = telebot.TeleBot(TOKEN)
tblogger = telebot.logger
telebot.logger.setLevel(logging.INFO)

# Setting Flask
app = Flask(__name__)

# registering into flask
app.config['TELEBOT'] = bot
app.config['TELEBOT_LOGGER'] = tblogger

# registering bot handlers
with app.app_context():

    from handlers import BotHandlers
    BotHandlers.register()


def run_long_polling():
    botlogger.info('Starting polling...')
    bot.infinity_polling(skip_pending=True)


if __name__ == '__main__':
    run_long_polling()
