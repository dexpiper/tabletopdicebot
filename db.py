from pony.orm import Database, set_sql_debug
from pony.orm import PrimaryKey, Required, Optional, Set
from pony.orm import db_session

from helpers import modifier_dictionary


db = Database()


class User(db.Entity):
    user_id = PrimaryKey(int, auto=False)
    chars = Set('Char')

    def active_char(self):
        return self.chars.filter(lambda x: x.active).get()

    @db_session
    def set_active_char(self, charname):
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

    def throw(self, name):
        return self.throws.filter(lambda x: x.name == name).get().formula

    def get_attribute(self, key, alias=False):
        if alias:
            by_alias = self.attributes.filter(
                lambda x: x.alias == key).get()
            if by_alias:
                return by_alias.modifier

        if not alias:
            by_name = self.attributes.filter(
                lambda x: x.name == key).get()
            if by_name:
                return by_name.modifier


class Throw(db.Entity):
    char = Required(Char)
    name = Required(str, unique=True)
    formula = Required(str)


class Attribute(db.Entity):
    char = Required(Char)
    name = Required(str)
    alias = Optional(str)
    value = Required(int)
    modifier = Optional(int)

    @staticmethod
    def get_modifier(value):
        return modifier_dictionary.get(value, 0)


db.bind(provider='sqlite', filename='dice.sqlite', create_db=True)
# db.bind(
#    provider='postgres', user='dicebot', password='12345678',
#    host='', database='postgres'
# )
db.generate_mapping(create_tables=True)
set_sql_debug(True)


if __name__ == '__main__':
    with db_session:
        alex = User(user_id=1234)
        tall = Char(owner=alex, name='Tall', active=True)
        dex = Attribute(
            char=tall, name='Dexterity', alias='DEX',
            value=20, modifier=Attribute.get_modifier(20)
        )
        throw = Throw(char=tall, name='MyThrow', formula='1d20 + $DEX')
    print('Everything should be commited by now')
