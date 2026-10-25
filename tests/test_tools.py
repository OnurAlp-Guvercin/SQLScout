"""harness/tools.py testleri: search_values (adım 3). ask_user test_help.py'de."""

import config
from harness import tools


def test_misspelled_value_is_found(db):
    assert tools.find_values(db, "Los Angles")[0] == ("items", "city", "Los Angeles")
    assert (config.PREPARED_DIR / "shop" / "values.sqlite").exists()  # index bir kez kurulup saklandı


def test_part_of_a_value_is_found(db):
    assert tools.find_values(db, "angeles") == [("items", "city", "Los Angeles")]


def test_nothing_found(db):
    assert tools.show_values("Paris", tools.find_values(db, "Paris")) == \
        "No values similar to 'Paris' were found."
    assert tools.find_values(db, "ab") == []  # trigram için çok kısa


def test_value_with_quote_is_written_as_sql():
    assert tools.sql_text("O'Brien") == "'O''Brien'"
