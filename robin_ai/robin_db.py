#!/usr/bin/env python3
import shelve
import sqlite3
# import contextlib
import os


class SqliteDb:
    def __init__(self, filename) -> None:
        self.initialized = False
        # with contextlib.suppress(FileNotFoundError):
        #     os.remove(filename)
        self.connection = sqlite3.connect(filename)
        cursor = self.connection.cursor()
        cursor.execute(
            ''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='daylog' ''')
        if cursor.fetchone()[0] == 1:
            pass
        else:
            cursor.execute("""CREATE TABLE daylog
                        (id DATE PRIMARY KEY,  
                        comment TEXT, 
                        idu REAL,
                        wa REAL,
                        nnla REAL,
                        nla REAL,
                        saa REAL,
                        haa REAL,
                        paa REAL)
                    """)
        self.connection.commit()
        self.initialized = True

    def get(self, query_text):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query_text)
            return cursor.fetchall()
        except sqlite3.ProgrammingError as e:
            print(e)
            raise sqlite3.ProgrammingError()

    def get_one(self, query_text):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query_text)
            return cursor.fetchone()
        except sqlite3.ProgrammingError as e:
            print(e)
            raise sqlite3.ProgrammingError()

    def change(self, query_text, query_var):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query_text, query_var)
            self.connection.commit()
        except sqlite3.ProgrammingError as e:
            print(e)
            raise sqlite3.ProgrammingError()

    def __del__(self):
        self.connection.close()


class RobinDb:
    def __init__(self, db_name, MODULES):
        sql_db_path = os.pardir = os.path.join(MODULES['config']['config_path'], db_name + '.sqlite')
        self.raw_sql = SqliteDb(sql_db_path)
        self.db_name = db_name
        shelve_db_path = os.pardir = os.path.join(MODULES['config']['config_path'], db_name + '.db')
        self.shelve_db = shelve.open(shelve_db_path)
        self.daylog = DayLog(self.raw_sql)

    def close(self):
        self.shelve_db.close()
        del self.raw_sql

    def __getitem__(self, key):
        if key in self.shelve_db.keys():
            return self.shelve_db[key]
        else:
            return None

    def __setitem__(self, key, value):
        self.shelve_db[key] = value

    def __delitem__(self, key):
        del self.shelve_db[key]

    def __del__(self):
        # del self.sql
        self.shelve_db.close()


class DayLog:
    def __init__(self, sqlitedb) -> None:
        self.sqlitedb = sqlitedb

    def add(self,
            date='',
            comment='',
            idu=0,
            wa=0,
            nnla=0,
            nla=0,
            saa=0,
            haa=0,
            paa=0):
        if not self.sqlitedb.initialized:
            return 
        day = (date, comment, idu, wa, nnla, nla, saa, haa, paa)
        self.sqlitedb.change(
            '''INSERT INTO daylog (id, comment, idu, wa, nnla, nla, saa, haa, paa) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            day
        )

    def get(self, date):
        res = self.sqlitedb.get('''SELECT * FROM daylog''')
        return res
