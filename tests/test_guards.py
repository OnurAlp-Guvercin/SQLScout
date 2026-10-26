"""harness/guards.py testleri: bozuk çıktının reddi, tekrar, kırpma, sıkıştırma."""

from types import SimpleNamespace

import config
from agent import prompts
from harness import guards
from harness.tools import execute_sql

TOOLS = prompts.TOOLS


def reply_with(name, arguments, text=""):
    return {"text": text, "tool_calls": [{"id": "c1", "function": {"name": name, "arguments": arguments}}]}


def test_valid_call_is_read():
    step = guards.read_tool_call(reply_with("search_values", '{"query": "Boston"}'), TOOLS)
    assert step["error"] is None
    assert step["tool"] == "search_values" and step["args"] == {"query": "Boston"} and step["id"] == "c1"
    assert "needs a non-empty value for: sql" in guards.read_tool_call(reply_with("submit", "{}"), TOOLS)["error"]


def test_sql_block_in_text_is_an_execute_step():
    step = guards.read_tool_call({"text": "Let me count.\n```sql\nSELECT 1\n```", "tool_calls": []}, TOOLS)
    assert step["error"] is None and step["tool"] == "execute_sql" and step["args"] == {"sql": "SELECT 1"}
    assert step["id"] is None
    assert guards.sql_block("```\nSELECT 2\n```") == "SELECT 2"
    assert guards.sql_block("```sql\nSELECT 3") == "SELECT 3"  # kapanmamış blok (cevap kesildi)


def test_plain_text_is_rejected():
    step = guards.read_tool_call({"text": "The answer is 150.", "tool_calls": []}, TOOLS)
    assert step["error"].startswith("Rejected: your reply was not a tool call")
    assert step["id"] is None


def test_unknown_tool_is_rejected():
    step = guards.read_tool_call(reply_with("drop_table", "{}"), TOOLS)
    assert "no tool named 'drop_table'" in step["error"]


def test_broken_json_is_rejected():
    step = guards.read_tool_call(reply_with("search_values", '{"query": "Boston"'), TOOLS)
    assert "not a valid JSON object" in step["error"]
    assert step["arguments"] == "{}"  # bozuk argument'lar konuşma geçmişine girmez


def test_arguments_that_are_not_an_object_are_rejected():
    step = guards.read_tool_call(reply_with("search_values", '["Boston"]'), TOOLS)
    assert "not a valid JSON object" in step["error"]
    assert step["arguments"] == "{}"


def test_missing_argument_is_rejected():
    step = guards.read_tool_call(reply_with("search_values", '{"query": "  "}'), TOOLS)
    assert "needs a non-empty value for: query" in step["error"]
    number = guards.read_tool_call(reply_with("search_values", '{"query": 123}'), TOOLS)
    assert "needs a non-empty value for: query" in number["error"]


def test_only_first_of_many_calls_is_taken():
    reply = {"text": "", "tool_calls": [
        {"id": "a", "function": {"name": "search_values", "arguments": '{"query": "Boston"}'}},
        {"id": "b", "function": {"name": "submit", "arguments": '{"sql": "SELECT 1"}'}},
    ]}
    assert guards.read_tool_call(reply, TOOLS)["args"] == {"query": "Boston"}


def past(*steps):
    return SimpleNamespace(steps=list(steps))


def test_repeat_rules():
    old = {"tool": "execute_sql", "args": {"sql": "SELECT 1"}, "result": "Columns: 1"}
    same_sql = {"tool": "execute_sql", "args": {"sql": " SELECT   1 "}}
    earlier = guards.earlier_calls(same_sql, past(old))
    assert earlier == [old]
    assert guards.repeat_note(earlier).endswith("Its result was:\nColumns: 1")
    other_sql = {"tool": "execute_sql", "args": {"sql": "SELECT 2"}}
    assert guards.earlier_calls(other_sql, past(old)) == []
    search = {"tool": "search_values", "args": {"query": "Boston"}, "result": "..."}
    assert guards.earlier_calls(dict(search), past(search, search)) == [search, search]  # tekrarlar sayılır
    submit = {"tool": "submit", "args": {"sql": "SELECT 1"}, "result": "Final check failed: ..."}
    assert guards.earlier_calls(dict(submit), past(submit)) == []  # submit hiç tekrar sayılmaz (final check sınırlar)
    rejected = {"tool": "execute_sql", "args": {}, "result": "Rejected: ..."}  # reddedilen çağrının argument'ı yok
    assert guards.earlier_calls(other_sql, past(rejected)) == []
    broken = {"tool": "execute_sql", "args": {}, "error": "Rejected: ..."}  # ör. bozuk JSON, önceden çalışmış SQL var
    assert guards.earlier_calls(broken, past(old)) == []


def test_long_rows_and_cells_are_trimmed():
    rows = [(i, "x" * 150, None) for i in range(25)]
    trimmed = execute_sql.trim_rows(rows)
    assert len(trimmed) == config.SHOWN_ROWS
    assert trimmed[0] == ["0", "x" * config.SHOWN_CELL_CHARS + "...", "NULL"]


def test_oldest_observations_are_shortened_first(monkeypatch):
    observation = "Columns: id\n150 rows (first 20 shown):\n" + "\n".join(str(i) for i in range(20))
    messages = [{"role": "system", "content": "system"}, {"role": "user", "content": "context " * 50}]
    for _ in range(3):
        messages.append({"role": "assistant", "content": "", "tool_calls": [
            {"id": "c", "type": "function", "function": {"name": "execute_sql", "arguments": "{}"}}]})
        messages.append({"role": "tool", "tool_call_id": "c", "content": observation})
    context = SimpleNamespace(messages=messages)
    total = guards.conversation_tokens(messages)
    monkeypatch.setattr(config, "CONVERSATION_MAX_TOKENS", total - 1)
    guards.compress(context)
    assert messages[3]["content"] == "[Old result, shortened] Columns: id | 150 rows (first 20 shown)"
    assert messages[5]["content"] == observation  # sınırın altına inince durdu
    assert messages[1]["content"] == "context " * 50  # adım 1'in bağlamı kısaltılmaz
