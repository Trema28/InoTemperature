from sys import argv
from datetime import timedelta

import telebot

import filefuncs
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
    print(ADMINS, USERS)
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
            bot.send_message(i, text, parse_mode='Markdown')

        text = 'wait till admin adds you'
        bot.send_message(message.chat.id, text)

@bot.message_handler(func=id_check, commands=['help'])
def command_start(message):
    text = ('/start - nothing for registered users\n'
            '/help - sends this message\n'
            '/time - get bot running time\n'
            '/temp - get temperatures from sensors\n')
    if is_admin(message):
        text += (
            '/queue - sends a list of unregistered users\n'
            '/all - sends a list of all registered users\n'
            '/adduser id [id ...]\n'
            '/addadmin id [id ...]\n'
            '/del id [id ...]')
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=id_check, commands=['time'])
def command_ping(message):
    text = str(timedelta(milliseconds=ino.ping())).rsplit('.', 1)[0]
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=id_check, commands=['temp'])
def command_temp(message):
    text = ''.join(
                f'{n}: {i}°C\n' for n, i in
                    enumerate(ino.get_temperatures(), start=1))
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=is_admin, commands=['queue'])
def command_temp(message):
    text = ''.join(f'@{i[1]}:`{i[0]}`' for i in QUEUE)
    text = 'queue:\n' + text

    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=is_admin, commands=['all'])
def command_temp(message):
    t = ''.join(f'@{n}:`{i}`' for i, n in zip(*ADMINS))
    text = 'admins:\n' + t

    t = ''.join(f'@{n}:`{i}`' for i, n in zip(*USERS))
    text += '\n\nusers:\n' + t

    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=is_admin, commands=['adduser'])
def command_temp(message):
    ids = message.text.split(' ')

    if len(ids) <= 1:
        text = 'id is required'
        bot.send_message(message.chat.id, text)
        return

    ids.pop(0)

    queue = [*zip(*QUEUE)]

    text = ''
    for i in ids:
        if i not in queue[0]:
            text = 'id is not in queue ' + i + '\n'
            continue

        if i in USERS[0] or i in ADMINS[0]:
            text = 'id already exists ' + i + '\n'
            continue

        index = queue[0].index(i)
        username = queue[1][index]
        filefuncs.write_id(FILE_USERS, i, username)
        USERS[0].append(i)
        USERS[1].append(username)

        text = 'user added ' + i + '\n'

    bot.send_message(message.chat.id, text)

@bot.message_handler(func=is_admin, commands=['addadmin'])
def command_temp(message):
    ids = message.text.split(' ')

    if len(ids) <= 1:
        text = 'id is required'
        bot.send_message(message.chat.id, text)
        return

    ids.pop(0)

    queue = [*zip(*QUEUE)]

    text = ''
    for i in ids:
        if i not in queue[0]:
            text += 'id is not in queue ' + i + '\n'
            continue

        if i in ADMINS[0]:
            text += 'id already exists ' + i + '\n'
            continue

        index = queue[0].index(i)
        username = queue[1][index]
        filefuncs.write_id(FILE_ADMINS, i, username)
        ADMINS[0].append(i)
        ADMINS[1].append(username)

        text += 'admin added ' + i + '\n'

    bot.send_message(message.chat.id, text)

@bot.message_handler(func=is_admin, commands=['del'])
def command_temp(message):
    ids = message.text.split(' ')

    if len(ids) <= 1:
        text = 'id is required'
        bot.send_message(message.chat.id, text)
        return

    ids.pop(0)

    filefuncs.delete_id([FILE_ADMINS, FILE_USERS], ids)

    ADMINS.clear()
    ADMINS.extend(filefuncs.read_ids(FILE_ADMINS))
    USERS.clear()
    USERS.extend(filefuncs.read_ids(FILE_USERS))

    print(ADMINS, USERS)

    text = 'done'
    bot.send_message(message.chat.id, text)

bot.infinity_polling(timeout=60, long_polling_timeout=60*5)
