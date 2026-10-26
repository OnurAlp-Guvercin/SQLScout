"""harness/tools/execute_sql.py testleri (adım 4–6): pre-check, cache ve sonucun metne çevrilmesi."""

from agent.context import Context
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
    second = execute_sql.run("SELECT COUNT(*)  FROM items", context)  # ör. bir candidate aynısını yazdı
    assert first == second
    assert context.stats["executions"] == 1


def test_empty_result_hints_search_values(db):
    context = Context("q", "", db)
    text = execute_sql.run("SELECT id FROM items WHERE city = 'Paris'", context)
    assert text == "Columns: id\nNo rows: the result is empty. " + execute_sql.EMPTY_HINT
    assert context.last_ok_sql is None
