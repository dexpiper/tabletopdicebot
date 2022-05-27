import functools
import logging

from flask import current_app
from pony.orm import db_session

import views
from roller import DiceRoller
from models import User, Char, Throw, Attribute  # noqa F401
from common.unicode import emoji


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

    @handler(append_to=handlers, commands=['createchar'])
    @db_session
    def create_char(message):
        """
        Creating a char
        """
        charname = message.text[12:].strip()
        if not charname:
            command_help = (
                '/createchar Charname'
            )
            bot.send_message(
                message.from_user.id,
                views.command_help(command_help),
                parse_mode='HTML'
            )
            return
        user_id = message.from_user.id
        user = User.get_user_by_id(user_id)
        try:
            newchar = user.create_char(charname)
        except Exception as exc:
            bot.reply_to(
                message,
                views.error(exc),
                parse_mode='HTML'
            )
        else:
            bot.reply_to(
                message,
                f'{emoji["horn"]} '
                f'New char {emoji["elf"]} {newchar.name} created!\n'
                'Your /chars have been updated.',
                parse_mode='HTML'
            )

    @handler(append_to=handlers, commands=['deletechar'])
    @db_session
    def delete_char(message):
        """
        Delete char
        """
        charname = message.text[12:].strip()
        if not charname:
            command_help = (
                '/deletechar Charname'
            )
            bot.send_message(
                message.from_user.id,
                views.command_help(command_help),
                parse_mode='HTML'
            )
            return
        user_id = message.from_user.id
        user = User.get_user_by_id(user_id)
        try:
            user.delete_char(name=charname)
        except Exception as exc:
            bot.reply_to(
                message,
                views.error(exc),
                parse_mode='HTML'
            )
        else:
            bot.reply_to(
                message,
                f'{emoji["trashbin"]} '
                f'Char {emoji["elf"]} {charname} deleted.',
                parse_mode='HTML'
            )

    @handler(append_to=handlers, commands=['activechar'])
    @db_session
    def set_active(message):
        """
        Change active char
        """
        charname = message.text[12:].strip()
        if not charname:
            command_help = (
                '/activechar Charname'
            )
            bot.send_message(
                message.from_user.id,
                views.command_help(command_help),
                parse_mode='HTML'
            )
            return
        user_id = message.from_user.id
        user = User.get_user_by_id(user_id)
        try:
            user.set_active_char(charname)
        except Exception as exc:
            bot.reply_to(
                message,
                views.error(exc),
                parse_mode='HTML'
            )
        else:
            ready_text = views.charlist(user)
            bot.reply_to(
                    message,
                    ready_text,
                    parse_mode='HTML'
                )

    @handler(append_to=handlers, commands=['createroll'])
    @db_session
    def create_throw(message):
        """
        Create custom throw
        """
        query = message.text[12:].split()
        try:
            throw_name, formula = query[0], ' '.join((query[1:]))
        except IndexError:
            error_text = (
                'Check if you entered the command correctly:\n\n'
                'Example: \n'
                '/createroll MyThrow 2d20 + 1d8 + $DEX'
            )
            bot.reply_to(
                message,
                views.error(error_text),
                parse_mode='HTML'
            )
            return
        user_id = message.from_user.id
        user = User.get_user_by_id(user_id)
        char = user.active_char()
        if not char:
            bot.reply_to(
                message,
                views.error('You have not a char yet.'),
                parse_mode='HTML'
            )
            return
        try:
            char.create_throw(throw_name, formula)
        except Exception as exc:
            bot.reply_to(
                message,
                views.error(exc),
                parse_mode='HTML'
            )
        else:
            ready_text = views.charlist(user)
            bot.reply_to(
                    message,
                    ready_text,
                    parse_mode='HTML'
                )

    @handler(append_to=handlers, commands=['deleteroll'])
    @db_session
    def delete_throw(message):
        """
        Delete custom throw
        """
        throw_name = message.text[12:]
        if not throw_name:
            error_text = (
                'Check if you entered the command correctly:\n\n'
                'Example: \n'
                '/deleteroll MyThrow'
            )
            bot.reply_to(
                message,
                views.error(error_text),
                parse_mode='HTML'
            )
            return
        user_id = message.from_user.id
        user = User.get_user_by_id(user_id)
        char = user.active_char()
        if not char:
            bot.reply_to(
                message,
                views.error('You have not a char yet.'),
                parse_mode='HTML'
            )
            return
        try:
            char.delete_throw(throw_name)
        except Exception as exc:
            bot.reply_to(
                message,
                views.error(exc),
                parse_mode='HTML'
            )
        else:
            ready_text = views.charlist(user)
            bot.reply_to(
                    message,
                    ready_text,
                    parse_mode='HTML'
                )

    @handler(append_to=handlers, commands=['addmod'])
    @db_session
    def create_attribute(message):
        query: list = message.text[8:].split()
        if len(query) < 3 or len(query) > 4:
            error_message = (
                'Incorrect command. Please check the examples: '
                '/addmod Dexterity DEX 20\n'
                '/addmod Dexterity DEX 20 5\n\n'
                'The command takes 3 or 4 arguments:\n'
                '1) NameOfAttribute (single_world!), 2) Alias, 3) Value and '
                '4) Modifier (optional)\n'
                'Arguments must be separated with spaces'
            )
            bot.reply_to(
                message,
                views.error(error_message),
                parse_mode='HTML'
            )
            return

        # getting user vars
        if len(query) == 3:
            name, alias, value = query
            mod = None
        elif len(query) == 4:
            name, alias, value, mod = query

        user_id = message.from_user.id
        user = User.get_user_by_id(user_id)
        char = user.active_char()
        if not char:
            bot.reply_to(
                message,
                views.error('You have not a char yet.'),
                parse_mode='HTML'
            )
            return

        try:
            char.create_attribute(name, alias, value, mod)
        except Exception as exc:
            bot.reply_to(
                message,
                views.error(exc),
                parse_mode='HTML'
            )
        else:
            ready_text = views.charlist(user)
            bot.reply_to(
                    message,
                    ready_text,
                    parse_mode='HTML'
                )

    @handler(append_to=handlers, commands=['deletemod'])
    @db_session
    def delete_attribute(message):
        name: list = message.text[11:]
        user_id = message.from_user.id
        user = User.get_user_by_id(user_id)
        char = user.active_char()
        if not char:
            bot.reply_to(
                message,
                views.error('You have not a char yet.'),
                parse_mode='HTML'
            )
            return
        try:
            char.delete_attribute(name)
        except Exception as exc:
            bot.reply_to(
                message,
                views.error(exc),
                parse_mode='HTML'
            )
        else:
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
