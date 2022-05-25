from models import User, Char


class DiceRoller:

    def __init__(self, raw_formula: str, telegram_user_object: object,
                 description: str = ''):
        self.formula: str = raw_formula
        self.user_id: int = telegram_user_object.id
        self.char: Char = self.get_char(self.user_id)
        self.name: str = ''
        self.description: str = description
        self.result: int = 0

        if self.char:
            self.name = self.char.name
        else:
            self.name = telegram_user_object.username

    def get_char(self, user_id):
        botuser = User.get_user_by_id(self.user_id)
        char = botuser.active_char()
        return char
