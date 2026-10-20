"""Adım 5: pre-check. SQL veritabanında çalıştırılmadan önce ucuz kontrollerden geçer ve nereye gideceği seçilir.
1. ve 2. soru: salt okuma ve EXPLAIN (aşama 8). 3. soru, cache: sonuçlar Context.cache'te sql_key ile saklanır (aşama 9).
4. soru, world model'e gidilsin mi (aşama 27): needs_world_model. Agent'ın SQL'leri, candidate'ler ve final check
gerçek çalıştırma için hep run'dan geçer; final check world model'e hiç gitmez."""

import re
import time

import config
from db import sqlite_db, sqlite_schema
from experience import log as experience_log
from harness import compare, cost


def run(sql, context, run_by="agent", forecast=None, prediction=None):
    """Pre-check'ten geçen SQL'in sonucu: daha önce çalıştıysa cache'ten, yoksa gerçek çalıştırmayla (adım 7);
    her gerçek çalıştırma experience log'a yazılır. Döner: (not, sonuç). Not doluysa sorgu çalıştırılmadı."""
    note = check(context.db_path, sql)
    if note:
        return note, None
    key = sql_key(sql)
    if key not in context.cache:
        start = time.monotonic()
        result = sqlite_db.execute(context.db_path, sql)
        context.executions += 1
        context.cache[key] = result
        seconds = time.monotonic() - start
        experience_log.write(context, sql, forecast, compare.summary(result), seconds, run_by, prediction)
        if result["ok"] and run_by != "candidate":  # fallback answer candidate'lerin SQL'ini kullanmaz
            context.last_ok_sql = sql
    return None, context.cache[key]


def check(db_path, sql):
    """Sorun yoksa None, varsa agent'a dönecek hata notu."""
    if not sqlite_db.is_read_only(sql):  # 1. salt okuma mı?
        return "Rejected: only read-only queries that start with SELECT or WITH can be run."
    plan = sqlite_db.explain(db_path, sql)  # 2. sözdizimi, tablo, sütun
    if not plan["ok"]:
        return f"Rejected before running: {plan['error']}" + column_hint(db_path, plan["error"])
    return None


def needs_world_model(sql, context):
    """4. soru: daha önce çalışmamış bir sorgu pahalı mı, ya da budget az mı? USE_WORLD_MODEL kapalıysa hep hayır."""
    if not config.USE_WORLD_MODEL or sql_key(sql) in context.cache:
        return False
    return cost.budget_low(context) or is_expensive(sql, context.db_path)


def is_expensive(sql, db_path):
    rows = cost.query_cost(db_path, sql)  # SIMULATE_COST açıksa simüle edilmiş maliyet
    return rows is not None and rows > config.EXPENSIVE_ROWS


def sql_key(sql):
    """Cache'in ve tekrar guardrail'inin anahtarı: boşlukları sadeleştirilmiş SQL metni."""
    return " ".join(sql.split())


def column_hint(db_path, error):
    """Olmayan bir sütun yazılmışsa o adda sütunu olan tabloları söyler (ör. sütun başka tablodadır)."""
    match = re.match(r"no such column: (.+)", error)
    if not match:
        return ""
    column = match.group(1).split(".")[-1].strip("`\"").lower()
    tables = []
    for table in sqlite_schema.schema(db_path):
        for info in table["columns"]:
            if info["name"].lower() == column:
                tables.append(table["name"])
    if not tables:
        return ""
    return f". A column with this name exists in: {', '.join(tables)}."
