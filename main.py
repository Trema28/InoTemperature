from time import sleep
import logging

import telebot

from inotemp import InoTemperature as Ino

TOKEN = ''
ADMIN_IDS = [725320156]
FILE_IDS = 'ids.txt'
FILE_LOG = 'log.log'

with open('TOKEN') as f:
    TOKEN = f.read()

with open(FILE_IDS, 'x'):
    pass

# logging.basicConfig(
#     filename=FILE_LOG,
#     filemode='a',
#     level=logging.DEBUG)
# telebot.logger.setLevel(logging.DEBUG)

# todo get ttyUSB from args
ino = Ino('/dev/ttyUSB0', timeout=.1)
bot = telebot.TeleBot(TOKEN)

def is_admin(message):
    if message.from_user.id in ADMIN_IDS:
        return True
    return False

def id_check(message):
    if is_admin(message):
        return True

    with open(FILE_IDS) as f:
        ids = f.read().split()
    if message.from_user.id in ids:
        return True

    bot.send_message(
        message.chat.id,
        f'wrong id\n{message.from_user.id}')
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

@bot.message_handler(func=is_admin, commands=['restart'])
def command_restart(message):
    print('stopped')
    bot.stop_polling()

@bot.message_handler(func=id_check, commands=['ping'])
def command_ping(message):
    startup = ino.ping()
    d = startup // (24 * 60 * 60 * 1000)
    h = (startup // (60 * 60 * 1000)) % 60
    m = (startup // (60 * 1000)) % 60
    s = (startup // 1000) % 60
    bot.send_message(
        message.chat.id,
        f'{d} days {h:02}:{m:02}:{s:02}' + f'\n{startup}')

@bot.message_handler(func=id_check, commands=['temp'])
def command_temp(message):
    bot.send_message(message.chat.id, f'{ino.getTemperature():.3f}')

while True:
    try:
        bot.polling(interval=3, timeout=3)
    except Exception as e:
        print(e)
        sleep(2)
    else:
        print('else')
