"""Adım 3: search_values (aşama 12) ve search_schema (aşama 13) tool'ları; bulduklarının bir kopyası search notes'a
yazılır, candidate prompt'una girer (aşama 18). Adım 1'deki değer eşleşmesi de find_values'u kullanır.
Değerler, her veritabanı için bir kez kurulan bir SQLite FTS5 index'inde aranır: data/prepared/<db_id>/values.sqlite.
Index trigram'lıdır (kelimenin bir parçası da eşleşir); adaylar difflib ile yazım benzerliğine göre sıralanır."""

import difflib
import re
import sqlite3
import threading
from pathlib import Path

import config
from db import sqlite_schema
from db.sqlite_db import connect, quote
from db.sqlite_schema import show_name
from harness import descriptions as bird_descriptions

index_lock = threading.Lock()


def run(step, context):
    """Agent'ın search tool call'unu çalıştırır; agent'a dönecek metni verir. Bir şey bulduysa search notes'a da yazar."""
    query = step["args"]["query"]
    if step["tool"] == "search_values":
        matches = find_values(context.db_path, query, config.SEARCH_RESULTS, allow_contains=True,
                              min_similarity=config.SEARCH_SIMILARITY)
        text = show_values(query, matches)
    else:
        matches = find_columns(context.db_path, query)
        text = show_columns(query, matches)
    if matches:
        context.search_notes.append(text)
    return text


def find_values(db_path, text, limit, allow_contains, min_similarity):
    """Metne yazılışça benzeyen değerler (difflib benzerliği en az min_similarity): [(tablo, sütun, değer)], en benzeri başta.
    allow_contains: metni içeren değerler de sayılır (search_values için; adım 1'de kapalı, yoksa "many" → "Germany")."""
    trigrams = []
    lowered = text.lower()
    for start in range(len(lowered) - 2):
        if lowered[start:start + 3] not in trigrams:
            trigrams.append(lowered[start:start + 3])
    if not trigrams:
        return []
    match = " OR ".join('"' + trigram.replace('"', '""') + '"' for trigram in trigrams)

    index = sqlite3.connect(index_path(db_path))
    try:
        rows = index.execute("SELECT tbl, col, value FROM value_index WHERE value_index MATCH ? ORDER BY rank LIMIT ?",
                             (match, config.SEARCH_CANDIDATES)).fetchall()
    finally:
        index.close()

    scored = []
    for table, column, value in rows:
        if allow_contains and lowered in value.lower():
            score = 1.0
        else:
            score = difflib.SequenceMatcher(None, lowered, value.lower()).ratio()
        if score >= min_similarity:
            scored.append((-score, len(value), table, column, value))
    scored.sort()
    return [(table, column, value) for _, _, table, column, value in scored[:limit]]


def index_path(db_path):
    """Değer index'inin yolu. Index yoksa önce kurulur (veritabanı başına bir kez)."""
    path = config.PREPARED_DIR / Path(db_path).stem / "values.sqlite"
    with index_lock:  # evaluate.py soruları aynı anda çalıştırır; index iki kez kurulmasın
        if not path.exists():
            build_index(db_path, path)
    return path


def build_index(db_path, path):
    """Her sütunun farklı metin değerlerini FTS5 index'ine yazar. Yarım kalan index kullanılmasın diye önce geçici dosyaya."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.unlink(missing_ok=True)
    index = sqlite3.connect(temporary)
    index.execute("CREATE VIRTUAL TABLE value_index USING fts5(value, tbl UNINDEXED, col UNINDEXED, tokenize='trigram')")
    conn = connect(db_path)
    try:
        for table in sqlite_schema.schema(db_path):
            for column in table["columns"]:
                col = quote(column["name"])
                values = conn.execute(f"SELECT DISTINCT {col} FROM {quote(table['name'])} "
                                      f"WHERE typeof({col}) = 'text' AND length({col}) <= ?",
                                      (config.INDEX_VALUE_MAX_CHARS,))
                for (value,) in values:
                    index.execute("INSERT INTO value_index VALUES (?, ?, ?)", (value, table["name"], column["name"]))
        index.commit()
    finally:
        conn.close()
        index.close()
    temporary.rename(path)


def show_values(query, matches):
    if not matches:
        return f"No values similar to '{query}' were found."
    lines = [f"Values similar to '{query}':"]
    for table, column, value in matches:
        lines.append(f"- {show_name(table)}.{show_name(column)} = {sql_text(value)}")
    return "\n".join(lines)


def sql_text(value):
    """Değeri SQL'e olduğu gibi yazılabilecek biçimde gösterir: 'O''Brien'."""
    return "'" + value.replace("'", "''") + "'"


def find_columns(db_path, query):
    """Sorgudaki kelimelerin tablo adında, sütun adında ya da BIRD açıklamasında geçtiği sütunlar.
    Addaki eşleşme açıklamadakinden iki kat sayılır. Döner: [(tablo, sütun, tip, açıklama)], en çok eşleşen başta."""
    query_words = re.findall(r"[a-z0-9]{3,}", query.lower())
    descriptions = bird_descriptions.load(db_path)
    scored = []
    for table in sqlite_schema.schema(db_path):
        table_descriptions = descriptions.get(table["name"].lower(), {})
        for column in table["columns"]:
            names = f"{table['name']} {column['name']}".lower()
            description = table_descriptions.get(column["name"].strip().lower(), "")
            score = 0
            for word in query_words:
                if word in names:
                    score += 2
                elif word in description.lower():
                    score += 1
            if score:
                scored.append((-score, len(scored), table["name"], column["name"], column["type"], description))
    scored.sort()
    return [(table, column, column_type, description) for _, _, table, column, column_type, description
            in scored[:config.SEARCH_RESULTS]]


def show_columns(query, matches):
    if not matches:
        return f"No tables or columns matching '{query}' were found."
    lines = [f"Columns matching '{query}':"]
    for table, column, column_type, description in matches:
        if len(description) > config.SEARCH_DESCRIPTION_MAX_CHARS:
            description = description[:config.SEARCH_DESCRIPTION_MAX_CHARS] + "..."
        line = f"- {show_name(table)}.{show_name(column)} {column_type}"
        lines.append(f"{line}: {description}" if description else line)
    return "\n".join(lines)
