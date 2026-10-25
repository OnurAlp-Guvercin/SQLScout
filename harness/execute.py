"""Adım 4–6: execute_sql. SQL önce ucuz kontrollerden geçer (pre-check), sonra çalıştırılır (ya da cache'ten gelir),
sonuç metne çevrilir ve agent'ın forecast'iyle karşılaştırılır; tutmadıysa surprise note eklenir.
Candidate'ler ve final check de SQL'i run ile çalıştırır."""

import json
import re

import config
from db import sqlite_db, sqlite_schema

TYPES = ["error", "empty", "rows"]


def run_query(sql, forecast, context):
    """Agent'ın execute_sql çağrısı. Döner: agent'a gidecek metin."""
    note = check(context.db_path, sql)  # adım 5
    if note:
        remember_mistake(sql, note, context)
        return note
    result = run(sql, context)  # adım 6
    text = format_result(result)
    if result["ok"]:
        context.last_ok_sql = sql
    else:
        remember_mistake(sql, text, context)
    context.last_forecast[sql_key(sql)] = forecast
    context.stats["forecasts"] += 1
    surprise = surprise_note(forecast, result)
    if surprise:
        remember_mistake(sql, surprise, context)
        text += "\n" + surprise
    else:
        context.stats["forecast_hits"] += 1
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
    """Cache'in ve tekrar guardrail'inin anahtarı: boşlukları sadeleştirilmiş SQL metni."""
    return " ".join(sql.split())


def remember_mistake(sql, note, context):
    """Sorudaki ilk hata; soru ok biterse database memory'ye yazılır."""
    if context.first_mistake is None:
        context.first_mistake = {"sql": sql, "note": note}


def format_result(result):
    """Gerçek sonucu agent'ın okuyacağı metne çevirir: sütunlar, satır sayısı ve kırpılmış satırlar ya da hata."""
    if not result["ok"]:
        return f"Error: {result['error']}"
    lines = [f"Columns: {', '.join(result['columns'])}"]
    if result["row_count"] == 0:
        lines.append("No rows: the result is empty.")
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


def read_forecast(args):
    """execute_sql'in argümanlarından forecast'i toplar. Alanlar en üst seviyede beklenir; küçük modeller bazen iç içe
    bir "forecast" nesnesi (ya da onun metnini) yazar, o da kabul edilir. Küçük biçim hataları düzeltilir:
    "true" → true, '["a"]' → ["a"], 358 → "100+"."""
    nested = args.get("forecast")
    if isinstance(nested, str):
        nested = parse_json(nested)
    if not isinstance(nested, dict):
        nested = {}
    forecast = {}
    for name in ("type", "columns", "rows", "trust"):
        value = args.get(name, nested.get(name))
        if isinstance(value, str) and name in ("type", "trust"):
            value = value.strip().lower()
            if name == "trust" and value in ("true", "false"):
                value = value == "true"
        if name == "columns" and isinstance(value, str):
            parsed = parse_json(value)
            value = parsed if isinstance(parsed, list) else [value]
        if name == "rows" and (isinstance(value, int) or (isinstance(value, str) and value.isdigit())):
            value = row_range(int(value))
        if value is not None:
            forecast[name] = value
    return forecast


def parse_json(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def forecast_error(forecast):
    """Forecast'in biçimi doğruysa None; değilse hatalı alanları adıyla söyleyen kısa metin. Yalnızca type zorunlu."""
    if not isinstance(forecast, dict):
        return 'it must be like {"type": "rows", "columns": ["name"], "rows": "1"}'
    problems = []
    if forecast.get("type") not in TYPES:
        problems.append(f"type must be one of: {', '.join(TYPES)}")
    if "columns" in forecast and (not isinstance(forecast["columns"], list) or not forecast["columns"]):
        problems.append("columns must be a non-empty list of the expected column names")
    if "rows" in forecast and forecast["rows"] not in config.ROW_RANGES:
        problems.append(f"rows must be one of: {', '.join(config.ROW_RANGES)}")
    if "trust" in forecast and not isinstance(forecast["trust"], bool):
        problems.append("trust must be true or false")
    return "; ".join(problems) or None


def summary(result):
    """Gerçek sonuç forecast biçiminde: type, sütun sayısı, satır aralığı."""
    if not result["ok"]:
        return {"type": "error", "columns": None, "rows": None}
    if result["row_count"] == 0:
        return {"type": "empty", "columns": len(result["columns"]), "rows": "0"}
    return {"type": "rows", "columns": len(result["columns"]), "rows": row_range(result["row_count"])}


def row_range(count):
    """Satır sayısının aralığı: config.ROW_RANGES'teki "0", "1", "2-10", "11-100", "100+" etiketlerinden biri."""
    for label in config.ROW_RANGES:
        if label.endswith("+"):
            if count > int(label[:-1]):
                return label
        elif "-" in label:
            low, high = label.split("-")
            if int(low) <= count <= int(high):
                return label
        elif count == int(label):
            return label
    return None


def surprise_note(forecast, result):
    """Forecast tuttuysa None. Tutması için type aynı olmalı; rows ise, yazıldıysa sütun sayısı ve satır aralığı da
    (sütun adlarına bakılmaz)."""
    actual = summary(result)
    hit = forecast["type"] == actual["type"]
    if hit and actual["type"] == "rows":
        if "columns" in forecast and len(forecast["columns"]) != actual["columns"]:
            hit = False
        if "rows" in forecast and forecast["rows"] != actual["rows"]:
            hit = False
    if hit:
        return None
    columns = len(forecast["columns"]) if "columns" in forecast else None
    expected = describe(forecast["type"], columns, forecast.get("rows"))
    real = describe(actual["type"], actual["columns"], actual["rows"])
    return f"Surprise: you forecast {expected}, but the real result is {real}. Check the query before you submit it."


def describe(result_type, columns, rows):
    if result_type == "error":
        return "an error"
    if result_type == "empty":
        return "an empty result"
    parts = []
    if columns is not None:
        parts.append(f"{columns} column(s)")
    if rows is not None:
        parts.append(f"{rows} row(s)")
    return " and ".join(parts) or "rows"
