"""SQLite veritabanı katmanı: execute, explain, estimate_cost. Şemayı ve column profile'ları sqlite_schema.py okur.
Akışta adım 5 (pre-check) ve adım 7 (gerçek çalıştırma). Veritabanı hep salt okunur açılır."""

import functools
import hashlib
import sqlite3
import time
from pathlib import Path

import config


def connect(db_path):
    uri = Path(db_path).resolve().as_uri() + "?mode=ro"
    return sqlite3.connect(uri, uri=True)


def quote(name):
    return '"' + name.replace('"', '""') + '"'


def is_read_only(sql):
    return sql.lstrip().upper().startswith(("SELECT", "WITH"))


def error_result(message):
    return {"ok": False, "error": message, "columns": [], "rows": [], "row_count": 0, "result_key": None}


def execute(db_path, sql):
    """Sorguyu çalıştırır. Agent'a en fazla MAX_RESULT_ROWS satır döner; result_key bütün satırlardan hesaplanır."""
    if not is_read_only(sql):
        return error_result("Yalnızca SELECT ya da WITH ile başlayan sorgular çalıştırılır.")

    conn = connect(db_path)
    deadline = time.monotonic() + config.QUERY_TIMEOUT_SECONDS
    conn.set_progress_handler(lambda: time.monotonic() > deadline, 10000)
    try:
        cursor = conn.execute(sql)
        columns = [description[0] for description in cursor.description]
        rows = []
        all_rows = set()
        row_count = 0
        for row in cursor:
            row_count += 1
            if len(rows) < config.MAX_RESULT_ROWS:
                rows.append(row)
            all_rows.add(normalize(row))
    except sqlite3.Error as error:
        if time.monotonic() > deadline:
            return error_result(f"Zaman aşımı: sorgu {config.QUERY_TIMEOUT_SECONDS} saniyede bitmedi.")
        return error_result(str(error))
    finally:
        conn.close()

    return {"ok": True, "error": None, "columns": columns, "rows": rows,
            "row_count": row_count, "result_key": result_key(all_rows)}


def normalize(row):
    # BIRD satırları Python'da set ile karşılaştırır ve orada 1 == 1.0 sayılır.
    # Hash'te de aynı çıksınlar diye tam sayı değerli float'lar int'e çevrilir.
    values = []
    for value in row:
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        values.append(value)
    return tuple(values)


def result_key(rows):
    """Satır kümesinin hash'i: satır sırası ve tekrarlar önemsiz, sütun sırası önemli (BIRD kuralı)."""
    ordered = sorted(rows, key=repr)
    return hashlib.sha256(repr(ordered).encode()).hexdigest()[:16]


def explain(db_path, sql):
    """Sorguyu çalıştırmadan planını verir; sözdizimi ya da eksik tablo/sütun varsa hata döner."""
    conn = connect(db_path)
    try:
        plan = [row[3] for row in conn.execute("EXPLAIN QUERY PLAN " + sql)]
    except sqlite3.Error as error:
        return {"ok": False, "error": str(error), "plan": []}
    finally:
        conn.close()
    return {"ok": True, "error": None, "plan": plan}


def estimate_cost(db_path, sql):
    """Tahmini taranacak satır sayısı: tam taranan her tablonun satır sayısı toplanır. SQL hatalıysa None."""
    conn = connect(db_path)
    try:
        table_of_rootpage = dict(conn.execute("SELECT rootpage, tbl_name FROM sqlite_master WHERE rootpage > 0"))
        program = conn.execute("EXPLAIN " + sql).fetchall()
    except sqlite3.Error:
        return None
    finally:
        conn.close()

    # EXPLAIN QUERY PLAN tablo yerine takma adı (T1) yazar; bu yüzden bytecode okunur.
    # OpenRead bir cursor'u bir tabloya ya da onun indeksine bağlar. O cursor'da Rewind ya da Last
    # varsa tablo baştan sona taranıyordur. İndeksli aramalarda bunlar yoktur; küçük oldukları için sayılmazlar.
    table_of_cursor = {}
    total = 0
    for row in program:
        opcode, cursor, rootpage = row[1], row[2], row[3]
        if opcode == "OpenRead" and rootpage in table_of_rootpage:
            table_of_cursor[cursor] = table_of_rootpage[rootpage]
        elif opcode in ("Rewind", "Last") and cursor in table_of_cursor:
            total += table_row_count(db_path, table_of_cursor[cursor])
    return total


@functools.lru_cache(maxsize=None)
def table_row_count(db_path, table):
    conn = connect(db_path)
    try:
        return conn.execute(f"SELECT COUNT(*) FROM {quote(table)}").fetchone()[0]
    finally:
        conn.close()
