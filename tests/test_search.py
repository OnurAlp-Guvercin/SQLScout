"""harness/search.py testleri: search_values (aşama 12), search_schema (aşama 13), adım 1'de değer eşleşmesi (aşama 14)."""

import config
from db import sqlite_schema
from harness import prepare, search, value_matches


def test_misspelled_value_is_found(db):
    assert search.find_values(db, "Los Angles", 5, True, 0.8)[0] == ("items", "city", "Los Angeles")
    assert (config.PREPARED_DIR / "shop" / "values.sqlite").exists()  # index bir kez kurulup saklandı


def test_part_of_a_value_is_found_only_when_allowed(db):
    assert search.find_values(db, "angeles", 5, True, 0.8) == [("items", "city", "Los Angeles")]
    assert search.find_values(db, "angeles", 5, False, 0.8) == []


def test_nothing_found(db):
    assert search.show_values("Paris", search.find_values(db, "Paris", 5, True, 0.8)) == \
        "No values similar to 'Paris' were found."
    assert search.find_values(db, "ab", 5, True, 0.8) == []  # trigram için çok kısa


def test_value_with_quote_is_written_as_sql():
    assert search.sql_text("O'Brien") == "'O''Brien'"


def test_schema_search_finds_column(db):
    matches = search.find_columns(db, "item price")
    assert matches[0][:2] == ("items", "price")
    text = search.show_columns("item price", matches)
    assert text.startswith("Columns matching 'item price':\n- items.price REAL")
    assert search.show_columns("phone", search.find_columns(db, "phone")) == \
        "No tables or columns matching 'phone' were found."


def test_question_words_are_matched_in_step_1(db):
    tables = sqlite_schema.schema(db)
    lines = value_matches.find("How many items are in Los Angles?", db, tables)
    assert lines == ["- \"Los Angles\": items.city = 'Los Angeles'"]
    # tek kelimede eşik 0.9: "Bostn" ~0.91 geçer, "Bost" 0.8 geçmez; "Los" (3 harf) hiç aranmaz
    assert value_matches.find("Items in Bostn?", db, tables) == ["- \"Bostn\": items.city = 'Boston'"]
    assert value_matches.find("Items in Bost or Los?", db, tables) == []
    context = prepare.build_context("How many items are in Los Angles?", "", db)
    assert "Database values similar to words in the question:\n- \"Los Angles\"" in context
