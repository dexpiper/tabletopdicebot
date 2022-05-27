from typing import Tuple

from pony.orm import Database  # , set_sql_debug
from pony.orm import PrimaryKey, Required, Optional, Set
from pony.orm import db_session
from pony.orm.core import ObjectNotFound, TransactionIntegrityError

from common.helpers import modifier_dictionary, check_formula


db = Database()


class User(db.Entity):
    user_id = PrimaryKey(int, auto=False)
    chars = Set('Char')

    @classmethod
    @db_session
    def get_user_by_id(cls, user_id: int):
        """
        Should always be used inside handlers instead of User[1234]
        """
        try:
            return cls[user_id]
        except ObjectNotFound:
            return cls.register_user(user_id)

    @classmethod
    def register_user(cls, user_id: int):
        """
        Try to make a User with the user_id
        """
        with db_session:
            try:
                user = User(user_id=user_id)
                return user
            except TransactionIntegrityError:
                pass

    @db_session
    def active_char(self):
        """
        Return active char for current user instance
        """
        return self.chars.filter(lambda x: x.active).get()

    @db_session
    def create_char(self, name: str) -> object:
        char_exists = self.chars.filter(lambda x: x.name == name).exists()
        if char_exists:
            raise NameError(
                f'You have a char named {name} already'
                'Check your charlist with /chars'
            )
        if name[0].isdigit():
            raise ValueError(
                'Your char name must not start with a digit.'
            )
        if len(name) > 20:
            raise ValueError(
                'Your char name is too long. Max length fro names - 20.'
            )

        newchar = Char(owner=self, name=name, active=False)
        self.set_active_char(newchar.name)
        return newchar

    @db_session
    def delete_char(self, name: str) -> bool:
        char = self.chars.filter(lambda x: x.name == name).get()
        if char:
            char.delete()
            if self.chars.count():
                next_active_char = self.chars.filter().first()
                self.set_active_char(next_active_char.name)
        else:
            raise NameError(
                f'You have not a char named {name}. '
                'Check your charlist with /chars'
            )

    @db_session
    def set_active_char(self, charname):
        """
        Should be used inside try/except. Check that in any case only
        one character would be active, safe to use on already active
        character.
        """
        if not self.chars.count():
            raise IndexError('You have not any chars yet.')
        char = self.chars.filter(lambda x: x.name == charname).get()
        if not char:
            raise NameError(
                f'You have not a char named {charname}')
        if not self.active_char:
            char.active = True
        else:
            for c in self.chars:
                c.active = False
            char.active = True


class Char(db.Entity):
    owner = Required(User)
    name = Required(str)
    throws = Set('Throw')
    attributes = Set('Attribute')
    active = Required(bool, default=False)

    @db_session
    def throw(self, name: str) -> str:
        requested_throw = self.throws.filter(lambda x: x.name == name).get()
        if requested_throw:
            return requested_throw.formula

    @db_session
    def create_throw(self, throw_name: str, formula: str) -> str:
        exists = self.throw(throw_name)
        if exists:
            raise NameError(
                f'You have a roll named {throw_name} already')
        formula_ok = check_formula(formula)
        if formula_ok:
            Throw(char=self, name=throw_name, formula=formula)
            return True
        else:
            raise NameError(
                f'Formula "{formula}" is invalid or empty. Please check it')

    @db_session
    def delete_throw(self, throw_name: str):
        throw = self.throws.filter(lambda x: x.name == throw_name).get()
        if not throw:
            raise NameError(
                f'Your active char {self.name} has not a roll '
                f'named {throw_name}. Please check /chars or ask for /help'
            )
        throw.delete()
        return True

    @db_session
    def create_attribute(self, name: str, alias: str, value: str,
                         modifier: str or None = None):
        """
        Create an attribute. Note func takes only strings as arguments
        """
        common_error_message = (
                'Incorrect command. Please check the examples: '
                '/addmod Dexterity DEX 20\n'
                '/addmod Dexterity DEX 20 5\n'
            )
        if not all((name, alias, value)):
            raise ValueError(common_error_message)

        if alias[0].isdigit():
            raise ValueError('Alias must not start with a digit!')

        if name[0].isdigit():
            raise ValueError('Attribute name must not start with a digit!')

        if any((len(name) > 25, len(alias) > 8)):
            raise ValueError(
                'Attribute name or alias are too long.\n'
                'Max length for attribute name: 25, '
                'Max length for alias: 8'
            )

        if any((len(name) < 4, len(alias) < 2)):
            raise ValueError(
                'Attribute name or alias are too short.\n'
                'Min length for attribute name: 4, '
                'Min length for alias: 2'
            )

        # existence check
        _, name_exists1 = self.get_attribute_by_alias(alias)
        name_exists2 = self.get_attribute_by_name(name)
        if any([name_exists1, name_exists2]):
            raise NameError(
                f'Your active char {self.name} has already an attribute '
                f'named {name} or attribute alias {alias}. '
                'Please check /chars or ask for /help'
            )

        # values check
        try:
            value = int(value)
            if modifier:
                modifier = int(modifier)
        except ValueError:
            raise ValueError(common_error_message)
        else:
            Attribute(
                char=self, name=name, alias=alias, value=value,
                modifier=modifier or Attribute.get_modifier(15)
            )

    @db_session
    def delete_attribute(self, name: str):
        attr = self.attributes.filter(
            lambda x: x.name == name).get()
        if not attr:
            raise IndexError(
                f'Your active char {self.name} has not an '
                f'attribute called {name}. '
                'Please check /chars or ask for /help'
            )
        attr.delete()

    @db_session
    def get_attribute_by_alias(self, alias: str) -> Tuple[int, str]:
        attr = self.attributes.filter(
            lambda x: x.alias == alias).get()
        if attr:
            return attr.modifier, attr.name
        else:
            return None, None

    @db_session
    def get_attribute_by_name(self, name: str) -> int:
        by_name = self.attributes.filter(
            lambda x: x.name == name).get()
        if by_name:
            return by_name.modifier


class Throw(db.Entity):
    char = Required(Char)
    name = Required(str)
    formula = Required(str)


class Attribute(db.Entity):
    char = Required(Char)
    name = Required(str)
    alias = Optional(str)
    value = Required(int)
    modifier = Optional(int)

    @staticmethod
    def get_modifier(value: int) -> int:
        """
        Get proper modifier for given characteristic value
        """
        return modifier_dictionary.get(value, 0)


db.bind(provider='sqlite', filename='dice.sqlite', create_db=True)
# db.bind(
#    provider='postgres', user='dicebot', password='12345678',
#    host='', database='postgres'
# )
db.generate_mapping(create_tables=True)
# set_sql_debug(True)


if __name__ == '__main__':
    with db_session:
        alex = User(user_id=138946204)
        tall = Char(owner=alex, name='Tall', active=True)
        dex = Attribute(
            char=tall, name='Dexterity', alias='DEX',
            value=20, modifier=Attribute.get_modifier(20)
        )
        throw = Throw(char=tall, name='MyThrow', formula='1d20 + $DEX')
        throw2 = Throw(char=tall, name='Wisdom', formula='1d20 2d4 + 3')

        alice = Char(owner=alex, name='Alice')
        strength = Attribute(
            char=alice, name='Strength', alias='STR',
            value=15, modifier=Attribute.get_modifier(15)
        )
        throw3 = Throw(char=alice, name='MyThrow3', formula='1d20 + $DEX')
        throw4 = Throw(char=alice, name='Insight', formula='1d20 2d4 + 3')
    print('Everything should be commited by now')
