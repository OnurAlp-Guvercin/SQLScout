"""agent/loop.py testleri: akış uçtan uca. Model yerine sırayla verilen sahte cevaplar kullanılır; API'ye istek gitmez."""

import json

import pytest

import config
from agent import llm, loop, prompts
from harness.tools import execute_sql, submit
from tests.fakes import call_reply, execute_reply, submit_reply, text_reply, observation

COUNT_SQL = "SELECT COUNT(*) FROM items"
EMPTY_SQL = "SELECT id FROM items WHERE city = 'Paris'"


def large_model_gives_up():
    """Handoff'tan sonra large model de çözemez: budget'ı boyunca bir şey yapmaz, fallback answer return edilir."""
    return [text_reply("I am not sure.")] * config.MAX_TOOL_CALLS


def different_queries(count):
    """Her biri dolu sonuç veren, birbirinden farklı sorgular: boşa gitmez, tekrar sayılmaz."""
    return [execute_reply(f"SELECT {number}") for number in range(1, count + 1)]


def agent_wastes_calls():
    """Small model arka arkaya bocalar (okunamayan cevaplar): erken handoff."""
    return [text_reply("I am not sure.")] * config.WASTED_CALLS


def test_execute_then_submit(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["sql"] == COUNT_SQL and answer["label"] == "ok"
    assert answer["tool_calls"] == 2 and answer["executions"] == 1  # final check sonucu cache'ten aldı
    assert "Table items (150 rows)" in seen[0][1]["content"]  # adım 1'in bağlamı modele gitti
    assert seen[1][-1]["role"] == "tool" and observation(seen[1][-1]) == "Columns: COUNT(*)\n1 rows:\n150"
    assert answer["cost"] == pytest.approx(0.003)  # small model'in 2 isteği ve large model kontrolü


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
    replies, _ = fake_model
    no_rows = [execute_reply(EMPTY_SQL), call_reply("search_values", {"query": "Paris"}),
               execute_reply("SELECT id FROM items WHERE city = 'Rome'"), call_reply("search_values", {"query": "Rome"}),
               execute_reply("SELECT id FROM items WHERE city = 'Oslo'"), call_reply("search_values", {"query": "Oslo"})]
    replies += no_rows[:config.PROGRESS_CALLS] + large_model_gives_up()
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == f"no query returned rows in the first {config.PROGRESS_CALLS} calls"
    assert answer["tool_calls"] == config.PROGRESS_CALLS + config.MAX_TOOL_CALLS  # large model'in tam budget'ı
    assert answer["label"] == "no_answer" and answer["sql"] is None  # hiçbir SQL submit edilmedi


def test_wasted_calls_hand_over_early(db, fake_model):
    replies, _ = fake_model
    replies += agent_wastes_calls() + large_model_gives_up()
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == f"{config.WASTED_CALLS} calls in a row were wasted"
    assert answer["tool_calls"] == config.WASTED_CALLS + config.MAX_TOOL_CALLS


def test_a_useful_call_resets_the_wasted_count(db, fake_model):
    replies, _ = fake_model
    almost = [text_reply("I am not sure.")] * (config.WASTED_CALLS - 1)
    replies += almost + [execute_reply(COUNT_SQL)] + almost + [execute_reply("SELECT 1")]  # arada dolu sonuç veren sorgular
    replies += large_model_gives_up()
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == "the tool-call budget ran out"  # hiçbir zaman arka arkaya 5 boşa çağrı olmadı


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
    assert len(text.splitlines()) == 2 + config.SHOWN_ROWS + 1  # başlık, satırlar ve kırpma notu
    assert text.endswith(execute_sql.TRIMMED_HINT)  # hepsini görmeden submit edebilir


def test_explored_queries_are_never_an_answer(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL), execute_reply(EMPTY_SQL)]
    replies += different_queries(config.MAX_TOOL_CALLS - 2) + large_model_gives_up()
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == "the tool-call budget ran out"
    assert answer["label"] == "no_answer" and answer["sql"] is None  # hiçbir SQL submit edilmedi
    assert answer["error_message"] == ("No answer: no SQL query that runs without error was submitted (handoff "
                                       "reason: the tool-call budget ran out; large model: the tool-call budget ran out).")


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


def test_submit_without_running_the_query_first(db, fake_model):
    replies, _ = fake_model
    replies += [submit_reply(COUNT_SQL)]  # agent sorguyu önce execute_sql ile denemedi
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "ok" and answer["tool_calls"] == 1 and answer["executions"] == 1  # final check çalıştırdı



def test_final_check_failing_twice_hands_over(db, fake_model):
    replies, _ = fake_model
    replies += [submit_reply("SELECT town FROM items"), submit_reply("SELECT town FROM items")] + large_model_gives_up()
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
    replies += different_queries(config.MAX_TOOL_CALLS) + large_model_gives_up()
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
    start = different_queries(config.PROGRESS_CALLS - 1)  # tekrarlar ilk çağrılardan sonra: erken handoff olmaz
    replies += start + [execute_reply(COUNT_SQL)] * (config.MAX_REPEATS + 1) + large_model_gives_up()
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == f"the same call was repeated {config.MAX_REPEATS} times"
    assert answer["steps"][len(start) + config.MAX_REPEATS]["result"] == (f"Handoff: the same call was repeated "
                                                                          f"{config.MAX_REPEATS} times.")


def test_large_model_starts_fresh_without_the_agents_conversation(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply(COUNT_SQL)] + agent_wastes_calls()  # agent bocaladı
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]  # large model: small model'in sorgusunu kendisi çalıştırır
    answer = loop.answer_question("How many items?", "", db)
    large_model_start = seen[1 + config.WASTED_CALLS]
    assert [message["content"] for message in large_model_start] == [message["content"] for message in seen[0]]
    assert answer["steps"][1 + config.WASTED_CALLS]["by"] == "large_model"  # large model'in ilk adımı kendi seçtiği tool call
    assert answer["label"] == "ok" and answer["answered_by"] == "large_model" and answer["sql"] == COUNT_SQL
    assert answer["steps"][-2]["result"] == "Columns: COUNT(*)\n1 rows:\n150"  # agent'ın tekrarı sayılmadı
    record = json.loads(config.EXPERIENCE_LOG.read_text())
    assert record["messages"][-1]["content"].startswith("Rejected: no valid tool call")  # agent'ın konuşması
    assert record["large_model_messages"][-1]["content"] == "Accepted."


def test_stuck_agent_samples_its_next_step(db, fake_model, monkeypatch):
    replies, _ = fake_model
    replies += [text_reply("hmm"), execute_reply(COUNT_SQL)] + different_queries(2)
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    temperatures = []
    fake = llm.chat

    def recording(messages, tools=None, temperature=None, model=None):
        if tools:  # yalnızca small model'in adımları; large model kontrolü kendi temperature'ıyla çalışır
            temperatures.append(temperature)
        return fake(messages, tools=tools, temperature=temperature, model=model)

    monkeypatch.setattr(llm, "chat", recording)
    loop.answer_question("How many items?", "", db)
    retry = config.RETRY_TEMPERATURE
    assert temperatures == [None, retry, None, None, None, retry]  # reddedilen ve tekrarlanan adımdan sonra örneklendi


def test_agent_samples_after_a_query_rejected_by_the_pre_check(db, fake_model, monkeypatch):
    replies, _ = fake_model
    replies += [execute_reply("SELECT town FROM items"), execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    temperatures = []
    fake = llm.chat

    def recording(messages, tools=None, temperature=None, model=None):
        if tools:
            temperatures.append(temperature)
        return fake(messages, tools=tools, temperature=temperature, model=model)

    monkeypatch.setattr(llm, "chat", recording)
    loop.answer_question("How many items?", "", db)
    assert temperatures == [None, config.RETRY_TEMPERATURE, None]  # "no such column" reddinden sonra örneklendi


def test_large_model_takes_over_when_the_small_model_fails(db, fake_model, monkeypatch):
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]  # large model
    fake = llm.chat

    def small_model_down(messages, tools=None, temperature=None, model=None):
        if model == config.SMALL_MODEL:
            raise RuntimeError("Insufficient Memory")
        return fake(messages, tools=tools, temperature=temperature, model=model)

    monkeypatch.setattr(llm, "chat", small_model_down)
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == "the small model gave an error: Insufficient Memory"
    assert answer["label"] == "ok" and answer["answered_by"] == "large_model" and answer["sql"] == COUNT_SQL
    record = json.loads(config.EXPERIENCE_LOG.read_text())
    assert record["handoff_reason"] == answer["handoff_reason"]  # soru experience log'dan kaybolmadı


def test_answer_the_large_model_does_not_approve_hands_over(db, fake_model, monkeypatch):
    monkeypatch.setattr(submit, "large_model_review", lambda sql, context: (context.large_model, "Wrong."))  # agent'ınkini reddeder
    replies, seen = fake_model
    replies += [execute_reply(EMPTY_SQL), submit_reply(EMPTY_SQL),  # small model: large model onaylamadı
                execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]  # large model: kendi cevabı onaylanır
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == "a reviewer judged the submitted query to be wrong"
    assert len(seen[2]) == 2  # large model sıfırdan başladı: sistem prompt'u ve adım 1
    assert answer["label"] == "ok" and answer["answered_by"] == "large_model" and answer["sql"] == COUNT_SQL


def test_rejected_answer_is_the_fallback_when_the_large_model_cannot_solve_it(db, fake_model, monkeypatch):
    monkeypatch.setattr(submit, "large_model_review", lambda sql, context: (context.large_model, "Wrong."))  # agent'ınkini reddeder
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)] + large_model_gives_up()
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "fallback" and answer["sql"] == COUNT_SQL and answer["answered_by"] == "small_model"


def test_fallback_is_the_last_submitted_sql(db, fake_model, monkeypatch):
    """Large model'in submit ettiği SQL de onaylanmaz ve budget'ı biterse fallback o SQL olur."""
    monkeypatch.setattr(submit, "large_model_review", lambda sql, context: (False, "Wrong."))  # hiçbir cevabı onaylamaz
    replies, _ = fake_model
    replies += [execute_reply(EMPTY_SQL), submit_reply(EMPTY_SQL)]  # small model: large model onaylamadı
    replies += [submit_reply(COUNT_SQL)] + [text_reply("I am not sure.")] * (config.MAX_TOOL_CALLS - 1)
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "fallback" and answer["sql"] == COUNT_SQL and answer["answered_by"] == "large_model"


def test_submit_without_the_semicolon_uses_the_cache(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL + ";"), submit_reply(COUNT_SQL)]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "ok" and answer["executions"] == 1  # aynı sorgu: final check sonucu cache'ten aldı


def test_large_model_starts_with_temperature_zero_after_a_stuck_agent(db, fake_model, monkeypatch):
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL)] * (1 + config.MAX_REPEATS)  # small model tekrarladı; son adımı örneklendi
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]  # large model
    calls = []
    fake = llm.chat

    def recording(messages, tools=None, temperature=None, model=None):
        if tools:
            calls.append((model, temperature))
        return fake(messages, tools=tools, temperature=temperature, model=model)

    monkeypatch.setattr(llm, "chat", recording)
    loop.answer_question("How many items?", "", db)
    assert calls[config.MAX_REPEATS][1] == config.RETRY_TEMPERATURE  # small model'in son adımı
    assert calls[config.MAX_REPEATS + 1] == (config.LARGE_MODEL, None)  # large model'in ilk adımı temperature 0


def test_fallback_is_kept_when_the_large_model_cannot_be_reached(db, fake_model, monkeypatch):
    monkeypatch.setattr(submit, "large_model_review", lambda sql, context: (context.large_model, "Wrong."))  # agent'ınkini reddeder
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    fake = llm.chat

    def large_model_down(messages, tools=None, temperature=None, model=None):
        if model == config.LARGE_MODEL:
            raise RuntimeError("Modele ulaşılamadı")
        return fake(messages, tools=tools, temperature=temperature, model=model)

    monkeypatch.setattr(llm, "chat", large_model_down)
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "fallback" and answer["sql"] == COUNT_SQL  # agent'ın submit ettiği SQL kaybolmadı
    assert answer["large_model_error"] == "Modele ulaşılamadı"
    record = json.loads(config.EXPERIENCE_LOG.read_text())
    assert record["large_model_error"] == "Modele ulaşılamadı"


def test_large_model_gets_its_own_final_check_tries(db, fake_model):
    replies, _ = fake_model
    broken = "SELECT town FROM items"
    replies += [execute_reply(COUNT_SQL), submit_reply(broken), submit_reply(broken)]  # agent: 2 kez geçmedi
    replies += [submit_reply(broken), execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]  # large model: bir hata, sonra doğru
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == f"the final check failed {config.FINAL_CHECK_TRIES} times"
    assert answer["label"] == "ok" and answer["answered_by"] == "large_model"
    handoff = answer["steps"][2]["result"]  # agent'ın ikinci hatalı submit'i: son not experience log'da kalır
    assert handoff.startswith("Final check failed: Rejected before running: no such column: town")
    assert handoff.endswith(f"Handoff: the final check failed {config.FINAL_CHECK_TRIES} times.")


def test_no_answer_says_why_the_large_model_stopped(db, fake_model):
    replies, _ = fake_model
    replies += agent_wastes_calls()
    replies += [execute_reply(COUNT_SQL)] * (config.MAX_REPEATS + 1)  # large model takıldı
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "no_answer" and answer["answered_by"] is None
    assert answer["large_model_stop_reason"] == f"the same call was repeated {config.MAX_REPEATS} times"


def test_rejected_large_model_answer_comes_back_as_a_note(db, fake_model, monkeypatch):
    monkeypatch.setattr(submit, "large_model_review", lambda sql, context: (sql == COUNT_SQL, "It lists ids."))
    replies, _ = fake_model
    replies += [execute_reply(EMPTY_SQL), submit_reply(EMPTY_SQL)]  # agent: reddedildi → handoff
    replies += [execute_reply("SELECT id FROM items"), submit_reply("SELECT id FROM items"),  # large model: reddedildi
                execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]  # large model düzeltti
    answer = loop.answer_question("How many items?", "", db)
    assert answer["steps"][-3]["result"] == submit.REVIEWER_NOTE.format(reason="It lists ids.")  # gerekçe large model'e döndü
    assert answer["label"] == "ok" and answer["answered_by"] == "large_model" and answer["sql"] == COUNT_SQL


def test_without_handoff_a_rejected_answer_comes_back_to_the_agent(db, fake_model, monkeypatch):
    monkeypatch.setattr(config, "HANDOFF", False)
    monkeypatch.setattr(submit, "large_model_review", lambda sql, context: (sql == COUNT_SQL, "It lists ids."))
    replies, _ = fake_model
    replies += [execute_reply(EMPTY_SQL), submit_reply(EMPTY_SQL),  # reddedildi: handoff yok, gerekçe agent'a döner
                execute_reply(COUNT_SQL), submit_reply(COUNT_SQL)]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["steps"][1]["result"] == submit.REVIEWER_NOTE.format(reason="It lists ids.")
    assert answer["label"] == "ok" and answer["answered_by"] == "small_model" and answer["handoff_reason"] is None


def test_without_handoff_the_agent_uses_its_whole_budget(db, fake_model, monkeypatch):
    monkeypatch.setattr(config, "HANDOFF", False)
    replies, _ = fake_model
    replies += agent_wastes_calls() + [text_reply("I am not sure.")] * (config.MAX_TOOL_CALLS - config.WASTED_CALLS)
    answer = loop.answer_question("How many items?", "", db)
    assert answer["tool_calls"] == config.MAX_TOOL_CALLS  # erken handoff yok
    assert all(step["by"] == "small_model" for step in answer["steps"])  # large model hiç devralmadı
    assert answer["label"] == "no_answer" and answer["handoff_reason"] == "the tool-call budget ran out"


def test_without_handoff_stop_notes_do_not_say_handoff(db, fake_model, monkeypatch):
    monkeypatch.setattr(config, "HANDOFF", False)
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL), submit_reply(COUNT_SQL), execute_reply(EMPTY_SQL), submit_reply(EMPTY_SQL)]
    fake = llm.chat

    def large_model_says_no(messages, **kwargs):
        if messages[0]["content"] == prompts.CHECK_ANSWER:
            return text_reply('{"reason": "Wrong.", "correct": false}')
        return fake(messages, **kwargs)

    monkeypatch.setattr(llm, "chat", large_model_says_no)
    answer = loop.answer_question("How many items?", "", db)
    assert answer["steps"][-1]["result"].endswith(f"Stopped: the final check failed {config.FINAL_CHECK_TRIES} times.")
    assert [check["sql"] for check in answer["large_model_checks"]] == [COUNT_SQL, EMPTY_SQL]  # her karar kayıtlı
    assert answer["label"] == "fallback" and answer["sql"] == EMPTY_SQL
