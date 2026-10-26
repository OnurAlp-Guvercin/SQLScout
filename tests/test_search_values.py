"""harness/tools/search_values.py testleri (adım 3). ask_user test_help.py'de."""

import config
from agent.context import Context
from harness.tools import search_values


def test_misspelled_value_is_found(db):
    assert search_values.find_values(db, "Los Angles")[0] == ("items", "city", "Los Angeles")
    assert (config.PREPARED_DIR / "shop" / "values.sqlite").exists()  # index bir kez kurulup saklandı


def test_part_of_a_value_is_found(db):
    assert search_values.find_values(db, "angeles") == [("items", "city", "Los Angeles")]


def test_nothing_found(db):
    assert search_values.show_values("Paris", search_values.find_values(db, "Paris")) == \
        "No values similar to 'Paris' were found."
    assert search_values.find_values(db, "ab") == []  # trigram için çok kısa


def test_column_name_search_points_to_the_column(db):
    context = Context("q", "", db)
    assert search_values.run("BackupItems", context) == (
        "No values similar to 'BackupItems' were found. search_values finds values stored in the database, not "
        "column names. Columns with a similar name: stores.backup_item.")
    assert search_values.run("Paris", context) == "No values similar to 'Paris' were found."
    assert context.search_notes == []


def test_value_with_quote_is_written_as_sql():
    assert search_values.sql_text("O'Brien") == "'O''Brien'"
