"""harness/execute.py testleri (adım 4–6): pre-check, cache, forecast'in biçimi, satır aralıkları ve surprise note."""

from agent.context import Context
from harness import execute
from tests.fakes import ONE_ROW


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


def test_row_ranges():
    labels = [execute.row_range(count) for count in (0, 1, 2, 10, 11, 100, 101, 5000)]
    assert labels == ["0", "1", "2-10", "2-10", "11-100", "11-100", "100+", "100+"]


def test_forecast_format():
    assert execute.forecast_error({"type": "empty"}) is None  # trust zorunlu değil
    assert execute.forecast_error({"type": "rows", "columns": ["a"], "rows": "1", "trust": True}) is None
    assert execute.forecast_error("rows").startswith("it must be like")
    assert execute.forecast_error({"type": "many", "trust": True}) == "type must be one of: error, empty, rows"


def test_hit_ignores_column_names_but_not_counts():
    actual = {"ok": True, "columns": ["a", "b"], "rows": [(1, 2), (3, 4)], "row_count": 2}
    assert execute.surprise_note({"type": "rows", "columns": ["x", "y"], "rows": "2-10"}, actual) is None
    note = execute.surprise_note({"type": "rows", "columns": ["x"], "rows": "2-10"}, actual)
    assert note.startswith("Surprise: you forecast 1 column(s) and 2-10 row(s), but the real result is "
                           "2 column(s) and 2-10 row(s).")


def test_summary_of_error_and_empty():
    error = {"ok": False, "error": "x", "columns": [], "rows": [], "row_count": 0, "result_key": None}
    assert execute.summary(error)["type"] == "error"
    empty = {"ok": True, "error": None, "columns": ["a"], "rows": [], "row_count": 0, "result_key": "k"}
    assert execute.summary(empty) == {"type": "empty", "columns": 1, "rows": "0"}
    assert execute.surprise_note({"type": "empty"}, empty) is None


def test_cache_returns_earlier_result_without_running(db):
    context = Context("How many items?", "", db)
    first = execute.run_query("SELECT COUNT(*) FROM items", ONE_ROW, context)
    second = execute.run_query("SELECT COUNT(*)  FROM items", ONE_ROW, context)  # ör. bir candidate aynısını yazdı
    assert first == second
    assert context.stats["executions"] == 1


def test_missing_columns_and_rows_are_not_compared():
    rows = {"ok": True, "columns": ["a", "b"], "rows": [(1, 2)], "row_count": 1}
    assert execute.surprise_note({"type": "rows"}, rows) is None
    assert execute.surprise_note({"type": "rows", "rows": "1"}, rows) is None
    empty = {"ok": True, "columns": ["a"], "rows": [], "row_count": 0}
    assert execute.surprise_note({"type": "rows"}, empty).startswith("Surprise: you forecast rows, but the real result is an empty result.")
