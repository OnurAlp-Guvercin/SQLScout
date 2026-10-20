"""Database memory (adım 1 ve soru bittikten sonra, aşama 25). Bir soru ok ile bittiyse ve yolda bir hata ya da
surprise note olduysa bir kayıt yazılır: soru, ilk hatalı SQL, aldığı not, cevap SQL'i. Aynı veritabanındaki benzer
sorular bunu adım 1'de görür. Gold SQL hiç kullanılmaz. Dosya: config.MEMORY_DIR / <db_id>.jsonl"""

import json
import re
import threading
from pathlib import Path

import config

memory_lock = threading.Lock()


def read(db_path, question):
    """Soruyla en çok kelime paylaşan en fazla MEMORY_RECORDS kayıt. USE_DB_MEMORY kapalıysa hiç okunmaz."""
    path = memory_path(db_path)
    if not config.USE_DB_MEMORY or not path.exists():
        return []
    scored = []
    for line in path.read_text().splitlines():
        record = json.loads(line)
        shared = len(words(question) & words(record["question"]))
        if shared:
            scored.append((-shared, len(scored), record))
    scored.sort()
    return [record for _, _, record in scored[:config.MEMORY_RECORDS]]


def write(context, answer):
    if not config.USE_DB_MEMORY or answer["label"] != "ok" or context.first_mistake is None:
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
