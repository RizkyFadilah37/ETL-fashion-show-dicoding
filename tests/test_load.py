import pandas as pd
import pytest
from utils.load import db_loader as loader


def test_run_loading_calls(monkeypatch, tmp_path):
    df = pd.DataFrame([{'Title': 'A', 'Price': 100}])
    calls = {}

    def fake_csv(df_arg, path):
        calls['csv'] = True
        return True

    def fake_gs(df_arg, cred, name):
        calls['gs'] = True
        return True

    def fake_pg(df_arg, url):
        calls['pg'] = True
        return True

    monkeypatch.setattr(loader, 'load_to_csv', fake_csv)
    monkeypatch.setattr(loader, 'load_to_gsheets', fake_gs)
    monkeypatch.setattr(loader, 'load_to_postgres', fake_pg)

    # Pass DataFrame directly
    loader.run_loading(df, 'cred.json', 'sheet', 'postgresql://u:p@h:5432/db')
    assert calls.get('csv') and calls.get('gs') and calls.get('pg')

    # Pass path to CSV
    csv_path = tmp_path / 'file.csv'
    df.to_csv(csv_path, index=False)
    calls.clear()
    loader.run_loading(str(csv_path), 'cred.json', 'sheet', 'postgresql://u:p@h:5432/db')
    assert calls.get('csv') and calls.get('gs') and calls.get('pg')


def test_run_loading_empty_dataframe():
    df_empty = pd.DataFrame()
    # Should handle gracefully
    loader.run_loading(df_empty, 'cred.json', 'sheet', 'postgresql://u:p@h:5432/db')
    # No exception should be raised


def test_run_loading_invalid_input():
    # Pass something that's not DataFrame or string
    loader.run_loading(123, 'cred.json', 'sheet', 'postgresql://u:p@h:5432/db')
    # Should handle gracefully


def test_run_loading_csv_path_not_found():
    # Path that doesn't exist
    loader.run_loading('/nonexistent/file.csv', 'cred.json', 'sheet', 'postgresql://u:p@h:5432/db')
    # Should handle gracefully


def test_load_to_csv_success(tmp_path):
    df = pd.DataFrame([{'a': 1, 'b': 2}])
    out = tmp_path / 'output.csv'
    result = loader.load_to_csv(df, str(out))
    assert result is True
    assert out.exists()


def test_load_to_csv_failure(monkeypatch):
    def fake_to_csv(path, index):
        raise Exception("Write failed")
    monkeypatch.setattr(pd.DataFrame, 'to_csv', fake_to_csv)
    df = pd.DataFrame([{'a': 1}])
    result = loader.load_to_csv(df, '/path/file.csv')
    assert result is False


def test_load_to_gsheets_exception(monkeypatch):
    def fake_gsheets(*args, **kwargs):
        raise Exception("GSheets API error")
    monkeypatch.setattr(loader, 'ServiceAccountCredentials', fake_gsheets)
    df = pd.DataFrame([{'Title': 'X'}])
    result = loader.load_to_gsheets(df, 'fake.json', 'sheet')
    assert result is False


def test_load_to_postgres_empty_dataframe():
    df_empty = pd.DataFrame()
    result = loader.load_to_postgres(df_empty, 'postgresql://u:p@h:5432/db')
    # Should handle or return False gracefully
    assert result is False
