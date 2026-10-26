"""Adım 4–6: execute_sql tool'u. SQL önce ucuz kontrollerden geçer (pre-check), sonra çalıştırılır (ya da cache'ten gelir) ve
sonuç agent'ın okuyacağı metne çevrilir. Final check de SQL'i run_sql ile çalıştırır."""

import re

import config
from db import sqlite_db, sqlite_schema
from db.sqlite_schema import show_name

EMPTY_HINT = "If the query filters on a text value, check how that value is written with search_values."


def run(sql, context):
    """Agent execute_sql(sql) çağırınca (ya da SQL'i ```sql bloğunda yazınca) run_steps bunu çağırır (adım 4–6).
    1. check (pre-check, adım 5): sorgu salt okuma mı, EXPLAIN geçiyor mu? Geçmiyorsa sorgu çalıştırılmaz, not
       return edilir.
    2. run_sql (adım 6): sorgu çalıştırılır; aynı SQL bu soruda daha önce çalıştıysa sonuç cache'ten gelir.
    3. format_result: sonuç metne çevrilir (en fazla 20 satır; boşsa search_values hatırlatması).
    4. SQL context.seen'e eklenir: agent sonucunu gördü (submit buna bakar). Hatasız ve dolu sonuç context.last_ok_sql
       olur (fallback için).
    Return: agent'a gidecek metin, ör. "Columns: superhero_name\n358 rows (first 20 shown):\n..." ya da pre-check notu."""
    note = check(context.db_path, sql)  # adım 5
    if note:
        return note
    result = run_sql(sql, context)  # adım 6
    text = format_result(result)
    context.seen.add(sql_key(sql))
    if result["ok"] and result["row_count"] > 0:
        context.last_ok_sql = sql
    return text


def check(db_path, sql):
    """Pre-check: sorun yoksa None, varsa agent'a dönecek not. Salt okuma mı, EXPLAIN geçiyor mu?"""
    if not sqlite_db.is_read_only(sql):
        return "Rejected: only read-only queries that start with SELECT or WITH can be run."
    plan = sqlite_db.explain(db_path, sql)  # sözdizimi, tablo, sütun
    if not plan["ok"]:
        return f"Rejected before running: {plan['error']}" + error_hint(db_path, sql, plan["error"])
    return None


def error_hint(db_path, sql, error):
    """Olmayan sütun ya da tablo, belirsiz sütun hatasına düzeltmek için gereken bilgiyi ekler: o adda sütunu olan
    tablolar, alias'ı olan bir tablonun kendi adıyla yazılması, sorgudaki tabloların (alias'larıyla) gerçek sütunları
    ya da veritabanındaki tablolar.
    Ör. "no such column: T1.backup_item" → ". A column with this name exists in: stores. Tables in your query and
    their columns: items (T1): id, city, price, status."."""
    tables = sqlite_schema.schema(db_path)
    if error.startswith("no such table:"):
        return ". Tables in this database: " + ", ".join(show_name(table["name"]) for table in tables) + "."
    if not error.startswith(("no such column:", "ambiguous column name:")):
        return ""
    name = error.split(":", 1)[1].strip()  # ör. "T1.backup_item" ya da "backup_item"
    qualifier, _, column = name.rpartition(".")
    qualifier, column = qualifier.strip("`\"[]").lower(), column.strip("`\"[]")
    having = [show_name(table["name"]) for table in tables
              if any(info["name"].lower() == column.lower() for info in table["columns"])]
    hint = ""
    if error.startswith("ambiguous"):
        hint += ". Several tables in your query have this column: write it with its table name or alias, e.g. T1.col"
    elif having:
        hint += f". A column with this name exists in: {', '.join(having)}"
    used = tables_in_query(sql, tables)
    if not used:
        return hint + ". Table and column names are listed in the schema at the start."
    parts = []
    for table, aliases in used:
        if aliases and qualifier == table["name"].lower():  # FROM client c ... client.gender: alias'la yazılmalı
            hint += f". {show_name(table['name'])} has the alias {aliases[0]} in your query: write {aliases[0]}.{column}"
        label = show_name(table["name"]) + (f" ({', '.join(aliases)})" if aliases else "")
        parts.append(label + ": " + ", ".join(show_name(info["name"]) for info in table["columns"]))
    return hint + ". Tables in your query and their columns: " + "; ".join(parts) + "."


# Tırnaksız yazılınca tablo adı ya da alias olamayan SQL kelimeleri (ör. ORDER BY, veritabanında order tablosu olsa da).
SQL_WORDS = {"select", "from", "where", "join", "inner", "left", "right", "full", "outer", "cross", "natural", "on",
             "using", "group", "order", "by", "having", "limit", "offset", "union", "except", "intersect", "and", "or",
             "not", "in", "is", "as", "case", "when", "then", "else", "end", "distinct", "between", "like", "null",
             "window", "values", "table", "index", "key", "check", "default", "references", "primary"}


def tables_in_query(sql, tables):
    """Sorguda adı geçen şema tabloları ve alias'ları: [(tablo, [alias, ...])], sorgudaki sırayla.
    SQL token'lara ayrılır; metin değerleri ('...') tek token olarak atlanır, böylece içlerindeki kelimeler tablo
    sanılmaz. Yalnızca not için kullanılır: bir alias'ı kaçırmak notu kısaltır, sonucu değiştirmez."""
    matches = list(re.finditer(r"'(?:[^']|'')*'|`[^`]*`|\"[^\"]*\"|\[[^\]]*\]|\w+", sql))
    by_name = {table["name"].lower(): table for table in tables}
    used = {}
    for number, match in enumerate(matches):
        token = match.group()
        word = token.strip("`\"[]")
        quoted = token != word
        if token.startswith("'") or (not quoted and word.lower() in SQL_WORDS) or word.lower() not in by_name:
            continue
        table = by_name[word.lower()]
        aliases = used.setdefault(table["name"], (table, []))[1]
        if sql[match.end():match.end() + 1] == ".":  # items.city: tablo adı sütunu niteliyor, ardından alias gelmez
            continue
        following = [item.group() for item in matches[number + 1:number + 3]]
        if following and following[0].lower() == "as":
            following = following[1:]
        if following and following[0].isidentifier() and following[0].lower() not in SQL_WORDS \
                and following[0].lower() not in by_name and following[0] not in aliases:
            aliases.append(following[0])
    return list(used.values())


def run_sql(sql, context):
    """Gerçek sonuç: aynı SQL bu soruda daha önce çalıştıysa cache'ten, yoksa veritabanından."""
    key = sql_key(sql)
    if key not in context.cache:
        context.cache[key] = sqlite_db.execute(context.db_path, sql)
        context.stats["executions"] += 1
    return context.cache[key]


def sql_key(sql):
    """Cache'in, tekrar guardrail'inin ve context.seen'in key'i: boşlukları sadeleştirilmiş SQL metni."""
    return " ".join(sql.split())


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
