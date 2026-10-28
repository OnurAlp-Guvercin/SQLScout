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


def test_plain_text_is_rejected():
    step = guards.read_tool_call({"text": "The answer is 150.", "tool_calls": []}, TOOLS)
    assert step["error"].startswith("Rejected: no valid tool call was found")
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


def past(*steps, large_model=False):
    return SimpleNamespace(steps=list(steps), large_model=large_model)


def test_repeat_rules():
    old = {"tool": "execute_sql", "args": {"sql": "SELECT 1"}, "result": "Columns: 1", "by": "small_model"}
    same_sql = {"tool": "execute_sql", "args": {"sql": " SELECT   1 "}}
    earlier = guards.earlier_calls(same_sql, past(old))
    assert earlier == [old]
    assert guards.repeat_note(earlier).endswith("Its result was:\nColumns: 1")
    other_sql = {"tool": "execute_sql", "args": {"sql": "SELECT 2"}}
    assert guards.earlier_calls(other_sql, past(old)) == []
    assert guards.earlier_calls(same_sql, past(old, large_model=True)) == []  # large model'e small model'in çağrısı tekrar sayılmaz
    search = {"tool": "search_values", "args": {"query": "Boston"}, "result": "...", "by": "small_model"}
    assert guards.earlier_calls(dict(search), past(search, search)) == [search, search]  # tekrarlar sayılır
    submit = {"tool": "submit", "args": {"sql": "SELECT 1"}, "result": "Final check failed: ...", "by": "small_model"}
    assert guards.earlier_calls(dict(submit), past(submit)) == []  # submit hiç tekrar sayılmaz (final check sınırlar)
    rejected = {"tool": "execute_sql", "args": {}, "result": "Rejected: ...", "by": "small_model"}  # reddedilen çağrının argument'ı yok
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
    total = guards.conversation_tokens(messages)
    monkeypatch.setattr(config, "CONVERSATION_MAX_TOKENS", total - 1)
    sent = guards.compress(messages)
    assert sent[3]["content"] == "[Old result, shortened] Columns: id | 150 rows (first 20 shown)"
    assert sent[5]["content"] == observation  # sınırın altına inince durdu
    assert sent[1]["content"] == "context " * 50  # adım 1'in bağlamı kısaltılmaz
    assert messages[3]["content"] == observation  # konuşmanın kendisi (experience log) tam kalır


def test_code_fences_and_comments_are_removed_from_sql():
    step = guards.read_tool_call(reply_with("execute_sql", '{"sql": "```sql\\n-- count them\\nSELECT 1\\n```"}'), TOOLS)
    assert step["error"] is None and step["args"]["sql"] == "SELECT 1"
    assert guards.clean_sql("```sqlite\nSELECT 1") == "SELECT 1"  # kapanmamış blok
    assert guards.clean_sql("SELECT 1\n```") == "SELECT 1"  # yalnızca kapanış işareti
    assert guards.clean_sql("SELECT 1 -- son yorum kalır") == "SELECT 1 -- son yorum kalır"
    empty = guards.read_tool_call(reply_with("submit", '{"sql": "```sql\\n```"}'), TOOLS)
    assert empty["error"].startswith("Rejected: 'submit' needs a non-empty value")


def test_block_comments_and_text_after_the_fence_are_removed():
    assert guards.clean_sql("/* count items */\nSELECT COUNT(*) FROM items") == "SELECT COUNT(*) FROM items"
    assert guards.clean_sql("```sql\nSELECT 1\n```\nThis counts rows.") == "SELECT 1"


def test_arguments_that_cannot_be_encoded_are_rejected():
    step = guards.read_tool_call(reply_with("execute_sql", '{"sql": "SELECT \'\\ud800\'"}'), TOOLS)
    assert step["error"] == "Rejected: the arguments of 'execute_sql' are not a valid JSON object."
