import sqlite3

class DataBase:
    ''' '''

    @property
    def admin(self):
        return 'admin'

    @property
    def user(self):
        return 'user'

    @property
    def queued(self):
        return 'queued'

    def __init__(self, file_name):
        self.con = sqlite3.connect(file_name)
        self.cur = self.con.cursor()

        self.cur.execute('''CREATE TABLE IF NOT EXISTS users (id TEXT, username TEXT, role TEXT)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS plot (time INTEGER, temperatures BLOB)''')
        self.con.commit()

    def __role_chek(self, role):
        assert role in (self.admin, self.user, self.queued), 'wrong role'

    def get_all_users(self):
        users = self.cur.execute('''SELECT * FROM users''')
        return users.fetchall()

    def get_users_by_role(self, role):
        self.__role_chek(role)

        users = self.cur.execute('''SELECT id, username FROM users WHERE role = ?''',
                                 (role,))
        return users.fetchall()

    def get_user(self, id):
        users = self.cur.execute('''SELECT * FROM users WHERE id = ?''',
                                 (id,))
        return users.fetchone()

    def add_user(self, id, username, role):
        self.__role_chek(role)

        self.cur.execute('''INSERT INTO users (id, username, role) VALUES (?, ?, ?)''',
                         (id, username, role))
        self.con.commit()

    def del_user(self, id):
        self.cur.execute('''DELETE FROM users WHERE id = ?''',
                         (id,))
        self.con.commit()

    def set_role(self, id, role):
        self.__role_chek(role)

        self.cur.execute('''UPDATE users SET role = ? WHERE id = ?''',
                         (role, id))
        self.con.commit()

    def save_plot_data(self, time, temps: list):
        t = temps.__str__()[1:-1]
        self.cur.execute('''INSERT INTO plot (time, temperatures) VALUES (?, ?)''',
                         (time, t))
        self.con.commit()

    def get_all_plot_data(self):
        plot = self.cur.execute('''SELECT * FROM plot''')
        return plot.fetchall()

    def del_old_plot_data(self, amount):
        ...
