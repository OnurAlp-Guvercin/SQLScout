"""harness/tools/submit.py testleri (adım 7): hatasız çalışıyor mu, large model kontrolü ve iki kez geçmeyince handoff."""

import json

import config
from agent import llm, prompts
from agent.context import Context
from harness.tools import submit


def test_final_check_accepts_a_query_that_runs_even_if_empty(db, monkeypatch):
    monkeypatch.setattr(submit, "large_model_review", lambda sql, context: (True, ""))
    context = Context("q", "", db)
    assert submit.run("SELECT COUNT(*) FROM items", context) == {"done": True, "note": None, "handoff": None}
    assert submit.runs_without_error("SELECT id FROM items WHERE city = 'Paris'", context) is None  # boş sonuç geçer


def test_final_check_catches_failing_queries(db):
    context = Context("q", "", db)
    assert submit.runs_without_error("SELECT town FROM items", context).startswith(
        "Final check failed: Rejected before running: no such column: town")


def test_second_failure_hands_over(db):
    context = Context("q", "", db)
    first = submit.run("SELECT town FROM items", context)
    assert first["note"].startswith("Final check failed") and first["handoff"] is None
    handoff = submit.run("SELECT town FROM items", context)["handoff"]
    assert handoff == f"the final check failed {config.FINAL_CHECK_TRIES} times"


def review(reason, correct):
    """Sahte large model kontrolü: modelin JSON cevabı."""
    text = json.dumps({"reason": reason, "correct": correct})
    return lambda messages, temperature=None, model=None: {"text": text, "cost": 0}


def test_large_model_check_sees_the_question_sql_and_result(db, monkeypatch):
    sent = {}

    def fake_chat(messages, temperature=None, model=None):
        sent.update(messages=messages, temperature=temperature, model=model)
        return {"text": '{"reason": "It counts every item.", "correct": true}', "cost": 0.0001}

    monkeypatch.setattr(llm, "chat", fake_chat)
    context = Context("How many items?", "", db)
    context.messages = [{}, {"content": "Database schema ... Question: How many items?"}]
    assert submit.large_model_review("SELECT COUNT(*) FROM items", context) == (True, "It counts every item.")
    assert sent["messages"][0]["content"] == prompts.CHECK_ANSWER
    assert sent["messages"][1]["content"].endswith("SELECT COUNT(*) FROM items\n```\nIts result:\nColumns: COUNT(*)\n1 rows:\n150")
    assert sent["temperature"] == 0 and sent["model"] == config.LARGE_MODEL


def test_large_model_decision_is_recorded_with_its_reason(db, monkeypatch):
    monkeypatch.setattr(llm, "chat", review("It counts rows, not cities.", False))
    context = Context("How many cities?", "", db)
    context.messages = [{}, {"content": "Question: How many cities?"}]
    assert submit.large_model_review("SELECT COUNT(*) FROM items", context) == (False, "It counts rows, not cities.")
    assert context.large_model_checks == [{"sql": "SELECT COUNT(*) FROM items", "approved": False,
                                       "reason": "It counts rows, not cities."}]


def test_answer_is_kept_when_the_large_model_cannot_be_reached(db, monkeypatch):
    def failing_chat(messages, temperature=None, model=None):
        raise RuntimeError("Model API hatası 429: engine_overloaded")

    monkeypatch.setattr(llm, "chat", failing_chat)
    context = Context("How many items?", "", db)
    context.messages = [{}, {"content": "Question: How many items?"}]
    assert submit.large_model_review("SELECT COUNT(*) FROM items", context) == (True, "")  # agent'ın cevabı kaybolmaz
    assert context.large_model_error == "Model API hatası 429: engine_overloaded"  # kontrolün yapılmadığı kayıtlı
    assert context.large_model_checks == []


def test_submitted_sql_is_kept_only_if_it_runs(db, monkeypatch):
    monkeypatch.setattr(submit, "large_model_review", lambda sql, context: (False, "Wrong."))
    context = Context("q", "", db)
    submit.run("SELECT town FROM items", context)  # hata veriyor: fallback olamaz
    assert context.submitted_sql is None
    submit.run("SELECT COUNT(*) FROM items", context)  # hatasız: fallback adayı
    assert context.submitted_sql == "SELECT COUNT(*) FROM items" and context.submitted_by == "small_model"


def test_review_is_read_from_json_even_inside_a_code_block():
    assert submit.read_review('```json\n{"reason": "Fine.", "correct": true}\n```') == (True, "Fine.")
    assert submit.read_review("Yes") == (False, "Unreadable review: Yes")  # JSON değil: onay sayılmaz
    assert submit.read_review('{"reason": "Fine.", "correct": "yes"}')[0] is False  # correct true/false değil


def test_rejected_agent_answer_hands_over_with_the_reason(db, monkeypatch):
    monkeypatch.setattr(llm, "chat", review("It returns an extra id column.", False))
    context = Context("q", "", db)
    context.messages = [{}, {"content": "Question: q"}]
    outcome = submit.run("SELECT id, city FROM items", context)
    assert outcome["handoff"] == "a reviewer judged the submitted query to be wrong"
    assert outcome["note"].startswith("Reviewer: It returns an extra id column.")  # agent'ın konuşmasında kalır


def test_large_model_check_does_not_see_the_agent_hint(db, monkeypatch):
    sent = []
    monkeypatch.setattr(llm, "chat", lambda messages, temperature=None, model=None: sent.append(messages) or
                        {"text": '{"reason": "Fine.", "correct": true}', "cost": 0})
    context = Context("How many?", "", db)
    context.messages = [{}, {"content": "Question: How many?"}]
    submit.large_model_review("SELECT COUNT(*) FROM items WHERE city = 'Paris'", context)
    assert sent[0][1]["content"].endswith("Its result:\nColumns: COUNT(*)\n1 rows:\n0")


def test_text_after_the_review_json_does_not_change_the_decision():
    assert submit.read_review('{"reason": "Fine.", "correct": true}\nNote: {x}') == (True, "Fine.")
