import datetime
import time
import asyncio

from telebot.async_telebot import AsyncTeleBot
import matplotlib.pyplot as plt
import matplotlib.dates as md
import PIL

from inotemp import InoTemperature
from database import DataBase

TIMER = 1

async def set_handlers(bot: AsyncTeleBot,
                       ino: InoTemperature,
                       db: DataBase,
                       OWNER_ID):

    def get_admins():
        return db.get_users_by_role(db.admin)

    def get_users():
        return db.get_users_by_role(db.user)

    def get_queued_users():
        return db.get_users_by_role(db.queued)

    def get_user(id):
        return db.get_user(id)

    def make_user(id):
        db.set_role(id, db.user)

    def make_admin(id):
        db.set_role(id, db.admin)

    def save_in_queue(message):
        id = str(message.from_user.id)
        username = message.from_user.username
        db.add_user(id, username, db.queued)

    def is_admin(message):
        id = str(message.from_user.id)

        if OWNER_ID == id:
            return True

        user = db.get_user(id)

        if user == None:
            return False

        return db.admin == user[2]

    def is_in_queue(message):
        user = db.get_user(str(message.from_user.id))
        if user == None:
            return False
        return db.queued == user[2]

    def id_check(message):
        if OWNER_ID == str(message.from_user.id):
            return True

        user = db.get_user(str(message.from_user.id))

        if user == None:
            return False

        if db.admin == user[2]:
            return True

        if db.user == user[2]:
            return True

        return False


    @bot.message_handler(commands=['start'])
    async def command_start(message):
        if id_check(message) or is_in_queue(message):
            return

        user_id = str(message.from_user.id)
        username = message.from_user.username

        if OWNER_ID == '':
            text = user_id
            await bot.send_message(message.chat.id, text)
        else:
            save_in_queue(message)

            text = ('new user in queue\n'
                    f'@{username}:`{user_id}`\n'
                    'use /adduser, /addadmin or ignore it')
            await bot.send_message(OWNER_ID, text, parse_mode='Markdown')
            for id, _ in get_admins():
                await bot.send_message(id, text, parse_mode='Markdown')

            text = 'wait until admin adds you'
            await bot.send_message(message.chat.id, text)

    @bot.message_handler(func=id_check, commands=['help'])
    async def command_help(message):
        text = ('/start - nothing for registered users\n'
                '/help - sends this message\n'
                '\n'
                '/time - get bot running time\n'
                '/temp - get temperatures from sensors\n'
                '/plot - \n')
        if is_admin(message):
            text += (
                '/settimer time\n'
                '\n'
                '/queue - sends a list of unregistered users\n'
                '/all - sends a list of all registered users\n'
                '/adduser id [id ...]\n'
                '/addadmin id [id ...]\n'
                '/del id [id ...]')
        await bot.send_message(message.chat.id, text)

    @bot.message_handler(func=id_check, commands=['time'])
    async def command_ping(message):
        text = str(datetime.timedelta(milliseconds=ino.ping()))
        text = text.rsplit('.', 1)[0]
        await bot.send_message(message.chat.id, text)

    @bot.message_handler(func=id_check, commands=['temp'])
    async def command_temp(message):
        text = ''.join(
                    f'{n}: {i}°C\n' for n, i in
                        enumerate(ino.get_temperatures(), start=1))
        await bot.send_message(message.chat.id, text)

    @bot.message_handler(func=is_admin, commands=['queue'])
    async def command_queue(message):
        text = ''.join(f'@{name}:`{id}`' for id, name in get_queued_users())
        text = 'queue:\n' + text

        await bot.send_message(message.chat.id, text, parse_mode='Markdown')

    @bot.message_handler(func=is_admin, commands=['all'])
    async def command_all(message):
        t = ''.join(f'@{name}:`{id}`' for id, name in get_admins())
        text = 'admins:\n' + t

        t = ''.join(f'@{name}:`{id}`' for id, name in get_users())
        text += '\n\nusers:\n' + t

        await bot.send_message(message.chat.id, text, parse_mode='Markdown')

    @bot.message_handler(func=is_admin, commands=['adduser'])
    async def command_adduser(message):
        ids = message.text.split(' ')

        if len(ids) <= 1:
            text = 'id is required'
            await bot.send_message(message.chat.id, text)
            return

        ids.pop(0)

        text = ''
        for id in ids:
            user = get_user(id)

            if user == None:
                text = 'id is not in queue ' + id + '\n'
                continue

            if user[2] == db.user:
                text = 'user already exists ' + id + '\n'
                continue

            make_user(id)
            text = 'user added ' + id + '\n'

        await bot.send_message(message.chat.id, text)

    @bot.message_handler(func=is_admin, commands=['addadmin'])
    async def command_addadmin(message):
        ids = message.text.split(' ')

        if len(ids) <= 1:
            text = 'id is required'
            await bot.send_message(message.chat.id, text)
            return

        ids.pop(0)

        text = ''
        for id in ids:
            user = get_user(id)

            if user == None:
                text += 'id is not in queue ' + id + '\n'
                continue

            if user[2] == db.admin:
                text += 'admin already exists ' + id + '\n'
                continue

            make_admin(id)
            text += 'admin added ' + id + '\n'

        await bot.send_message(message.chat.id, text)

    @bot.message_handler(func=is_admin, commands=['del'])
    async def command_del(message):
        ids = message.text.split(' ')

        if len(ids) <= 1:
            text = 'id is required'
            await bot.send_message(message.chat.id, text)
            return

        ids.pop(0)

        for id in ids:
            db.del_user(id)

        text = 'done'
        await bot.send_message(message.chat.id, text)

    @bot.message_handler(func=id_check, commands=['plot'])
    async def command_plot(message):
        data = db.get_all_plot_data()
        data = [*zip(*data)]

        unix_time = data[0]
        temps = data[1]
        temps = [[*map(float, i.split(', '))] for i in temps]
        date = [datetime.datetime.fromtimestamp(i) for i in unix_time]

        fig, ax = plt.subplots()
        plt.grid(True)

        xfmt = md.DateFormatter('%H:%M')
        ax.xaxis.set_major_formatter(xfmt)

        ax.plot(date, temps, label=range(1, len(temps[0]) + 1))
        ax.legend(loc='best')

        fig.canvas.draw()
        temp_canvas = fig.canvas
        plt.close()

        pil_image = PIL.Image.frombytes('RGB', temp_canvas.get_width_height(), temp_canvas.tostring_rgb())

        await bot.send_chat_action(message.chat.id, 'upload_photo')
        await bot.send_photo(message.chat.id, pil_image)

    @bot.message_handler(func=is_admin, commands=['settimer'])
    async def command_settimer(message):
        args = message.text.split(' ')

        if len(args) <= 1:
            text = 'delay is required'
            await bot.send_message(message.chat.id, text)
            return

        if not args[1].isnumeric():
            text = 'delay should be integer'
            await bot.send_message(message.chat.id, text)
            return

        delay = int(args[1])

        if 60*24 < delay:
            text = 'delay out of range 0 - 60*24'
            await bot.send_message(message.chat.id, text)
            return

        global TIMER
        TIMER = delay

        if delay != 0:
            text = f'timer = {delay}'
        else:
            text = 'timer off'
        await bot.send_message(message.chat.id, text)

async def tempr_recorder(ino: InoTemperature, db: DataBase):
    while True:
        timer = TIMER
        for _ in range(timer):
            await asyncio.sleep(60)

            if timer != TIMER:
                break

            if timer == 0:
                break
        else:
            utime = int(time.time())
            temps = ino.get_temperatures()
            db.save_plot_data(utime, temps)

async def run(PORT, FILE_DB, TOKEN, OWNER_ID):
    ino = InoTemperature(port=PORT)
    db = DataBase(FILE_DB)
    bot = AsyncTeleBot(TOKEN)

    await set_handlers(bot, ino, db, OWNER_ID)

    await asyncio.gather(
        bot.infinity_polling(timeout=60, request_timeout=60*5),
        tempr_recorder(ino, db))
