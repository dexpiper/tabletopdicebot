import re
import random
from typing import List, Tuple

from models import User, Char
from common.unicode import emoji


class DiceGroup:

    def __init__(self, number: int = 1, value: int = 1):
        self.number: int = number
        self.value: int = value
        self._results: List[int] = []

    @property
    def results(self):
        if self._results:
            return self._results
        roll_results: List[int] = []
        for i in range(self.number):
            roll_results.append(random.randint(1, self.value))
        self._results = roll_results
        return self._results

    @property
    def verbose(self):
        return ' + '.join(
            [
                ''.join([emoji['lightning'], str(r)])
                if r == self.value else str(r)
                for r in self.results
            ]
        )

    @property
    def summary(self):
        return sum(self.results)

    def __repr__(self):
        return f'{self.number}d{self.value}'


class Hand:
    def __init__(self):
        self.dices: List[DiceGroup] = []
        self.attrs: List[Tuple[int, str]] = []
        self.modifiers: List[int] = []
        self.description: str = ''

    @property
    def result(self):
        dices_result = sum([sum(dg.results) for dg in self.dices])
        return (
            dices_result +
            sum([attr[0] for attr in self.attrs if attr[0]]) +
            sum(self.modifiers)
        )

    def __repr__(self):
        return (
            f'Dices: {self.dices} '
            f'Attrs: {self.attrs} '
            f'Mods: {self.modifiers} '
            f'Descr: {self.description} '
            f'Result: {self.result}'
        )


class DiceRoller:

    def __init__(self, raw_formula: str, telegram_user_object: object):
        self.formula: str = raw_formula
        self.user_id: int = telegram_user_object.id
        self.char: Char = self._get_char()
        self.name: str = ''
        self._hand: Hand = None

        if self.char:
            self.name = self.char.name
        else:
            self.name = telegram_user_object.username

    @property
    def hand(self):
        if self._hand:
            return self._hand
        else:
            self._hand = self._get_hand()
        return self._hand

    def _get_char(self) -> Char or None:
        botuser = User.get_user_by_id(self.user_id)
        char = botuser.active_char()
        return char

    def _get_hand(self) -> Hand:
        hand = Hand()
        sign = 1                             # sign in [1, -1]
        sequence = self.formula.split()

        for i, elem in enumerate(sequence):
            # dices
            dicegroup: re.Match = re.match(
                r'(\d{0,3})[d, D, д, Д](\d{1,3})', elem)
            if dicegroup:
                number = dicegroup.group(1) or 1
                hand.dices.append(
                    DiceGroup(
                        number=int(number),
                        value=int(dicegroup.group(2))
                    ))
                continue

            # modifiers
            modifier: re.Match = re.match(r'\d{1,3}', elem)
            if modifier:
                hand.modifiers.append(int(modifier.group(0))*sign)
                sign = 1
                continue

            # custom char attributes and attr aliases
            alias: re.Match = re.match(r'\$([a-zA-ZА-Яа-я\-_]{2,7})', elem)
            attr: re.Match = re.match(r'&([a-zA-ZА-Яа-я\-_]{2,25})', elem)
            if any((alias, attr)) and self.char:
                if alias:
                    alias = alias.group(1)
                    mod, name = self.char.get_attribute_by_alias(
                        alias=alias
                    )
                    hand.attrs.append((mod, name) if name else (None, alias))
                elif attr:
                    name = attr.group(1)  # without leading "& sign
                    mod = self.char.get_attribute_by_name(attr.group(1))
                    hand.attrs.append((mod, name) if name else (None, name))
                continue

            # description (last word in formula)
            if i == len(sequence) - 1:                 # if the last element
                descr: re.Match = re.match(r'[a-zA-ZА-Яа-я\-_]{3,25}', elem)
                if descr:
                    hand.description = descr.group(0)
                    break

            # deal with +/-
            if elem == '+': sign = 1         # noqa E701
            elif elem == '-': sign = -1      # noqa E701

        return hand


if __name__ == '__main__':

    from collections import namedtuple
    Tuser = namedtuple('Tuser', ['id', 'username'])
    alex = Tuser(138946204, 'dexpiper')
    roller = DiceRoller('2d20 + d6 + &Dexterity - 2 Dexterity_roll', alex)
    print(roller.hand)
    for dg in roller.hand.dices:
        print(dg, dg.results)
