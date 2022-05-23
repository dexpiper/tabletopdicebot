import random
import re
from collections import namedtuple


def rolling(message, bot, formula='', roller=False):
    """
    TODO: rewrite roller
    """
    if not roller:
        if formula:
            roller = DiceRoller(formula)
        else:
            roller = DiceRoller(message.text)

    username = message.from_user.username

    if roller.valid:
        # rolling dice, constructing raw log message
        result = roller.roll()
        the_log = roller.log

        # cooking answer
        if roller.addition and roller.addition > 0:
            mod = '\U00002795 <b>Modifier: + {}</b>'.format(roller.addition)
        elif roller.addition and roller.addition < 0:
            mod = '\U00002796 <b>Modifier: - {}</b>'.format(
                abs(roller.addition)
            )
        else:
            mod = ''

        if roller.description:
            descr = '<b>----> {}</b>'.format(roller.description)
        else:
            descr = ''

        ready_message_for_user = (
            '@{username} rolled <b><i>{dice}</i></b> {descr}:\n'
            '{log}{mod}\n'
            '\U0001F4CB <b>Result:</b> <b>{result}</b>'
            ).format(
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
        if not formula:
            ready_message_for_user = (
                '\U0001F6D1 <b>Sorry, this format is not acceptable.</b>\n'
                '<i>Check the example:</i> <b>2d100 + 2</b>'
            )
        else:
            ready_message_for_user = (
                f'\U0001F6D1 <b>Sorry, this format {formula} '
                'is not acceptable.</b>\n'
                '<i>Check the example:</i> <b>2d100 + 2</b>'
            )
        bot.reply_to(
            message,
            ready_message_for_user,
            parse_mode='HTML'
            )


class StringConstructor:
    """
    Class for constructing log strings
    """
    def __init__(self):
        self.log = ''

    def append(self, arg, ends=False):
        self.log += arg
        if ends:
            self.log += ends

    def replace(self, old, new):
        self.log = self.log.replace(old, new)

    def __repr__(self):
        return self.log


class DiceRoller:
    """
    Class to deal with dice rolls.

    Usage:

    roller = DiceRoller(message.text)
    if roller.valid:
        result = roller.dice.roll()
        ready_message_for_user = roller.dice.log

    """
    # Dice object represented as collections.namedtuple
    Dice = namedtuple('Dice', 'dice, number')

    def __init__(self, command: str):
        """
        command - text sent by the user

        expected pattern:
        '/roll <x>d<n> (<x>d<n>...) + <add> + <description>'
        Example: /roll 2d6 1d20 - 2 Dexterity
        """

        self._command = command + ' '
        self.dices = False
        self.description = False
        self.addition = False
        self.valid = self.examine()
        self.result = False
        self.log = StringConstructor()

    def examine(self):
        """
        Founds variables in the command sent by the user, returns True
        if the command is valid
        """

        regexes = {
            # regex for every dice in a command
            'dices': r'(\s\d?\d?[d, D, д, Д]\d{1,3})',
            # roll with a positive addition (2d100 + 3 ==> 3)
            'add_positive': r'[d, D, д, Д]\d{1,3}\s?\+\s?(\d{1,3})',
            # roll with a negative addition (2d100 + 3 ==> 3)
            'add_negative': r'[d, D, д, Д]\d{1,3}\s?-\s?(\d{1,3})',
            # description
            'description': r'/roll.*\s([a-zA-Zа-яА-Я!]{1,15}\s?[-_!\?@\*&%$#:\\/]?[a-zA-Zа-яА-Я!]{0,15})\s'  # noqa E501
        }

        checks = {}
        variables = {}

        for name, regex in regexes.items():
            compiled = re.compile(regex)
            try:
                found_items = compiled.findall(self._command)
                if name == 'dices':
                    if len(found_items) != 0:
                        variables['dices'] = found_items
                        checks['dices'] = 'Y'
                    else:
                        checks['dices'] = 'N'
                        return False
                if name != 'description':
                    variables[name] = int(found_items[0])
                    checks[name] = 'Y'
                else:
                    variables[name] = found_items[0]
                    checks[name] = 'Y'
            except Exception:
                checks[name] = 'N'

        # extract dices, build Dice class entities and store them
        dices_regexes = {
            # number of rolls of a dice (2d100 ==> 2)
            'number': r'(\d{1,2})[d, D, д, Д]\d{1,3}',
            # dice type (2d100 ==> 100)
            'dice': r'\s\d?\d?[d, D, д, Д](\d{1,3})'
            }

        self.dices = []
        for dice in variables['dices']:
            future_dice = {}
            for name, regex in dices_regexes.items():
                compiled = re.compile(regex)
                try:
                    future_dice[name] = int(compiled.findall(dice)[0])
                except Exception:
                    if name == 'number':
                        future_dice[name] = 1
                    else:
                        checks['dices'] = 'N'
                        return False

            # then we append a Dice instance in the class var <self.dices>
            self.dices.append(
                self.Dice._make(
                    [future_dice['dice'], future_dice['number']]
                    )
            )

        # adding addtition (modifier) and description, if there is any
        if checks['description'] == 'Y':
            self.description = variables['description']
        if checks['add_positive'] == 'Y':
            self.addition = variables['add_positive']
        if checks['add_negative'] == 'Y':
            self.addition = variables['add_negative'] * -1

        return True

    def __repr__(self):
        if not self.dices:
            return 'No dices have been found'
        string = ''
        for dice in self.dices:
            string += '%sd%s ' % (dice.number, dice.dice)
        if self.addition:
            if self.addition < 0:
                string += ' - %s' % (abs(self.addition))
            else:
                string += ' + %s' % (self.addition)
        return string

    def roll(self):
        """
        Rolling dices, adding modifiers and description (if provided)
        and constructing log
        """
        self.result = 0
        if len(self.dices) == 1:
            counter = False
        else:
            counter = 0

        for dice in self.dices:
            if counter is not False:
                counter += 1

            # dealing with d1 dice
            if dice.dice == 1:
                self.log.append((
                    '<b>Wow.</b>You\'ve rolled d1. '
                    'Result is <b>1</b>, what '
                    'an <i>astonishing</i> surprise!'), ends='\n')

            # setup
            try_list = []
            badluck_marker_set = False
            if self.dices.index(dice) == len(self.dices) - 1:  # if last dice
                end_marker = True
            else:
                end_marker = False

            # rolling dice, storing results in <try_list>
            for roll_try in range(dice.number):
                roll_try = random.randint(1, dice.dice)
                try_list.append(roll_try)

                # whether to mark the ones (1) in rolls or not
                if roll_try == 1 and dice.dice >= 6 and not badluck_marker_set:
                    badluck_marker_set = True
                else:
                    badluck_marker_set = False

            # constructing log of current dice
            self.log.append(
                self.log_constructor(
                  try_list,
                  crit=dice.dice,
                  badluck_marker=badluck_marker_set,
                  count=counter,
                  end_marker=end_marker
                  )
            )

            # adding the sum of all the rolls to the current result
            self.result += sum(try_list)

            ##############
            # end of cycle

        # adding modifier and description
        if self.addition:
            self.result += self.addition

        # returning out with a result
        return self.result

    @staticmethod
    def log_constructor(
            list_of_rolls: list,
            crit=False,
            badluck_marker=False,
            count=False,
            end_marker=False):
        """
        Constructing log for a single dice roll
        """
        log_string = StringConstructor()
        if count:
            log_string.append('\U0001F3B2 <b>%s:</b> <i>rolling %sd%s:</i>' % (
                count, len(list_of_rolls), crit
                )
            )

        # adding first roll result
        if len(list_of_rolls) == 1 and count:
            log_string.append(' ---> <b>{}</b>'.format(str(list_of_rolls[0])))
        elif len(list_of_rolls) == 1:
            log_string.append(
                '\U0001F3B2 ---> <b>{}</b>'.format(str(list_of_rolls[0])))

        # adding other results
        elif len(list_of_rolls) > 1:
            if not count:
                log_string.append(
                    '\n\U0001F3B2 --->   ' + str(list_of_rolls[0]))
            else:
                log_string.append('\n ' + str(list_of_rolls[0]))
            for i in range(1, len(list_of_rolls)):
                log_string.append(' + {}'.format(list_of_rolls[i]))

            log_string.append(' = <b>{}</b>'.format(
                sum(list_of_rolls))
                )

        log_string.append('', ends='\n\n')

        # marking critical damage
        if crit:
            if str(crit) in log_string.log and (
                    '<b>' + str(crit) not in log_string.log) and (
                    'd1' not in log_string.log):
                log_string.replace(
                    str(crit) + ' ',  # space here is mandatory
                    ''.join(('\U000026A1', '<b>', str(crit), '!', '</b>', ' '))
                )

        # if the dice type is d6 and higher, marking badluck rolls
        if badluck_marker:
            if ' 1 ' in log_string.log:
                log_string.replace(
                    ' 1 ',
                    ''.join((' ', '<b>', '1', '...', '</b>', ' '))
                )

        return log_string.log
