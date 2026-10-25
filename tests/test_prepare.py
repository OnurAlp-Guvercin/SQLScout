"""harness/prepare.py testleri (aşama 3): başlangıç bağlamı ve sınır aşılınca tablo seçimi."""

from pathlib import Path

import pytest

import config
from agent import llm
from harness import prepare
from tests.fakes import text_reply

QUESTION = "Which city has the most returned items?"
EVIDENCE = "returned refers to status = 'returned'"


@pytest.fixture
def bird_db(db, tmp_path, monkeypatch):
    """BIRD gibi: veritabanının yanında database_description CSV'leri. Biri Windows kodlamasında."""
    monkeypatch.setattr(config, "PREPARED_DIR", tmp_path / "prepared")
    folder = Path(db).parent / "database_description"
    folder.mkdir()
    header = "original_column_name,column_name,column_description,data_format,value_description\n"
    items = header + "city,city,Shop city,text,\nstatus,,order status,text,returned: the item came back\n"
    (folder / "items.csv").write_text(items, encoding="utf-8-sig")
    stores = header + "name,store name,• name on the door,text,\n"
    (folder / "stores.csv").write_bytes(stores.encode("cp1252"))
    return db


def test_context_has_schema_descriptions_profiles_and_question(bird_db):
    context = prepare.build_context(QUESTION, EVIDENCE, bird_db)
    assert "Table items (150 rows)" in context
    assert "- id INTEGER, primary key; range: 0 to 149\n" in context  # sayısal: yalnızca aralık
    assert "- city TEXT; Shop city; all values: 'Boston', 'Chicago', 'Los Angeles'\n" in context
    assert "value description: returned: the item came back; all values: 'returned', 'ok'\n" in context
    assert "- price REAL; range: 0.0 to 223.5\n" in context
    assert "- name TEXT; store name. • name on the door; all values: 'Store 0', 'Store 1', 'Store 2'\n" in context
    assert "• name on the door" in context
    assert "- stores.item_id = items.id" in context
    assert f"Evidence: {EVIDENCE}" in context
    assert context.endswith(f"Question: {QUESTION}")


def test_many_values_show_most_common_without_counts(bird_db, monkeypatch):
    monkeypatch.setattr(config, "PROFILE_TOP_VALUES", 2)
    context = prepare.build_context(QUESTION, EVIDENCE, bird_db)
    assert "- city TEXT; Shop city; e.g. 'Boston', 'Chicago'\n" in context
    assert "- name TEXT; store name. • name on the door; e.g. 'Store 0', 'Store 1'\n" in context  # her değer bir kez
    assert "- id INTEGER, primary key; range: 0 to 149\n" in context


def test_profiles_are_saved_once(bird_db):
    prepare.build_context(QUESTION, EVIDENCE, bird_db)
    assert (config.PREPARED_DIR / "shop" / "profiles.json").exists()


def test_long_context_keeps_only_tables_the_model_selects(bird_db, monkeypatch):
    full = prepare.build_context(QUESTION, EVIDENCE, bird_db)
    assert "details omitted" not in full

    monkeypatch.setattr(config, "CONTEXT_MAX_TOKENS", llm.count_tokens(full) - 1)
    monkeypatch.setattr(llm, "chat", lambda messages, temperature=None: text_reply('["items"]'))
    shortened = prepare.build_context(QUESTION, EVIDENCE, bird_db)
    assert "Table stores (3 rows), details omitted: id INTEGER, item_id INTEGER, backup_item INTEGER, name TEXT" in shortened
    assert "- city TEXT; Shop city" in shortened


# Bağlam sınırı aşılınca LLM'in soruya gereken tabloları seçmesi (schema linking).
BLOCKS = {"orders": "Table orders\n- id INTEGER", "customers": "Table customers\n- id INTEGER",
          "colour": "Table colour\n- colour TEXT"}


def fake_chat(monkeypatch, answers):
    """Model sırayla answers'taki metinleri return eder; modele giden şema parçaları kaydedilir."""
    seen = []

    def chat(messages, temperature=None):
        seen.append(messages[1]["content"])
        return text_reply(answers.pop(0))

    monkeypatch.setattr(llm, "chat", chat)
    return seen


def test_schema_is_split_into_chunks_and_selections_are_joined(monkeypatch):
    two_tables = llm.count_tokens(BLOCKS["orders"]) + llm.count_tokens(BLOCKS["customers"])
    monkeypatch.setattr(config, "CONTEXT_MAX_TOKENS", two_tables)  # parçalar: orders + customers, colour
    seen = fake_chat(monkeypatch, ['Tables: ["orders", "Customers"]', "[]"])
    assert prepare.select_tables("How many orders per customer?", "", BLOCKS) == {"orders", "customers"}
    assert len(seen) == 2 and seen[1].startswith("Table colour")
    assert "Table customers" in seen[0] and seen[0].endswith("Question: How many orders per customer?")


def test_selection_that_still_does_not_fit_is_selected_again(monkeypatch):
    monkeypatch.setattr(config, "CONTEXT_MAX_TOKENS", llm.count_tokens(BLOCKS["orders"]) + 1)
    fake_chat(monkeypatch, ['["orders"]', '["customers"]', "[]", '["orders"]', "[]"])
    assert prepare.select_tables("q", "", BLOCKS) == {"orders"}


def test_broken_answer_selects_nothing(monkeypatch):
    fake_chat(monkeypatch, ['{"tables": "orders"}'])
    assert prepare.select_tables("q", "", BLOCKS) == set()
    fake_chat(monkeypatch, ["[orders, customers"])
    assert prepare.select_tables("q", "", BLOCKS) == set()
    fake_chat(monkeypatch, ['[["orders"], "missing", "colour"]'])
    assert prepare.select_tables("q", "", BLOCKS) == {"colour"}
