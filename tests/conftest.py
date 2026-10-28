"""Testlerin ortak küçük veritabanı. Kod içinde, her test için geçici bir klasörde kurulur."""

import sqlite3

import numpy as np
import pytest

import config
from agent import llm, prompts
from harness import memory
from tests.fakes import text_reply


@pytest.fixture(autouse=True)
def files_in_tmp(tmp_path, monkeypatch):
    """Testler gerçek data/prepared/, experience/log.jsonl ve experience/memory.sqlite dosyalarına yazmasın."""
    monkeypatch.setattr(config, "PREPARED_DIR", tmp_path / "prepared")
    monkeypatch.setattr(config, "EXPERIENCE_LOG", tmp_path / "log.jsonl")
    monkeypatch.setattr(config, "MEMORY_DB", tmp_path / "memory.sqlite")


@pytest.fixture(autouse=True)
def fake_embedding(monkeypatch):
    """Embedding modeli yüklenmez: her metin, içindeki kelimelerin sayıldığı normalize bir vektör olur. Aynı kelimeleri
    paylaşan metinler birbirine benzer."""
    def embed(texts):
        vectors = []
        for text in texts:
            vector = np.zeros(64, dtype=np.float32)
            for word in text.lower().replace("?", "").split():
                vector[sum(map(ord, word)) % 64] += 1
            vectors.append(vector / np.linalg.norm(vector))
        return np.array(vectors)

    monkeypatch.setattr(memory, "embed", embed)


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "shop.sqlite"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, city TEXT, price REAL, status TEXT)")
    conn.execute("CREATE INDEX items_city ON items(city)")
    cities = ["Los Angeles", "Boston", "Chicago"]
    for i in range(150):
        status = None if i % 10 == 0 else ("returned" if i % 2 else "ok")
        conn.execute("INSERT INTO items VALUES (?, ?, ?, ?)", (i, cities[i % 3], i * 1.5, status))
    conn.execute("CREATE TABLE stores (id INTEGER PRIMARY KEY, item_id INTEGER REFERENCES items(id), "
                 "backup_item INTEGER REFERENCES items, name TEXT, FOREIGN KEY (item_id) REFERENCES items(id))")
    for i in range(3):
        conn.execute("INSERT INTO stores VALUES (?, ?, ?, ?)", (i, i, i + 1, f"Store {i}"))
    conn.commit()
    conn.close()
    return str(path)


@pytest.fixture
def fake_model(monkeypatch):
    """Modelin sırayla vereceği cevapları ayarlar ve modele giden mesajları kaydeder. Large model kontrolü (adım 7) sıraya
    girmez: sahte large model her cevabı onaylar; onaylamamayı deneyen testler submit.large_model_review'u değiştirir."""
    replies, seen = [], []

    def fake_chat(messages, tools=None, temperature=None, model=None):
        if messages[0]["content"] == prompts.CHECK_ANSWER:
            return text_reply('{"reason": "It answers the question.", "correct": true}')
        seen.append(list(messages))
        return replies.pop(0)

    monkeypatch.setattr(llm, "chat", fake_chat)
    return replies, seen
