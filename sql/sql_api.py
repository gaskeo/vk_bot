import sqlite3

from constants import ANSWER_CHANCE, LADNO_CHANCE, HUY_CHANCE, NU_POLUCHAETSYA_CHANCE


class Sqlite:
    def __init__(self, db_name: str) -> None:
        """
        init method
        :param db_name: name of database file

        """
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()

    def add_user(self, user_id: int, name: str) -> None:
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

    def add_chat(self, chat_id: int) -> None:
        """
        add new chat in database or nothing if chat already in database
        :param chat_id: id of new chat

        """
        if self.check_chat_in_db(abs(chat_id)):
            return
        self.cur.execute("INSERT INTO chats VALUES ({}, {}, {}, {}, {}, {})".format(
            abs(chat_id), 30, 30, 30, 30, 1))
        self.conn.commit()

    def check_chat_in_db(self, chat_id: int) -> bool:
        """
        checking if user in db via user's id
        :param chat_id: chat's id
        :return: True if chat in db or False if chat not in db

        """
        chat = self.cur.execute(
            f"SELECT id FROM chats WHERE ID == {abs(chat_id)} LIMIT 1;"
        ).fetchone()
        return True if chat else False

    def get_chances(self, chat_id: int, params: dict) -> dict:
        """
        get weights of answers in chat
        :param chat_id:  chat's id
        :param params: answers that need weights like {ANSWER_CHANCE: True, ...}
        :return: dict with weights like {ANSWER_CHANCE: 30, ...}

        """
        if not self.check_chat_in_db(abs(chat_id)):
            return {}
        answer = {}
        if params.get(ANSWER_CHANCE, False):
            chance = self.cur.execute(f"SELECT {ANSWER_CHANCE} FROM chats "
                                      f"WHERE id == {abs(chat_id)} LIMIT 1;").fetchone()
            chance = float(chance[0]) if chance else 0
            answer[ANSWER_CHANCE] = chance

        if params.get(HUY_CHANCE, False):
            chance = self.cur.execute(f"SELECT {HUY_CHANCE} FROM chats "
                                      f"WHERE id == {abs(chat_id)} LIMIT 1;").fetchone()
            chance = chance[0] if chance else 0
            answer[HUY_CHANCE] = chance

        if params.get(LADNO_CHANCE, False):
            chance = self.cur.execute(f"SELECT {LADNO_CHANCE} FROM chats "
                                      f"WHERE id == {abs(chat_id)} LIMIT 1;").fetchone()
            chance = chance[0] if chance else 0
            answer[LADNO_CHANCE] = chance

        if params.get(NU_POLUCHAETSYA_CHANCE, False):
            chance = self.cur.execute(f"SELECT {NU_POLUCHAETSYA_CHANCE} FROM chats "
                                      f"WHERE id == {abs(chat_id)} LIMIT 1;").fetchone()
            chance = chance[0] if chance else 0
            answer[NU_POLUCHAETSYA_CHANCE] = chance

        return answer

    def change_chances(self, chat_id: int, params: dict) -> None:
        """
        change chances of answers
        :param chat_id: chat's id
        :param params: dict like {ANSWER_CHANCE: 100 (new chance), ...}

        """
        if not self.check_chat_in_db(abs(chat_id)):
            self.add_chat(chat_id)
        if 0 <= params.get(ANSWER_CHANCE, -1) <= 100:
            self.cur.execute(f"UPDATE chats SET {ANSWER_CHANCE} = {params[ANSWER_CHANCE]}"
                             f" WHERE id == {abs(chat_id)};")
            self.conn.commit()

        if 0 <= params.get(HUY_CHANCE, -1) <= 100:
            self.cur.execute(f"UPDATE chats SET {HUY_CHANCE} = {params[HUY_CHANCE]}"
                             f" WHERE id == {abs(chat_id)};")
            self.conn.commit()

        if 0 <= params.get(LADNO_CHANCE, -1) <= 100:
            self.cur.execute(f"UPDATE chats SET {LADNO_CHANCE} = {params[LADNO_CHANCE]}"
                             f" WHERE id == {abs(chat_id)};")
            self.conn.commit()

        if 0 <= params.get(NU_POLUCHAETSYA_CHANCE, -1) <= 100:
            self.cur.execute(f"UPDATE chats SET {NU_POLUCHAETSYA_CHANCE} = "
                             f"{params[NU_POLUCHAETSYA_CHANCE]}"
                             f" WHERE id == {abs(chat_id)};")
            self.conn.commit()

    def get_who_can_change_chances(self, chat_id: int) -> int:
        """
        get who can change chances in chat
        :param chat_id: chat's id
        :return: who can: 1 - admins only; 0 - all

        """
        if not self.check_chat_in_db(abs(chat_id)):
            self.add_chat(chat_id)
        who = self.cur.execute(f"SELECT who_can_change_chances FROM chats "
                               f"WHERE id == {abs(chat_id)} LIMIT 1;").fetchone()
        return who[0]

    def toggle_access_chances(self, chat_id) -> int:
        """
        toggle who can change chances
        :param chat_id: chat's id
        :return: who can change chances now

        """
        if not self.check_chat_in_db(abs(chat_id)):
            self.add_chat(chat_id)
        who = 1 - self.get_who_can_change_chances(chat_id)
        self.cur.execute(f"UPDATE chats SET who_can_change_chances = "
                         f"{who}"
                         f" WHERE id == {abs(chat_id)};")
        self.conn.commit()
        return who

    def set_admin(self, user_id: int, access_level: int) -> str:
        """
        adding user in admin's db
        :param user_id: user's id who need admin permissions
        :param access_level: level of admin access
        :return: text of reply message

        """
        user = self.cur.execute(f"SELECT id FROM users WHERE ID == {user_id} LIMIT 1;").fetchone()
        if user:
            is_admin = self.cur.execute(f"SELECT * FROM admins WHERE ID == {user_id} LIMIT 1;") \
                .fetchone()
            if is_admin:
                self.cur.execute(f"UPDATE admins SET access_level = {access_level} "
                                 f"WHERE id == {user_id}")
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

    def exit_db(self):
        self.conn.close()
        return True
