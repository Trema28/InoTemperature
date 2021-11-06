
def create_files(files):
    for i in files:
        with open(i, 'a+'):
            pass

def read_token(file):
    with open(file) as f:
        return f.read().strip()

def read_ids(file):
    with open(file) as f:
        ids = f.read().strip()
    if ids:
        return [*zip(*map(lambda s: s.split(' '), ids.split('\n')))]
    return [[], []]

def write_id(file, user_id, username):
    with open(file, 'a') as f:
        f.write(f'{user_id} {username}\n')

def delete_id(files, del_ids):
    for file in files:
        ids = read_ids(file)

        to_save = ''
        for i, n in zip(*ids):
            if i in del_ids:
                continue

            to_save += f'{i} {n}\n'

        with open(file, 'w') as f:
            f.write(to_save)
