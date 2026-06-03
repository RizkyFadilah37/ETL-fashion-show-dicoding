import pandas as pd
import os
import builtins
import psycopg2
from types import SimpleNamespace
import utils.load.db_loader as loader


def test_load_to_csv_writes_file(tmp_path):
    df = pd.DataFrame([{'a': 1, 'b': 2}])
    out = tmp_path / 'out.csv'
    ok = loader.load_to_csv(df, str(out))
    assert ok is True
    assert out.exists()


def test_load_to_gsheets_success(monkeypatch):
    updated = {}

    class FakeSheet:
        def clear(self):
            updated['cleared'] = True

        def update(self, data):
            updated['data'] = data

    class FakeClient:
        def open(self, name):
            return SimpleNamespace(sheet1=FakeSheet())

    monkeypatch.setattr(loader, 'ServiceAccountCredentials', SimpleNamespace(from_json_keyfile_name=lambda f, s: 'creds'))
    monkeypatch.setattr(loader, 'gspread', SimpleNamespace(authorize=lambda creds: FakeClient()))

    df = pd.DataFrame([{'Title': 'X', 'Price': 10}])
    ok = loader.load_to_gsheets(df, 'fake.json', 'sheetname')
    assert ok is True
    assert updated.get('cleared') is True
    assert isinstance(updated.get('data'), list)


def test_load_to_postgres_creates_db_and_writes(monkeypatch):
    # Simulate psycopg2.connect behavior: first attempt to target DB fails,
    # second attempt to default 'postgres' succeeds and allows CREATE DATABASE
    calls = {'connects': []}

    class FakeCursor:
        def execute(self, q):
            calls.setdefault('executed', []).append(str(q))

        def close(self):
            pass

    class FakeConn:
        def __init__(self):
            self.autocommit = False

        def cursor(self):
            return FakeCursor()

        def close(self):
            calls['closed'] = True

    def fake_connect(**kwargs):
        dbname = kwargs.get('dbname')
        calls['connects'].append(dbname)
        if dbname == 'fashion_db':
            raise psycopg2.OperationalError('db does not exist')
        return FakeConn()

    monkeypatch.setattr(loader, 'psycopg2', loader.psycopg2)
    monkeypatch.setattr(loader.psycopg2, 'connect', fake_connect)

    # Mock sqlalchemy create_engine and pandas.DataFrame.to_sql
    monkeypatch.setattr(loader, 'create_engine', lambda url: 'engine')

    to_sql_called = {}

    def fake_to_sql(self, name, engine, if_exists, index):
        to_sql_called['ok'] = True

    monkeypatch.setattr(pd.DataFrame, 'to_sql', fake_to_sql)

    df = pd.DataFrame([{'Title': 'A'}])
    db_url = 'postgresql://postgres:admin@localhost:5432/fashion_db'
    ok = loader.load_to_postgres(df, db_url, table_name='fashion_products_test')
    assert ok is True
    assert 'fashion_db' in calls['connects']
    assert to_sql_called.get('ok') is True
