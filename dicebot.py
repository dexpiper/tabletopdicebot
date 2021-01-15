import logging

from flask import Flask, request
import telebot

# WARNING! Define TOKEN variable in config.py
from config import TOKEN, URL, startmessage
import rolldice

bot = telebot.TeleBot(TOKEN)
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

app = Flask(__name__)

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    bot.remove_webhook()
    s = bot.set_webhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/')
def index():
    return '.'

@bot.message_handler(commands=['start'])
def answer_start(message):
    """
    Answering to the /start command
    """
    bot.reply_to(message, startmessage, parse_mode='HTML')

@bot.message_handler(commands=['roll'])
def answer_find(message):
    """
    Answering to the /roll command
    """
    username = message.from_user.username
    roller = rolldice.DiceRoller(message.text)
    if roller.valid:
        # rolling dice, condtructing raw log message
        result = roller.dice.roll()
        the_log = roller.dice.log

        # cooking answer
        ready_message_for_user =\
'@{username} rolled <b><i>{dice}</i></b>:\n\n{log}\n\nResult: <b>{result}</b>'.format(
            dice=roller.dice,
            log=the_log,
            username=username, 
            result=result)

        bot.reply_to(
            message, 
            ready_message_for_user,
            parse_mode='HTML'
            )
    else:
        ready_message_for_user =\
'*** Sorry, this format is not acceptable.\n\n<i>Check the example:</i> <b>2d100 + 2</b>'
        bot.reply_to(
            message, 
            ready_message_for_user,
            parse_mode='HTML'
            )

if __name__ == '__main__':
    app.run(threaded=True)