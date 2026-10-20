"""Adım 1: başlangıç bağlamı. Şemayı, BIRD sütun açıklamalarını, foreign key'leri, column profile'ları, sorudaki
kelimelerin değer eşleşmelerini (value_matches.py), database memory'yi (aşama 25), evidence'ı ve soruyu birleştirir.
Metin sınırı aşarsa soruyla en az eşleşen tablolar kısaltılır.
Denemek için: python -m harness.prepare <sqlite yolu> "soru" ["evidence"]"""

import json
import re
import sys
import threading
from pathlib import Path

import config
from agent import llm
from db import sqlite_schema
from db.sqlite_schema import show_name
from experience import memory
from harness import descriptions as bird_descriptions
from harness import value_matches

profiles_lock = threading.Lock()


def build_context(question, evidence, db_path):
    tables = sqlite_schema.schema(db_path)
    profiles = load_profiles(db_path, tables)
    descriptions = bird_descriptions.load(db_path)
    question_words = words(question + " " + evidence)
    matches = value_matches.find(question, db_path, tables)  # aşama 14
    corrections = past_corrections(db_path, question)  # aşama 25: database memory

    shortened = set()
    context = render(tables, profiles, descriptions, shortened, matches, corrections, question, evidence)
    least_matching_first = sorted(tables, key=lambda table: match_score(table, question_words))
    for table in least_matching_first:
        if llm.count_tokens(context) <= config.CONTEXT_MAX_TOKENS:
            break
        shortened.add(table["name"])
        context = render(tables, profiles, descriptions, shortened, matches, corrections, question, evidence)
    return context


def past_corrections(db_path, question):
    """Database memory kayıtları bağlamda ayrı bir bölümde, her biri tek satır olarak gösterilir."""
    lines = []
    for record in memory.read(db_path, question):
        note = record["note"].splitlines()[-1]
        lines.append(f"- Earlier question \"{record['question']}\": {record['wrong_sql']} → {note} "
                     f"Corrected: {record['answer_sql']}")
    return lines


def render(tables, profiles, descriptions, shortened, matches, corrections, question, evidence):
    lines = ["Database schema (SQLite):", ""]
    foreign_keys = []
    for table in tables:
        profile = profiles[table["name"]]
        if table["name"] in shortened:
            lines.append(short_table(table, profile))
        else:
            lines.extend(full_table(table, profile, descriptions.get(table["name"].lower(), {})))
        lines.append("")
        for fk in table["foreign_keys"]:
            foreign_keys.append(f"- {show_name(table['name'])}.{show_name(fk['column'])} = "
                                f"{show_name(fk['ref_table'])}.{show_name(fk['ref_column'])}")
    if foreign_keys:
        lines += ["Foreign keys:"] + foreign_keys + [""]
    if matches:
        lines += ["Database values similar to words in the question:"] + matches + [""]
    if corrections:
        lines += ["Mistakes made and corrected earlier on this database:"] + corrections + [""]
    if evidence:
        lines.append(f"Evidence: {evidence}")
    lines.append(f"Question: {question}")
    return "\n".join(lines)


def full_table(table, profile, descriptions):
    primary_keys = [column["name"] for column in table["columns"] if column["primary_key"]]
    lines = [f"Table {show_name(table['name'])} ({profile['row_count']} rows)"]
    for column in profile["columns"]:
        description = descriptions.get(column["name"].strip().lower(), "")
        lines.append(column_line(column, column["name"] in primary_keys, description))
    return lines


def short_table(table, profile):
    columns = ", ".join(f"{show_name(column['name'])} {column['type']}" for column in table["columns"])
    return f"Table {show_name(table['name'])} ({profile['row_count']} rows), details omitted: {columns}"


def column_line(column, is_primary_key, description):
    head = f"- {show_name(column['name'])} {column['type']}"
    if is_primary_key:
        head += ", primary key"
    parts = [head]
    if description:
        parts.append(description)
    if column["null_ratio"]:
        parts.append(f"{column['null_ratio']:.1%} NULL")
    if column["top_values"]:
        values = ", ".join(f"{show_value(value)} ({count})" for value, count in column["top_values"])
        if column["all_values_shown"]:
            parts.append(f"all values: {values}")
        else:
            parts.append(f"{column['distinct']} distinct values, most common: {values}")
    if column["min"] is not None:
        parts.append(f"range: {column['min']} to {column['max']}")
    return "; ".join(parts)


def show_value(value):
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


def words(text):
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)  # camelCase sütun adlarını kelimelere ayırır
    return set(re.findall(r"[a-z0-9]{3,}", text.lower()))


def match_score(table, question_words):
    names = table["name"] + " " + " ".join(column["name"] for column in table["columns"])
    return len(words(names) & question_words)


if __name__ == "__main__":
    db_path, question = sys.argv[1], sys.argv[2]
    evidence = sys.argv[3] if len(sys.argv) > 3 else ""
    context = build_context(question, evidence, db_path)
    print(context)
    print(f"\n[{llm.count_tokens(context)} token]")
