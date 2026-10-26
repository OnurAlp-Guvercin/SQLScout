"""harness/tools/submit.py testleri (adım 7): final check ve iki kez geçmeyince handoff."""

from agent.context import Context
from harness.tools import execute_sql, submit


def test_final_check_accepts_a_query_that_runs_even_if_empty(db):
    context = Context("q", "", db)
    execute_sql.run("SELECT COUNT(*) FROM items", context)  # agent sonucu gördü
    assert submit.run("SELECT COUNT(*) FROM items", context) == {"done": True, "note": None, "handoff": None}
    assert submit.final_check("SELECT id FROM items WHERE city = 'Paris'", context) is None  # boş sonuç geçer


def test_final_check_catches_failing_queries(db):
    context = Context("q", "", db)
    assert submit.final_check("SELECT town FROM items", context).startswith(
        "Final check failed: Rejected before running: no such column: town")


def test_second_failure_hands_over(db):
    context = Context("q", "", db)
    first = submit.run("SELECT town FROM items", context)
    assert first["note"].startswith("Final check failed") and first["handoff"] is None
    assert submit.run("SELECT town FROM items", context)["handoff"] == "final check 2 kez geçmedi"
