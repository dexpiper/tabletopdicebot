import os
import logging

import telebot
from flask import Flask, request

import models


botlogger = logging.getLogger('botlogger')

TOKEN = os.environ.get('TOKEN')
URL = os.environ.get('URL')
DATABASE_URL = os.environ.get('DATABASE_URL')

if not TOKEN:
    botlogger.warning('TOKEN should be defined as system var')
if not URL:
    botlogger.warning('URL should be defined as system var')


# connect to database
creds, host_and_database = DATABASE_URL[11:].split('@')
host_and_port, database = host_and_database.split('/')
host, port = host_and_port.split(':')
user, password = creds.split(':')

models.db.bind(provider='postgres', user=user, password=password,
               host=host, port=port, database=database)
models.db.generate_mapping(create_tables=True)


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


#
# FLASK ROUTES
#
@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    app.logger.debug('Get some message')
    bot.process_new_updates([update])
    return "!", 200


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    bot.remove_webhook()
    s = bot.set_webhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        app.logger.info('Webhook setup successful')
        return "webhook setup ok"
    else:
        app.logger.critical('Webhook setup failed!')
        return "webhook setup failed"


@app.route('/')
def index():
    app.logger.debug('Operational test. Serving normally')
    return '.'
