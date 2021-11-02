from sys import argv
from os.path import exists
from datetime import timedelta

import telebot

from inotemp import InoTemperature as Ino

TOKEN = ''

FILE_TOKEN = 'TOKEN.txt'
FILE_ADMINS = 'admins.txt'
FILE_USERS = 'users.txt'

PORT = None

if len(argv) > 1:
    PORT = argv[1]

for i in [FILE_TOKEN, FILE_ADMINS, FILE_USERS]:
    if not exists(i):
        with open(i, 'x'):
            pass
        print('file created: ' + i)

with open('TOKEN.txt') as f:
    TOKEN = f.read().strip()

if not TOKEN:
    print('write the TOKEN in ' + FILE_TOKEN)
    exit(1)

bot = telebot.TeleBot(TOKEN)

def read_ids_file(file):
    with open(file) as f:
        ids = f.read().strip().split('\n')
    return ids

def is_admin(message):
    if str(message.from_user.id) in read_ids_file(FILE_ADMINS):
        return True
    return False

def is_user(message):
    if str(message.from_user.id) in read_ids_file(FILE_USERS):
        return True
    return False

def id_check(message):
    if is_admin(message) or is_user(message):
        return True

    bot.send_message(
        message.chat.id,
        f'wrong id: {message.from_user.id}')

    for i in read_ids_file(FILE_ADMINS):
        bot.send_message(
            i,
            f'user messaged the bot: {message.from_user.id}\n'
          + 'use /adduser or /addadmin')

    # todo add registration
    return False

@bot.message_handler(func=id_check, commands=['start', 'help'])
def command_start(message):
    print(message.text)
    bot.send_message(
        message.chat.id,
        '/ping - get time since launch\n'
        '/temp - get temperature from sensor',
        timeout=1)

@bot.message_handler(func=is_admin, commands=['stop'])
def command_restart(message):
    print('stopped')
    bot.stop_polling()

@bot.message_handler(func=id_check, commands=['ping'])
def command_ping(message):
    start_time = ino.ping()
    bot.send_message(
        message.chat.id,
        str(timedelta(milliseconds=start_time)).rsplit('.', 1)[0])

@bot.message_handler(func=id_check, commands=['temp'])
def command_temp(message):
    bot.send_message(message.chat.id, f'{ino.get_temperature():.2f} °C')


# ino = Ino('/dev/ttyUSB0')
ino = Ino(PORT)

bot.infinity_polling(timeout=60, long_polling_timeout=60*5)
