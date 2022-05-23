import functools
import logging

from flask import current_app
from pony.orm import db_session
from pony.orm.core import ObjectNotFound

from roller import DiceRoller, rolling
from db import User, Char, Throw, Attribute  # noqa F401


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

    #
    # Service handlers
    #
    @handler(append_to=handlers, commands=['start'])
    def answer_start(message):
        """
        Bot sends welcome message
        """
        bot.send_message(
            message.chat.id,
            'Hello! This is beta-version of TabletopDiceBot!',
            parse_mode='HTML'
        )

    #
    # Managing user settings handlers
    #
    @handler(append_to=handlers, commands=['chars'])
    @db_session
    def show_user_chars_list(message):
        """
        Show charlist for user
        """
        user_id = message.from_user.id
        try:
            user = User[user_id]
        except ObjectNotFound:
            bot.reply_to(
                message,
                '\U0001F6D1 <b>Sorry, you are not registered</b>',
                parse_mode='HTML'
            )
            return
        if not len(user.chars):
            bot.reply_to(
                message,
                '\U0001F6D1 <b>Sorry, you have no chars</b>',
                parse_mode='HTML'
            )
            return

        descrs = []
        for char in user.chars:
            active = '   (<b>ACTIVE</b>)' if char.active else ''
            throws = []
            attributes = []
            if len(char.throws):
                for throw in char.throws:
                    throw_description = (
                        f'\U0001F3B2 {throw.name}: <i>{throw.formula}</i>\n'
                    )
                    throws.append(throw_description)
            if len(char.attributes):
                for attr in char.attributes:
                    attr_description = (
                        f'\U00003030 <b>{attr.name}</b> '
                        f'(${attr.alias or "NO_ALIAS"}): '
                        f'<i>{attr.value}</i> '
                        f'Modifier: <b>{attr.modifier}</b>\n\n'
                    )
                    attributes.append(attr_description)
            char_description = (
                f'\U0001F9DD <b>Name:</b> {char.name} '
                f'{active}\n\n'
                '<b>Throws</b>: \n'
                f'{"".join(throws)}\n'
                '<b>Attributes:</b> \n'
                f'{"".join(attributes)}\n\n'
            )
            descrs.append(char_description)

        bot.reply_to(
                message,
                '/n'.join(descrs),
                parse_mode='HTML'
            )

    #
    # Rolls handlers
    #
    @handler(append_to=handlers, commands=['roll'])
    def roll_anything(message):
        """
        Answering to the /roll command
        """
        rolling(message, bot)

    @handler(append_to=handlers, commands=['rollme'])
    @db_session
    def roll_custom_throw(message):
        """
        Rolling pre-defined throws by name
        """
        user_id = message.from_user.id
        try:
            user = User[user_id]
        except ObjectNotFound:
            bot.reply_to(
                message,
                '\U0001F6D1 <b>Sorry, you are not registered</b>',
                parse_mode='HTML'
            )
            return
        userchar = user.active_char()
        if userchar:
            throwname = message.text[7:].strip()
            formula = userchar.throw(throwname)
        if formula:
            rolling(message, bot, formula=' ' + formula)
        else:
            bot.reply_to(
                message,
                f'\U0001F6D1 <b>Sorry, such Throw ({throwname}) is not '
                f'registered for your active char {userchar.name}</b>',
                parse_mode='HTML'
            )

    #
    # Roll shorthands
    #
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
