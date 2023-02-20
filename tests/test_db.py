#!/usr/bin/env python3
#!/usr/bin/env python3
#!/usr/bin/env python3
import pytest
from src.robin_db import RobinDb, SqliteDb
from pathlib import Path


class TestDbs:

    def setup(self):
        self.robin_db = RobinDb('just_test')

    def teardown(self):
        self.robin_db.close()
        sqlite_db_file = Path(self.robin_db.db_name + '.sqlite')
        db_file = Path(self.robin_db.db_name + '.db')
        sqlite_db_file.unlink()
        db_file.unlink()

    def test_sql1(self):
        sqlite_db_file = Path(self.robin_db.db_name + '.sqlite')
        assert sqlite_db_file.is_file() == True, "Sqlite db does not exist"