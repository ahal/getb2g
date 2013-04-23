import base64
import os
import sqlite3

__all__ = ('StorageMixin',)

class StorageMixin(object):
    db = os.path.expanduser(os.path.join('~', '.getb2g', 'storage.db'))

    def __init__(self, **kwargs):
        if not os.path.isdir(os.path.dirname(self.db)):
            os.makedirs(os.path.dirname(self.db))
        self.conn = sqlite3.connect(self.db)
        self.cur = self.conn.cursor()
        self.cur.execute('create table if not exists passwords (domain, user, passwd)')

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def save_auth(self, url, user, password):
        if os.path.isfile(os.path.join(os.path.dirname(self.db), 'no-store')):
            return

        self.cur.execute('insert into passwords values (?, ?, ?)', (url, user, base64.b64encode(password)))

    def load_auth(self, url):
        self.cur.execute('select user, passwd from passwords where domain=?', (url,))
        return [(a[0], base64.b64decode(a[1])) for a in self.cur.fetchall()]
