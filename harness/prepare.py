"""Adım 1: başlangıç bağlamı. Şemayı, BIRD sütun açıklamalarını, foreign key'leri, column profile'ları,
evidence'ı ve soruyu birleştirir. Denemek için: python -m harness.prepare <sqlite yolu> "soru" ["evidence"]"""

import json
import sys
import threading
from pathlib import Path

import config
from agent import llm
from db import sqlite_schema
from db.sqlite_schema import show_name

profiles_lock = threading.Lock()


def build_context(question, evidence, db_path):
    """Agent'ın ilk göreceği metin (string): tablolar, foreign key'ler, evidence, soru (en sonda).
    BIRD dev'de en büyüğü ~12K token; bağlam sınırına yaklaşmaz."""
    tables = sqlite_schema.schema(db_path)
    profiles = load_profiles(db_path, tables)
    descriptions = sqlite_schema.descriptions(db_path)
    lines = ["Database schema (SQLite):", ""]
    foreign_keys = []
    for table in tables:
        lines.extend(full_table(table, profiles[table["name"]], descriptions))
        lines.append("")
        for fk in table["foreign_keys"]:
            foreign_keys.append(f"- {show_name(table['name'])}.{show_name(fk['column'])} = "
                                f"{show_name(fk['ref_table'])}.{show_name(fk['ref_column'])}")
    if foreign_keys:
        lines += ["Foreign keys:"] + foreign_keys + [""]
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


if __name__ == "__main__":
    db_path, question = sys.argv[1], sys.argv[2]
    evidence = sys.argv[3] if len(sys.argv) > 3 else ""
    context = build_context(question, evidence, db_path)
    print(context)
    print(f"\n[{llm.count_tokens(context)} token]")
