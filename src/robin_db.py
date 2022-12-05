#!/usr/bin/env python3
import shelve


class RobinDb:
    def __init__(self, db_name):
        self.db_name = db_name
        self.db = shelve.open(db_name)

    def close(self):
        self.db.close()

    def __getitem__(self, key):
        if key in self.db.keys():
            return self.db[key]
        else:
            return None

    def __setitem__(self, key, value):
        self.db[key] = value

    def __delitem__(self, key):
        del self.db[key]