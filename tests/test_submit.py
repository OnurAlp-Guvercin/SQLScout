"""harness/tools/submit.py testleri (adım 7): final check, sütun kontrolü ve iki kez geçmeyince handoff."""

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
    handoff = submit.run("SELECT town FROM items", context)["handoff"]
    assert handoff == f"the final check failed {config.FINAL_CHECK_TRIES} times"


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


def test_teacher_decision_is_recorded(db, monkeypatch):
    monkeypatch.setattr(llm, "chat", lambda messages, temperature=None, model=None: {"text": "no", "cost": 0})
    context = Context("How many items?", "", db)
    context.messages = [{}, {"content": "Question: How many items?"}]
    submit.teacher_approves("SELECT COUNT(*) FROM items", context)
    assert context.teacher_check == {"sql": "SELECT COUNT(*) FROM items", "approved": False}


def test_answer_is_kept_when_the_teacher_cannot_be_reached(db, monkeypatch):
    def failing_chat(messages, temperature=None, model=None):
        raise RuntimeError("Model API hatası 429: engine_overloaded")

    monkeypatch.setattr(llm, "chat", failing_chat)
    context = Context("How many items?", "", db)
    context.messages = [{}, {"content": "Question: How many items?"}]
    assert submit.teacher_approves("SELECT COUNT(*) FROM items", context) is True  # agent'ın cevabı kaybolmaz
    assert context.teacher_error == "Model API hatası 429: engine_overloaded"  # kontrolün yapılmadığı kayıtlı
    assert context.teacher_check is None


def test_submitted_sql_is_kept_only_if_it_runs(db, monkeypatch):
    monkeypatch.setattr(submit, "teacher_approves", lambda sql, context: False)
    context = Context("q", "", db)
    submit.run("SELECT town FROM items", context)  # hata veriyor: fallback olamaz
    assert context.submitted_sql is None
    submit.run("SELECT COUNT(*) FROM items", context)  # hatasız ama sonucu görülmemiş: yine de aday
    assert context.submitted_sql == "SELECT COUNT(*) FROM items" and context.submitted_by == "agent"


def test_decorated_yes_counts_as_approval(db, monkeypatch):
    monkeypatch.setattr(llm, "chat", lambda messages, temperature=None, model=None: {"text": "**Yes**", "cost": 0})
    context = Context("How many items?", "", db)
    context.messages = [{}, {"content": "Question: How many items?"}]
    assert submit.teacher_approves("SELECT COUNT(*) FROM items", context) is True


def test_teacher_check_does_not_see_the_agent_hint(db, monkeypatch):
    sent = []
    monkeypatch.setattr(llm, "chat", lambda messages, temperature=None, model=None: sent.append(messages) or
                        {"text": "yes", "cost": 0})
    context = Context("How many?", "", db)
    context.messages = [{}, {"content": "Question: How many?"}]
    submit.teacher_approves("SELECT COUNT(*) FROM items WHERE city = 'Paris'", context)
    assert sent[0][1]["content"].endswith("Its result:\nColumns: COUNT(*)\n1 rows:\n0")


def test_column_check_sees_only_the_question_evidence_and_columns(db, monkeypatch):
    sent = {}

    def fake_chat(messages, temperature=None, model=None):
        sent.update(messages=messages, temperature=temperature, model=model)
        return {"text": "no", "cost": 0}

    monkeypatch.setattr(llm, "chat", fake_chat)
    context = Context("Which city has item 5?", "item 5 refers to id = 5", db)
    note = submit.extra_column_note("SELECT id, city FROM items WHERE id = 5", context)
    assert note == submit.COLUMNS_NOTE.format(columns="`id`, `city`")
    assert sent["messages"][0]["content"] == prompts.COLUMN_CHECK
    assert sent["messages"][1]["content"] == ("Evidence: item 5 refers to id = 5\nQuestion: Which city has item 5?\n\n"
                                              "Columns of the result (2): `id`, `city`")
    assert sent["temperature"] == 0 and sent["model"] == config.TEACHER_MODEL


def test_single_column_is_not_checked(db, monkeypatch):
    monkeypatch.setattr(llm, "chat", lambda *args, **kwargs: 1 / 0)  # model çağrılmamalı
    assert submit.extra_column_note("SELECT city FROM items", Context("q", "", db)) is None


def test_extra_column_comes_back_as_a_note_not_a_handoff(db, monkeypatch):
    monkeypatch.setattr(submit, "teacher_approves", lambda sql, context: True)
    monkeypatch.setattr(llm, "chat", lambda messages, temperature=None, model=None: {"text": "No.", "cost": 0})
    context = Context("q", "", db)
    for sql in ("SELECT id, city FROM items", "SELECT city, price FROM items"):
        execute_sql.run(sql, context)
    outcome = submit.run("SELECT id, city FROM items", context)
    assert outcome == {"done": False, "note": submit.COLUMNS_NOTE.format(columns="`id`, `city`"), "handoff": None}
    assert context.final_check_fails == 1  # final check hakkından düşer: ikinci notta handoff
    assert submit.run("SELECT city, price FROM items", context)["handoff"] == (
        f"the final check failed {config.FINAL_CHECK_TRIES} times")


def test_resubmitting_the_same_columns_skips_the_column_check(db, monkeypatch):
    monkeypatch.setattr(submit, "teacher_approves", lambda sql, context: True)
    monkeypatch.setattr(llm, "chat", lambda messages, temperature=None, model=None: {"text": "no", "cost": 0})
    context = Context("q", "", db)
    execute_sql.run("SELECT id, city FROM items", context)
    assert submit.run("SELECT id, city FROM items", context)["note"].startswith("A reviewer found a column")
    assert submit.run("SELECT id, city FROM items;", context)["done"] is True  # ısrar: karar teacher_approves'ta


def test_column_check_is_skipped_when_the_teacher_cannot_be_reached(db, monkeypatch):
    def failing_chat(messages, temperature=None, model=None):
        raise RuntimeError("Model API hatası 429: engine_overloaded")

    monkeypatch.setattr(llm, "chat", failing_chat)
    context = Context("q", "", db)
    assert submit.extra_column_note("SELECT id, city FROM items", context) is None  # kontrol atlanır
    assert context.teacher_error is None  # cevabı teacher_approves yine kontrol eder; hata orada kaydedilir
