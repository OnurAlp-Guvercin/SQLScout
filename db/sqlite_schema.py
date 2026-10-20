"""SQLite veritabanının yapısını okur: tablolar, sütunlar, foreign key'ler ve column profile'ları.
Akışta adım 1 (başlangıç bağlamı) bunu kullanır. Veritabanı salt okunur açılır."""

import config
from db.sqlite_db import connect, quote


def schema(db_path):
    """Her tablo için: ad, sütunlar (ad, tip, primary key mi) ve foreign key'ler."""
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


def show_name(name):
    """Adı SQL'de yazılacağı gibi gösterir: düz adlar olduğu gibi, boşluklu ya da özel karakterli adlar backtick içinde."""
    return name if name.isidentifier() else f"`{name}`"


def primary_key_of(conn, table):
    # Foreign key hedef sütun yazmadan tanımlanmışsa hedef tablonun primary key'ini gösterir.
    for info in conn.execute(f"PRAGMA table_info({quote(table)})"):
        if info[5] == 1:
            return info[1]
    return None


def profile(db_path, table):
    """Tablonun her sütunu için column profile."""
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
    col = quote(column)
    non_null, distinct = conn.execute(f"SELECT COUNT({col}), COUNT(DISTINCT {col}) FROM {table}").fetchone()
    all_values_shown = distinct <= config.PROFILE_ALL_VALUES_MAX
    limit = distinct if all_values_shown else config.PROFILE_TOP_VALUES
    top_values = conn.execute(
        f"SELECT {col}, COUNT(*) AS n FROM {table} WHERE {col} IS NOT NULL "
        f"GROUP BY {col} ORDER BY n DESC, {col} LIMIT ?", (limit,)).fetchall()
    low, high = conn.execute(
        f"SELECT MIN({col}), MAX({col}) FROM {table} WHERE typeof({col}) IN ('integer', 'real')").fetchone()
    return {
        "name": column,
        "type": column_type,
        "null_ratio": (total - non_null) / total if total else None,
        "distinct": distinct,
        "all_values_shown": all_values_shown,
        "top_values": [[value, count] for value, count in top_values],
        "min": low,
        "max": high,
    }
