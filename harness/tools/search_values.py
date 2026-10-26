"""Adım 3: search_values tool'u. Bir değerin veritabanında nasıl yazıldığını bulur. Değerler, her veritabanı için bir
kez kurulan bir SQLite FTS5 index'inde aranır (data/prepared/<db_id>/values.sqlite); index trigram'lıdır (kelimenin bir
parçası da eşleşir), adaylar difflib ile yazım benzerliğine göre sıralanır."""

import difflib
import sqlite3
import threading
from pathlib import Path

import config
from db import sqlite_schema
from db.sqlite_db import connect, quote
from db.sqlite_schema import show_name

index_lock = threading.Lock()


def run(query, context):
    """Agent search_values(query) çağırınca run_steps bunu çağırır (adım 3).
    1. find_values: query'yi veritabanındaki bütün metin değerleri arasında arar; içinde geçen ya da yazılışı
       benzeyen en fazla 5 değeri (tablo, sütun, değer) bulur.
    2. show_values: bulunanları agent'ın okuyacağı metne çevirir.
    3. Bir şey bulunduysa metnin bir kopyası context.search_notes'a eklenir; candidate'ler (adım 7) agent'ın konuşmasını
       görmediği için bulunan değeri buradan öğrenir.
    4. Hiçbir değer bulunmadıysa ve aranan bir sütun adına benziyorsa o sütunlar söylenir: küçük modeller sütun
       adlarını da bu tool'la arar.
    Return: agent'a gidecek metin, ör. "Values similar to 'super strength':\n- superpower.power_name = 'Super Strength'"
    ya da "No values similar to '...' were found."."""
    matches = find_values(context.db_path, query)
    text = show_values(query, matches)
    if matches:
        context.search_notes.append(text)
        return text
    columns = similar_columns(context.db_path, query)
    if columns:
        text += (" search_values finds values stored in the database, not column names. Columns with a similar "
                 "name: " + ", ".join(columns) + ".")
    return text


def similar_columns(db_path, query):
    """Adı aranan kelimeyi içeren, onun içinde geçen ya da ona yazılışça benzeyen sütunlar: ["tablo.sütun", ...].
    Ör. "CumsumConsumption" → ["yearmonth.Consumption"]."""
    lowered = query.lower().replace(" ", "_")
    found = []
    for table in sqlite_schema.schema(db_path):
        for column in table["columns"]:
            name = column["name"].lower()
            inside = min(len(name), len(lowered)) >= 4 and (name in lowered or lowered in name)
            if inside or difflib.SequenceMatcher(None, lowered, name).ratio() >= config.SEARCH_SIMILARITY:
                found.append(f"{show_name(table['name'])}.{show_name(column['name'])}")
    return found[:config.SEARCH_RESULTS]


def find_values(db_path, text):
    """Metni içeren ya da ona yazılışça benzeyen (difflib ≥ SEARCH_SIMILARITY) en fazla SEARCH_RESULTS değer:
    [(tablo, sütun, değer)], en benzeri başta. Ör. "Los Angles" → [("items", "city", "Los Angeles")]"""
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
        if lowered in value.lower():
            score = 1.0
        else:
            score = difflib.SequenceMatcher(None, lowered, value.lower()).ratio()
        if score >= config.SEARCH_SIMILARITY:
            scored.append((-score, len(value), table, column, value))
    scored.sort()
    return [(table, column, value) for _, _, table, column, value in scored[:config.SEARCH_RESULTS]]


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
