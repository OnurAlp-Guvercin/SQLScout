"""agent/loop.py testleri: akış uçtan uca. Model yerine sırayla verilen sahte cevaplar kullanılır; API'ye istek gitmez."""

import json

import pytest

import config
from agent import llm, loop
from harness.tools import submit
from tests.fakes import call_reply, execute_reply, submit_reply, text_reply, observation

COUNT_SQL = "SELECT COUNT(*) FROM items"
EMPTY_SQL = "SELECT id FROM items WHERE city = 'Paris'"


def teacher_gives_up():
    """Handoff'tan sonra teacher da çözemez: yarım budget'ı boyunca bir şey yapmaz, fallback answer return edilir."""
    return [text_reply("I am not sure.")] * (config.MAX_TOOL_CALLS // 2)


def test_execute_then_submit(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["sql"] == COUNT_SQL and answer["label"] == "ok"
    assert answer["tool_calls"] == 2 and answer["executions"] == 1  # final check sonucu cache'ten aldı
    assert "Table items (150 rows)" in seen[0][1]["content"]  # adım 1'in bağlamı modele gitti
    assert seen[1][-1]["role"] == "tool" and observation(seen[1][-1]) == "Columns: COUNT(*)\n1 rows:\n150"
    assert answer["cost"] == pytest.approx(0.003)  # agent'ın 2 isteği ve teacher kontrolü


def test_submit_returns_the_chosen_query_not_the_last_one(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL), execute_reply("SELECT id FROM items LIMIT 5"),  # ara sorgu
                submit_reply(COUNT_SQL)]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "ok" and answer["sql"] == COUNT_SQL


def test_broken_output_is_rejected_and_counted(db, fake_model):
    replies, seen = fake_model
    replies += [text_reply("The answer is 150."), execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "ok" and answer["tool_calls"] == 3  # reddedilen cevap da budget'tan düştü
    assert observation(seen[1][-1]).startswith("Rejected: no valid tool call was found")


def test_no_progress_hands_over_early(db, fake_model):
    replies, seen = fake_model
    replies += [text_reply("I am not sure.")] * config.PROGRESS_CALLS + teacher_gives_up()
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == f"no query returned rows in the first {config.PROGRESS_CALLS} calls"
    assert answer["tool_calls"] == config.PROGRESS_CALLS + config.MAX_TOOL_CALLS // 2  # teacher yarım budget alır
    assert observation(seen[config.PROGRESS_CALLS][-1]).startswith("A smaller agent worked on this question")
    assert answer["label"] == "no_answer" and answer["sql"] is None  # hiçbir SQL submit edilmedi


def test_error_and_empty_result_go_back_to_agent(db, fake_model):
    replies, seen = fake_model
    boston = "SELECT id FROM items WHERE city = 'Boston'"
    replies += [execute_reply("SELECT town FROM items"), execute_reply(EMPTY_SQL), execute_reply(boston),
                submit_reply(boston)]
    answer = loop.answer_question("Which items are in Boston?", "", db)
    assert observation(seen[1][-1]).startswith("Rejected before running: no such column: town. ")  # pre-check yakaladı
    assert observation(seen[2][-1]).startswith("Columns: id\nNo rows: the result is empty. If the query filters")
    assert answer["label"] == "ok" and answer["executions"] == 2  # ilk SQL çalıştırılmadı


def test_long_result_says_how_many_rows_are_shown(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply("SELECT id FROM items"), submit_reply("SELECT id FROM items")]
    loop.answer_question("List all items.", "", db)
    text = observation(seen[1][-1])
    assert f"150 rows (first {config.SHOWN_ROWS} shown):" in text  # kırpma
    assert len(text.splitlines()) == 2 + config.SHOWN_ROWS  # başlık ve satırlar


def test_explored_queries_are_never_an_answer(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL), execute_reply(EMPTY_SQL)]
    replies += [text_reply("I am not sure.")] * (config.MAX_TOOL_CALLS - 2) + teacher_gives_up()
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == "the tool-call budget ran out"
    assert answer["label"] == "no_answer" and answer["sql"] is None  # hiçbir SQL submit edilmedi
    assert answer["error_message"] == ("No answer: no SQL query that runs without error was submitted (handoff "
                                       "reason: the tool-call budget ran out; teacher: the tool-call budget ran out).")


def test_repeated_sql_is_not_run_again(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply(COUNT_SQL), execute_reply("SELECT  COUNT(*)\nFROM items"),  # aynı SQL, farklı boşluk
                submit_reply(COUNT_SQL)]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["executions"] == 1 and answer["tool_calls"] == 3  # tekrar çalıştırılmadı ama budget'tan düştü
    assert observation(seen[2][-1]) == "Not run again: this exact call was already made and its result will not " \
                                     "change. Try a different query, or submit your answer. Its result was:\n" \
                                     "Columns: COUNT(*)\n1 rows:\n150"


def test_search_values_tool(db, fake_model):
    replies, seen = fake_model
    replies += [call_reply("search_values", {"query": "Los Angles"}), execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    loop.answer_question("Items in LA?", "", db)
    assert observation(seen[1][-1]) == "Values similar to 'Los Angles':\n- items.city = 'Los Angeles'"


def test_final_check_rejects_a_query_that_does_not_run(db, fake_model):
    replies, seen = fake_model
    replies += [submit_reply("SELECT town FROM items"), execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    answer = loop.answer_question("How many items?", "", db)
    assert observation(seen[1][-1]).startswith("Final check failed: Rejected before running: no such column: town. ")
    assert answer["label"] == "ok" and answer["sql"] == COUNT_SQL


def test_submit_of_an_unseen_query_shows_its_result_first(db, fake_model):
    replies, seen = fake_model
    replies += [submit_reply(COUNT_SQL), submit_reply(COUNT_SQL)]  # agent sonucu görmeden submit etti
    answer = loop.answer_question("How many items?", "", db)
    assert observation(seen[1][-1]) == ("You had not seen the result of this query yet. Its result:\n"
                                        "Columns: COUNT(*)\n1 rows:\n150\n"
                                        "If it answers the question, call submit with it again.")
    assert answer["label"] == "ok" and answer["tool_calls"] == 2  # hata sayılmadı; ikinci submit kabul edildi



def test_final_check_failing_twice_hands_over(db, fake_model):
    replies, _ = fake_model
    replies += [submit_reply("SELECT town FROM items"), submit_reply("SELECT town FROM items")] + teacher_gives_up()
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == f"the final check failed {config.FINAL_CHECK_TRIES} times"
    assert answer["label"] == "no_answer"


def test_empty_result_is_accepted(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply(EMPTY_SQL), submit_reply(EMPTY_SQL)]
    answer = loop.answer_question("Which items are in Paris?", "", db)
    assert answer["label"] == "ok" and answer["sql"] == EMPTY_SQL


def test_every_question_is_written_to_the_experience_log(db, fake_model):
    """Kullanımda (ör. run.py) da her soru loga girer; doğru SQL olmadığı için correct boş kalır."""
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    loop.answer_question("How many items?", "", db)
    record = json.loads(config.EXPERIENCE_LOG.read_text())
    assert record["split"] == "use" and record["correct"] is None and record["label"] == "ok"
    assert record["messages"][1]["content"].endswith("Question: How many items?")  # adım 1'in bağlamı
    assert record["messages"][-1]["content"] == "Accepted."


def test_agent_is_reminded_to_submit_when_the_budget_is_almost_gone(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply(COUNT_SQL)]
    replies += [text_reply("I am not sure.")] * (config.MAX_TOOL_CALLS - 1) + teacher_gives_up()
    loop.answer_question("How many items?", "", db)
    last_agent_turn = seen[config.MAX_TOOL_CALLS - 1][-1]["content"]  # agent'ın son isteğinden önceki not
    assert last_agent_turn.endswith("[1 tool call(s) left. If a query you ran answers the question, call submit with it now.]")


def test_remaining_budget_is_shown_under_every_result(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    answer = loop.answer_question("How many items?", "", db)
    assert seen[1][-1]["content"].endswith(f"\n[{config.MAX_TOOL_CALLS - 1} tool call(s) left.]")
    assert answer["steps"][0]["result"] == "Columns: COUNT(*)\n1 rows:\n150"  # adım kaydında budget notu yok


def test_third_repeat_of_the_same_call_hands_over(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL)] * (config.MAX_REPEATS + 1) + teacher_gives_up()
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == f"the same call was repeated {config.MAX_REPEATS} times"
    assert answer["steps"][config.MAX_REPEATS]["result"] == "Handoff: the same call was repeated too many times."


def test_teacher_repeating_the_agents_call_is_not_stuck(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL)] * (config.MAX_REPEATS + 1)  # agent takıldı
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]  # teacher
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "ok" and answer["answered_by"] == "teacher" and answer["sql"] == COUNT_SQL
    assert answer["steps"][-2]["result"].startswith("Not run again")  # teacher önceki sonucu gördü, devam etti


def test_stuck_agent_samples_its_next_step(db, fake_model, monkeypatch):
    replies, _ = fake_model
    replies += [text_reply("hmm"), execute_reply(COUNT_SQL), execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    temperatures = []
    fake = llm.chat

    def recording(messages, tools=None, temperature=None, model=None):
        if tools:  # yalnızca agent'ın adımları; teacher kontrolü kendi temperature'ıyla çalışır
            temperatures.append(temperature)
        return fake(messages, tools=tools, temperature=temperature, model=model)

    monkeypatch.setattr(llm, "chat", recording)
    loop.answer_question("How many items?", "", db)
    retry = config.RETRY_TEMPERATURE
    assert temperatures == [None, retry, None, retry]  # reddedilen ve tekrarlanan adımdan sonra örneklendi


def test_answer_the_teacher_does_not_approve_hands_over(db, fake_model, monkeypatch):
    monkeypatch.setattr(submit, "teacher_approves", lambda sql, context: False)
    replies, seen = fake_model
    replies += [execute_reply(EMPTY_SQL), submit_reply(EMPTY_SQL),  # agent: teacher onaylamadı
                execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]  # teacher: kendi submit'i kontrol edilmez
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == "a reviewer judged the submitted query to be wrong"
    assert observation(seen[2][-1]).startswith("A smaller agent worked on this question and handed it over to you.")
    assert answer["label"] == "ok" and answer["answered_by"] == "teacher" and answer["sql"] == COUNT_SQL


def test_rejected_answer_is_the_fallback_when_the_teacher_cannot_solve_it(db, fake_model, monkeypatch):
    monkeypatch.setattr(submit, "teacher_approves", lambda sql, context: False)
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)] + teacher_gives_up()
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "fallback" and answer["sql"] == COUNT_SQL and answer["answered_by"] == "agent"


def test_fallback_is_the_last_submitted_sql(db, fake_model, monkeypatch):
    """Teacher sonucunu görmediği bir SQL submit edip ikinci kez submit etmeden budget'ı biterse fallback o SQL olur."""
    monkeypatch.setattr(submit, "teacher_approves", lambda sql, context: False)
    replies, _ = fake_model
    replies += [execute_reply(EMPTY_SQL), submit_reply(EMPTY_SQL)]  # agent: teacher onaylamadı
    replies += [submit_reply(COUNT_SQL)] + [text_reply("I am not sure.")] * (config.MAX_TOOL_CALLS // 2 - 1)
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "fallback" and answer["sql"] == COUNT_SQL and answer["answered_by"] == "teacher"


def test_submit_without_the_semicolon_counts_as_seen(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL + ";"), submit_reply(COUNT_SQL)]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "ok" and answer["tool_calls"] == 2  # "sonucu görmedin" denmedi, hak boşa gitmedi


def test_teacher_starts_with_temperature_zero_after_a_stuck_agent(db, fake_model, monkeypatch):
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL)] * (config.MAX_REPEATS + 1)  # agent takıldı; son adımları örneklendi
    replies += [submit_reply(COUNT_SQL)]  # teacher
    calls = []
    fake = llm.chat

    def recording(messages, tools=None, temperature=None, model=None):
        if tools:
            calls.append((model, temperature))
        return fake(messages, tools=tools, temperature=temperature, model=model)

    monkeypatch.setattr(llm, "chat", recording)
    loop.answer_question("How many items?", "", db)
    assert calls[-2][1] == config.RETRY_TEMPERATURE  # agent'ın son adımı
    assert calls[-1] == (config.TEACHER_MODEL, None)  # teacher'ın ilk adımı temperature 0


def test_teacher_takeover_message_is_english(db, fake_model):
    replies, seen = fake_model
    replies += [text_reply("I am not sure.")] * config.PROGRESS_CALLS + teacher_gives_up()
    loop.answer_question("How many items?", "", db)
    takeover = observation(seen[config.PROGRESS_CALLS][-1])
    assert f"Reason: no query returned rows in the first {config.PROGRESS_CALLS} calls." in takeover


def test_fallback_is_kept_when_the_teacher_cannot_be_reached(db, fake_model, monkeypatch):
    monkeypatch.setattr(submit, "teacher_approves", lambda sql, context: False)
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    fake = llm.chat

    def teacher_down(messages, tools=None, temperature=None, model=None):
        if model == config.TEACHER_MODEL:
            raise RuntimeError("Modele ulaşılamadı")
        return fake(messages, tools=tools, temperature=temperature, model=model)

    monkeypatch.setattr(llm, "chat", teacher_down)
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "fallback" and answer["sql"] == COUNT_SQL  # agent'ın submit ettiği SQL kaybolmadı
    assert answer["teacher_error"] == "Modele ulaşılamadı"
    record = json.loads(config.EXPERIENCE_LOG.read_text())
    assert record["teacher_error"] == "Modele ulaşılamadı"


def test_teacher_gets_its_own_final_check_tries_and_sees_the_last_error(db, fake_model):
    replies, seen = fake_model
    broken = "SELECT town FROM items"
    replies += [execute_reply(COUNT_SQL), submit_reply(broken), submit_reply(broken)]  # agent: 2 kez geçmedi
    replies += [submit_reply(broken), submit_reply(COUNT_SQL)]  # teacher: bir hata, sonra doğru cevap
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "ok" and answer["answered_by"] == "teacher"
    handoff = seen[3][-2]["content"]  # agent'ın ikinci hatalı submit'inin sonucu, teacher'ın gördüğü
    assert handoff.startswith("Final check failed: Rejected before running: no such column: town")
    assert handoff.endswith(f"Handoff: the final check failed {config.FINAL_CHECK_TRIES} times.")


def test_no_answer_says_why_the_teacher_stopped(db, fake_model):
    replies, _ = fake_model
    replies += [text_reply("I am not sure.")] * config.PROGRESS_CALLS
    replies += [execute_reply(COUNT_SQL)] * (config.MAX_REPEATS + 1)  # teacher takıldı
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "no_answer" and answer["answered_by"] is None
    assert answer["teacher_stop_reason"] == f"the same call was repeated {config.MAX_REPEATS} times"
