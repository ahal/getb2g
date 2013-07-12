import base64
import os
import sqlite3

from ..prompt import prompt

__all__ = ('StorageMixin',)

class StorageMixin(object):
    storage_dir = os.path.expanduser(os.path.join('~', '.getb2g'))
    db = os.path.join(storage_dir, 'storage.db')

    def __init__(self, **kwargs):
        if not os.path.isdir(self.storage_dir):
            os.makedirs(self.storage_dir)
        self.conn = sqlite3.connect(self.db)
        self.cur = self.conn.cursor()
        self.cur.execute('create table if not exists passwords (domain, user, passwd)')

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def save_auth(self, url, user, password):
        if not self.metadata['store']:
            if os.path.isfile(os.path.join(self.storage_dir, 'dont')):
                return
            response = prompt("Save this password in plain text for later?", valid_answers=('y', 'n', 'never'))
            if response == 'never':
                with open(os.path.join(self.storage_dir, 'dont'), 'w') as f:
                    pass
                return
            elif response == 'n':
                return
        self.cur.execute('insert into passwords values (?, ?, ?)', (url, user, base64.b64encode(password)))

    def load_auth(self, url):
        self.cur.execute('select user, passwd from passwords where domain=?', (url,))
        return [(a[0], base64.b64decode(a[1])) for a in self.cur.fetchall()]
