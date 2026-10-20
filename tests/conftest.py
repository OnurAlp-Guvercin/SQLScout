"""Testlerin ortak küçük veritabanı. Kod içinde, her test için geçici bir klasörde kurulur."""

import sqlite3

import pytest

import config
from agent import llm


@pytest.fixture(autouse=True)
def files_in_tmp(tmp_path, monkeypatch):
    """Testler gerçek data/prepared/, experience/log.jsonl ve experience/memory/ dosyalarına yazmasın."""
    monkeypatch.setattr(config, "PREPARED_DIR", tmp_path / "prepared")
    monkeypatch.setattr(config, "EXPERIENCE_LOG", tmp_path / "log.jsonl")
    monkeypatch.setattr(config, "MEMORY_DIR", tmp_path / "memory")


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
    """Modelin sırayla vereceği cevapları ayarlar ve modele giden mesajları kaydeder. Candidate'ler (adım 8) kapalı;
    açan testler candidate cevaplarını da aynı sıraya koyar."""
    for flag in ("USE_CANDIDATES", "USE_HANDOFF", "USE_WORLD_MODEL"):  # açan testler kendisi açar
        monkeypatch.setattr(config, flag, False)
    replies, seen = [], []

    def fake_chat(messages, tools=None, seed=None, temperature=None, model=None):
        seen.append(list(messages))
        return replies.pop(0)

    monkeypatch.setattr(llm, "chat", fake_chat)
    return replies, seen
