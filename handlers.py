import functools
import logging

from flask import current_app

from roller import DiceRoller, rolling


app = current_app
with app.app_context():
    bot = app.config['TELEBOT']
    botlogger = app.config['TELEBOT_LOGGER']


class BotHandlers:
    """
    Message handlers.
    For use only within app.app_context.

    Every single handler function should be decorated
    with custom @handler decorator.
    """

    handlers = []

    @classmethod
    def register(cls):
        """
        Register message handlers defined below into a TeleBot.
        """
        try:
            for handler in BotHandlers.handlers:
                name = handler[0]
                kwargs = handler[1]
                bot.register_message_handler(name, **kwargs)
            return True
        except Exception as exc:
            logging.error('Cannot register handlers: %s', exc)
            return False

    def handler(append_to=handlers, **out_kwargs):
        """
        Decorator to register telebot handlers
        """
        def decorator_register(func):
            if out_kwargs:
                append_to.append((func, out_kwargs))

            @functools.wraps(func)
            def wrapper_register(*args, **kwargs):

                return func(*args, **kwargs)

            return wrapper_register
        return decorator_register

    @handler(append_to=handlers, commands=['start'])
    def answer_start(message):
        """
        Bot sends welcome message
        """
        botlogger.debug('Start message recieved')
        bot.send_message(
            message.chat.id,
            'Hello! This is beta-version of TabletopDiceBot!',
            parse_mode='HTML'
        )

    @handler(append_to=handlers, commands=['roll'])
    def roll_anything(message):
        """
        Answering to the /roll command
        """
        rolling(message, bot)

    @handler(commands=['roll20'])
    def roll_20(message):
        roller = DiceRoller('/roll d20 ' + message.text[6:])
        rolling(message, bot, roller=roller)

    @handler(commands=['roll12'])
    def roll_12(message):
        roller = DiceRoller('/roll d12 ' + message.text[6:])
        rolling(message, bot, roller=roller)

    @handler(commands=['roll10'])
    def roll_10(message):
        roller = DiceRoller('/roll d10 ' + message.text[6:])
        rolling(message, bot, roller=roller)

    @handler(commands=['roll8'])
    def roll_8(message):
        roller = DiceRoller('/roll d8 ' + message.text[5:])
        rolling(message, bot, roller=roller)

    @handler(commands=['roll6'])
    def roll_6(message):
        roller = DiceRoller('/roll d6 ' + message.text[5:])
        rolling(message, bot, roller=roller)

    @handler(commands=['roll4'])
    def roll_4(message):
        roller = DiceRoller('/roll d4 ' + message.text[5:])
        rolling(message, bot, roller=roller)
