TOKEN = ''
test_TOKEN = ''

URL = '' # URL

startmessage = '''
<b>Tabletop RPG helper - Dice Roller</b>

Version: <i>1.0</i>
Coded in: <i>Python 3.9.0</i>, <i>pyTelegramBotAPI lib</i>
For queries: <a href="tg://user?id=138946204">please write me here</a>

Bot helps rolling dices for classical RPG games. Could be added into a group.

<b>Commands:</b>

/start --> <i>show the start message</i>

/roll d20 --> <i>roll one dice</i>
/roll 2d6 + 2 --> <i>roll two d6 dices + modifier</i>
/roll 8d100 - 16 --> <i>roll eight d100 dices - modifier</i>
/roll d20 3d4 d8 - 2 Description --> <i>roll d20 + three d4 dices + one d8 dice - modifier + Description</i>

<i>Shortcuts for single dices:</i>

/roll20, /roll12, /roll10, /roll8, /roll6, /roll4

<b>Constraints:</b>
- on dices: from d1 to d999
- on the number of rolls: from 1d(x) to 99d(x)


'''