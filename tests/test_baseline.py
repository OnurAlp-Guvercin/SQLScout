"""baseline.py testleri: tool'suz tek SQL. API'ye istek gitmez."""

import baseline
from agent import llm, prompts


def test_extract_sql_from_blocks_and_plain_text():
    assert baseline.extract_sql("Here it is:\n```sql\nSELECT name\nFROM users;\n```\nDone.") == "SELECT name\nFROM users;"
    assert baseline.extract_sql("```\nSELECT 1\n```") == "SELECT 1"
    assert baseline.extract_sql("```sql\nSELECT 1") == "SELECT 1"  # kapanmamış blok (cevap kesildi)
    assert baseline.extract_sql("```sqlite\nSELECT 1\n```") == "SELECT 1"
    assert baseline.extract_sql("  SELECT 1  ") == "SELECT 1"


def test_answer_writes_one_sql_and_scores_it(db, monkeypatch):
    sent = {}

    def fake_chat(messages, temperature=None, model=None):
        sent.update(messages=messages, temperature=temperature)
        return {"text": "```sql\nSELECT COUNT(*) FROM items\n```", "prompt_tokens": 10, "completion_tokens": 5,
                "cost": None}

    monkeypatch.setattr(llm, "chat", fake_chat)
    question = {"question_id": 1, "db_id": "shop", "db_path": db, "question": "How many items?", "evidence": "",
                "SQL": "SELECT COUNT(id) FROM items"}
    row = baseline.answer(question, "model")
    assert row["sql"] == "SELECT COUNT(*) FROM items" and row["correct"] is True and row["cost"] == 0
    assert sent["messages"][0] == {"role": "system", "content": prompts.WRITE_SQL}
    assert sent["messages"][1]["content"].endswith("Question: How many items?")
    assert sent["temperature"] == 0


def test_api_error_is_recorded_and_the_run_goes_on(db, monkeypatch):
    def failing_chat(messages, temperature=None, model=None):
        raise RuntimeError("Model API hatası 429: engine_overloaded")

    monkeypatch.setattr(llm, "chat", failing_chat)
    question = {"question_id": 1, "db_id": "shop", "db_path": db, "question": "How many items?", "evidence": "",
                "SQL": "SELECT COUNT(id) FROM items"}
    row = baseline.answer(question, "model")
    assert row["sql"] is None and row["correct"] is False and row["error"].startswith("Model API hatası 429")
