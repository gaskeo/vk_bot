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
        return True if user else False

    def set_admin(self, id: str, access_level: str):
        user = self.cur.execute(f"SELECT id FROM users WHERE ID == {id} LIMIT 1;").fetchone()
        if user:
            is_admin = self.cur.execute(f"SELECT * FROM admins WHERE ID == {id} LIMIT 1;")\
                .fetchone()
            if is_admin:
                self.cur.execute(f"UPDATE admins SET access_level = {access_level} WHERE id == {id}")
            else:
                self.cur.execute(f"INSERT INTO admins VALUES ({id}, {access_level})")
            self.conn.commit()
            return f"Для @id{id} поставлен уровень доступа {access_level}"
        else:
            return "Пользователя не использует данного бота"

    def get_admin(self, id: str):
        admin = self.cur.execute(f"SELECT * FROM admins WHERE ID == {id} LIMIT 1;").fetchone()
        if admin:
            return admin[1]
        return 0

    def get_all_admins(self):
        admins = self.cur.execute(f"SELECT * FROM admins ORDER BY access_level").fetchall()
        return admins

