"""B4 testleri: teacher'a handoff (aşama 22), ask_user ve user simulator (aşama 23, 24), database memory (aşama 25)."""

import config
from agent import loop, tools
from agent.context import Context
from harness import ask_user, candidates
from tests.fakes import ONE_ROW, call_reply, execute_reply, submit_reply, text_reply

EMPTY_SQL = "SELECT id FROM items WHERE city = 'Paris'"
COUNT_SQL = "SELECT COUNT(*) FROM items"


def test_teacher_continues_after_forced_handoff(db, fake_model, monkeypatch):
    monkeypatch.setattr(config, "USE_HANDOFF", True)
    replies, seen = fake_model
    replies += [submit_reply(EMPTY_SQL), submit_reply(EMPTY_SQL),  # agent: final check 2 kez geçmedi
                submit_reply(COUNT_SQL)]  # teacher
    answer = loop.answer_question("How many items?", "", db)
    takeover = seen[2][-1]["content"]
    assert takeover.startswith("A smaller agent worked on this question and handed it over to you. "
                               "Reason: final check 2 kez geçmedi.")
    assert answer["label"] == "ok" and answer["answered_by"] == "teacher" and answer["sql"] == COUNT_SQL
    assert answer["steps"][-1]["by"] == "teacher"


def test_agent_hands_off_and_teacher_answer_failing_final_check_is_low_confidence(db, fake_model, monkeypatch):
    monkeypatch.setattr(config, "USE_HANDOFF", True)
    replies, _ = fake_model
    replies += [call_reply("handoff", {"reason": "stuck"}), submit_reply(EMPTY_SQL)]
    answer = loop.answer_question("Which items are in Paris?", "", db)
    assert answer["handoff_reason"] == "stuck"
    assert answer["label"] == "low_confidence" and answer["answered_by"] == "teacher" and answer["sql"] == EMPTY_SQL


def test_teacher_gets_no_handoff_tool():
    names = [tool["function"]["name"] for tool in tools.offered(teacher=True)]
    assert "handoff" not in names and "ask_user" in names
    assert "handoff" in [tool["function"]["name"] for tool in tools.offered(teacher=False)]


def test_ask_user_in_terminal_and_limit(db, fake_model, monkeypatch):
    monkeypatch.setattr(config, "MAX_ASK_USER", 1)
    monkeypatch.setattr("builtins.input", lambda prompt: "count them")
    replies, seen = fake_model
    replies += [call_reply("ask_user", {"question": "Count or sum?"}), call_reply("ask_user", {"question": "Sure?"}),
                submit_reply(COUNT_SQL)]
    answer = loop.answer_question("How many items?", "", db)
    assert seen[1][-1]["content"] == "User's answer: count them"
    assert seen[2][-1]["content"] == "Rejected: you can ask the user at most 1 times for one question."
    assert answer["clarifications"] == [{"question": "Count or sum?", "answer": "count them"}]


def test_simulator_sees_gold_but_agent_never_does(db, fake_model):
    replies, seen = fake_model
    replies += [call_reply("ask_user", {"question": "Count or sum?"}), text_reply("The number of items."),
                submit_reply(COUNT_SQL)]
    loop.answer_question("How many items?", "", db, gold_sql="SELECT COUNT(id) FROM items")
    assert "Secret SQL (what you meant): SELECT COUNT(id) FROM items" in seen[1][1]["content"]
    for message in seen[0] + seen[2]:  # agent'ın gördüğü bütün mesajlar
        assert "COUNT(id)" not in str(message["content"])
    assert seen[2][-1]["content"] == "User's answer: The number of items."


def test_simulator_answer_with_sql_is_replaced(db, fake_model):
    replies, _ = fake_model
    replies.append(text_reply("Just run SELECT COUNT(*) FROM items."))
    context = Context("How many items?", "", db, gold_sql=COUNT_SQL)
    assert ask_user.run("Count or sum?", context) == f"User's answer: {ask_user.REFUSAL}"


def test_clarifications_go_into_candidate_prompt(db):
    context = Context("How many items?", "", db)
    context.messages = [{}, {"content": "schema and question"}]
    context.clarifications.append({"question": "Count or sum?", "answer": "count"})
    assert candidates.candidate_prompt(context).endswith("The user clarified the question:\n- Q: Count or sum? A: count")


def test_corrected_mistake_is_remembered_for_similar_question(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply(EMPTY_SQL, ONE_ROW), submit_reply(COUNT_SQL)]  # surprise note, sonra ok
    loop.answer_question("How many items are there in Paris?", "", db)
    replies.append(submit_reply(COUNT_SQL))
    loop.answer_question("How many items in Paris?", "", db)
    context = seen[-1][1]["content"]
    assert "Mistakes made and corrected earlier on this database:" in context
    assert f"{EMPTY_SQL} → Surprise: you forecast 1 column(s) and 1 row(s)" in context
    assert f"Corrected: {COUNT_SQL}" in context


def test_memory_flag_off(db, fake_model, monkeypatch):
    monkeypatch.setattr(config, "USE_DB_MEMORY", False)
    replies, _ = fake_model
    replies += [execute_reply(EMPTY_SQL, ONE_ROW), submit_reply(COUNT_SQL)]
    loop.answer_question("How many items are there in Paris?", "", db)
    assert not config.MEMORY_DIR.exists()
