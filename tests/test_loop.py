"""agent/loop.py testleri: akış uçtan uca. Model yerine sırayla verilen sahte cevaplar kullanılır; API'ye istek gitmez."""

import json

import pytest

import config
from agent import llm, loop
from tests.fakes import call_reply, execute_reply, submit_reply, text_reply, observation

COUNT_SQL = "SELECT COUNT(*) FROM items"
EMPTY_SQL = "SELECT id FROM items WHERE city = 'Paris'"


def teacher_gives_up():
    """Handoff'tan sonra teacher da çözemez: yarım budget'ı boyunca bir şey yapmaz, fallback answer return edilir."""
    return [text_reply("I am not sure.")] * (config.MAX_TOOL_CALLS // 2)


def test_sql_block_runs_and_submit_returns_it(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply(COUNT_SQL), submit_reply()]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["sql"] == COUNT_SQL and answer["label"] == "ok"
    assert answer["tool_calls"] == 2 and answer["executions"] == 1
    assert "Table items (150 rows)" in seen[0][1]["content"]  # adım 1'in bağlamı modele gitti
    assert seen[1][-1]["role"] == "user"  # SQL bloğunun sonucu kullanıcı mesajı olarak döner
    assert observation(seen[1][-1]) == "Columns: COUNT(*)\n1 rows:\n150"
    assert answer["cost"] == pytest.approx(0.002)


def test_reply_without_sql_block_or_tool_is_rejected_and_counted(db, fake_model):
    replies, seen = fake_model
    replies += [text_reply("The answer is 150."), execute_reply(COUNT_SQL), submit_reply()]
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "ok" and answer["tool_calls"] == 3  # reddedilen cevap da budget'tan düştü
    assert observation(seen[1][-1]).startswith("Rejected: your reply was not a tool call")


def test_no_progress_hands_over_early(db, fake_model):
    replies, seen = fake_model
    replies += [text_reply("I am not sure.")] * config.PROGRESS_CALLS + teacher_gives_up()
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == "ilerleme yok"  # dolu sonuç veren SQL yok: budget bitmeden teacher devraldı
    assert answer["tool_calls"] == config.PROGRESS_CALLS + config.MAX_TOOL_CALLS // 2  # teacher yarım budget alır
    assert observation(seen[config.PROGRESS_CALLS][-1]).startswith("A smaller agent worked on this question")
    assert answer["label"] == "no_answer" and answer["sql"] is None  # hiçbir SQL çalışmadı


def test_error_and_empty_result_go_back_to_agent(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply("SELECT town FROM items"), execute_reply(EMPTY_SQL),
                execute_reply("SELECT id FROM items WHERE city = 'Boston'"), submit_reply()]
    answer = loop.answer_question("Which items are in Boston?", "", db)
    assert observation(seen[1][-1]).startswith("Rejected before running: no such column: town. ")  # pre-check yakaladı
    assert observation(seen[2][-1]).startswith("Columns: id\nNo rows: the result is empty. If the query filters")
    assert answer["label"] == "ok" and answer["executions"] == 2  # ilk SQL çalıştırılmadı; final check cache'ten


def test_long_result_says_how_many_rows_are_shown(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply("SELECT id FROM items"), submit_reply()]
    loop.answer_question("List all items.", "", db)
    text = observation(seen[1][-1])
    assert f"150 rows (first {config.SHOWN_ROWS} shown):" in text  # kırpma
    assert len(text.splitlines()) == 2 + config.SHOWN_ROWS  # başlık ve satırlar


def test_fallback_uses_the_last_sql_that_returned_rows(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL), execute_reply(EMPTY_SQL)]
    replies += [text_reply("I am not sure.")] * (config.MAX_TOOL_CALLS - 2) + teacher_gives_up()
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == "budget bitti"
    assert answer["label"] == "fallback" and answer["sql"] == COUNT_SQL  # boş sonuç veren SQL fallback olmaz


def test_repeated_sql_is_not_run_again_but_can_be_submitted(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply(COUNT_SQL), execute_reply(EMPTY_SQL),
                execute_reply("SELECT  COUNT(*)\nFROM items"), submit_reply()]  # aynı SQL, farklı boşluk
    answer = loop.answer_question("How many items?", "", db)
    assert answer["executions"] == 2 and answer["tool_calls"] == 4  # tekrar çalıştırılmadı ama budget'tan düştü
    assert observation(seen[3][-1]) == "Not run again: you already made this exact call and its result will not " \
                                     "change. Try a different query, or submit your answer. Its result was:\n" \
                                     "Columns: COUNT(*)\n1 rows:\n150"
    assert answer["sql"] == "SELECT  COUNT(*)\nFROM items"  # tekrar edilen SQL submit edildi, boş olan değil


def test_search_values_tool(db, fake_model):
    replies, seen = fake_model
    replies += [call_reply("search_values", {"query": "Los Angles"}), execute_reply(COUNT_SQL), submit_reply()]
    loop.answer_question("Items in LA?", "", db)
    assert observation(seen[1][-1]) == "Values similar to 'Los Angles':\n- items.city = 'Los Angeles'"


def test_final_check_rejects_submit_before_any_query_and_a_failing_query(db, fake_model):
    replies, seen = fake_model
    replies += [submit_reply(), execute_reply("SELECT town FROM items"), submit_reply()] + teacher_gives_up()
    answer = loop.answer_question("How many items?", "", db)
    assert observation(seen[1][-1]).startswith("Final check failed: you have not run a query yet")
    assert answer["handoff_reason"] == "final check 2 kez geçmedi"  # çalışmayan SQL'in submit'i ikinci başarısızlık
    assert answer["label"] == "no_answer"


def test_empty_result_the_agent_saw_is_accepted(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply(EMPTY_SQL), submit_reply()]
    answer = loop.answer_question("Which items are in Paris?", "", db)
    assert answer["label"] == "ok" and answer["sql"] == EMPTY_SQL


def test_every_question_is_written_to_the_experience_log(db, fake_model):
    """Kullanımda (ör. run.py) da her soru loga girer; doğru SQL olmadığı için correct boş kalır."""
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL), submit_reply()]
    loop.answer_question("How many items?", "", db)
    record = json.loads(config.EXPERIENCE_LOG.read_text())
    assert record["split"] == "use" and record["correct"] is None and record["label"] == "ok"
    assert record["messages"][1]["content"].endswith("Question: How many items?")  # adım 1'in bağlamı
    assert record["messages"][2]["content"] == f"```sql\n{COUNT_SQL}\n```"  # agent'ın SQL bloğu
    assert record["messages"][-1]["content"] == "Accepted."


def test_agent_is_reminded_to_submit_when_the_budget_is_almost_gone(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply(COUNT_SQL)]
    replies += [text_reply("I am not sure.")] * (config.MAX_TOOL_CALLS - 1) + teacher_gives_up()
    loop.answer_question("How many items?", "", db)
    last_agent_turn = seen[config.MAX_TOOL_CALLS - 1][-1]["content"]  # agent'ın son isteğinden önceki not
    assert last_agent_turn.endswith("[1 tool call(s) left. If the last query you ran answers the question, call submit now.]")


def test_remaining_budget_is_shown_under_every_result(db, fake_model):
    replies, seen = fake_model
    replies += [execute_reply(COUNT_SQL), submit_reply()]
    answer = loop.answer_question("How many items?", "", db)
    assert seen[1][-1]["content"].endswith(f"\n[{config.MAX_TOOL_CALLS - 1} tool call(s) left.]")
    assert answer["steps"][0]["result"] == "Columns: COUNT(*)\n1 rows:\n150"  # adım kaydında budget notu yok


def test_third_repeat_of_the_same_call_hands_over(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL)] * (config.MAX_REPEATS + 1) + teacher_gives_up()
    answer = loop.answer_question("How many items?", "", db)
    assert answer["handoff_reason"] == "aynı çağrı 3 kez tekrarlandı"
    assert answer["steps"][config.MAX_REPEATS]["result"] == "Handoff: the same call was repeated too many times."


def test_teacher_repeating_the_agents_call_is_not_stuck(db, fake_model):
    replies, _ = fake_model
    replies += [execute_reply(COUNT_SQL)] * (config.MAX_REPEATS + 1)  # agent takıldı
    replies += [execute_reply(COUNT_SQL), submit_reply()]  # teacher
    answer = loop.answer_question("How many items?", "", db)
    assert answer["label"] == "ok" and answer["answered_by"] == "teacher" and answer["sql"] == COUNT_SQL
    assert answer["steps"][-2]["result"].startswith("Not run again")  # teacher önceki sonucu gördü, devam etti


def test_stuck_agent_samples_its_next_step(db, fake_model, monkeypatch):
    replies, _ = fake_model
    replies += [text_reply("hmm"), execute_reply(COUNT_SQL), execute_reply(COUNT_SQL), submit_reply()]
    temperatures = []
    fake = llm.chat

    def recording(messages, tools=None, seed=None, temperature=None, model=None):
        temperatures.append(temperature)
        return fake(messages, tools=tools, seed=seed, temperature=temperature, model=model)

    monkeypatch.setattr(llm, "chat", recording)
    loop.answer_question("How many items?", "", db)
    retry = config.RETRY_TEMPERATURE
    assert temperatures == [None, retry, None, retry]  # reddedilen ve tekrarlanan adımdan sonra örneklendi


def test_execute_sql_tool_call_runs_the_query(db, fake_model):
    replies, seen = fake_model
    replies += [call_reply("execute_sql", {"sql": COUNT_SQL}), submit_reply()]
    answer = loop.answer_question("How many items?", "", db)
    assert seen[1][-1]["role"] == "tool" and observation(seen[1][-1]) == "Columns: COUNT(*)\n1 rows:\n150"
    assert answer["label"] == "ok" and answer["sql"] == COUNT_SQL
