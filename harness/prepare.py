"""Adım 1: başlangıç bağlamı. Şemayı, BIRD sütun açıklamalarını, foreign key'leri, column profile'ları, database
memory'yi, evidence'ı ve soruyu birleştirir.
Metin sınırı aşarsa soruya gereken tabloları bir LLM seçer (select_tables; schema linking, MAC-SQL'in Selector'ı
gibi), diğerleri tek satıra iner. Model şemayı yeniden yazmaz, yalnızca tablo adı seçer: olmayan sütun uyduramaz.
Denemek için: python -m harness.prepare <sqlite yolu> "soru" ["evidence"]"""

import json
import re
import sys
import threading
from pathlib import Path

import config
from agent import llm, prompts
from db import sqlite_schema
from db.sqlite_schema import show_name
from harness import memory

profiles_lock = threading.Lock()


def build_context(question, evidence, db_path):
    """Agent'ın ilk göreceği metin (string): parçaları toplar, render ile metne çevirir; metin CONTEXT_MAX_TOKENS'ı
    aşarsa yalnızca LLM'in soruya gerekli bulduğu tablolar tam yazılır, diğerleri tek satıra iner."""
    tables = sqlite_schema.schema(db_path)
    profiles = load_profiles(db_path, tables)
    descriptions = sqlite_schema.descriptions(db_path)
    corrections = past_corrections(db_path, question)  # database memory

    context = render(tables, profiles, descriptions, corrections, question, evidence)
    if llm.count_tokens(context) <= config.CONTEXT_MAX_TOKENS:
        return context
    blocks = {}
    for table in tables:
        blocks[table["name"]] = "\n".join(full_table(table, profiles[table["name"]], descriptions))
    needed = select_tables(question, evidence, blocks)
    shortened = {table["name"] for table in tables if table["name"] not in needed}
    return render(tables, profiles, descriptions, corrections, question, evidence, shortened)


def past_corrections(db_path, question):
    """Database memory kayıtları bağlamda ayrı bir bölümde, her biri tek satır olarak gösterilir."""
    lines = []
    for record in memory.read(db_path, question):
        note = record["note"].splitlines()[-1]
        lines.append(f"- Earlier question \"{record['question']}\": {record['wrong_sql']} → {note} "
                     f"Corrected: {record['answer_sql']}")
    return lines


def render(tables, profiles, descriptions, corrections, question, evidence, shortened=()):
    """Parçaları tek metne dizer: tablolar, foreign key'ler, memory, evidence, soru (en sonda).
    shortened'daki tablolar tek satır (short_table), diğerleri tam (full_table) yazılır."""
    lines = ["Database schema (SQLite):", ""]
    foreign_keys = []
    for table in tables:
        profile = profiles[table["name"]]
        if table["name"] in shortened:
            lines.append(short_table(table, profile))
        else:
            lines.extend(full_table(table, profile, descriptions))
        lines.append("")
        for fk in table["foreign_keys"]:
            foreign_keys.append(f"- {show_name(table['name'])}.{show_name(fk['column'])} = "
                                f"{show_name(fk['ref_table'])}.{show_name(fk['ref_column'])}")
    if foreign_keys:
        lines += ["Foreign keys:"] + foreign_keys + [""]
    if corrections:
        lines += ["Mistakes made and corrected earlier on this database:"] + corrections + [""]
    if evidence:
        lines.append(f"Evidence: {evidence}")
    lines.append(f"Question: {question}")
    return "\n".join(lines)


def full_table(table, profile, descriptions):
    """Tablonun tam hâli: "Table gender (3 rows)" başlığı ve her sütun için bir satır (column_line).
    descriptions: bütün veritabanının sütun açıklamaları, {tablo: {sütun: açıklama}}."""
    primary_keys = [column["name"] for column in table["columns"] if column["primary_key"]]
    table_descriptions = descriptions.get(table["name"].lower(), {})
    lines = [f"Table {show_name(table['name'])} ({profile['row_count']} rows)"]
    for column in profile["columns"]:
        description = table_descriptions.get(column["name"].strip().lower(), "")
        lines.append(column_line(column, column["name"] in primary_keys, description))
    return lines


def short_table(table, profile):
    """Kısaltılmış tablo, tek satır: "Table publisher (25 rows), details omitted: id INTEGER, publisher_name TEXT"."""
    columns = ", ".join(f"{show_name(column['name'])} {column['type']}" for column in table["columns"])
    return f"Table {show_name(table['name'])} ({profile['row_count']} rows), details omitted: {columns}"


def column_line(column, is_primary_key, description):
    """Bir sütunun satırı, ör. "- gender TEXT; the gender of the superhero; all values: 'Female', 'Male', 'N/A'"."""
    head = f"- {show_name(column['name'])} {column['type']}"
    if is_primary_key:
        head += ", primary key"
    parts = [head]
    if description:
        parts.append(description)
    # Sayısal sütunlarda yalnızca aralık; metin sütunlarında model yazılışı görsün diye değerler (sayıları değil).
    if column["min"] is not None:
        parts.append(f"range: {column['min']} to {column['max']}")
    elif column["top_values"]:
        label = "all values: " if column["all_values_shown"] else "e.g. "
        parts.append(label + ", ".join(show_value(value) for value, _ in column["top_values"]))
    return "; ".join(parts)


def show_value(value):
    """Bir değeri metne yazar: metinler tırnak içinde ve PROFILE_VALUE_MAX_CHARS'ta kırpılmış, sayılar olduğu gibi."""
    if not isinstance(value, str):
        return str(value)
    if len(value) > config.PROFILE_VALUE_MAX_CHARS:
        value = value[:config.PROFILE_VALUE_MAX_CHARS] + "..."
    return "'" + value.replace("\n", "\\n") + "'"


def load_profiles(db_path, tables):
    """Column profile'lar her veritabanı için bir kez hesaplanır ve data/prepared/<db_id>/profiles.json'da saklanır."""
    path = config.PREPARED_DIR / Path(db_path).stem / "profiles.json"
    with profiles_lock:  # evaluate.py soruları aynı anda çalıştırır; yarım yazılmış dosya okunmasın
        if not path.exists():
            profiles = {}
            for table in tables:
                profiles[table["name"]] = sqlite_schema.profile(db_path, table["name"])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(profiles, ensure_ascii=False, default=lambda blob: f"<{len(blob)} byte blob>"))
        return json.loads(path.read_text())


def select_tables(question, evidence, blocks):
    """blocks: {tablo adı: tablonun tam metni}. Döner: soruya gereken tablo adları, ör. {"superhero", "superpower"}."""
    selected = set()
    for chunk in split(blocks):
        selected |= ask(question, evidence, chunk)
    kept = {name: text for name, text in blocks.items() if name in selected}
    if len(kept) < len(blocks) and tokens(kept) > config.CONTEXT_MAX_TOKENS:
        return select_tables(question, evidence, kept)
    return set(kept)


def split(blocks):
    """Tabloları sırayla, her parça CONTEXT_MAX_TOKENS'a sığacak şekilde gruplar."""
    chunks, chunk = [], {}
    for name, text in blocks.items():
        if chunk and tokens(chunk) + llm.count_tokens(text) > config.CONTEXT_MAX_TOKENS:
            chunks.append(chunk)
            chunk = {}
        chunk[name] = text
    return chunks + [chunk]


def ask(question, evidence, chunk):
    """Modele bir parça şemayı ve soruyu verir; seçtiği tablolardan bu parçada olanları döndürür."""
    schema = "\n\n".join(chunk.values())
    evidence_line = f"Evidence: {evidence}\n" if evidence else ""
    messages = [{"role": "system", "content": prompts.SELECT_TABLES},
                {"role": "user", "content": f"{schema}\n\n{evidence_line}Question: {question}"}]
    text = llm.chat(messages, temperature=config.SCHEMA_SELECT_TEMPERATURE)["text"]
    match = re.search(r"\[.*\]", text, re.DOTALL)
    try:
        names = json.loads(match.group(0)) if match else []
    except json.JSONDecodeError:  # bozuk cevapta bu parçadan hiçbir tablo seçilmemiş sayılır
        names = []
    by_lower = {name.lower(): name for name in chunk}  # model adı başka büyük/küçük harfle yazabilir
    return {by_lower[name.lower()] for name in names if isinstance(name, str) and name.lower() in by_lower}


def tokens(blocks):
    return sum(llm.count_tokens(text) for text in blocks.values())


if __name__ == "__main__":
    db_path, question = sys.argv[1], sys.argv[2]
    evidence = sys.argv[3] if len(sys.argv) > 3 else ""
    context = build_context(question, evidence, db_path)
    print(context)
    print(f"\n[{llm.count_tokens(context)} token]")
