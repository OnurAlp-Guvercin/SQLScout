"""Sütun açıklamalarını okur: BIRD'de veritabanının yanındaki database_description/<tablo>.csv dosyaları,
Mini-Interact'te <db>_column_meaning_base.json. Adım 1 (başlangıç bağlamı) ve search_schema (adım 3) kullanır."""

import csv
import io
import json
from pathlib import Path


def load(db_path):
    """Döner: {tablo: {sütun: açıklama}}, adlar küçük harfle. Açıklama dosyası yoksa boş."""
    folder = Path(db_path).parent / "database_description"
    descriptions = {}
    for csv_path in sorted(folder.glob("*.csv")):
        columns = {}
        for row in csv.DictReader(io.StringIO(read_text(csv_path))):
            name = clean(row.get("original_column_name")).lower()
            if name:
                columns[name] = describe(row)
        descriptions[csv_path.stem.lower()] = columns

    meanings = Path(db_path).with_name(f"{Path(db_path).stem}_column_meaning_base.json")
    if meanings.exists():  # Mini-Interact: {"db|tablo|sütun": açıklama}; JSON sütunlarında alanların anlamı da var
        for key, meaning in json.loads(meanings.read_text()).items():
            _, table, column = key.split("|")
            if isinstance(meaning, dict):
                fields = "; ".join(f"{name}: {text}" for name, text in meaning["fields_meaning"].items())
                meaning = f"{meaning['column_meaning']} Fields: {fields}"
            descriptions.setdefault(table.lower(), {})[column.lower()] = clean(meaning)
    return descriptions


def read_text(path):
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252")  # BIRD'deki birkaç CSV Windows kodlamasıyla kaydedilmiş


def describe(row):
    original = clean(row.get("original_column_name"))
    full_name = clean(row.get("column_name"))
    meaning = clean(row.get("column_description"))
    value_description = clean(row.get("value_description"))
    parts = []
    if full_name and full_name.lower() != original.lower():
        parts.append(full_name)
    if meaning and meaning.lower() not in (original.lower(), full_name.lower()):
        parts.append(meaning)
    if value_description:
        parts.append(f"value description: {value_description}")
    return ". ".join(parts)


def clean(text):
    return " ".join((text or "").split())
