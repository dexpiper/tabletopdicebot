import random
import re

class DiceRoller:
    '''
    Class to deal with dice rolls.

    Usage:

    roller = DiceRoller(message.text)
    if roller.valid:
        result = roller.dice.roll()
        ready_message_for_user = roller.dice.log

    '''

    def __init__(self, command: str):
        '''
        command - text sent by the user
        
        expecting pattern:
        '/roll <x>d<n> + <add>' (example: /roll 2d6 + 2)
        '''

        self._command = command
        self.dice = None
        self.valid = self.examine()

    def examine(self):
        '''
        Trying to check if the given command is valid for rolling,
        then store found dices and params into vars inside the 
        class instance <self.dice>
        '''
        regexes = {
            # number of rolls of a dice (2d100 ==> 2)
            'number' : r'(\d{1,2})[d, D, д, Д]\d{1,3}',
            # dice type (2d100 ==> 100)
            'dice' : r'\s\d?\d?[d, D, д, Д](\d{1,3})',
            # roll with a positive addition (2d100 + 3 ==> 3)
            'add_positive' : r'[d, D, д, Д]\d{1,3}\s?\+\s?(\d{1,3})',
            # roll with a negative addition (2d100 + 3 ==> 3)
            'add_negative' : r'[d, D, д, Д]\d{1,3}\s?-\s?(\d{1,3})',
            # description
            'description' : r'/roll.*\d\s+(\w{1,15}\s?-?\w{0,15})'
        }

        checks = {}
        variables = {}

        for name, regex in regexes.items():
            compiled = re.compile(regex)
            try:
                found_items = compiled.findall(self._command)
                if name != 'description':
                    variables[name] = int(found_items[0])
                    checks[name] = 'Y'
                else:
                    variables[name] = found_items[0]
                    checks[name] = 'Y'
            except Exception:
                checks[name] = 'N'
        
        # go through checks and store variables
        # actual dices represents by the Dice class
        if checks['dice'] == 'Y':
            if checks['number'] == 'Y':
                num = variables['number']
            else:
                num = 1
            if checks['description'] == 'Y':
                descr = variables['description']
            else:
                descr = False
            if checks['add_positive'] == 'Y':
                self.dice = Dice(
                    variables['dice'],
                    number=num,
                    description=descr,
                    addition=variables['add_positive']
                )
            elif checks['add_negative'] == 'Y':
                self.dice = Dice(
                    variables['dice'],
                    number=num,
                    description=descr,
                    addition=variables['add_negative'] * -1  # makes negative actually negative
                )
            else:
                self.dice = Dice(
                    variables['dice'],
                    number=num,
                    description=descr
                )
            return True

        # if no dice found, returning False
        else:
            return False

                

class Dice(DiceRoller):
    '''
    Class represents single dice roll
    '''
    def __init__(self, dicetype: int, number=1, addition=False, description=False):
        '''
        Represents dices and provides rolling mechanism.

        dicetype - kind of dice (d100, d20, d4 etc.), int
        number   - number of dices of a kind, int
        addition - an integer summed to result of a diceroll
        description - description of the current roll
        '''
        self.dtype = dicetype
        self.number = number
        self.addition = addition
        self.description = description
    
    def roll(self):
        if self.dtype == 1:
            self.result = 1
            self.log = 'You\'ve rolled d1. Result is <b>1</b>, what an <i>astonishing</i> surprise!'
            return self.result
        
        try_list = []
        badluck_marker_set = False

        # rolling dice, storing results in <try_list>
        for roll_try in range(self.number):

            roll_try = random.randint(1, self.dtype)
            try_list.append(roll_try)

            # whether to mark the ones (1) in rolls or not
            if roll_try == 1 and self.dtype >= 6:
                badluck_marker_set = True
        
        # constructing log
        self.log = self.log_constructor(
            try_list, 
            addition=self.addition, 
            crit=self.dtype,
            badluck_marker=badluck_marker_set,
            description=self.description
            )
        
        # checking the sum
        if self.addition:
            self.result = sum(try_list) + self.addition
        else:
            self.result = sum(try_list)

        # returning out with a result
        return self.result

    @staticmethod
    def log_constructor(
        list_of_rolls: list, 
        addition=False, 
        crit=False, 
        badluck_marker=False, 
        description=False):
        '''
        Method for constructing ready-to-use line:

        5 + <b>20!</b> + <b>1...</b> - <i>2*</i> = <b>23</b>

        '''
        ready_log_string = ''

        # adding first roll result
        ready_log_string = ' ' + str(list_of_rolls[0])

        # adding other results
        if len(list_of_rolls) > 1 or addition:
            for i in range(1, len(list_of_rolls)):
                ready_log_string += ' + {}'.format(list_of_rolls[i])
            if addition:
                if addition >= 0:
                    ready_log_string += ' + <i>{}*</i>'.format(addition)
                else:
                    ready_log_string += ' - <i>{}*</i>'.format(abs(addition))
                summ = sum(list_of_rolls) + addition
            else:
                summ = sum(list_of_rolls)
            ready_log_string += ' = <b>{}</b>'.format(summ)

        # adding space char to assert single roll crit would be detected
        else:
            ready_log_string += ' '

        # marking critical damage
        if crit:
            if (str(crit) in ready_log_string) and (
            '<b>' + str(crit) not in ready_log_string):
                ready_log_string = ready_log_string.replace(
                    str(crit) + ' ',                            # space here is mandatory
                    ''.join(('<b>', str(crit), '!', '</b>', ' '))
                )

        # if the dice type is d6 and higher, marking badluck rolls
        if badluck_marker:
            if ' 1 ' in ready_log_string:
                ready_log_string = ready_log_string.replace(
                    ' 1 ',
                    ''.join((' ', '<b>', '1', '...', '</b>', ' '))
                )

        if description:
            ready_log_string += ' --> <b>{}</b>'.format(description)

        return ready_log_string


    def __repr__(self):
        if self.addition:
            if self.addition < 0:
                return '%sd%s - %s' % (self.number, self.dtype, abs(self.addition))
            else:
                return '%sd%s + %s' % (self.number, self.dtype, self.addition)
        else:
            return '%sd%s' % (self.number, self.dtype)

# for testing usage only
if __name__ == '__main__':

    roller = DiceRoller('/roll д20-1 teststring')
    if roller.valid:
        print(roller.dice)
        result = roller.dice.roll()
        ready_message_for_user = roller.dice.log
        print(ready_message_for_user)
    else:
        print('Mistake has occured')