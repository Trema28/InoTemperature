from sys import argv
import asyncio

import bot

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


if __name__ == '__main__':
    asyncio.run(bot.run(PORT, FILE_DB, TOKEN, OWNER_ID))
