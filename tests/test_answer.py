"""harness/answer.py testleri (adım 7–9): candidate yazımı, gruplama, seçim ve confidence gate. Model yerine sahte
bir cevap kullanılır; API'ye istek gitmez."""

from agent import llm, prompts
from harness import answer


def result(key):
    return {"ok": True, "result_key": key, "columns": ["n"], "rows": [(key,)], "row_count": 1}


def test_grouping_ties_and_errors():
    sqls = ["agent", "b1", "c1", "b2", "c2", "broken"]
    results = [result("a"), result("b"), result("c"), result("b"), result("c"), None]
    groups = answer.group(sqls, results)
    assert [group["sqls"] for group in groups] == [["b1", "b2"], ["c1", "c2"], ["agent"]]  # hata veren grupsuz
    tie = answer.group(["agent", "b1"], [result("a"), result("b")])
    assert tie[0]["sqls"] == ["agent"]  # başa başta agent'ın grubu


def test_confidence_levels():
    def groups_of(size):
        return [{"sqls": ["x"] * size}]
    assert answer.confidence(groups_of(3), 3) == "high"
    assert answer.confidence(groups_of(6), 8) == "high"
    assert answer.confidence(groups_of(5), 8) == "medium"
    assert answer.confidence(groups_of(4), 8) == "medium"
    assert answer.confidence(groups_of(3), 8) == "low"
    assert answer.confidence([], 8) == "low"  # hepsi hata verdi


def test_extract_sql_from_sql_block():
    text = "Here it is:\n```sql\nSELECT name\nFROM users;\n```\nDone."
    assert answer.extract_sql(text) == "SELECT name\nFROM users;"


def test_extract_sql_from_plain_block():
    assert answer.extract_sql("```\nSELECT 1\n```") == "SELECT 1"


def test_extract_sql_without_block():
    assert answer.extract_sql("  SELECT 1  ") == "SELECT 1"


def test_write_sql_sends_system_prompt_and_context(monkeypatch):
    sent = {}

    def fake_chat(messages, temperature=None, seed=None):
        sent["messages"] = messages
        sent["seed"] = seed
        return {"text": "```sql\nSELECT 1\n```", "prompt_tokens": 10, "completion_tokens": 5}

    monkeypatch.setattr(llm, "chat", fake_chat)
    reply = answer.write_sql("Database schema ... Question: how many?", seed=3)
    assert reply["sql"] == "SELECT 1"
    assert sent["messages"][0] == {"role": "system", "content": prompts.WRITE_SQL}
    assert sent["messages"][1] == {"role": "user", "content": "Database schema ... Question: how many?"}
    assert sent["seed"] == 3
