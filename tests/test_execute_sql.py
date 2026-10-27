"""harness/tools/execute_sql.py testleri (adım 4–6): pre-check, cache ve sonucun metne çevrilmesi."""

import sqlite3

import config
from agent.context import Context
from db import sqlite_db
from harness.tools import execute_sql


def test_valid_query_passes(db):
    assert execute_sql.check(db, "SELECT city FROM items") is None


def test_write_query_is_rejected(db):
    assert execute_sql.check(db, "DELETE FROM items").startswith("Rejected: only read-only queries")


def test_missing_column_is_caught_with_a_hint(db):
    note = execute_sql.check(db, "SELECT T1.backup_item FROM items AS T1")
    assert note == ("Rejected before running: no such column: T1.backup_item. "
                    "A column with this name exists in: stores. "
                    "Tables in your query and their columns: items (T1): id, city, price, status.")


def test_hint_finds_tables_and_aliases_of_the_query(db):
    sql = ("SELECT s.name, items.city FROM items JOIN stores s ON s.item_id = items.id "
           "WHERE items.status = 'stores x' ORDER BY s.id")
    tables = execute_sql.tables_in_query(sql, execute_sql.sqlite_schema.schema(db))
    assert [(table["name"], aliases) for table, aliases in tables] == [("items", []), ("stores", ["s"])]
    note = execute_sql.check(db, "SELECT id FROM items JOIN stores ON stores.item_id = items.id")
    assert note.startswith("Rejected before running: ambiguous column name: id. Several tables in your query")
    note = execute_sql.check(db, "SELECT name FROM sqlite_master WHERE column_name = 'x'")
    assert note.endswith("Table and column names are listed in the schema at the start.")


def test_missing_table_and_syntax_error_are_caught(db):
    assert execute_sql.check(db, "SELECT * FROM shops") == \
        "Rejected before running: no such table: shops. Tables in this database: items, stores."
    assert execute_sql.check(db, "SELECT * FORM items").startswith("Rejected before running:")


def test_second_statement_is_caught(db):
    assert execute_sql.check(db, "SELECT 1; ATTACH 'other.db' AS other").startswith("Rejected before running:")


def test_cache_returns_earlier_result_without_running(db):
    context = Context("How many items?", "", db)
    first = execute_sql.run("SELECT COUNT(*) FROM items", context)
    second = execute_sql.run("SELECT COUNT(*)  FROM items", context)  # aynı SQL, farklı boşluk
    assert first == second
    assert context.stats["executions"] == 1


def test_empty_result_hints_search_values(db):
    context = Context("q", "", db)
    text = execute_sql.run("SELECT id FROM items WHERE city = 'Paris'", context)
    assert text == "Columns: id\nNo rows: the result is empty. " + execute_sql.EMPTY_HINT
    assert context.last_ok_sql is None


def test_only_zero_or_null_counts_as_empty(db):
    """Yanlış yazılmış bir değerle COUNT(*) 0, AVG(...) NULL döner: not gösterilir, ilerleme sayılmaz."""
    context = Context("q", "", db)
    for sql in ["SELECT COUNT(*) FROM items WHERE city = 'Paris'", "SELECT AVG(price) FROM items WHERE city = 'Paris'"]:
        assert execute_sql.run(sql, context).endswith("\nThe result is only 0 or NULL. " + execute_sql.EMPTY_HINT)
    assert context.last_ok_sql is None
    assert execute_sql.run("SELECT COUNT(*) FROM items", context) == "Columns: COUNT(*)\n1 rows:\n150"
    assert context.last_ok_sql == "SELECT COUNT(*) FROM items"
    execute_sql.run("SELECT id FROM items WHERE id < 2", context)  # iki satır, biri 0: dolu
    assert context.last_ok_sql == "SELECT id FROM items WHERE id < 2"


def test_trailing_semicolon_is_the_same_query():
    assert execute_sql.sql_key("SELECT  COUNT(*) FROM items ;\n") == execute_sql.sql_key("SELECT COUNT(*) FROM items")


def test_alias_hint_quotes_names_that_need_it(tmp_path):
    path = tmp_path / "school.sqlite"
    conn = sqlite3.connect(path)
    conn.execute('CREATE TABLE frpm (id INTEGER, "Free Meal Count (K-12)" REAL)')
    conn.close()
    note = execute_sql.check(str(path), 'SELECT frpm."Free Meal Count (K-12)" FROM frpm f')
    assert "write f.`Free Meal Count (K-12)`" in note


def test_missing_column_hint_suggests_similar_names(tmp_path):
    path = tmp_path / "school.sqlite"
    conn = sqlite3.connect(path)
    conn.execute('CREATE TABLE frpm (id INTEGER, "Free Meal Count (K-12)" REAL)')
    conn.close()
    note = execute_sql.check(str(path), 'SELECT `Free Meal Count` FROM frpm')
    assert "Columns with a similar name: frpm.`Free Meal Count (K-12)`" in note


def test_exploration_timeout_is_short_and_a_submitted_query_gets_the_long_one(db, monkeypatch):
    calls = []
    real_execute = sqlite_db.execute

    def slow(path, sql, timeout):
        calls.append(timeout)
        if timeout < config.ANSWER_TIMEOUT_SECONDS:
            return sqlite_db.error_result(f"Timeout: the query did not finish in {timeout} seconds.", timed_out=True)
        return real_execute(path, sql, timeout)

    monkeypatch.setattr(execute_sql.sqlite_db, "execute", slow)
    context = Context("q", "", db)
    text = execute_sql.run("SELECT COUNT(*) FROM items", context)
    assert text.endswith(execute_sql.TIMEOUT_HINT)
    assert execute_sql.sql_key("SELECT COUNT(*) FROM items") not in context.seen  # zaman aşımı sonuç sayılmaz
    assert execute_sql.run_sql("SELECT COUNT(*) FROM items", context, answer=True)["rows"] == [(150,)]
    # Keşifteki zaman aşımı cache'e girmedi: submit edilince uzun sınırla yeniden çalıştı.
    assert calls == [config.EXPLORE_TIMEOUT_SECONDS, config.ANSWER_TIMEOUT_SECONDS]


def test_double_quoted_missing_column_gets_a_hint(db):
    note = execute_sql.check(db, 'SELECT COUNT(*) FROM items WHERE "town" = \'x\'')
    assert note.startswith('Rejected before running: no such column: "town" - should this be a string literal')
    assert "Tables in your query and their columns: items: id, city, price, status." in note


def test_no_timeout_hint_after_the_long_limit(db, monkeypatch):
    """Submit edilmiş ve uzun sınırda da bitmemiş sorgu yeniden çalıştırılırsa "submit et" önerilmez."""
    monkeypatch.setattr(execute_sql.sqlite_db, "execute", lambda path, sql, timeout: sqlite_db.error_result(
        f"Timeout: the query did not finish in {timeout} seconds.", timed_out=True))
    context = Context("q", "", db)
    execute_sql.run_sql("SELECT COUNT(*) FROM items", context, answer=True)
    text = execute_sql.run("SELECT COUNT(*) FROM items", context)
    assert text == f"Error: Timeout: the query did not finish in {config.ANSWER_TIMEOUT_SECONDS} seconds."


def test_double_quoted_text_with_a_dot_is_not_read_as_table_and_column(db):
    note = execute_sql.check(db, 'SELECT id FROM items WHERE city = "St. Louis"')
    assert "should this be a string literal in single-quotes?" in note
    assert "has the alias" not in note and "similar name" not in note
