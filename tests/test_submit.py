"""harness/tools/submit.py testleri (adım 7): final check ve iki kez geçmeyince handoff."""

import config
from agent import llm, prompts
from agent.context import Context
from harness.tools import execute_sql, submit


def test_final_check_accepts_a_query_that_runs_even_if_empty(db, monkeypatch):
    monkeypatch.setattr(submit, "teacher_approves", lambda sql, context: True)
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


def test_teacher_check_sees_the_question_sql_and_result(db, monkeypatch):
    sent = {}

    def fake_chat(messages, temperature=None, model=None):
        sent.update(messages=messages, temperature=temperature, model=model)
        return {"text": "Yes.", "prompt_tokens": 10, "completion_tokens": 1, "cost": 0.0001}

    monkeypatch.setattr(llm, "chat", fake_chat)
    context = Context("How many items?", "", db)
    context.messages = [{}, {"content": "Database schema ... Question: How many items?"}]
    assert submit.teacher_approves("SELECT COUNT(*) FROM items", context) is True
    assert sent["messages"][0]["content"] == prompts.CHECK_ANSWER
    assert sent["messages"][1]["content"].endswith("SELECT COUNT(*) FROM items\n```\nIts result:\nColumns: COUNT(*)\n1 rows:\n150")
    assert sent["temperature"] == 0 and sent["model"] == config.TEACHER_MODEL
    monkeypatch.setattr(llm, "chat", lambda messages, temperature=None, model=None: {"text": "no", "cost": 0})
    assert submit.teacher_approves("SELECT COUNT(*) FROM items", context) is False
