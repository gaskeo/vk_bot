import sqlite3


class Sqlite:
    def __init__(self, db_name: str, password=None):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()

    def add_user(self, user_id: int, name: str):
        """
        adding users in db or doing nothing if user already in db
        :param user_id: unique user id from vk
        :param name: user's name

        """
        if self.check_user_in_db(user_id):
            return
        self.cur.execute("INSERT INTO users VALUES ({}, {})".format(user_id, name or "\'\'"))
        self.conn.commit()

    def check_user_in_db(self, user_id: int) -> bool:
        """
        checking if user in db via user's id
        :param user_id: user's id
        :return: True if user in db or False if user not in db

        """
        user = self.cur.execute(f"SELECT id FROM users WHERE ID == {user_id} LIMIT 1;").fetchone()
        return True if user else False

    def set_admin(self, user_id: int, access_level: int) -> str:
        """
        adding user in admin's db
        :param user_id: user's id who need admin permissions
        :param access_level: level of admin access
        :return: text of reply message

        """
        user = self.cur.execute(f"SELECT id FROM users WHERE ID == {user_id} LIMIT 1;").fetchone()
        if user:
            is_admin = self.cur.execute(f"SELECT * FROM admins WHERE ID == {user_id} LIMIT 1;")\
                .fetchone()
            if is_admin:
                self.cur.execute(f"UPDATE admins SET access_level = {access_level} WHERE id == {user_id}")
            else:
                self.cur.execute(f"INSERT INTO admins VALUES ({user_id}, {access_level})")
            self.conn.commit()
            return f"Для @id{user_id} поставлен уровень доступа {access_level}"
        else:
            return "Пользователя не использует данного бота"

    def get_admin(self, user_id: int) -> int:
        """
        check if user is admin
        :param user_id: user's id
        :return: level of admin or 0 if user is not admin

        """
        admin = self.cur.execute(f"SELECT * FROM admins WHERE ID == {user_id} LIMIT 1;").fetchone()
        if admin:
            return admin[1]
        return 0

    def get_all_admins(self) -> list:
        """
        get all admins from db
        :return: list of admins

        """
        admins = self.cur.execute(f"SELECT * FROM admins ORDER BY access_level").fetchall()
        return admins

