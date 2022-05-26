from typing import Tuple

from pony.orm import Database  # , set_sql_debug
from pony.orm import PrimaryKey, Required, Optional, Set
from pony.orm import db_session
from pony.orm.core import ObjectNotFound, TransactionIntegrityError

from common.helpers import modifier_dictionary


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
    def set_active_char(self, charname):
        """
        Should be used inside try/except. Check that in any case only
        one character would be active, safe to use on already active
        character.
        """
        if not self.chars.count():
            raise IndexError(f'User {self.user_id} has not any chars yet.')
        char = self.chars.filter(lambda x: x.name == charname).get()
        if not char:
            raise NameError(
                f'User {self.user_id} has not char named {charname}')
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
