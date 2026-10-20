"""agent/policy.py testleri (aşama 5). Model yerine sahte bir cevap kullanılır; API'ye istek gitmez."""

from agent import llm, policy, prompts


def test_extract_sql_from_sql_block():
    text = "Here it is:\n```sql\nSELECT name\nFROM users;\n```\nDone."
    assert policy.extract_sql(text) == "SELECT name\nFROM users;"


def test_extract_sql_from_plain_block():
    assert policy.extract_sql("```\nSELECT 1\n```") == "SELECT 1"


def test_extract_sql_without_block():
    assert policy.extract_sql("  SELECT 1  ") == "SELECT 1"


def test_write_sql_sends_system_prompt_and_context(monkeypatch):
    sent = {}

    def fake_chat(messages, temperature=None, seed=None):
        sent["messages"] = messages
        sent["seed"] = seed
        return {"text": "```sql\nSELECT 1\n```", "prompt_tokens": 10, "completion_tokens": 5}

    monkeypatch.setattr(llm, "chat", fake_chat)
    reply = policy.write_sql("Database schema ... Question: how many?", seed=3)
    assert reply["sql"] == "SELECT 1"
    assert sent["messages"][0] == {"role": "system", "content": prompts.WRITE_SQL}
    assert sent["messages"][1] == {"role": "user", "content": "Database schema ... Question: how many?"}
    assert sent["seed"] == 3
