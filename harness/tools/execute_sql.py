"""Adım 4–6: execute_sql tool'u. SQL önce ucuz kontrollerden geçer (pre-check), sonra çalıştırılır (ya da cache'ten gelir) ve
sonuç agent'ın okuyacağı metne çevrilir. Final check de SQL'i run_sql ile çalıştırır."""

import re

import config
from db import sqlite_db, sqlite_schema
from db.sqlite_schema import SQL_WORDS, show_name
from harness.tools.search_values import similar_columns

EMPTY_HINT = "If the query filters on a text value, check how that value is written with search_values."
TRIMMED_HINT = ("You do not need to see every row: if this query answers the question, submit it as it is; the answer "
                "keeps all rows.")
TIMEOUT_HINT = (f"Exploration queries may run {config.EXPLORE_TIMEOUT_SECONDS} seconds. If this query answers the "
                f"question, you can submit it: a submitted query may run {config.ANSWER_TIMEOUT_SECONDS} seconds.")


def run(sql, context):
    """Agent execute_sql(sql) çağırınca run_steps bunu çağırır (adım 4–6).
    1. check (pre-check, adım 5): sorgu salt okuma mı, EXPLAIN geçiyor mu? Geçmiyorsa sorgu çalıştırılmaz, not
       return edilir.
    2. run_sql (adım 6): sorgu en fazla EXPLORE_TIMEOUT_SECONDS çalıştırılır; aynı SQL bu soruda daha önce çalıştıysa
       sonuç cache'ten gelir. Keşifte zaman aşımında agent'a submit edilen sorgunun daha uzun çalışabileceği söylenir.
    3. format_result: sonuç metne çevrilir (en fazla 20 satır; boşsa ya da yalnızca 0/NULL ise search_values
       hatırlatması).
    4. Hatasız ve dolu sonuç (has_rows) context.last_ok_sql olur (ilerleme sınırı için).
    Return: agent'a gidecek metin, ör. "Columns: superhero_name\n358 rows (first 20 shown):\n..." ya da pre-check notu."""
    note = check(context.db_path, sql)  # adım 5
    if note:
        return note
    result = run_sql(sql, context)  # adım 6
    text = format_result(result)
    if result["timed_out"]:
        if sql_key(sql) in context.cache:  # submit edilmiş ve uzun sınırda da bitmemiş: yeniden submit önerilmez
            return text
        return text + " " + TIMEOUT_HINT
    if has_rows(result):
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
    tablolar (yoksa adı benzeyen sütunlar), alias'ı olan bir tablonun kendi adıyla yazılması, sorgudaki tabloların
    (alias'larıyla) gerçek sütunları ya da veritabanındaki tablolar.
    Ör. "no such column: T1.backup_item" → ". A column with this name exists in: stores. Tables in your query and
    their columns: items (T1): id, city, price, status."."""
    tables = sqlite_schema.schema(db_path)
    if error.startswith("no such table:"):
        return ". Tables in this database: " + ", ".join(show_name(table["name"]) for table in tables) + "."
    if not error.startswith(("no such column:", "ambiguous column name:")):
        return ""
    name = error.split(":", 1)[1].split(" - should this be")[0].strip()  # ör. "T1.backup_item" ya da "backup_item"
    if "should this be a string literal" in error:  # "St. Louis" gibi bir metin: nokta tablo.sütun ayırıcı değil
        qualifier, column = "", name
    else:
        qualifier, _, column = name.rpartition(".")
    qualifier, column = qualifier.strip("`\"[]").lower(), column.strip("`\"[]")
    having = [show_name(table["name"]) for table in tables
              if any(info["name"].lower() == column.lower() for info in table["columns"])]
    hint = ""
    if error.startswith("ambiguous"):
        hint += ". Several tables in your query have this column: write it with its table name or alias, e.g. T1.col"
    elif having:
        hint += f". A column with this name exists in: {', '.join(having)}"
    else:
        similar = similar_columns(db_path, column)  # ör. "Free Meal Count" → frpm.`Free Meal Count (K-12)`
        if similar:
            hint += f". Columns with a similar name: {', '.join(similar)}"
    used = tables_in_query(sql, tables)
    if not used:
        return hint + ". Table and column names are listed in the schema at the start."
    parts = []
    for table, aliases in used:
        if aliases and qualifier == table["name"].lower():  # FROM client c ... client.gender: alias'la yazılmalı
            hint += (f". {show_name(table['name'])} has the alias {aliases[0]} in your query: "
                     f"write {aliases[0]}.{show_name(column)}")
        label = show_name(table["name"]) + (f" ({', '.join(aliases)})" if aliases else "")
        parts.append(label + ": " + ", ".join(show_name(info["name"]) for info in table["columns"]))
    return hint + ". Tables in your query and their columns: " + "; ".join(parts) + "."


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


def run_sql(sql, context, answer=False):
    """Gerçek sonuç: aynı SQL bu soruda daha önce çalıştıysa cache'ten, yoksa veritabanından. Keşif ve deneme
    sorguları en fazla EXPLORE_TIMEOUT_SECONDS, cevap olarak submit edilen sorgu (answer) ANSWER_TIMEOUT_SECONDS
    çalışır. Keşifte zaman aşımına uğrayan sorgu cache'e girmez: submit edilirse uzun sınırla yeniden çalışır."""
    key = sql_key(sql)
    if key in context.cache:
        return context.cache[key]
    timeout = config.ANSWER_TIMEOUT_SECONDS if answer else config.EXPLORE_TIMEOUT_SECONDS
    result = sqlite_db.execute(context.db_path, sql, timeout)
    context.stats["executions"] += 1
    if answer or not result["timed_out"]:
        context.cache[key] = result
    return result


def sql_key(sql):
    """Cache'in ve tekrar guardrail'inin key'i: boşlukları sadeleştirilmiş, sondaki ';' atılmış SQL metni. Ör.
    "SELECT  1;" ile "SELECT 1" aynı sorgudur. Metin değerlerinin ('A  B') içindeki boşluklar olduğu gibi kalır."""
    parts = re.split(r"('(?:[^']|'')*')", sql.strip().rstrip(";"))
    for number in range(0, len(parts), 2):  # çift sıradakiler metin değeri değil
        parts[number] = " ".join(parts[number].split())
    return "".join(parts).strip()


def has_rows(result):
    """Sonuç gerçekten dolu mu: hatasız, en az bir satır ve tek satırsa yalnızca 0 ya da NULL değil. Yanlış yazılmış bir
    değerle COUNT(*) 0, AVG(...) NULL döner; bu boş sonuç gibidir."""
    if not result["ok"] or result["row_count"] == 0:
        return False
    if result["row_count"] == 1:
        return any(value is not None and value != 0 for value in result["rows"][0])
    return True


def format_result(result, hint=True):
    """Gerçek sonucu metne çevirir: sütunlar, satır sayısı ve kırpılmış satırlar ya da hata. Agent'a notlar (hint):
    sonuç boşsa ya da yalnızca 0/NULL ise değerin yazılışını kontrol etmesi; satırlar kırpıldıysa hepsini görmeden
    submit edebileceği (yoksa satırları sayfa sayfa görmeye çalışıp budget'ı bitirebilir). Large model kontrolü (adım 7)
    sonucu notsuz görür."""
    if not result["ok"]:
        return f"Error: {result['error']}"
    lines = [f"Columns: {', '.join(result['columns'])}"]
    if result["row_count"] == 0:
        lines.append("No rows: the result is empty." + (" " + EMPTY_HINT if hint else ""))
        return "\n".join(lines)
    rows = trim_rows(result["rows"])
    if len(rows) < result["row_count"]:
        lines.append(f"{result['row_count']} rows (first {len(rows)} shown):")
    else:
        lines.append(f"{result['row_count']} rows:")
    for row in rows:
        lines.append(" | ".join(row))
    if hint and len(rows) < result["row_count"]:
        lines.append(TRIMMED_HINT)
    if hint and not has_rows(result):
        lines.append("The result is only 0 or NULL. " + EMPTY_HINT)
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
