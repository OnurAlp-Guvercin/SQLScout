"""Adım 1: memory. Daha önce doğru çözülmüş sorular (soru, evidence, SQL) embedding'leriyle bir SQLite dosyasında
(config.MEMORY_DB) durur; yeni bir soruya en benzer olanlar adım 1'in bağlamına eklenir.
BIRD train'i eklemek için: python -m harness.memory <train.json>"""

import functools
import json
import sqlite3
import sys
import threading

import mlx.core as mx
import numpy as np
from mlx_lm.models import qwen3
from tokenizers import Tokenizer

import config

lock = threading.Lock()  # evaluate.py soruları aynı anda çalıştırır: embedding modeli ve yazma tek tek


def similar(question, evidence, run):
    """Soruya en benzer, aday olan (is_candidate) en fazla MEMORY_EXAMPLES satır; benzerliği MEMORY_MIN_SIMILARITY'nin
    altındakiler gelmez. Return: [{"question", "evidence", "sql"}], en benzeri başta."""
    rows = [row for row in read_rows() if is_candidate(row, run)]
    if not rows:
        return []
    vectors = np.stack([np.frombuffer(row["vector"], dtype=np.float32) for row in rows])
    scores = vectors @ embed([text(question, evidence)])[0]  # vektörler normalize: dot product = cosine benzerliği
    found = []
    for number in np.argsort(-scores)[:config.MEMORY_EXAMPLES]:
        if scores[number] >= config.MEMORY_MIN_SIMILARITY:
            found.append({"question": rows[number]["question"], "evidence": rows[number]["evidence"],
                          "sql": rows[number]["sql"]})
    return found


def is_candidate(row, run):
    """Train'de gold'a göre doğru olanlar; diğerlerinde large model'in onayladıkları (gold'a bakmak kopya olur).
    Değerlendirmede (run, koşunun adı) yalnızca train ve bu koşunun soruları: başka koşuların cevapları sızmasın."""
    good = row["correct"] if row["split"] == "train" else row["label"] == "ok"
    return bool(good) and (run is None or row["split"] == "train" or row["run"] == run)


def add(rows):
    """Satırları ({"question", "evidence", "sql", "split", "run", "correct", "label"}) embed edip belleğe yazar."""
    vectors = embed([text(row["question"], row["evidence"]) for row in rows])
    with lock:
        conn = connect()
        for row, vector in zip(rows, vectors):
            conn.execute("INSERT INTO memory VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                         (row["question"], row["evidence"], row["sql"], row["split"], row["run"], row["correct"],
                          row["label"], vector.astype(np.float32).tobytes()))
        conn.commit()
        conn.close()


def text(question, evidence):
    """Embed edilen metin: soru ve varsa evidence."""
    return f"{question} {evidence or ''}".strip()


def read_rows():
    with lock:
        conn = connect()
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM memory").fetchall()
        conn.close()
    return rows


def connect():
    config.MEMORY_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.MEMORY_DB)
    conn.execute("CREATE TABLE IF NOT EXISTS memory (question TEXT, evidence TEXT, sql TEXT, split TEXT, run TEXT, "
                 "correct INTEGER, label TEXT, vector BLOB)")
    return conn


def embed(texts):
    """Metinlerin normalize embedding'leri (Qwen3-Embedding, MLX ile; model ilk çağrıda bir kez yüklenir). Tokenizer
    metnin sonuna <|endoftext|> ekler; o son token'ın vektörü metnin embedding'idir (modelin kendi kullanımı)."""
    vectors = []
    with lock:
        model, tokenizer = embedding_model()
        for sentence in texts:
            vector = model.model(mx.array([tokenizer.encode(sentence).ids]))[0, -1]
            vector = np.array(vector.astype(mx.float32))
            vectors.append(vector / np.linalg.norm(vector))
    return np.array(vectors)


@functools.lru_cache(maxsize=None)
def embedding_model():
    folder = config.PROJECT_DIR / config.EMBEDDING_MODEL
    model = qwen3.Model(qwen3.ModelArgs.from_dict(json.loads((folder / "config.json").read_text())))
    model.model.load_weights(list(mx.load(str(folder / "model.safetensors")).items()))  # ağırlıklar "model." öneksiz
    return model, Tokenizer.from_file(str(folder / "tokenizer.json"))


def add_bird_train(path):
    """BIRD train'in gold soru–SQL çiftleri: split = train, correct = True. Bellekte train varsa bir şey yapmaz."""
    if any(row["split"] == "train" for row in read_rows()):
        print("Train zaten bellekte.")
        return
    rows = []
    for item in json.load(open(path)):
        rows.append({"question": item["question"], "evidence": item["evidence"], "sql": item["SQL"],
                     "split": "train", "run": None, "correct": True, "label": None})
    for start in range(0, len(rows), 256):  # parça parça: ilerleme görünsün
        add(rows[start:start + 256])
        print(f"{min(start + 256, len(rows))}/{len(rows)}", flush=True)


if __name__ == "__main__":
    add_bird_train(sys.argv[1])
