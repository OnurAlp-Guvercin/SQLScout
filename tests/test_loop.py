"""agent/loop.py testleri: akış uçtan uca. Model yerine sırayla verilen sahte cevaplar kullanılır; API'ye istek gitmez."""

import json

import pytest

import config
from agent import llm, loop
from tests.fakes import call_reply, execute_reply, sql_reply, submit_reply, text_reply, observation


def teacher_gives_up():
    """Handoff'tan sonra teacher da çözemez: yarım budget'ı boyunca tool çağırmaz, fallback answer return edilir."""
    return [text_reply("I am not sure.")] * (config.MAX_TOOL_CALLS // 2)


def test_submit_ends_the_loop(db, fake_model):
    replies, seen = fake_model
    replies.append(submit_reply("SELECT COUNT(*) FROM items"))
    answer = loop.answer_question("How many items?", "", db)
    assert answer["sql"] == "SELECT COUNT(*) FROM items"
    assert answer["label"] == "ok"
    assert answer["tool_calls"] == 1
    assert "Table items (150 rows)" in seen[0][1]["content"]  # adım 1'in bağlamı modele gitti
    assert answer["cost"] == pytest.approx(0.003)  # agent'ın isteği + 2 candidate'in isteği


def test_broken_output_is_rejected_and_counted(db, fake_model):
    replies, seen = fake_model
    replies += [text_reply("SELECT 1"), submit_reply("SELECT 1")]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "ok"
    assert answer["tool_calls"] == 2  # reddedilen çıktı da budget'tan düştü
    assert observation(seen[1][-1]).startswith("Rejected: your reply was not a tool call")  # hata agent'a döndü


def test_budget_runs_out_into_fallback_answer(db, fake_model):
    replies, _ = fake_model
    replies += [text_reply("I am not sure.")] * config.MAX_TOOL_CALLS + teacher_gives_up()
    answer = loop.answer_question("How many items?", "", db)
    assert answer["tool_calls"] == config.MAX_TOOL_CALLS + config.MAX_TOOL_CALLS // 2  # teacher yarım budget alır
    assert answer["handoff_reason"] == "budget bitti"
    assert answer["label"] == "low_confidence" and answer["sql"] == "SELECT 1"  # candidate'lerin consensus'u
    assert answer["candidates"] == config.TOTAL_CANDIDATES


def test_execute_sql_shows_the_real_result(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply("SELECT city, COUNT(*) FROM items GROUP BY city ORDER BY city"),
                submit_reply("SELECT city, COUNT(*) FROM items GROUP BY city ORDER BY city")]
    answer = loop.answer_question("How many items per city?", "", db)
    assert seen[1][-1]["role"] == "tool"
    assert observation(seen[1][-1]) == "Columns: city, COUNT(*)\n3 rows:\nBoston | 50\nChicago | 50\nLos Angeles | 50"
    assert answer["label"] == "ok"
    assert answer["tool_calls"] == 2
    assert answer["executions"] == 1


def test_execute_sql_error_and_empty_result_go_back_to_agent(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply("SELECT town FROM items"),
                execute_reply("SELECT id FROM items WHERE city = 'Paris'"),
                submit_reply("SELECT id FROM items WHERE city = 'Boston'")]
    answer = loop.answer_question("Which items are in Boston?", "", db)
    assert observation(seen[1][-1]).startswith("Rejected before running: no such column: town. ")  # pre-check yakaladı
    assert answer["executions"] == 2  # ilk SQL pre-check'te kaldı; ikincisi ve submit edilen çalıştı
    assert observation(seen[2][-1]).startswith("Columns: id\nNo rows: the result is empty. If the query filters")
    assert answer["label"] == "ok"  # submit edilen SQL final check'te çalıştırıldı (2. gerçek çalıştırma)


def test_long_result_says_how_many_rows_are_shown(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply("SELECT id FROM items"), submit_reply("SELECT id FROM items")]
    loop.answer_question("List all items.", "", db)
    text = observation(seen[1][-1])
    assert f"150 rows (first {config.SHOWN_ROWS} shown):" in text  # kırpma
    assert len(text.splitlines()) == 2 + config.SHOWN_ROWS  # başlık ve satırlar


def test_fallback_uses_last_sql_that_ran_when_all_candidates_fail(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply("SELECT COUNT(*) FROM items")]
    replies += [text_reply("I am not sure.")] * (config.MAX_TOOL_CALLS - 1) + teacher_gives_up()
    replies += [sql_reply("SELECT town FROM items")] * config.TOTAL_CANDIDATES  # hepsi hata verir
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "low_confidence"
    assert answer["sql"] == "SELECT COUNT(*) FROM items"


def test_nothing_runs_gives_no_answer(db, fake_model):
    replies, _ = fake_model
    replies += [text_reply("I am not sure.")] * config.MAX_TOOL_CALLS + teacher_gives_up()
    replies += [sql_reply("SELECT town FROM items")] * config.TOTAL_CANDIDATES
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "no_answer" and answer["sql"] is None


def test_repeated_sql_is_not_run_again(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply("SELECT COUNT(*) FROM items"),
                execute_reply("SELECT  COUNT(*)\nFROM items"),  # aynı SQL, farklı boşluk
                submit_reply("SELECT COUNT(*) FROM items")]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["executions"] == 1
    assert answer["tool_calls"] == 3  # tekrar da budget'tan düştü
    assert observation(seen[2][-1]) == "Not run again: you already made this exact call and its result will not " \
                                     "change. Try a different query, or submit your answer. Its result was:\n" \
                                     "Columns: COUNT(*)\n1 rows:\n150"


def test_search_values_tool(db, fake_model):
    replies, seen = fake_model
    replies += [call_reply("search_values", {"query": "Los Angles"}), submit_reply("SELECT 1")]
    loop.answer_question("Items in LA?", "", db)
    assert observation(seen[1][-1]) == "Values similar to 'Los Angles':\n- items.city = 'Los Angeles'"


def test_final_check_rejects_unexpected_empty_result(db, fake_model):
    replies, seen = fake_model
    empty_sql = "SELECT id FROM items WHERE city = 'Paris'"
    replies += [submit_reply(empty_sql), submit_reply(empty_sql)] + teacher_gives_up()
    answer = loop.answer_question("Which items are in Paris?", "", db)
    assert observation(seen[1][-1]).startswith("Final check failed: the query returns no rows")
    assert answer["label"] == "low_confidence"  # 2 kez geçmedi → teacher → fallback answer
    assert answer["handoff_reason"] == "final check 2 kez geçmedi"
    assert answer["sql"] == empty_sql


def test_final_check_accepts_empty_result_the_agent_already_saw(db, fake_model):
    replies, _ = fake_model
    empty_sql = "SELECT id FROM items WHERE city = 'Paris'"
    replies += [execute_reply(empty_sql), submit_reply(empty_sql)]
    assert loop.answer_question("Which items are in Paris?", "", db)["label"] == "ok"


def test_candidates_agree_high(db, fake_model, monkeypatch):
    replies, seen = fake_model
    replies += [call_reply("search_values", {"query": "Bostn"}),
                submit_reply("SELECT 1"), sql_reply("SELECT 1"), sql_reply("SELECT  1")]
    answer = loop.answer_question("One?", "", db)
    assert answer["label"] == "ok" and answer["candidates"] == 2  # 3/3 aynı: 8'e tamamlanmadı
    candidate_prompt = seen[2][1]["content"]
    assert "Search results found while working on this question:\nValues similar to 'Bostn'" in candidate_prompt
    assert "SELECT 1" not in candidate_prompt  # agent'ın SQL'i candidate prompt'una girmez


def test_candidates_disagree_medium_then_high(db, fake_model, monkeypatch):
    replies, seen = fake_model
    first_round = ["SELECT 2", "SELECT 2", "SELECT 1", "SELECT 1", "SELECT 1", "SELECT 2", "SELECT 3"]  # 1: 4/8
    replies += [submit_reply("SELECT 1")] + [sql_reply(sql) for sql in first_round]
    replies += [submit_reply("SELECT 1"), sql_reply("SELECT 1"), sql_reply("SELECT 1")]  # ikinci submit: 3/3
    answer = loop.answer_question("One?", "", db)
    note = observation(seen[8][-1])
    assert note.startswith("Medium confidence")
    assert "Group 1 (4 of 8 candidates): SELECT 1" in note and "Group 2 (3 of 8 candidates): SELECT 2" in note
    assert answer["label"] == "ok" and answer["candidates"] == 9


def test_candidates_low_goes_to_fallback(db, fake_model, monkeypatch):
    replies, _ = fake_model
    replies += [submit_reply("SELECT 1")] + [sql_reply(f"SELECT {n}") for n in range(2, 9)]  # hepsi farklı
    replies += teacher_gives_up()
    answer = loop.answer_question("One?", "", db)
    assert answer["label"] == "low_confidence" and answer["handoff_reason"] == "confidence low"
    assert answer["sql"] == "SELECT 1"  # başa başta agent'ın grubu seçilir


def test_every_question_is_written_to_the_experience_log(db, fake_model):
    """Kullanımda (ör. run.py) da her soru loga girer; doğru SQL olmadığı için correct boş kalır."""
    replies, _ = fake_model
    replies += [execute_reply("SELECT COUNT(*) FROM items"), submit_reply("SELECT COUNT(*) FROM items")]
    loop.answer_question("How many items?", "", db)
    record = json.loads(config.EXPERIENCE_LOG.read_text())
    assert record["split"] == "use" and record["correct"] is None and record["label"] == "ok"
    assert record["messages"][1]["content"].endswith("Question: How many items?")  # adım 1'in bağlamı
    assert record["messages"][-1]["content"] == "Accepted."


def test_submitted_sql_that_does_not_run_goes_back_without_candidates(db, fake_model):
    replies, seen = fake_model
    replies += [submit_reply("SELECT town FROM items"), submit_reply("SELECT COUNT(*) FROM items")]
    answer = loop.answer_question("How many items?", "", db)
    assert observation(seen[1][-1]).startswith(
        "Submit rejected: your query does not run: Rejected before running: no such column: town. ")
    assert answer["label"] == "ok" and answer["candidates"] == 2  # yalnızca ikinci submit candidate üretti


def test_agent_is_reminded_to_submit_when_the_budget_is_almost_gone(db, fake_model):
    replies, seen = fake_model
    replies += [text_reply("I am not sure.")] * config.MAX_TOOL_CALLS + teacher_gives_up()
    loop.answer_question("How many items?", "", db)
    last_agent_turn = seen[config.MAX_TOOL_CALLS - 1][-1]["content"]  # agent'ın son isteğinden önceki not
    assert last_agent_turn.endswith("[1 tool call(s) left. If a query you ran answers the question, call submit with it now.]")


def test_remaining_budget_is_shown_under_every_result(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply("SELECT COUNT(*) FROM items"), submit_reply("SELECT COUNT(*) FROM items")]
    answer = loop.answer_question("How many items?", "", db)
    assert seen[1][-1]["content"].endswith(f"\n[{config.MAX_TOOL_CALLS - 1} tool call(s) left.]")
    assert answer["steps"][0]["result"] == "Columns: COUNT(*)\n1 rows:\n150"  # adım kaydında budget notu yok


def test_third_repeat_of_the_same_call_hands_over(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply("SELECT COUNT(*) FROM items")] * (config.MAX_REPEATS + 1) + teacher_gives_up()
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == "aynı çağrı 3 kez tekrarlandı"
    assert answer["steps"][config.MAX_REPEATS]["result"] == "Handoff: the same call was repeated too many times."


def test_teacher_repeating_the_agents_call_is_not_stuck(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply("SELECT COUNT(*) FROM items")] * (config.MAX_REPEATS + 1)  # agent takıldı
    replies += [execute_reply("SELECT COUNT(*) FROM items"), submit_reply("SELECT COUNT(*) FROM items")]  # teacher
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "ok" and answer["answered_by"] == "teacher"
    assert answer["steps"][-2]["result"].startswith("Not run again")  # teacher önceki sonucu gördü, devam etti


def test_stuck_agent_samples_its_next_step(db, fake_model, monkeypatch):
    replies, _ = fake_model
    replies += [text_reply("hmm"), execute_reply("SELECT 1"), execute_reply("SELECT 1"), submit_reply("SELECT 1")]
    temperatures = []
    fake = llm.chat

    def recording(messages, tools=None, seed=None, temperature=None, model=None):
        if tools:  # yalnızca agent'ın adımları; candidate'ler kendi temperature'ıyla yazılır
            temperatures.append(temperature)
        return fake(messages, tools=tools, seed=seed, temperature=temperature, model=model)

    monkeypatch.setattr(llm, "chat", recording)
    loop.answer_question("One?", "", db)
    retry = config.RETRY_TEMPERATURE
    assert temperatures == [None, retry, None, retry]  # reddedilen ve tekrarlanan çağrıdan sonra örneklendi
