"""harness/compare.py testleri (aşama 15): forecast'in biçimi, satır aralıkları ve surprise note."""

from harness import compare


def test_row_ranges():
    labels = [compare.row_range(count) for count in (0, 1, 2, 10, 11, 100, 101, 5000)]
    assert labels == ["0", "1", "2-10", "2-10", "11-100", "11-100", "100+", "100+"]


def test_forecast_format():
    assert compare.forecast_error({"type": "empty", "trust": False}) is None
    assert compare.forecast_error({"type": "rows", "columns": ["a"], "rows": "1", "trust": True}) is None
    assert compare.forecast_error("rows").startswith("it must be an object")
    assert compare.forecast_error({"type": "many", "trust": True}) == "type must be one of: error, empty, rows"


def test_hit_ignores_column_names_but_not_counts():
    actual = {"type": "rows", "columns": 2, "rows": "2-10", "result_key": "k"}
    assert compare.surprise_note({"type": "rows", "columns": ["x", "y"], "rows": "2-10"}, actual) is None
    note = compare.surprise_note({"type": "rows", "columns": ["x"], "rows": "2-10"}, actual)
    assert note.startswith("Surprise: you forecast 1 column(s) and 2-10 row(s), but the real result is "
                           "2 column(s) and 2-10 row(s).")


def test_summary_of_error_and_empty():
    error = {"ok": False, "error": "x", "columns": [], "rows": [], "row_count": 0, "result_key": None}
    assert compare.summary(error)["type"] == "error"
    empty = {"ok": True, "error": None, "columns": ["a"], "rows": [], "row_count": 0, "result_key": "k"}
    assert compare.summary(empty) == {"type": "empty", "columns": 1, "rows": "0", "result_key": "k"}
    assert compare.forecast_hit({"type": "empty"}, compare.summary(empty))
