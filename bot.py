from datetime import timedelta

def set_handlers(bot, ino, db, OWNER_ID):

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
    def command_start(message):
        if id_check(message) or is_in_queue(message):
            return

        user_id = str(message.from_user.id)
        username = message.from_user.username

        if OWNER_ID == '':
            text = user_id
            bot.send_message(message.chat.id, text)
        else:
            save_in_queue(message)

            text = ('new user in queue\n'
                    f'@{username}:`{user_id}`\n'
                    'use /adduser, /addadmin or ignore it')
            bot.send_message(OWNER_ID, text, parse_mode='Markdown')
            for id, _ in get_admins():
                bot.send_message(id, text, parse_mode='Markdown')

            text = 'wait until admin adds you'
            bot.send_message(message.chat.id, text)

    @bot.message_handler(func=id_check, commands=['help'])
    def command_help(message):
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
    def command_queue(message):
        text = ''.join(f'@{name}:`{id}`' for id, name in get_queued_users())
        text = 'queue:\n' + text

        bot.send_message(message.chat.id, text, parse_mode='Markdown')

    @bot.message_handler(func=is_admin, commands=['all'])
    def command_all(message):
        t = ''.join(f'@{name}:`{id}`' for id, name in get_admins())
        text = 'admins:\n' + t

        t = ''.join(f'@{name}:`{id}`' for id, name in get_users())
        text += '\n\nusers:\n' + t

        bot.send_message(message.chat.id, text, parse_mode='Markdown')

    @bot.message_handler(func=is_admin, commands=['adduser'])
    def command_adduser(message):
        ids = message.text.split(' ')

        if len(ids) <= 1:
            text = 'id is required'
            bot.send_message(message.chat.id, text)
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

        bot.send_message(message.chat.id, text)

    @bot.message_handler(func=is_admin, commands=['addadmin'])
    def command_addadmin(message):
        ids = message.text.split(' ')

        if len(ids) <= 1:
            text = 'id is required'
            bot.send_message(message.chat.id, text)
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

        bot.send_message(message.chat.id, text)

    @bot.message_handler(func=is_admin, commands=['del'])
    def command_del(message):
        ids = message.text.split(' ')

        if len(ids) <= 1:
            text = 'id is required'
            bot.send_message(message.chat.id, text)
            return

        ids.pop(0)

        for id in ids:
            db.del_user(id)

        text = 'done'
        bot.send_message(message.chat.id, text)
