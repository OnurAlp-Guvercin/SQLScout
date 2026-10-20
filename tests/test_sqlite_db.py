"""db/sqlite_db.py testleri (aşama 1). Test veritabanı conftest.py'de kurulur."""

import sqlite3

import config
from db import sqlite_db


def test_write_query_is_rejected(db):
    result = sqlite_db.execute(db, "DELETE FROM items")
    assert not result["ok"]
    assert sqlite_db.execute(db, "SELECT COUNT(*) FROM items")["rows"] == [(150,)]


def test_write_inside_with_is_stopped_by_read_only_mode(db):
    result = sqlite_db.execute(db, "WITH x AS (SELECT 1) DELETE FROM items")
    assert not result["ok"]
    assert "readonly" in result["error"]


def test_row_limit_and_row_count(db):
    result = sqlite_db.execute(db, "SELECT * FROM items")
    assert result["ok"]
    assert result["columns"] == ["id", "city", "price", "status"]
    assert len(result["rows"]) == config.MAX_RESULT_ROWS
    assert result["row_count"] == 150


def test_result_key_ignores_row_order(db):
    up = sqlite_db.execute(db, "SELECT id, city FROM items ORDER BY id")
    down = sqlite_db.execute(db, "SELECT id, city FROM items ORDER BY id DESC")
    assert up["result_key"] == down["result_key"]


def test_result_key_ignores_duplicate_rows(db):
    every = sqlite_db.execute(db, "SELECT city FROM items")
    distinct = sqlite_db.execute(db, "SELECT DISTINCT city FROM items")
    assert every["result_key"] == distinct["result_key"]


def test_result_key_depends_on_column_order(db):
    first = sqlite_db.execute(db, "SELECT id, city FROM items")
    second = sqlite_db.execute(db, "SELECT city, id FROM items")
    assert first["result_key"] != second["result_key"]


def test_result_key_treats_int_and_float_alike(db):
    assert sqlite_db.execute(db, "SELECT 1")["result_key"] == sqlite_db.execute(db, "SELECT 1.0")["result_key"]
    assert sqlite_db.execute(db, "SELECT 1")["result_key"] != sqlite_db.execute(db, "SELECT 2")["result_key"]


def test_syntax_error_is_returned(db):
    result = sqlite_db.execute(db, "SELECT * FORM items")
    assert not result["ok"]
    assert result["error"]


def test_timeout(db, monkeypatch):
    monkeypatch.setattr(config, "QUERY_TIMEOUT_SECONDS", 0.2)
    endless = "WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM n) SELECT COUNT(*) FROM n"
    result = sqlite_db.execute(db, endless)
    assert not result["ok"]
    assert "Zaman aşımı" in result["error"]


def test_explain_finds_missing_column(db):
    assert sqlite_db.explain(db, "SELECT city FROM items")["ok"]
    result = sqlite_db.explain(db, "SELECT town FROM items")
    assert not result["ok"]
    assert "town" in result["error"]


def test_estimate_cost(db):
    assert sqlite_db.estimate_cost(db, "SELECT * FROM items") == 150
    assert sqlite_db.estimate_cost(db, "SELECT * FROM items WHERE id = 5") == 0
    assert sqlite_db.estimate_cost(db, "SELECT * FROM items WHERE city = 'Boston'") == 0
    join = "SELECT T1.city FROM items AS T1 JOIN items AS T2 ON T1.id = T2.id"
    assert sqlite_db.estimate_cost(db, join) == 150
    assert sqlite_db.estimate_cost(db, "SELECT town FROM items") is None


def test_fts5_trigram_is_available():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE VIRTUAL TABLE words USING fts5(value, tokenize = 'trigram')")
    conn.execute("INSERT INTO words VALUES ('Los Angeles')")
    assert conn.execute("SELECT value FROM words WHERE words MATCH 'Angel'").fetchall() == [("Los Angeles",)]
