'''
Telegram bot and simple HTTP-server for getting messages via webhook
'''

from flask import Flask, request
import telebot
import logging

# WARNING! Define TOKEN variable in config.py
from config import TOKEN, URL, startmessage
import rolldice

# Setting bot
bot = telebot.TeleBot(TOKEN)

# Setting logger
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

# Setting Flask
app = Flask(__name__)

###
### Routes
###
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

###
### Message handlers
###
@bot.message_handler(commands=['start'])
def answer_start(message):
    """
    Answering to the /start command
    """
    bot.reply_to(message, startmessage, parse_mode='HTML')

@bot.message_handler(commands=['roll'])
def roll_anything(message):
    """
    Answering to the /roll command
    """
    rolling(message)

@bot.message_handler(commands=['roll20'])
def roll_20(message):
    roller = rolldice.DiceRoller('/roll d20 ' + message.text[6:])
    rolling(message, roller=roller)

@bot.message_handler(commands=['roll12'])
def roll_12(message):
    roller = rolldice.DiceRoller('/roll d12 ' + message.text[6:])
    rolling(message, roller=roller)

@bot.message_handler(commands=['roll10'])
def roll_10(message):
    roller = rolldice.DiceRoller('/roll d10 ' + message.text[6:])
    rolling(message, roller=roller)

@bot.message_handler(commands=['roll8'])
def roll_8(message):
    roller = rolldice.DiceRoller('/roll d8 ' + message.text[5:])
    rolling(message, roller=roller)

@bot.message_handler(commands=['roll6'])
def roll_6(message):
    roller = rolldice.DiceRoller('/roll d6 ' + message.text[5:])
    rolling(message, roller=roller)

@bot.message_handler(commands=['roll4'])
def roll_4(message):
    roller = rolldice.DiceRoller('/roll d4 ' + message.text[5:])
    rolling(message, roller=roller)

def rolling(message, roller=False):
    '''
    Base function to make the bot decode the command in message,
    roll the dices, calculate answer and send it to the user.

    Position arg roller is a <rolldice.DiceRoller('<command>')> object. 
    Used to simplify commands-shortcuts like /roll20
    '''
    if not roller:
        roller = rolldice.DiceRoller(message.text)

    username = message.from_user.username
    if roller.valid:
        # rolling dice, constructing raw log message
        result = roller.roll()
        the_log = roller.log

        # cooking answer
        if roller.addition and roller.addition > 0:
            mod = '\U00002795 <b>Modifier: + {}</b>'.format(roller.addition)
        elif roller.addition and roller.addition < 0:
            mod = '\U00002796 <b>Modifier: - {}</b>'.format(abs(roller.addition))
        else:
            mod = ''

        if roller.description:
            descr = '<b>----> {}</b>'.format(roller.description)
        else:
            descr = ''

        ready_message_for_user =\
'''@{username} rolled <b><i>{dice}</i></b> {descr}:

{log}{mod}
\U0001F4CB <b>Result:</b> <b>{result}</b>'''.format(
            dice=roller,
            log=the_log,
            username=username, 
            result=result,
            mod=mod,
            descr=descr
            )

        bot.reply_to(
            message, 
            ready_message_for_user,
            parse_mode='HTML'
            )
    else:
        ready_message_for_user =\
'''\U0001F6D1 <b>Sorry, this format is not acceptable.</b>\n
<i>Check the example:</i> <b>2d100 + 2</b>'''
        bot.reply_to(
            message, 
            ready_message_for_user,
            parse_mode='HTML'
            )

if __name__ == '__main__':
    app.run(threaded=True)
