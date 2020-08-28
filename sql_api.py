import sqlite3


class Sqlite:
    def __init__(self, db_name, password=None):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()

    def add_user(self, id, name):
        self.cur.execute("INSERT INTO users VALUES ({}, {})".format(id, name or "\'\'"))
        self.conn.commit()

    def check_user_in_db(self, id):
        user = self.cur.execute(f"SELECT id FROM users WHERE ID == {id} LIMIT 1;").fetchone()
        if user:
            print(len(tuple(user)), bool(len(tuple(user))))
            return bool(len(tuple(user)))

