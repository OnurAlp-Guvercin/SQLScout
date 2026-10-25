"""Database memory (adım 1 ve soru bittikten sonra). Bir soru ok ile bittiyse, yolda bir hata ya da
boş sonuç olduysa ve cevap SQL'i o hatalı SQL'den farklıysa bir kayıt yazılır: soru, ilk hatalı SQL, aldığı not,
cevap SQL'i. Aynı veritabanındaki benzer sorular bunu adım 1'de görür. Gold SQL hiç kullanılmaz.
Dosya: config.MEMORY_DIR / <db_id>.jsonl"""

import json
import math
import re
import threading
from pathlib import Path

import config
from harness.tools import execute_sql

memory_lock = threading.Lock()


def read(db_path, question):
    """Soruya en çok benzeyen en fazla MEMORY_RECORDS kayıt (TF-IDF benzerliği)."""
    path = memory_path(db_path)
    if not path.exists():
        return []
    with memory_lock:  # evaluate.py soruları aynı anda çalıştırır; yarım yazılmış satır okunmasın
        records = [json.loads(line) for line in path.read_text().splitlines()]
    record_words = [words(record["question"]) for record in records]
    idf = inverse_frequency(record_words)
    scored = []
    for number, record in enumerate(records):
        score = similarity(words(question), record_words[number], idf)
        if score > 0:
            scored.append((-score, number, record))
    scored.sort()
    return [record for _, _, record in scored[:config.MEMORY_RECORDS]]


def inverse_frequency(word_sets):
    """Her kelimenin ağırlığı: ne kadar çok kayıtta geçiyorsa o kadar düşük ("how", "many" düşük, "superpower" yüksek)."""
    counts = {}
    for word_set in word_sets:
        for word in word_set:
            counts[word] = counts.get(word, 0) + 1
    return {word: math.log((len(word_sets) + 1) / (count + 1)) + 1 for word, count in counts.items()}


def similarity(question_words, record_words, idf):
    """Ortak kelimelerin ağırlıklarının toplamı, kaydın uzunluğuna bölünmüş (cosine benzerliği; sorunun uzunluğu her
    kayıt için aynı olduğu için sıralamayı değiştirmez ve atlanır)."""
    shared = sum(idf[word] ** 2 for word in question_words & record_words)
    length = math.sqrt(sum(idf[word] ** 2 for word in record_words))
    return shared / length if length else 0


def write(context, answer):
    if answer["label"] != "ok" or context.first_mistake is None:
        return
    # SQL değişmediyse kayıt bir düzeltme öğretmez, bağlama gürültü katar.
    if execute_sql.sql_key(context.first_mistake["sql"]) == execute_sql.sql_key(answer["sql"]):
        return
    record = {"question": context.question, "wrong_sql": context.first_mistake["sql"],
              "note": context.first_mistake["note"], "answer_sql": answer["sql"]}
    path = memory_path(context.db_path)
    with memory_lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def memory_path(db_path):
    return config.MEMORY_DIR / f"{Path(db_path).stem}.jsonl"


def words(text):
    return set(re.findall(r"[a-z0-9]{3,}", text.lower()))
