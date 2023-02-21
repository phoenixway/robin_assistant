#!/usr/bin/env python3

import pytest
import logging
import sys
from src.robin_db import RobinDb, SqliteDb
from pathlib import Path



class TestDbs:

    def setup_method(self):
        self.robin_db = RobinDb('just_test')

    def teardown_method(self):
        self.robin_db.close()
        sqlite_db_file = Path(self.robin_db.db_name + '.sqlite')
        db_file = Path(self.robin_db.db_name + '.db')
        sqlite_db_file.unlink()
        db_file.unlink()

    def test_sql1(self):
        sqlite_db_file = Path(self.robin_db.db_name + '.sqlite')
        assert sqlite_db_file.is_file() == True, "Sqlite db does not exist"

    def test_sql_table_created(self):
        num = self.robin_db.raw_sql.get_one(
            ''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='daylog' ''')[0]
        assert num == 1, "No tables in sqlite db"

    def test_sql_insertion(self):
        day = (
            '20/02/2023',
            'test comment',
            0.3,
            5,
            3,
            0,
            2.5,
            1,
            1)
        self.robin_db.raw_sql.change('''
            INSERT INTO daylog (id, comment, idu, wa, nnla, nla, saa, haa, paa) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
                    day
                    )
        result = self.robin_db.raw_sql.get("SELECT * FROM daylog")
        #print(result)
        assert len(result) == 1, "Wrong raw number" 
        assert result[0][0] == '20/02/2023', 'Wrong column data'
        assert result[0][1] == 'test comment', 'Wrong column data'

    def test_daylog(self):
        data = (
            '22/02/2023',
            'test comment',
            0.2,
            5,
            0,
            0.2,
            0,
            5,
            0
        )
        self.robin_db.daylog.add(
            date=data[0],
            comment=data[1],
            idu=data[2],
            wa=data[3],
            nnla=data[4],
            nla=data[5],
            saa=data[6],
            haa=data[7],
            paa=data[8]
        )

        result = self.robin_db.daylog.get('22/02/2023')
        print(f"len is {len(result)}")
        for i in range(8):
            assert data[i] == result[0][i], 'Wrong data check in result'

