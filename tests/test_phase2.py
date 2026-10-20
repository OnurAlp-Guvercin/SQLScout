"""Phase 2 testleri: Mini-Interact verisi (aşama 30), onun user simulator'ü (aşama 31), cost simulation (aşama 32)."""

import json
import shutil

import config
import mini_interact
from agent import loop
from agent.context import Context
from harness import ask_user, cost, descriptions, precheck
from tests.fakes import ONE_ROW, call_reply, execute_reply, submit_reply, text_reply

AMBIGUITY = {"user_query_ambiguity": {"critical_ambiguity": [{"term": "good items", "sql_snippet": "price > 100"}]},
             "knowledge_ambiguity": [{"term": "Premium", "sql_snippet": "price > 200", "deleted_knowledge": 1}]}


def mini_dataset(db, tmp_path, monkeypatch, with_gold):
    """Tek görevli küçük bir Mini-Interact klasörü: görev, bilgi tabanı, sütun anlamları, şema, isteğe bağlı gold."""
    folder = tmp_path / "mini"
    (folder / "shop").mkdir(parents=True)
    shutil.copy(db, folder / "shop" / "shop.sqlite")
    task = {"instance_id": "shop_1", "selected_database": "shop", "amb_user_query": "How many good items?"}
    task.update(AMBIGUITY)
    (folder / "mini_interact.jsonl").write_text(json.dumps(task) + "\n")
    knowledge = [{"id": 0, "knowledge": "Cheap", "definition": "price < 10"},
                 {"id": 1, "knowledge": "Premium", "definition": "price > 200"}]
    (folder / "shop" / "shop_kb.jsonl").write_text("\n".join(json.dumps(item) for item in knowledge))
    meanings = {"shop|items|price": "Price in dollars.",
                "shop|items|status": {"column_meaning": "JSON column.", "fields_meaning": {"code": "status code"}}}
    (folder / "shop" / "shop_column_meaning_base.json").write_text(json.dumps(meanings))
    (folder / "shop" / "shop_schema.txt").write_text("CREATE TABLE items (...)")
    monkeypatch.setattr(config, "MINI_INTERACT_DIR", folder)
    monkeypatch.setattr(config, "MINI_INTERACT_GOLD", folder / "gold.jsonl")
    if with_gold:
        (folder / "gold.jsonl").write_text(json.dumps({"instance_id": "shop_1", "sol_sql": ["SELECT 1"]}))
    return folder


def test_tasks_become_questions_without_hidden_knowledge(db, tmp_path, monkeypatch):
    mini_dataset(db, tmp_path, monkeypatch, with_gold=False)
    question = mini_interact.load_questions()[0]
    assert question["question"] == "How many good items?" and question["SQL"] is None
    assert question["evidence"] == "Knowledge base of this database:\n- Cheap: price < 10"  # Premium gizli
    assert question["ambiguity"] == AMBIGUITY and question["db_path"].endswith("shop/shop.sqlite")


def test_gold_is_read_when_present(db, tmp_path, monkeypatch):
    mini_dataset(db, tmp_path, monkeypatch, with_gold=True)
    assert mini_interact.load_questions()[0]["SQL"] == "SELECT 1"


def test_column_meanings_include_json_fields(db, tmp_path, monkeypatch):
    folder = mini_dataset(db, tmp_path, monkeypatch, with_gold=False)
    columns = descriptions.load(str(folder / "shop" / "shop.sqlite"))["items"]
    assert columns["price"] == "Price in dollars."
    assert columns["status"] == "JSON column. Fields: code: status code"


def test_mini_interact_simulator_has_two_steps_and_agent_never_sees_notes(db, tmp_path, monkeypatch, fake_model):
    folder = mini_dataset(db, tmp_path, monkeypatch, with_gold=False)
    question = mini_interact.load_questions()[0]
    replies, seen = fake_model
    replies += [call_reply("ask_user", {"question": "What are good items?"}),
                text_reply('labeled("good items")</s>'), text_reply("Items that cost more than 100.</s>"),
                submit_reply("SELECT COUNT(*) FROM items")]
    answer = loop.answer_question(question["question"], question["evidence"], question["db_path"],
                                  ambiguity=question["ambiguity"])
    encoder, decoder = seen[1][0]["content"], seen[2][0]["content"]
    assert '"sql_snippet": "price > 100"' in encoder and "What are good items?" in encoder
    assert '# Action Used: \nlabeled("good items")' in decoder and "CREATE TABLE items (...)" in decoder
    assert answer["clarifications"] == [{"question": "What are good items?", "answer": "Items that cost more than 100."}]
    for message in seen[0] + seen[3]:  # agent'ın gördüğü bütün mesajlar
        assert "price > 100" not in str(message["content"]) and "price > 200" not in str(message["content"])


def test_bird_coin_budget(db, fake_model, monkeypatch):
    monkeypatch.setattr(config, "SIMULATE_COST", True)
    assert cost.start_coins(AMBIGUITY) == 6 + 2 * 2 + 6
    assert cost.start_coins(None) == 12  # BIRD sorusu: belirsizlik notu yok
    replies, _ = fake_model
    replies += [execute_reply(f"SELECT {n}", ONE_ROW) for n in range(12)]  # 12 × 1 coin
    answer = loop.answer_question("One?", "", db)
    assert answer["tool_calls"] == 10  # tool-call budget'ı da geçerli: hangisi önce biterse
    assert answer["coins_left"] == 2


def test_coins_run_out_before_tool_calls(db, fake_model, monkeypatch):
    monkeypatch.setattr(config, "SIMULATE_COST", True)
    monkeypatch.setattr(config, "USER_PATIENCE", 0)  # 6 coin
    replies, _ = fake_model
    replies += [submit_reply("SELECT id FROM items WHERE price < 0")] * 2  # 3 + 3 coin, final check geçmez
    answer = loop.answer_question("Which items are free?", "", db)
    assert answer["tool_calls"] == 2 and answer["coins_left"] == 0 and answer["label"] == "low_confidence"


def test_budget_low_and_query_cost_follow_bird_coins(db, monkeypatch):
    monkeypatch.setattr(config, "SIMULATE_COST", True)
    context = Context("q", "", db, coins=12, coins_left=2, budget_end=10, calls=1)
    assert cost.budget_low(context)  # 2 < 0.25 × 12
    sql = "SELECT id FROM items WHERE price > 1"  # price'ta index yok: 150 satır taranır
    assert cost.query_cost(db, sql) == 150 * config.SIMULATED_ROW_COST
    monkeypatch.setattr(config, "EXPENSIVE_ROWS", 100_000)
    assert precheck.is_expensive(sql, db)
    monkeypatch.setattr(config, "SIMULATE_COST", False)
    assert cost.query_cost(db, sql) == 150 and not precheck.is_expensive(sql, db)
