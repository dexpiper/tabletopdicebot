# Tabletop DiceBot

Telegram bot for rolling dices in RPG-like games with some handy advanced features.
Currently available at https://t.me/tabletop_dice_bot, deployed at Heroku.

### Table of contents
* [Introduction](#introduction)
* [Technologies and libraries](#technologies-and-libraries)
* [Scope of functionalities](#scope-of-functionalities)
* [Examples of use](#examples-of-use)

### Introduction

In spite of dozens dice bot exist in Telegram, few of them are suitable for online implementation of classic RPG-games that heavily depend on dice rolls. First of all, user (and Game Master) wants to roll a bunch of dices, not only 6-side cubes (d6), but also a 4-side, 8-side, 10-side etc., and such requirement cuts off the majority of simple Telegram dicebots. Furthermore, one wants to roll a handful of distinct dices and dicetypes sometimes, and get the sum. Additionally, it is useful to add some number to the result or remove some fine (positive or negative modifiers).

All this issues are taken in account in this bot. It supports multiple rolls with multiple dices and dicetypes, modifiers (+ n and - n) and roll descriptions.

**Example:** /roll 3d20 d4 + 2 *Dexterity*

```@username rolled 3d20 1d4  + 2 ----> Dexterity:

🎲 1: rolling 3d20:
 ⚡️20! + 6 + 13 = 39
🎲 2: rolling 1d4: ---> 1
➕ Modifier: + 2
📋 Result: 42
```

### Technologies and libraries

Project is created with:
* Python 3.9.0
* Flask
* [pyTelegramBotAPI 3.7.3](https://github.com/eternnoir/pyTelegramBotAPI)
* Heroku

### Scope of functionalities

**Command Syntax:**

*/roll {dice} {dice} {dice}... + 2 Description*,
where *dice* has a classic form like *2d20*: the first number is the number of dices (up to 99), and the second - the amount of sides (up to 999).

Basic **single dice rolls** can be performed with */roll d20* or simple */roll20*, number of dices (aka 2d20) is optional. *d4, d6, d8, d10, d12, d20* supported as basic dices for /roll{dice} commands.

**Addition modifiers** can be positive or negative: */roll d20 - 2, /roll d20 + 2*

**Descriptions** should be added in the end of the command string after a space character. A description should be a single word or multiple words separated with any char from the list: *@\*&%$#:*. "?" and "!" also accepted.

### Examples of use

**/roll d20** or **/roll20**

```@username rolled 1d20  :
🎲 ---> 12
📋 Result: 12
```

**/roll 2d20 + 2 Description**

```@username rolled 2d20  + 2 ----> Description:
🎲 --->   19 + 15 = 34
➕ Modifier: + 2
📋 Result: 36
```

**/roll 2d20 d8 2d4 - 4 Description**

```@username rolled 2d20 1d8 2d4  - 4 ----> Description:

🎲 1: rolling 2d20:
 ⚡️20! + 15 = 35
🎲 2: rolling 1d8: ---> 8
🎲 3: rolling 2d4:
 3 + 3 = 6
➖ Modifier: - 4
📋 Result: 45
```
