"""db/sqlite_schema.py testleri (aşama 1 ve 3): şema, foreign key'ler ve column profile'ları."""

import pytest

import config
from db import sqlite_schema


def test_schema_lists_tables_columns_and_primary_keys(db):
    tables = {table["name"]: table for table in sqlite_schema.schema(db)}
    assert list(tables) == ["items", "stores"]
    items_columns = tables["items"]["columns"]
    assert [column["name"] for column in items_columns] == ["id", "city", "price", "status"]
    assert items_columns[0]["primary_key"]
    assert not items_columns[1]["primary_key"]


def test_schema_foreign_keys(db):
    stores = sqlite_schema.schema(db)[1]
    # item_id'nin bağlantısı iki kez tanımlı; bir kez listelenir.
    assert stores["foreign_keys"].count({"column": "item_id", "ref_table": "items", "ref_column": "id"}) == 1
    # Hedef sütun yazılmadan tanımlanmış foreign key, hedef tablonun primary key'ine bağlanır.
    assert {"column": "backup_item", "ref_table": "items", "ref_column": "id"} in stores["foreign_keys"]


def test_profile(db):
    result = sqlite_schema.profile(db, "items")
    assert result["row_count"] == 150
    columns = {column["name"]: column for column in result["columns"]}

    status = columns["status"]
    assert status["null_ratio"] == pytest.approx(0.1)
    assert status["distinct"] == 2
    assert status["all_values_shown"]
    assert status["top_values"] == [["returned", 75], ["ok", 60]]
    assert status["min"] is None

    identifier = columns["id"]
    assert identifier["distinct"] == 150
    assert not identifier["all_values_shown"]
    assert len(identifier["top_values"]) == config.PROFILE_TOP_VALUES

    assert columns["price"]["min"] == 0
    assert columns["price"]["max"] == 149 * 1.5


def test_names_that_are_sql_words_are_quoted():
    assert sqlite_schema.show_name("order") == "`order`"  # financial veritabanındaki tablo
    assert sqlite_schema.show_name("Free Meal Count") == "`Free Meal Count`"
    assert sqlite_schema.show_name("orders") == "orders"
