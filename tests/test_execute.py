"""harness/execute.py testleri (adım 4–6): pre-check, cache ve sonucun metne çevrilmesi."""

from agent.context import Context
from harness import execute


def test_valid_query_passes(db):
    assert execute.check(db, "SELECT city FROM items") is None


def test_write_query_is_rejected(db):
    assert execute.check(db, "DELETE FROM items").startswith("Rejected: only read-only queries")


def test_missing_column_is_caught_with_a_hint(db):
    note = execute.check(db, "SELECT T1.backup_item FROM items AS T1")
    assert note == ("Rejected before running: no such column: T1.backup_item. "
                    "A column with this name exists in: stores.")


def test_missing_table_and_syntax_error_are_caught(db):
    assert execute.check(db, "SELECT * FROM shops") == "Rejected before running: no such table: shops"
    assert execute.check(db, "SELECT * FORM items").startswith("Rejected before running:")


def test_second_statement_is_caught(db):
    assert execute.check(db, "SELECT 1; ATTACH 'other.db' AS other").startswith("Rejected before running:")


def test_cache_returns_earlier_result_without_running(db):
    context = Context("How many items?", "", db)
    first = execute.run_query("SELECT COUNT(*) FROM items", context)
    second = execute.run_query("SELECT COUNT(*)  FROM items", context)  # ör. bir candidate aynısını yazdı
    assert first == second
    assert context.stats["executions"] == 1


def test_empty_result_hints_search_values_and_is_remembered_as_a_mistake(db):
    context = Context("q", "", db)
    text = execute.run_query("SELECT id FROM items WHERE city = 'Paris'", context)
    assert text == "Columns: id\nNo rows: the result is empty. " + execute.EMPTY_HINT
    assert context.first_mistake["sql"] == "SELECT id FROM items WHERE city = 'Paris'"
    assert context.last_ok_sql is None
