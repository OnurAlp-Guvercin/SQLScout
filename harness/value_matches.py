"""Adım 1: sorudaki kelimelerin değer eşleşmeleri (aşama 14). Harness, agent daha arama yapmadan sorudaki
kelime gruplarını veritabanındaki değerlerde arar; bulduklarını prepare.py başlangıç bağlamına ekler.
Arama search_values'ınkiyle aynıdır (search.find_values), ama kelimeyi içeren değerleri saymaz."""

import re

import config
from db.sqlite_schema import show_name
from harness import search

# Değer eşleşmesinde bu kelimelerle başlayan ya da biten kelime grupları aranmaz.
STOPWORDS = {"a", "an", "the", "of", "in", "on", "at", "to", "for", "by", "with", "from", "and", "or", "is", "are",
             "was", "were", "be", "been", "what", "which", "who", "whose", "how", "many", "much", "list", "give",
             "show", "name", "names", "all", "each", "that", "this", "these", "those", "their", "its", "it", "as",
             "than", "do", "does", "did", "has", "have", "had", "there", "among", "per", "most", "more", "least",
             "less", "number", "total", "average", "please", "between", "not", "no", "any", "his", "her", "they"}


def find(question, db_path, tables):
    """Sorudaki kelime gruplarına (en fazla CONTEXT_PHRASE_WORDS kelime) yazılışça benzeyen değerler.
    Örnek: "Los Angles" → schools.City = 'Los Angeles'. Uzun gruplar önce aranır; aynı değer bir kez gösterilir.
    Gürültüye karşı: kısa tek kelimeler ve tablo/sütun adları aranmaz, tek kelimelerde eşik daha sıkıdır."""
    names = set()
    for table in tables:
        names.add(table["name"].lower())
        for column in table["columns"]:
            names.add(column["name"].lower())
    tokens = re.findall(r"[\w'-]+", question)
    lines, seen = [], set()
    for size in range(config.CONTEXT_PHRASE_WORDS, 0, -1):
        similarity = config.SEARCH_SIMILARITY if size > 1 else config.CONTEXT_WORD_SIMILARITY
        for start in range(len(tokens) - size + 1):
            group = tokens[start:start + size]
            phrase = " ".join(group)
            if group[0].lower() in STOPWORDS or group[-1].lower() in STOPWORDS or phrase.lower() in names:
                continue
            if size == 1 and len(phrase) < config.CONTEXT_MIN_WORD_CHARS:
                continue
            found = []
            matches = search.find_values(db_path, phrase, config.CONTEXT_VALUE_MATCHES, allow_contains=False,
                                         min_similarity=similarity)
            for table, column, value in matches:
                if (table, column, value) not in seen:
                    seen.add((table, column, value))
                    found.append(f"{show_name(table)}.{show_name(column)} = {search.sql_text(value)}")
            if found:
                lines.append(f'- "{phrase}": ' + "; ".join(found))
    return lines
