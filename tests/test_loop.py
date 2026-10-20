"""agent/loop.py testleri (aşama 6–16). Model yerine sırayla verilen sahte cevaplar kullanılır; API'ye istek gitmez."""

import json

import pytest

import config
from agent import loop
from tests.fakes import EMPTY, ONE_ROW, call_reply, execute_reply, sql_reply, submit_reply, text_reply


def test_submit_ends_the_loop(db, fake_model):
    replies, seen = fake_model
    replies.append(submit_reply("SELECT COUNT(*) FROM items"))
    answer = loop.answer_question("How many items?", "", db)
    assert answer["sql"] == "SELECT COUNT(*) FROM items"
    assert answer["label"] == "ok"
    assert answer["tool_calls"] == 1
    assert "Table items (150 rows)" in seen[0][1]["content"]  # adım 1'in bağlamı modele gitti
    assert answer["cost"] == pytest.approx(0.001)


def test_broken_output_is_rejected_and_counted(db, fake_model):
    replies, seen = fake_model
    replies += [text_reply("SELECT 1"), submit_reply("SELECT 1")]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "ok"
    assert answer["tool_calls"] == 2  # reddedilen çıktı da budget'tan düştü
    assert seen[1][-1]["content"].startswith("Rejected: your reply was not a tool call")  # hata agent'a döndü


def test_budget_runs_out_into_fallback_answer(db, fake_model):
    replies, _ = fake_model
    replies += [text_reply("I am not sure.")] * config.MAX_TOOL_CALLS
    answer = loop.answer_question("How many items?", "", db)
    assert answer["tool_calls"] == config.MAX_TOOL_CALLS
    assert answer["label"] == "no_answer"
    assert answer["sql"] is None
    assert answer["handoff_reason"] == "budget bitti"


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
    assert f"150 rows (first {config.SHOWN_ROWS} shown):" in observation  # aşama 10: kırpma
    assert len(observation.splitlines()) == 2 + config.SHOWN_ROWS + 1  # başlık, satırlar, surprise note


def test_fallback_uses_last_sql_that_ran(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply("SELECT COUNT(*) FROM items")]
    replies += [text_reply("I am not sure.")] * (config.MAX_TOOL_CALLS - 1)
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "low_confidence"
    assert answer["sql"] == "SELECT COUNT(*) FROM items"


def test_repeated_sql_is_not_run_again(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply("SELECT COUNT(*) FROM items"),
                execute_reply("SELECT  COUNT(*)\nFROM items", EMPTY),  # aynı SQL, farklı boşluk ve forecast
                submit_reply("SELECT COUNT(*) FROM items")]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["executions"] == 1
    assert answer["tool_calls"] == 3  # tekrar da budget'tan düştü
    assert seen[2][-1]["content"] == "Not run again: you already made this exact call. Its result was:\n" \
                                     "Columns: COUNT(*)\n1 rows:\n150"


def test_cache_returns_earlier_result_without_running(db, monkeypatch):
    monkeypatch.setattr(config, "USE_WORLD_MODEL", False)
    context = loop.Context("How many items?", "", db)
    first = loop.run_query("SELECT COUNT(*) FROM items", None, context)
    second = loop.run_query("SELECT COUNT(*)  FROM items", None, context)  # ör. bir candidate aynısını yazdı
    assert first == second
    assert context.executions == 1


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
    assert seen[1][-1]["content"] == "Rejected: 'execute_sql' needs a non-empty value for: forecast."
    assert answer["executions"] == 1  # yalnızca final check çalıştırdı


def test_forecast_flag_off(db, fake_model, monkeypatch):
    monkeypatch.setattr(config, "USE_AGENT_FORECAST", False)
    replies, seen = fake_model
    replies += [call_reply("execute_sql", {"sql": "SELECT 1", "forecast": "bozuk"}), submit_reply("SELECT 1")]
    answer = loop.answer_question("One?", "", db)
    assert seen[1][-1]["content"] == "Columns: 1\n1 rows:\n1"  # istenmeyen forecast'e bakılmadı
    assert answer["executions"] == 1 and answer["forecasts"] == 0


def test_search_values_tool(db, fake_model):
    replies, seen = fake_model
    replies += [call_reply("search_values", {"query": "Los Angles"}), submit_reply("SELECT 1")]
    loop.answer_question("Items in LA?", "", db)
    assert seen[1][-1]["content"] == "Values similar to 'Los Angles':\n- items.city = 'Los Angeles'"


def test_every_real_run_is_logged(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply("SELECT COUNT(*) FROM items"), submit_reply("SELECT COUNT(*) FROM items")]
    loop.answer_question("How many items?", "", db, seed=0, question_id=7, split="dev")
    lines = config.EXPERIENCE_LOG.read_text().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["question_id"] == 7 and record["split"] == "dev" and record["db_id"] == "shop"
    assert record["sql"] == "SELECT COUNT(*) FROM items" and record["run_by"] == "agent"
    assert record["forecast"] == ONE_ROW and record["forecast_hit"] is True
    assert record["result"]["type"] == "rows" and record["result"]["rows"] == "1"
    assert record["model"] == config.POLICY_MODEL and record["seed"] == 0




def test_final_check_rejects_unexpected_empty_result(db, fake_model):
    replies, seen = fake_model
    empty_sql = "SELECT id FROM items WHERE city = 'Paris'"
    replies += [submit_reply(empty_sql), submit_reply(empty_sql)]
    answer = loop.answer_question("Which items are in Paris?", "", db)
    assert seen[1][-1]["content"].startswith("Final check failed: the query returns no rows")
    assert answer["label"] == "low_confidence"  # 2 kez geçmedi → fallback answer
    assert answer["handoff_reason"] == "final check 2 kez geçmedi"
    assert answer["sql"] == empty_sql


def test_final_check_accepts_empty_result_that_was_forecast(db, fake_model):
    replies, _ = fake_model
    empty_sql = "SELECT id FROM items WHERE city = 'Paris'"
    replies += [execute_reply(empty_sql, EMPTY), submit_reply(empty_sql)]
    assert loop.answer_question("Which items are in Paris?", "", db)["label"] == "ok"


def test_final_check_catches_broken_sql_that_never_ran(db, fake_model):
    replies, seen = fake_model
    replies += [submit_reply("SELECT town FROM items"), submit_reply("SELECT COUNT(*) FROM items")]
    answer = loop.answer_question("How many items?", "", db)
    assert seen[1][-1]["content"] == "Final check failed: Rejected before running: no such column: town"
    assert answer["label"] == "ok" and answer["sql"] == "SELECT COUNT(*) FROM items"


def test_candidates_agree_high(db, fake_model, monkeypatch):
    monkeypatch.setattr(config, "USE_CANDIDATES", True)
    replies, seen = fake_model
    replies += [call_reply("search_values", {"query": "Bostn"}),
                submit_reply("SELECT 1"), sql_reply("SELECT 1"), sql_reply("SELECT  1")]
    answer = loop.answer_question("One?", "", db)
    assert answer["label"] == "ok" and answer["candidates"] == 2  # 3/3 aynı: 8'e tamamlanmadı
    candidate_prompt = seen[2][1]["content"]
    assert "Search results found while working on this question:\nValues similar to 'Bostn'" in candidate_prompt
    assert "SELECT 1" not in candidate_prompt  # agent'ın SQL'i candidate prompt'una girmez


def test_candidates_disagree_medium_then_high(db, fake_model, monkeypatch):
    monkeypatch.setattr(config, "USE_CANDIDATES", True)
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
    monkeypatch.setattr(config, "USE_CANDIDATES", True)
    replies, _ = fake_model
    replies += [submit_reply("SELECT 1")] + [sql_reply(f"SELECT {n}") for n in range(2, 9)]  # hepsi farklı
    answer = loop.answer_question("One?", "", db)
    assert answer["label"] == "low_confidence" and answer["handoff_reason"] == "confidence low"
    assert answer["sql"] == "SELECT 1"  # başa başta agent'ın grubu seçilir
