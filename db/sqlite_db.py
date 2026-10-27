"""SQLite veritabanı katmanı: execute, explain. Şemayı ve column profile'ları sqlite_schema.py okur.
Akışta adım 5 (pre-check) ve adım 6 (gerçek çalıştırma). Veritabanı hep salt okunur açılır."""

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


def error_result(message, timed_out=False):
    return {"ok": False, "error": message, "timed_out": timed_out, "columns": [], "rows": [], "row_count": 0,
            "result_key": None}


def execute(db_path, sql, timeout_seconds):
    """Sorguyu en fazla timeout_seconds saniye çalıştırır (keşifte EXPLORE_TIMEOUT_SECONDS, ana sorguda
    ANSWER_TIMEOUT_SECONDS). Agent'a en fazla MAX_RESULT_ROWS satır return eder; result_key bütün satırlardan
    hesaplanır. Zaman aşımında timed_out True olur. MAX_TOTAL_ROWS'tan çok satır (ör. JOIN koşulu unutulmuş bir sorgu)
    hata sayılır: bütün satırlar result_key için bellekte tutulur."""
    if not is_read_only(sql):
        return error_result("Only queries that start with SELECT or WITH can be run.")

    conn = connect(db_path)
    deadline = time.monotonic() + timeout_seconds
    conn.set_progress_handler(lambda: time.monotonic() > deadline, 10000)
    try:
        cursor = conn.execute(sql)
        columns = [description[0] for description in cursor.description]
        rows = []
        all_rows = set()
        row_count = 0
        for row in cursor:
            row_count += 1
            if row_count > config.MAX_TOTAL_ROWS:
                return error_result(f"Too many rows: the result has more than {config.MAX_TOTAL_ROWS} rows. "
                                    "Add a join condition or a filter.")
            if len(rows) < config.MAX_RESULT_ROWS:
                rows.append(row)
            all_rows.add(normalize(row))
    except sqlite3.Error as error:
        if time.monotonic() > deadline:
            return error_result(f"Timeout: the query did not finish in {timeout_seconds} seconds.", timed_out=True)
        return error_result(str(error))
    finally:
        conn.close()

    return {"ok": True, "error": None, "timed_out": False, "columns": columns, "rows": rows,
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
    """Sorguyu çalıştırmadan planını verir; sözdizimi ya da eksik tablo/sütun varsa hata return eder.
    SQLite normalde bulamadığı "çift tırnaklı" sütun adını metin sayar: "Free Meal Count" > 10 hatasız ama yanlış
    çalışır. Burada bu davranış kapalıdır; hata ve SQLite'ın "tek tırnak mı olmalıydı?" sorusu agent'a döner."""
    conn = connect(db_path)
    conn.setconfig(sqlite3.SQLITE_DBCONFIG_DQS_DML, False)
    try:
        plan = [row[3] for row in conn.execute("EXPLAIN QUERY PLAN " + sql)]
    except sqlite3.Error as error:
        return {"ok": False, "error": str(error), "plan": []}
    finally:
        conn.close()
    return {"ok": True, "error": None, "plan": plan}
