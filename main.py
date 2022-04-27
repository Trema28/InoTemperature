from sys import argv

from telebot import TeleBot

from database import DataBase
from inotemp import InoTemperature as Ino
from bot import set_handlers

TOKEN = ''
OWNER_ID = ''
PORT = ''

FILE_TOKEN = 'TOKEN.txt'
FILE_OWNER_ID = 'OWNER_ID.txt'
FILE_DB = 'database.db'

if TOKEN == '':
    try:
        with open(FILE_TOKEN) as f:
            TOKEN = f.read().strip()
    except FileNotFoundError:
        with open(FILE_TOKEN, 'x'):
            pass

    assert TOKEN, '!!! need token !!!'

if OWNER_ID == '':
    try:
        with open(FILE_OWNER_ID) as f:
            OWNER_ID = f.read().strip()
    except FileNotFoundError:
        with open(FILE_OWNER_ID, 'x'):
            pass

if PORT == '':
    PORT = argv[1] if len(argv) > 1 else None

ino = Ino(port=PORT)
db = DataBase(FILE_DB)
bot = TeleBot(TOKEN, threaded=False)

set_handlers(bot, ino, db, OWNER_ID)

bot.infinity_polling(timeout=60, long_polling_timeout=60*5)
