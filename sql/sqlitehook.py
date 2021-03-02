from queue import Queue

from sql.sql_api import Sqlite
from utils import exception_checker, StopEvent, Nothing


class SqliteHook:
    def __init__(self, sqlite: Sqlite):
        self.sqlite = sqlite
        self.events = Queue()
        self.answers = {}

    def check_event_type(self):
        while True:
            try:
                for event in iter(self.events.get, None):
                    if event[0] == StopEvent:
                        return
                    z, args, kwargs, package_id = event
                    self.answers[package_id] = z(self.sqlite, *args, **kwargs)
            except Exception:
                exception_checker()

    def del_answer(self, package_id):
        if self.answers.get(package_id, Nothing) != Nothing:
            self.answers.pop(package_id)

    def add_in_q(self, z, args=None, kwargs=None, package_id=0):
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = dict()
        self.events.put((z, args, kwargs, package_id))

    def get_answer(self, key):
        return self.answers.get(key, Nothing)
