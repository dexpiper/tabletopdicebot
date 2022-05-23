import os
import logging

import telebot
from flask import Flask


botlogger = logging.getLogger('botlogger')


TOKEN = os.environ.get('TOKEN')
URL = os.environ.get('URL')

if not TOKEN:
    botlogger.warning('TOKEN should be defined as system var')
if not URL:
    botlogger.warning('URL should be defined as system var')

# starting database
botlogger.info('Starting database...')
import db  # noqa E402

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
    bot.infinity_polling()


if __name__ == '__main__':
    run_long_polling()
