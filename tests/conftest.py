"""Testlerin ortak küçük veritabanı. Kod içinde, her test için geçici bir klasörde kurulur."""

import json
import sqlite3

import pytest

import config
from agent import llm, prompts
from tests.fakes import sql_reply


@pytest.fixture(autouse=True)
def files_in_tmp(tmp_path, monkeypatch):
    """Testler gerçek data/prepared/ ve experience/log.jsonl dosyalarına yazmasın."""
    monkeypatch.setattr(config, "PREPARED_DIR", tmp_path / "prepared")
    monkeypatch.setattr(config, "EXPERIENCE_LOG", tmp_path / "log.jsonl")


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
    """Modelin sırayla vereceği cevapları ayarlar ve modele giden mesajları kaydeder.
    Test bir candidate (adım 7) cevabı sıraya koymadıysa sahte model kendisi cevaplar: candidate agent'ın son submit
    ettiği SQL'i yazar (consensus: high). Bu cevaplar seen'e yazılmaz; candidate'leri deneyen testler cevaplarını
    sıraya koyar."""
    replies, seen = [], []
    last_submit = {}

    def fake_chat(messages, tools=None, seed=None, temperature=None, model=None):
        system = messages[0]["content"]
        head = replies[0]["text"] if replies else ""
        if system == prompts.WRITE_SQL and not head.startswith("```sql"):
            return sql_reply(last_submit.get("sql", "SELECT 1"))
        seen.append(list(messages))
        reply = replies.pop(0)
        for call in reply["tool_calls"]:
            if call["function"]["name"] == "submit":
                last_submit["sql"] = json.loads(call["function"]["arguments"])["sql"]
        return reply

    monkeypatch.setattr(llm, "chat", fake_chat)
    return replies, seen
