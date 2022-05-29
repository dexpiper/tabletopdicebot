import functools
import logging

from flask import current_app
from pony.orm import db_session

import views
from roller import DiceRoller
from models import User
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

    def with_info(f):
        """
        Decorator to get user and char database objects as
        child function attributes:

        @handler(...)
        @with_info
        def some_function(message, user, char):
            ...

        """
        @functools.wraps(f)
        def wrapper_with_info(*args, **kwargs):
            message = args[0]
            user_id = message.from_user.id
            user = User.get_user_by_id(user_id)
            char = user.active_char()
            new_args = args + (user, char,)
            f(*new_args, **kwargs)
        return wrapper_with_info

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
        send(message, views.hello(message.from_user.username))

    #
    # Managing user settings handlers
    #
    @handler(append_to=handlers, commands=['char', 'chars'])
    @db_session
    @with_info
    def show_user_chars_list(message, user, char):
        """
        Show charlist for user
        """
        reply(message, views.charlist(user))

    @handler(append_to=handlers, commands=['createchar'])
    @db_session
    @with_info
    def create_char(message, user, char):
        """
        Creating a char
        """
        charname = message.text[12:].strip()
        if not charname:
            send(message, views.command_help('/createchar'))
            return
        try:
            newchar = user.create_char(charname)
        except Exception as exc:
            reply(message, views.error(exc))
        else:
            answer = (
                f'{emoji["horn"]} '
                f'New char {emoji["elf"]} {newchar.name} created!\n'
                'Your /chars have been updated.'
            )
            reply(message, answer)

    @handler(append_to=handlers, commands=['deletechar'])
    @db_session
    @with_info
    def delete_char(message, user, char):
        """
        Delete char
        """
        charname = message.text[12:].strip()
        if not charname or len(charname.split()) > 1:
            # charname should be a single word
            reply(message, views.command_help('deletechar'))
            return
        try:
            user.delete_char(name=charname)
        except Exception as exc:
            reply(message, views.error(exc))
        else:
            answer = (
                f'{emoji["trashbin"]} '
                f'Char {emoji["elf"]} {charname} deleted.'
            )
            reply(message, answer)

    @handler(append_to=handlers, commands=['activechar'])
    @db_session
    @with_info
    def set_active(message, user, char):
        """
        Change active char
        """
        charname = message.text[12:].strip()
        if not charname:
            reply(message, views.command_help('activechar'))
            return
        try:
            user.set_active_char(charname)
        except Exception as exc:
            reply(message, views.error(exc))
        else:
            reply(message, views.charlist(user))

    @handler(append_to=handlers, commands=['createroll'])
    @db_session
    @with_info
    def create_throw(message, user, char):
        """
        Create custom throw
        """
        if not message.text[12:].strip():
            reply(message, views.command_help('createroll'))
            return
        query = message.text[12:].split()
        try:
            throw_name, formula = query[0], ' '.join((query[1:]))
        except IndexError:
            error_text = 'Incorrect command syntax'
            reply(message, views.command_help('createroll', error_text))
            return
        if not char:
            reply(message, views.error('You have not a char yet.'))
            return
        try:
            char.create_throw(throw_name, formula)
        except Exception as exc:
            reply(message, views.error(exc))
        else:
            reply(message, views.charlist(user))

    @handler(append_to=handlers, commands=['deleteroll', 'deletethrow'])
    @db_session
    @with_info
    def delete_throw(message, user, char):
        """
        Delete custom throw
        """
        throw_name = message.text[12:]
        if not throw_name:
            reply(message, views.command_help('deleteroll'))
            return
        if not char:
            reply(message, views.error('You have no chars. Use /createchar'))
            return
        try:
            char.delete_throw(throw_name)
        except Exception as exc:
            reply(message, views.error(exc))
        else:
            reply(message, views.charlist(user))

    @handler(append_to=handlers, commands=['addmod'])
    @db_session
    @with_info
    def create_attribute(message, user, char):
        query: list = message.text[8:].strip().split()
        if len(query) < 3 or len(query) > 4:
            if len(query):  # empty query
                error_text = 'Incorrect command syntax.'
            else:
                error_text = ''
            reply(message, views.command_help('addmod', error_text=error_text))
            return

        # getting user vars
        if len(query) == 3:
            name, alias, value = query
            mod = None
        elif len(query) == 4:
            name, alias, value, mod = query

        if not char:
            reply(message, views.error('You have no chars. Use /createchar'))
            return

        try:
            char.create_attribute(name, alias, value, mod)
        except Exception as exc:
            reply(message, views.error(exc))
        else:
            reply(message, views.charlist(user))

    @handler(append_to=handlers, commands=['deletemod'])
    @db_session
    @with_info
    def delete_attribute(message, user, char):
        name = message.text[11:].strip()
        if not name:
            reply(message, views.command_help('deletemod'))
            return
        if not char:
            reply(message, views.error('You have not a char yet. /createchar'))
            return
        try:
            char.delete_attribute(name)
        except Exception as exc:
            reply(message, views.error(exc))
        else:
            reply(message, views.charlist(user))

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
        reply(message, views.roll(roller, hand))

    @handler(append_to=handlers, commands=['rollme'])
    @db_session
    @with_info
    def roll_custom_throw(message, user, char):
        """
        Rolling pre-defined throws by name
        """
        if not char:
            reply(message, views.error('You have not a char yet. /createchar'))
            return
        throwname = message.text[7:].strip()
        formula = char.throw(throwname)
        if formula:
            roller = DiceRoller(formula, message.from_user)
            hand = roller.hand
            reply(message, views.roll(roller, hand))
        else:
            error_text = (
                f'Sorry, such Throw ({throwname}) is not '
                f'registered for your active char {char.name}'
            )
            reply(message, views.error(error_text))

    #
    # Roll shorthands commands
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


#
#
# HELPER FUNCTIONS
#
#
def reply(to_message: object, with_message: str):
    """
    Reply to given incoming message with outcoming message
    (with Telegram reply wrapper).

    * to_message: the original message object
          came to bot from user
    * with_message: answer the bot should send to
          the author of incoming_message
    """
    bot.reply_to(
            to_message,
            with_message,
            parse_mode='HTML'
        )


def send(incoming_message: object, outcoming_message: str):
    """
    Send message (without Telegram reply wrapper).

    * incoming_message: the original message object
          came to bot from user
    * outcoming_message: answer the bot should send to
          the author of incoming_message
    """
    bot.send_message(
        incoming_message.from_user.id,
        outcoming_message,
        parse_mode='HTML'
    )


def shorthand(message: object, dice: int):
    """
    Make a throw with one dice of cpecified type and
    send the roll result to the user.

    * message: the original message object
          came to bot from user
    * dice: dice type (for exaple, 1d20 dice should be described
          as 20, 1d100 as 100, etc.)
    """
    descr = message.text[8:] if dice > 9 else message.text[7:]
    roller = DiceRoller(f'/roll d{dice} ' + descr, message.from_user)
    hand = roller.hand
    reply(message, views.roll(roller, hand))
