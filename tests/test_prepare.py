"""harness/prepare.py testleri (aşama 3): başlangıç bağlamı ve kısaltma."""

from pathlib import Path

import pytest

import config
from agent import llm
from harness import prepare

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
    assert "- id INTEGER, primary key" in context
    assert "- city TEXT; Shop city; all values: 'Boston' (50), 'Chicago' (50), 'Los Angeles' (50)" in context
    assert "value description: returned: the item came back" in context
    assert "10.0% NULL" in context
    assert "range: 0.0 to 223.5" in context
    assert "• name on the door" in context
    assert "- stores.item_id = items.id" in context
    assert f"Evidence: {EVIDENCE}" in context
    assert context.endswith(f"Question: {QUESTION}")


def test_profiles_are_saved_once(bird_db):
    prepare.build_context(QUESTION, EVIDENCE, bird_db)
    assert (config.PREPARED_DIR / "shop" / "profiles.json").exists()


def test_long_context_shortens_least_matching_table(bird_db, monkeypatch):
    full = prepare.build_context(QUESTION, EVIDENCE, bird_db)
    assert "details omitted" not in full

    monkeypatch.setattr(config, "CONTEXT_MAX_TOKENS", llm.count_tokens(full) - 1)
    shortened = prepare.build_context(QUESTION, EVIDENCE, bird_db)
    assert "Table stores (3 rows), details omitted: id INTEGER, item_id INTEGER, backup_item INTEGER, name TEXT" in shortened
    assert "- city TEXT; Shop city" in shortened
    assert llm.count_tokens(shortened) <= config.CONTEXT_MAX_TOKENS
