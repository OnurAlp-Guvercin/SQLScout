"""agent/loop.py testleri: akış uçtan uca. Model yerine sırayla verilen sahte cevaplar kullanılır; API'ye istek gitmez."""

import json

import pytest

import config
from agent import loop
from tests.fakes import EMPTY, call_reply, execute_reply, sql_reply, submit_reply, text_reply


def teacher_gives_up():
    """Handoff'tan sonra teacher da çözemez: yarım budget'ı boyunca tool çağırmaz, fallback answer döner."""
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
    assert seen[1][-1]["content"].startswith("Rejected: your reply was not a tool call")  # hata agent'a döndü


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
    forecast = {"type": "rows", "columns": ["city", "n"], "rows": "2-10", "trust": True}
    replies += [execute_reply("SELECT city, COUNT(*) FROM items GROUP BY city ORDER BY city", forecast),
                submit_reply("SELECT city, COUNT(*) FROM items GROUP BY city ORDER BY city")]
    answer = loop.answer_question("How many items per city?", "", db)
    observation = seen[1][-1]
    assert observation["role"] == "tool"
    assert observation["content"] == "Columns: city, COUNT(*)\n3 rows:\nBoston | 50\nChicago | 50\nLos Angeles | 50"
    assert answer["label"] == "ok"
    assert answer["tool_calls"] == 2
    assert answer["executions"] == 1
    assert answer["forecast_hits"] == 1


def test_execute_sql_error_and_empty_result_go_back_to_agent(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply("SELECT town FROM items"),
                execute_reply("SELECT id FROM items WHERE city = 'Paris'", EMPTY),
                submit_reply("SELECT id FROM items WHERE city = 'Boston'")]
    answer = loop.answer_question("Which items are in Boston?", "", db)
    assert seen[1][-1]["content"] == "Rejected before running: no such column: town"  # pre-check yakaladı
    assert answer["executions"] == 2  # ilk SQL pre-check'te kaldı; ikincisi ve submit edilen çalıştı
    assert seen[2][-1]["content"] == "Columns: id\nNo rows: the result is empty."
    assert answer["label"] == "ok"  # submit edilen SQL final check'te çalıştırıldı (2. gerçek çalıştırma)


def test_long_result_says_how_many_rows_are_shown(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply("SELECT id FROM items"), submit_reply("SELECT id FROM items")]
    loop.answer_question("List all items.", "", db)
    observation = seen[1][-1]["content"]
    assert f"150 rows (first {config.SHOWN_ROWS} shown):" in observation  # kırpma
    assert len(observation.splitlines()) == 2 + config.SHOWN_ROWS + 1  # başlık, satırlar, surprise note


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
                execute_reply("SELECT  COUNT(*)\nFROM items", EMPTY),  # aynı SQL, farklı boşluk ve forecast
                submit_reply("SELECT COUNT(*) FROM items")]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["executions"] == 1
    assert answer["tool_calls"] == 3  # tekrar da budget'tan düştü
    assert seen[2][-1]["content"] == "Not run again: you already made this exact call and its result will not " \
                                     "change. Try a different query, or submit your answer. Its result was:\n" \
                                     "Columns: COUNT(*)\n1 rows:\n150"


def test_wrong_forecast_gets_a_surprise_note(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply("SELECT id FROM items WHERE city = 'Paris'"), submit_reply("SELECT 1")]
    answer = loop.answer_question("Which items are in Paris?", "", db)
    assert seen[1][-1]["content"].endswith("Surprise: you forecast 1 column(s) and 1 row(s), but the real result "
                                           "is an empty result. Check the query before you submit it.")
    assert answer["forecasts"] == 1 and answer["forecast_hits"] == 0


def test_execute_sql_without_forecast_is_rejected(db, fake_model):
    replies, seen = fake_model
    replies += [call_reply("execute_sql", {"sql": "SELECT 1"}), submit_reply("SELECT 1")]
    answer = loop.answer_question("One?", "", db)
    assert seen[1][-1]["content"] == "Rejected: 'execute_sql' needs a non-empty value for: type."
    assert answer["executions"] == 1  # yalnızca final check çalıştırdı


def test_search_values_tool(db, fake_model):
    replies, seen = fake_model
    replies += [call_reply("search_values", {"query": "Los Angles"}), submit_reply("SELECT 1")]
    loop.answer_question("Items in LA?", "", db)
    assert seen[1][-1]["content"] == "Values similar to 'Los Angles':\n- items.city = 'Los Angeles'"


def test_final_check_rejects_unexpected_empty_result(db, fake_model):
    replies, seen = fake_model
    empty_sql = "SELECT id FROM items WHERE city = 'Paris'"
    replies += [submit_reply(empty_sql), submit_reply(empty_sql)] + teacher_gives_up()
    answer = loop.answer_question("Which items are in Paris?", "", db)
    assert seen[1][-1]["content"].startswith("Final check failed: the query returns no rows")
    assert answer["label"] == "low_confidence"  # 2 kez geçmedi → teacher → fallback answer
    assert answer["handoff_reason"] == "final check 2 kez geçmedi"
    assert answer["sql"] == empty_sql


def test_final_check_accepts_empty_result_that_was_forecast(db, fake_model):
    replies, _ = fake_model
    empty_sql = "SELECT id FROM items WHERE city = 'Paris'"
    replies += [execute_reply(empty_sql, EMPTY), submit_reply(empty_sql)]
    assert loop.answer_question("Which items are in Paris?", "", db)["label"] == "ok"


def test_final_check_catches_broken_sql_that_never_ran(db, fake_model):
    """Teacher'ın submit'i candidate'lere gitmez; final check çalışmayan SQL'i yakalar ve bu SQL cevap olmaz:
    fallback answer'a gidilir (burada sahte candidate'ler de aynı bozuk SQL'i yazdığı için cevap yok)."""
    replies, _ = fake_model
    replies += [text_reply("I am not sure.")] * config.MAX_TOOL_CALLS + [submit_reply("SELECT town FROM items")]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["steps"][-1]["result"] == "Final check failed: Rejected before running: no such column: town"
    assert answer["label"] == "no_answer" and answer["sql"] is None
    assert answer["executions"] == 0  # pre-check'te kaldı, hiç çalışmadı


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
    note = seen[8][-1]["content"]
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
    assert seen[1][-1]["content"] == "Submit rejected: your query does not run: Rejected before running: no such column: town"
    assert answer["label"] == "ok" and answer["candidates"] == 2  # yalnızca ikinci submit candidate üretti


def test_agent_is_reminded_to_submit_when_the_budget_is_almost_gone(db, fake_model):
    replies, seen = fake_model
    replies += [text_reply("I am not sure.")] * config.MAX_TOOL_CALLS + teacher_gives_up()
    loop.answer_question("How many items?", "", db)
    last_agent_turn = seen[config.MAX_TOOL_CALLS - 1][-1]["content"]  # agent'ın son isteğinden önceki not
    assert last_agent_turn.endswith("[1 tool call(s) left. If a query you ran answers the question, call submit with it now.]")
