
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

def delete_id(file, user_id):
    ids = read_ids(file)

    with open(file, 'w') as f:
        pass

    found = False
    for i, n in zip(*ids):
        if user_id == i:
            found = True
            continue
        write_id(file, i, n)

    return found
