"""SQLite veritabanının yapısını okur: tablolar, sütunlar, foreign key'ler, column profile'ları ve sütun açıklamaları.
Akışta adım 1 (başlangıç bağlamı) bunu kullanır. Veritabanı salt okunur açılır."""

import csv
import io
from pathlib import Path

import config
from db.sqlite_db import connect, quote


def schema(db_path):
    """Veritabanının iskeleti; her tablo için: ad, sütunlar (ad, tip, primary key mi) ve foreign key'ler.
    Ör. [{"name": "gender", "columns": [{"name": "id", "type": "INTEGER", "primary_key": True}, ...], "foreign_keys": []}]"""
    conn = connect(db_path)
    try:
        names = [row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'")]
        tables = []
        for name in names:
            columns = []
            for info in conn.execute(f"PRAGMA table_info({quote(name)})"):
                columns.append({"name": info[1], "type": info[2], "primary_key": info[5] > 0})
            foreign_keys = []
            for fk in conn.execute(f"PRAGMA foreign_key_list({quote(name)})").fetchall():
                ref_column = fk[4] or primary_key_of(conn, fk[2])
                foreign_key = {"column": fk[3], "ref_table": fk[2], "ref_column": ref_column}
                if foreign_key not in foreign_keys:  # bazı veritabanlarında aynı bağlantı iki kez tanımlı
                    foreign_keys.append(foreign_key)
            tables.append({"name": name, "columns": columns, "foreign_keys": foreign_keys})
    finally:
        conn.close()
    return tables


# Tırnaksız yazılınca tablo adı ya da alias olamayan SQL kelimeleri (ör. ORDER BY, veritabanında order tablosu olsa da).
SQL_WORDS = {"select", "from", "where", "join", "inner", "left", "right", "full", "outer", "cross", "natural", "on",
             "using", "group", "order", "by", "having", "limit", "offset", "union", "except", "intersect", "and", "or",
             "not", "in", "is", "as", "case", "when", "then", "else", "end", "distinct", "between", "like", "null",
             "window", "values", "table", "index", "key", "check", "default", "references", "primary"}


def show_name(name):
    """Adı SQL'de yazılacağı gibi gösterir: düz adlar olduğu gibi; boşluklu, özel karakterli ya da SQL kelimesi olan
    adlar (ör. financial'daki order tablosu) backtick içinde."""
    if name.isidentifier() and name.lower() not in SQL_WORDS:
        return name
    return f"`{name}`"


def primary_key_of(conn, table):
    """Tablonun primary key sütununun adı, yoksa None. Hedef sütunu yazılmamış foreign key'ler buna bağlanır."""
    for info in conn.execute(f"PRAGMA table_info({quote(table)})"):
        if info[5] == 1:
            return info[1]
    return None


def profile(db_path, table):
    """Tablonun satır sayısı ve her sütununun özeti (profile_column). Return: {"table", "row_count", "columns"}.
    Adım 1 bunu her veritabanı için bir kez hesaplatır ve data/prepared/<db_id>/profiles.json'a yazar."""
    conn = connect(db_path)
    try:
        name = quote(table)
        total = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        columns = []
        for column_info in conn.execute(f"PRAGMA table_info({name})").fetchall():
            column, column_type = column_info[1], column_info[2]
            columns.append(profile_column(conn, name, column, column_type, total))
    finally:
        conn.close()
    return {"table": table, "row_count": total, "columns": columns}


def profile_column(conn, table, column, column_type, total):
    """Tek bir sütunun özeti: NULL oranı, farklı değer sayısı, en sık değerler ([değer, kaç kez]), sayısalsa min ve max.
    En sık PROFILE_TOP_VALUES değer alınır; farklı değer sayısı bundan azsa hepsi alınmış olur (all_values_shown).
    Ör. {"name": "gender", "distinct": 3, "all_values_shown": True, "top_values": [["Female", 1], ...], "min": None}"""
    col = quote(column)
    non_null, distinct = conn.execute(f"SELECT COUNT({col}), COUNT(DISTINCT {col}) FROM {table}").fetchone()
    top_values = conn.execute(
        f"SELECT {col}, COUNT(*) AS n FROM {table} WHERE {col} IS NOT NULL "
        f"GROUP BY {col} ORDER BY n DESC, {col} LIMIT ?", (config.PROFILE_TOP_VALUES,)).fetchall()
    low, high = conn.execute(
        f"SELECT MIN({col}), MAX({col}) FROM {table} WHERE typeof({col}) IN ('integer', 'real')").fetchone()
    return {
        "name": column,
        "type": column_type,
        "null_ratio": (total - non_null) / total if total else None,
        "distinct": distinct,
        "all_values_shown": distinct <= config.PROFILE_TOP_VALUES,
        "top_values": [[value, count] for value, count in top_values],
        "min": low,
        "max": high,
    }


def descriptions(db_path):
    """Sütun açıklamaları: BIRD'de veritabanının yanındaki database_description/<tablo>.csv dosyaları.
    Return: {tablo: {sütun: açıklama}}, adlar küçük harfle. Açıklama dosyası yoksa boş."""
    folder = Path(db_path).parent / "database_description"
    found = {}
    for csv_path in sorted(folder.glob("*.csv")):
        columns = {}
        for row in csv.DictReader(io.StringIO(read_text(csv_path))):
            name = clean(row.get("original_column_name")).lower()
            if name:
                columns[name] = describe_row(row)
        found[csv_path.stem.lower()] = columns
    return found


def read_text(path):
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252")  # BIRD'deki birkaç CSV Windows kodlamasıyla kaydedilmiş


def describe_row(row):
    original = clean(row.get("original_column_name"))
    full_name = clean(row.get("column_name"))
    meaning = clean(row.get("column_description"))
    value_description = clean(row.get("value_description"))
    parts = []
    if full_name and full_name.lower() != original.lower():
        parts.append(full_name)
    if meaning and meaning.lower() not in (original.lower(), full_name.lower()):
        parts.append(meaning)
    if value_description:
        parts.append(f"value description: {value_description}")
    return ". ".join(parts)


def clean(text):
    return " ".join((text or "").split())
