"""harness/prepare.py testleri (aşama 3): başlangıç bağlamı."""

from pathlib import Path

import pytest

import config
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
