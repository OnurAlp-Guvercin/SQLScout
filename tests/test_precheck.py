"""harness/precheck.py testleri (aşama 8)."""

from harness import precheck


def test_valid_query_passes(db):
    assert precheck.check(db, "SELECT city FROM items") is None


def test_write_query_is_rejected(db):
    assert precheck.check(db, "DELETE FROM items").startswith("Rejected: only read-only queries")


def test_missing_column_is_caught_with_a_hint(db):
    note = precheck.check(db, "SELECT T1.backup_item FROM items AS T1")
    assert note == ("Rejected before running: no such column: T1.backup_item. "
                    "A column with this name exists in: stores.")


def test_missing_table_and_syntax_error_are_caught(db):
    assert precheck.check(db, "SELECT * FROM shops") == "Rejected before running: no such table: shops"
    assert precheck.check(db, "SELECT * FORM items").startswith("Rejected before running:")


def test_second_statement_is_caught(db):
    assert precheck.check(db, "SELECT 1; ATTACH 'other.db' AS other").startswith("Rejected before running:")
