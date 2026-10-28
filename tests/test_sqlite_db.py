"""db/sqlite_db.py testleri (aşama 1). Test veritabanı conftest.py'de kurulur."""

import sqlite3

import config
from db import sqlite_db


def execute(db, sql):
    return sqlite_db.execute(db, sql, config.EXPLORE_TIMEOUT_SECONDS)


def test_write_query_is_rejected(db):
    result = execute(db, "DELETE FROM items")
    assert not result["ok"]
    assert execute(db, "SELECT COUNT(*) FROM items")["rows"] == [(150,)]


def test_write_inside_with_is_stopped_by_read_only_mode(db):
    result = execute(db, "WITH x AS (SELECT 1) DELETE FROM items")
    assert not result["ok"]
    assert "readonly" in result["error"]


def test_row_limit_and_row_count(db):
    result = execute(db, "SELECT * FROM items")
    assert result["ok"]
    assert result["columns"] == ["id", "city", "price", "status"]
    assert len(result["rows"]) == config.MAX_RESULT_ROWS
    assert result["row_count"] == 150


def test_result_key_ignores_row_order(db):
    up = execute(db, "SELECT id, city FROM items ORDER BY id")
    down = execute(db, "SELECT id, city FROM items ORDER BY id DESC")
    assert up["result_key"] == down["result_key"]


def test_result_key_ignores_duplicate_rows(db):
    every = execute(db, "SELECT city FROM items")
    distinct = execute(db, "SELECT DISTINCT city FROM items")
    assert every["result_key"] == distinct["result_key"]


def test_result_key_depends_on_column_order(db):
    first = execute(db, "SELECT id, city FROM items")
    second = execute(db, "SELECT city, id FROM items")
    assert first["result_key"] != second["result_key"]


def test_result_key_treats_int_and_float_alike(db):
    assert execute(db, "SELECT 1")["result_key"] == execute(db, "SELECT 1.0")["result_key"]
    assert execute(db, "SELECT 1")["result_key"] != execute(db, "SELECT 2")["result_key"]


def test_syntax_error_is_returned(db):
    result = execute(db, "SELECT * FORM items")
    assert not result["ok"]
    assert result["error"]


def test_timeout(db):
    endless = "WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM n) SELECT COUNT(*) FROM n"
    result = sqlite_db.execute(db, endless, 0.2)
    assert not result["ok"] and result["timed_out"]
    assert result["error"] == "Timeout: the query did not finish in 0.2 seconds."


def test_explain_finds_missing_column(db):
    assert sqlite_db.explain(db, "SELECT city FROM items")["ok"]
    result = sqlite_db.explain(db, "SELECT town FROM items")
    assert not result["ok"]
    assert "town" in result["error"]


def test_fts5_trigram_is_available():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE VIRTUAL TABLE words USING fts5(value, tokenize = 'trigram')")
    conn.execute("INSERT INTO words VALUES ('Los Angeles')")
    assert conn.execute("SELECT value FROM words WHERE words MATCH 'Angel'").fetchall() == [("Los Angeles",)]


def test_too_many_rows_is_an_error(db, monkeypatch):
    monkeypatch.setattr(config, "MAX_TOTAL_ROWS", 100)
    result = execute(db, "SELECT a.id, b.id FROM items a, items b")  # JOIN koşulu unutulmuş: 22500 satır
    assert not result["ok"]
    assert result["error"] == ("Too many rows: the result has more than 100 different rows. "
                               "Add a join condition or a filter.")


def test_repeated_rows_do_not_count_toward_the_row_limit(db, monkeypatch):
    """BIRD satır kümesine bakar: aynı satırın binlerce tekrarı tek satırdır, sonuç geçerlidir."""
    monkeypatch.setattr(config, "MAX_TOTAL_ROWS", 100)
    result = execute(db, "SELECT a.city FROM items a, items b")  # 22500 satır, 3 farklı satır
    assert result["ok"] and result["row_count"] == 22500


def test_unencodable_sql_is_an_error_not_a_crash(db):
    result = execute(db, "SELECT '\ud800'")
    assert not result["ok"]


def test_explain_rejects_a_double_quoted_missing_column(db):
    """SQLite normalde bulamadığı "çift tırnaklı" adı metin sayar ve sorgu yanlış ama hatasız çalışır."""
    assert execute(db, 'SELECT COUNT(*) FROM items WHERE "town" = \'x\'')["ok"]  # çalıştırmada eski davranış
    result = sqlite_db.explain(db, 'SELECT COUNT(*) FROM items WHERE "town" = \'x\'')
    assert result["error"] == 'no such column: "town" - should this be a string literal in single-quotes?'
    assert sqlite_db.explain(db, 'SELECT "city" FROM items')["ok"]  # var olan sütun çift tırnakla yazılabilir
