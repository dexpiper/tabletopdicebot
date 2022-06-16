# Tabletop DiceBot

Telegram bot for rolling dices in RPG-like games with some handy advanced features. Currently available at https://t.me/tabletop_dice_bot, deployed at Heroku.

### Table of contents
* [Introduction](#introduction)
* [Technologies and libraries](#technologies-and-libraries)
* [Basic command syntax](#basic_command_syntax)
* [Advanced features](#advanced_features)
* [Examples of use](#examples-of-use)
* [Contribution to the projects](#contribution)

### Introduction

In spite of dozens dice bot exist in Telegram, few of them are suitable for online implementation of classic RPG-games that heavily depend on dice rolls. First of all, user (and Game Master) wants to roll a bunch of dices, not only 6-side cubes (d6), but also a 4-side, 8-side, 10-side etc., and such requirement cuts off the majority of simple Telegram dicebots. Furthermore, one wants to roll a handful of distinct dices and dicetypes sometimes, and get the sum. Additionally, it is useful to add some number to the result or remove some fine (positive or negative modifiers).

All this issues are taken in account in this bot. It supports multiple rolls with multiple dices and dicetypes, modifiers (+ n and - n) and roll descriptions.

New version of the bot has been presented in June, 2022. Now it can store your character attributes and modifiers and use them in rolls. Also pre-defined rolls supported.

**Basic example:** /roll 3d20 d4 + 2 *Dexterity*

```
🧝Ann rolled 3d20 d4 + 2 Dexterity:

    🎲 rolling 3d20:
    ⚡️20 + 9 + 5 = 34

    🎲 rolling 1d4:
    3 = 3

➕ 2
📋 Result: 39     -----> Dexterity
```

**Advanced example:** /roll 2d20 d6 + *$STR* - 2

```
🧝Tall rolled 2d20 d6 + $STR - 2:

    🎲 rolling 2d20:
    2 + 7 = 9

    🎲 rolling 1d6:
    4 = 4

⚙️ Strength 5
➖ 2
📋 Result: 16
```

### Technologies and libraries

Project is created with:
* Python 3.9.0
* Flask
* gunicorn
* [pyTelegramBotAPI 3.7.3](https://github.com/eternnoir/pyTelegramBotAPI)
* Jinja2
* PonyORM
* Postgres (psycopg2)
* Heroku

### Basic command syntax

**Command Syntax:**

***/roll {dice} {dice} {dice}... +/- {modifier} Description***,

where *dice* has a classic form like *2d20*: the first number is the number of dices (up to 99), and the second - the amount of sides (up to 999).

Basic **single dice rolls** can be performed with */roll d20* or simple */roll20*, number of dices (aka 1d20) is optional. *d4, d6, d8, d10, d12, d20* supported as basic dices for /roll{dice} commands.

**Addition modifiers** can be positive or negative: */roll d20 - 2, /roll d20 + 2*

**Descriptions** should be added in the end of the command string after a space character. A description should be a single word or multiple words separated with any char from the list: *@\*&%$#:*. "?" and "!" also accepted.

### Advanced features

With bot you can create a character, add your custom modifiers and use them in your throws. No need to look to your charsheet for Dexterity modifier of your char every time you roll a throw using it - just put it like:

***/roll 2d20 + $DEX***

Also you can save your time for rolling the same formula. Just save your custom throw and use it like:

***/rollme Dexterity - 2***

**Chars**

To create a char, use /createchar command + the name of your char. To delete a char, use /deletechar. After char created, you can check your charlist with /chars command.

```
🧝 Name: Ann 

    Throws:

    Attributes:

🧝 Name: Tall  ♟ 

    Throws:
            🎲 MyThrow: 2d20 + 1d8 + $DEX -2

    Attributes:
            ⚙️ Strength Alias:  $STR  Value: 20 Modifier: 5
```

Chess emoji indicates the *active char*. You can use only your active char's attributes and modifiers. To change active char, use /activechar command.

**Modifiers**

To create a modifier for your char, use /addmod command.

The command takes 3 or 4 arguments:

    * NameOfAttribute -- single world, "-" and "_" allowed. Max 25 characters long, should not start with a digit.
    * Alias -- single word, uppercase, "-" and "_" allowed. Max 8 characters long, should not start with a digit.
    * Value -- integer. Would not be used in your throws directly.
    * Modifier, optional -- integer. By default, it is computed from value with the DnD5 rule set (6 -> -2; 12 -> 1;, 25 -> 7, 30 -> 10 etc.). If you would like to apply other rules, you may specify your modifier directly from the command.

Arguments must be separated with spaces.

You may excess the modifiers:

💲 by alias (like $STR)
📎 by attribute name (like &NameOfAttribute).

Some examples:
    ***/roll 2d20 + 1d6 + $STR - 2***
    ***/roll 1d12 + 1d4 + &Dexterity + 1***

**Custom throws**

/createroll - use to create new throws (custom rolls) for your character
/rollme - to roll your custom throws

* First argument should be the name of your throw. Single word, "-" and "_" are allowed. You would type your throw name after /rollme command, so please be advised to make it short and distinguishable, so you can easily use it in your game session.
* After your argument goes your roll formula. You may use the common syntax as for the /roll command, inculding your modifiers' aliases (like $DEX).

📎 Note that you would have access only for custom rolls defined for your active character.

You can delete your custom throws with /deleteroll.


### Contribution

Dear friends, you are welcome to contribute for this project. Just create a fork and make a pull request.

### Chat group

Telegram chat group: https://t.me/dicebot_community

* Chat, suggestions, bugs and maintenance