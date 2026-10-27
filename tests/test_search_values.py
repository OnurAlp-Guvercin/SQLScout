"""harness/tools/search_values.py testleri (adım 3)."""

import sqlite3

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
    assert search_values.find_values(db, "ab") == []


def test_column_name_search_points_to_the_column(db):
    context = Context("q", "", db)
    assert search_values.run("BackupItems", context) == (
        "No values similar to 'BackupItems' were found. search_values finds values stored in the database, not "
        "column names. Columns with a similar name: stores.backup_item.")
    assert search_values.run("Paris", context) == "No values similar to 'Paris' were found."


def test_value_with_quote_is_written_as_sql():
    assert search_values.sql_text("O'Brien") == "'O''Brien'"


def test_short_value_is_found_exactly(db):
    """Trigram index 3 harften kısa metni arayamaz; kısa metin büyük/küçük harf farkı gözetmeden tam eşleşmeyle aranır."""
    assert search_values.find_values(db, "OK") == [("items", "status", "ok")]


def test_words_are_searched_separately_when_the_whole_text_is_not_found(db):
    context = Context("q", "", db)
    text = search_values.run("Boston Chicago", context)
    assert text == ("No values similar to 'Boston Chicago' were found. Each word separately:\n"
                    "Values similar to 'Boston':\n- items.city = 'Boston'\n"
                    "Values similar to 'Chicago':\n- items.city = 'Chicago'")


def test_exact_spelling_comes_first(tmp_path):
    path = tmp_path / "f1.sqlite"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE drivers (driverRef TEXT, surname TEXT)")
    conn.execute("INSERT INTO drivers VALUES ('hamilton', 'Hamilton')")
    conn.commit()
    conn.close()
    assert search_values.find_values(str(path), "Hamilton")[0] == ("drivers", "surname", "Hamilton")


def test_similar_columns_put_the_closest_name_first(tmp_path):
    path = tmp_path / "f1.sqlite"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE races (time TEXT, date TEXT)")
    conn.execute("CREATE TABLE laps (time TEXT, lap_time TEXT)")
    conn.execute("CREATE TABLE results (time TEXT, fastestLap INTEGER, fastestLapTime TEXT)")
    conn.close()
    assert search_values.similar_columns(str(path), "fastestLapTimes")[0] == "results.fastestLapTime"
