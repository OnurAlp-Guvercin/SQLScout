"""B4 testleri: teacher'a handoff (aşama 22), ask_user (aşama 23), database memory (aşama 25)."""

import json

import config
from agent import loop
from agent.context import Context
from harness import answer, memory
from tests.fakes import EMPTY, ONE_ROW, call_reply, execute_reply, submit_reply, text_reply

EMPTY_SQL = "SELECT id FROM items WHERE city = 'Paris'"
COUNT_SQL = "SELECT COUNT(*) FROM items"


def test_teacher_continues_after_forced_handoff(db, fake_model, monkeypatch):
    replies, seen = fake_model
    replies += [submit_reply(EMPTY_SQL), submit_reply(EMPTY_SQL),  # agent: final check 2 kez geçmedi
                submit_reply(COUNT_SQL)]  # teacher
    answer = loop.answer_question("How many items?", "", db)
    takeover = seen[2][-1]["content"]
    assert takeover.startswith("A smaller agent worked on this question and handed it over to you. "
                               "Reason: final check 2 kez geçmedi.")
    assert answer["label"] == "ok" and answer["answered_by"] == "teacher" and answer["sql"] == COUNT_SQL
    assert answer["steps"][-1]["by"] == "teacher"


def test_teacher_answer_failing_final_check_is_low_confidence(db, fake_model, monkeypatch):
    replies, _ = fake_model
    replies += [text_reply("I am not sure.")] * config.MAX_TOOL_CALLS + [submit_reply(EMPTY_SQL)]
    answer = loop.answer_question("Which items are in Paris?", "", db)
    assert answer["handoff_reason"] == "budget bitti"
    assert answer["label"] == "low_confidence" and answer["answered_by"] == "teacher" and answer["sql"] == EMPTY_SQL


def test_ask_user_in_terminal_and_limit(db, fake_model, monkeypatch):
    monkeypatch.setattr(config, "MAX_ASK_USER", 1)
    prompts = []
    monkeypatch.setattr("builtins.input", lambda prompt: prompts.append(prompt) or "count them")
    replies, seen = fake_model
    replies += [call_reply("ask_user", {"question": "Count or sum?"}), call_reply("ask_user", {"question": "Sure?"}),
                submit_reply(COUNT_SQL)]
    answer = loop.answer_question("How many items?", "", db)
    assert seen[1][-1]["content"] == "User's answer: count them"
    assert seen[2][-1]["content"] == "Rejected: you can ask the user at most 1 times for one question."
    assert answer["clarifications"] == [{"question": "Count or sum?", "answer": "count them"}]
    assert prompts == ["\nQuestion: How many items?\nAgent asks: Count or sum?\nYour answer: "]  # ikinci soru sorulmadı


def test_clarifications_go_into_candidate_prompt(db):
    context = Context("How many items?", "", db)
    context.messages = [{}, {"content": "schema and question"}]
    context.clarifications.append({"question": "Count or sum?", "answer": "count"})
    assert answer.candidate_prompt(context).endswith("The user clarified the question:\n- Q: Count or sum? A: count")


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


def test_memory_prefers_rare_shared_words(db, monkeypatch):
    """TF-IDF: her kayıtta geçen "how many" az sayılır; sorunun asıl konusunu ("superpower") paylaşan kayıt öne çıkar."""
    monkeypatch.setattr(config, "MEMORY_RECORDS", 1)
    words = ["tall", "short", "female", "strong", "fast", "good", "evil", "rich", "young", "old"]
    questions = [f"How many heroes are {word}?" for word in words] + ["List the superpower names."]
    config.MEMORY_DIR.mkdir(parents=True)
    with open(memory.memory_path(db), "w") as file:
        for question in questions:
            file.write(json.dumps({"question": question, "wrong_sql": "", "note": "", "answer_sql": ""}) + "\n")
    assert memory.read(db, "How many heroes have the superpower Flight?")[0]["question"] == "List the superpower names."


def test_wrong_forecast_with_unchanged_sql_is_not_remembered(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL, EMPTY), submit_reply(COUNT_SQL)]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "ok" and "Surprise" in answer["steps"][0]["result"]
    assert not config.MEMORY_DIR.exists()
