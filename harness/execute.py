"""Adım 4–6: execute_sql. SQL önce ucuz kontrollerden geçer (pre-check), sonra çalıştırılır (ya da cache'ten gelir) ve
sonuç agent'ın okuyacağı metne çevrilir. Candidate'ler ve final check de SQL'i run ile çalıştırır."""

import re

import config
from db import sqlite_db, sqlite_schema

EMPTY_HINT = "If the query filters on a text value, check how that value is written with search_values."


def run_query(sql, context):
    """Agent'ın execute_sql çağrısı. Return: agent'a gidecek metin."""
    note = check(context.db_path, sql)  # adım 5
    if note:
        remember_mistake(sql, note, context)
        return note
    result = run(sql, context)  # adım 6
    context.ran_by_agent.add(sql_key(sql))
    text = format_result(result)
    if not result["ok"] or result["row_count"] == 0:
        remember_mistake(sql, text, context)
    else:
        context.last_ok_sql = sql
    return text


def check(db_path, sql):
    """Pre-check: sorun yoksa None, varsa agent'a dönecek not. Salt okuma mı, EXPLAIN geçiyor mu?"""
    if not sqlite_db.is_read_only(sql):
        return "Rejected: only read-only queries that start with SELECT or WITH can be run."
    plan = sqlite_db.explain(db_path, sql)  # sözdizimi, tablo, sütun
    if not plan["ok"]:
        return f"Rejected before running: {plan['error']}" + column_hint(db_path, plan["error"])
    return None


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


def run(sql, context):
    """Gerçek sonuç: aynı SQL bu soruda daha önce çalıştıysa cache'ten, yoksa veritabanından."""
    key = sql_key(sql)
    if key not in context.cache:
        context.cache[key] = sqlite_db.execute(context.db_path, sql)
        context.stats["executions"] += 1
    return context.cache[key]


def sql_key(sql):
    """Cache'in ve tekrar guardrail'inin key'i: boşlukları sadeleştirilmiş SQL metni."""
    return " ".join(sql.split())


def remember_mistake(sql, note, context):
    """Sorudaki ilk hata (pre-check notu, SQL hatası ya da boş sonuç); soru ok biterse database memory'ye yazılır."""
    if context.first_mistake is None:
        context.first_mistake = {"sql": sql, "note": note}


def format_result(result):
    """Gerçek sonucu agent'ın okuyacağı metne çevirir: sütunlar, satır sayısı ve kırpılmış satırlar ya da hata.
    Sonuç boşsa değerin yazılışını kontrol etmesi hatırlatılır."""
    if not result["ok"]:
        return f"Error: {result['error']}"
    lines = [f"Columns: {', '.join(result['columns'])}"]
    if result["row_count"] == 0:
        lines.append("No rows: the result is empty. " + EMPTY_HINT)
        return "\n".join(lines)
    rows = trim_rows(result["rows"])
    if len(rows) < result["row_count"]:
        lines.append(f"{result['row_count']} rows (first {len(rows)} shown):")
    else:
        lines.append(f"{result['row_count']} rows:")
    for row in rows:
        lines.append(" | ".join(row))
    return "\n".join(lines)


def trim_rows(rows):
    """Agent en fazla SHOWN_ROWS satır görür; uzun hücreler SHOWN_CELL_CHARS karakterde kesilir."""
    trimmed = []
    for row in rows[:config.SHOWN_ROWS]:
        cells = []
        for value in row:
            text = "NULL" if value is None else str(value)
            if len(text) > config.SHOWN_CELL_CHARS:
                text = text[:config.SHOWN_CELL_CHARS] + "..."
            cells.append(text)
        trimmed.append(cells)
    return trimmed
