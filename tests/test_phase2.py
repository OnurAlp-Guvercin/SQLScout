"""Mini-Interact verisi testleri: görevlerin soruya dönüşmesi, doğru SQL dosyası ve sütun anlamları."""

import json
import shutil

import config
import mini_interact
from db import sqlite_schema

AMBIGUITY = {"user_query_ambiguity": {"critical_ambiguity": [{"term": "good items", "sql_snippet": "price > 100"}]},
             "knowledge_ambiguity": [{"term": "Premium", "sql_snippet": "price > 200", "deleted_knowledge": 1}]}


def mini_dataset(db, tmp_path, monkeypatch, with_gold):
    """Tek görevli küçük bir Mini-Interact klasörü: görev, bilgi tabanı, sütun anlamları, isteğe bağlı gold."""
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
    assert question["db_path"].endswith("shop/shop.sqlite")


def test_gold_is_read_when_present(db, tmp_path, monkeypatch):
    mini_dataset(db, tmp_path, monkeypatch, with_gold=True)
    assert mini_interact.load_questions()[0]["SQL"] == "SELECT 1"


def test_column_meanings_include_json_fields(db, tmp_path, monkeypatch):
    folder = mini_dataset(db, tmp_path, monkeypatch, with_gold=False)
    columns = sqlite_schema.descriptions(str(folder / "shop" / "shop.sqlite"))["items"]
    assert columns["price"] == "Price in dollars."
    assert columns["status"] == "JSON column. Fields: code: status code"
