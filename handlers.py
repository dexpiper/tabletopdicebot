import functools
import logging

from flask import current_app
from pony.orm import db_session

import views
from roller import DiceRoller
from models import User, Char, Throw, Attribute  # noqa F401


# getting data from flask.app_context
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

############################################################
#                                                          #
#                  BOT MESSAGE HANDLERS                    #
#                                                          #
############################################################

    #
    # Service handlers
    #
    @handler(append_to=handlers, commands=['start', 'help'])
    def answer_start(message):
        """
        Bot sends general help page and basic bot info
        """
        bot.send_message(
            message.chat.id,
            views.hello(message.from_user.username),
            parse_mode='HTML'
        )

    #
    # Managing user settings handlers
    #
    @handler(append_to=handlers, commands=['char', 'chars'])
    @db_session
    def show_user_chars_list(message):
        """
        Show charlist for user
        """
        user_id = message.from_user.id
        user = User.get_user_by_id(user_id)
        ready_text = views.charlist(user)
        bot.reply_to(
                message,
                ready_text,
                parse_mode='HTML'
            )

    #
    # Rolls handlers
    #
    @handler(append_to=handlers, commands=['roll'])
    @db_session
    def roll_anything(message):
        """
        Answering to the /roll command
        """
        telegram_user = message.from_user
        raw_formula = message.text[6:]  # removeprefix /roll
        roller = DiceRoller(raw_formula, telegram_user)
        hand = roller.hand
        ready_text = views.roll(roller, hand)
        bot.reply_to(
            message,
            ready_text,
            parse_mode='HTML'
        )

    @handler(append_to=handlers, commands=['rollme'])
    @db_session
    def roll_custom_throw(message):
        """
        Rolling pre-defined throws by name
        """
        user_id = message.from_user.id
        user = User.get_user_by_id(user_id)
        userchar = user.active_char()
        if not userchar:
            error_text = (
                'Sorry, you have no active character. '
                'Call /createchar to create one!'
            )
            bot.reply_to(
                message,
                views.error(error_text),
                parse_mode='HTML'
            )
            return
        throwname = message.text[7:].strip()
        formula = userchar.throw(throwname)
        if formula:
            roller = DiceRoller(formula, message.from_user)
            hand = roller.hand
            ready_text = views.roll(roller, hand)
            bot.reply_to(
                message,
                ready_text,
                parse_mode='HTML'
            )
        else:
            error_text = (
                f'Sorry, such Throw ({throwname}) is not '
                f'registered for your active char {userchar.name}'
            )
            bot.reply_to(
                message,
                views.error(error_text),
                parse_mode='HTML'
            )

    #
    # Roll shorthands
    #
    @handler(commands=['roll20'])
    def roll_20(message):
        shorthand(message, 20)

    @handler(commands=['roll12'])
    def roll_12(message):
        shorthand(message, 12)

    @handler(commands=['roll10'])
    def roll_10(message):
        shorthand(message, 10)

    @handler(commands=['roll8'])
    def roll_8(message):
        shorthand(message, 8)

    @handler(commands=['roll6'])
    def roll_6(message):
        shorthand(message, 6)

    @handler(commands=['roll4'])
    def roll_4(message):
        shorthand(message, 4)


def shorthand(message, dice: int):
    descr = message.text[8:] if dice > 9 else message.text[7:]
    roller = DiceRoller(f'/roll d{dice} ' + descr, message.from_user)
    hand = roller.hand
    ready_text = views.roll(roller, hand)
    bot.reply_to(
            message,
            ready_text,
            parse_mode='HTML'
        )
