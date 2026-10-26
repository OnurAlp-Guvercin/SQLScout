"""Yardım testleri: teacher'a handoff ve ask_user."""

import config
from agent import loop
from agent.context import Context
from harness.tools import submit
from tests.fakes import call_reply, sql_reply, submit_reply, text_reply, observation

EMPTY_SQL = "SELECT id FROM items WHERE city = 'Paris'"
COUNT_SQL = "SELECT COUNT(*) FROM items"


def test_teacher_continues_after_forced_handoff(db, fake_model, monkeypatch):
    replies, seen = fake_model
    replies += [submit_reply(EMPTY_SQL), submit_reply(EMPTY_SQL),  # agent: final check 2 kez geçmedi
                submit_reply(COUNT_SQL)]  # teacher
    answer = loop.answer_question("How many items?", "", db)
    takeover = observation(seen[2][-1])
    assert takeover.startswith("A smaller agent worked on this question and handed it over to you. "
                               "Reason: final check 2 kez geçmedi.")
    assert answer["label"] == "ok" and answer["answered_by"] == "teacher" and answer["sql"] == COUNT_SQL
    assert answer["steps"][-1]["by"] == "teacher"


def test_teacher_submit_goes_through_the_gate(db, fake_model):
    """Teacher'ın submit'i de candidate'lerden geçer: candidate'ler başka bir sonuçta uzlaşırsa o sonuç seçilir."""
    replies, _ = fake_model
    replies += [text_reply("I am not sure.")] * config.MAX_TOOL_CALLS + [submit_reply(EMPTY_SQL)]
    replies += [sql_reply(COUNT_SQL)] * (config.TOTAL_CANDIDATES - 1)
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == "budget bitti"
    assert answer["label"] == "ok" and answer["answered_by"] == "teacher" and answer["sql"] == COUNT_SQL


def test_ask_user_in_terminal_and_limit(db, fake_model, monkeypatch):
    monkeypatch.setattr(config, "MAX_ASK_USER", 1)
    prompts = []
    monkeypatch.setattr("builtins.input", lambda prompt: prompts.append(prompt) or "count them")
    replies, seen = fake_model
    replies += [call_reply("ask_user", {"question": "Count or sum?"}), call_reply("ask_user", {"question": "Sure?"}),
                submit_reply(COUNT_SQL)]
    answer = loop.answer_question("How many items?", "", db)
    assert observation(seen[1][-1]) == "User's answer: count them"
    assert observation(seen[2][-1]) == "Rejected: you can ask the user at most 1 times for one question."
    assert answer["clarifications"] == [{"question": "Count or sum?", "answer": "count them"}]
    assert prompts == ["\nQuestion: How many items?\nAgent asks: Count or sum?\nYour answer: "]  # ikinci soru sorulmadı


def test_clarifications_go_into_candidate_prompt(db):
    context = Context("How many items?", "", db)
    context.messages = [{}, {"content": "schema and question"}]
    context.clarifications.append({"question": "Count or sum?", "answer": "count"})
    assert submit.candidate_prompt(context).endswith("The user clarified the question:\n- Q: Count or sum? A: count")
