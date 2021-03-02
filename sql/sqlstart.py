from sql.sql_api import Sqlite
from sql.sqlitehook import SqliteHook

from constants import SQL_FILE_NAME


class SqliteStart:
    def __init__(self):
        self.sqlite = None
        self.sqlhook = None

    def get_sql(self):
        return self.sqlite

    def create(self):
        self.sqlite = Sqlite(SQL_FILE_NAME)
        self.sqlhook = SqliteHook(self.sqlite)
        self.check_event_type()

    def get_sqlkook(self):
        return self.sqlhook

    def check_event_type(self):
        self.sqlhook.check_event_type()