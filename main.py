from sys import argv
from datetime import timedelta

import telebot

from utils import filefuncs
from inotemp import InoTemperature as Ino

TOKEN = ''

FILE_TOKEN = 'TOKEN.txt'
FILE_ADMINS = 'admins.txt'
FILE_USERS = 'users.txt'

PORT = None

if not PORT and len(argv) > 1:
    PORT = argv[1]

filefuncs.create_files([FILE_TOKEN, FILE_ADMINS, FILE_USERS])

if not TOKEN:
    TOKEN = filefuncs.read_token(FILE_TOKEN)

if not TOKEN:
    exit(1)

ino = Ino(PORT)
bot = telebot.TeleBot(TOKEN, threaded=False)

ADMINS = filefuncs.read_ids(FILE_ADMINS)
USERS = filefuncs.read_ids(FILE_USERS)

QUEUE = []

def save_admin(user_id, username):
    filefuncs.write_id(FILE_ADMINS, user_id, username)
    ADMINS[0].append(str(user_id))
    ADMINS[1].append(username)

def save_user(user_id, username):
    filefuncs.write_id(USERS, user_id, username)
    USERS[0].append(str(user_id))
    USERS[1].append(username)

def is_admin(message):
    if str(message.from_user.id) in ADMINS[0]:
        return True
    return False

def is_user(message):
    if str(message.from_user.id) in USERS[0]:
        return True
    return False

def id_check(message):
    if is_admin(message) or is_user(message):
        return True
    return False

@bot.message_handler(commands=['start'])
def command_start(message):
    if id_check(message):
        return

    user_id = message.from_user.id
    username = message.from_user.username

    if not ADMINS[0]:
        save_admin(user_id, username)

        text = 'hello admin'
        bot.send_message(message.chat.id, text)

    elif user_id not in QUEUE:
        QUEUE.append([user_id, username])

        text = (f'@{username}:`{user_id}` messaged the bot\n'
             + 'use /adduser, /addadmin or ignore it')
        for i in ADMINS[0]:
            bot.send_message(i, text, parse_mode="Markdown")

        text = 'wait till admin adds you'
        bot.send_message(message.chat.id, text)

@bot.message_handler(func=id_check, commands=['help'])
def command_start(message):
    text = ('/start\n'
          + '/time - get bot running time\n'
          + '/temp - get temperature from sensors\n'
          + '/queue\n'
          + '/all\n'
          + '/adduser id [id ...]\n'
          + '/addadmin id [id ...]\n'
          + '/del id [id ...]')
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=id_check, commands=['time'])
def command_ping(message):
    text = str(timedelta(milliseconds=ino.ping())).rsplit('.', 1)[0]
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=id_check, commands=['temp'])
def command_temp(message):
    text = ''.join(
                f'{n + 1}: {i}°C\n' for n, i in
                    enumerate(ino.get_temperatures()))
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=is_admin, commands=['queue'])
def command_temp(message):
    # todo
    text = 'done'
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=is_admin, commands=['all'])
def command_temp(message):
    # todo
    text = 'done'
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=is_admin, commands=['adduser'])
def command_temp(message):
    ...
    # todo
    # ids = message.text.split(' ')

    # if len(ids) <= 1:
    #     text = 'id is required'
    #     bot.send_message(message.chat.id, text)
    #     return

    # ids.pop(0)

    # try:
    #     ids = map(int, ids)
    # except ValueError:
    #     text = 'bad id'
    #     bot.send_message(message.chat.id, text)
    #     return

    # for i in ids:
    #     if i not in [*zip(*QUEUE)][0]:
    #         text = 'id is not in queue ' + i
    #         bot.send_message(message.chat.id, text)
    #         continue

    #     filefuncs.write_id(FILE_USERS, i, username)

    # text = 'done'
    # bot.send_message(message.chat.id, text)

@bot.message_handler(func=is_admin, commands=['addadmin'])
def command_temp(message):
    # todo
    text = 'done'
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=is_admin, commands=['del'])
def command_temp(message):
    # todo
    text = 'done'
    bot.send_message(message.chat.id, text)

bot.infinity_polling(timeout=60, long_polling_timeout=60*5)
