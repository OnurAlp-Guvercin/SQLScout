"""harness/guards.py testleri: bozuk çıktının reddi (aşama 6), tekrar (9), kırpma (10), sıkıştırma (11), forecast (15)."""

from types import SimpleNamespace

import config
from agent import tools
from harness import guards

TOOLS = [tools.SUBMIT]


def reply_with(name, arguments, text=""):
    return {"text": text, "tool_calls": [{"id": "c1", "function": {"name": name, "arguments": arguments}}]}


def test_valid_submit_is_read():
    step = guards.read_tool_call(reply_with("submit", '{"sql": "SELECT 1"}'), TOOLS)
    assert step["error"] is None
    assert step["tool"] == "submit"
    assert step["args"] == {"sql": "SELECT 1"}
    assert step["id"] == "c1"


def test_plain_text_is_rejected():
    step = guards.read_tool_call({"text": "SELECT 1", "tool_calls": []}, TOOLS)
    assert step["error"].startswith("Rejected: your reply was not a tool call")
    assert step["id"] is None


def test_unknown_tool_is_rejected():
    step = guards.read_tool_call(reply_with("drop_table", "{}"), TOOLS)
    assert "no tool named 'drop_table'" in step["error"]


def test_broken_json_is_rejected():
    step = guards.read_tool_call(reply_with("submit", '{"sql": "SELECT 1"'), TOOLS)
    assert "not a valid JSON object" in step["error"]
    assert step["arguments"] == "{}"  # bozuk argümanlar konuşma geçmişine girmez


def test_arguments_that_are_not_an_object_are_rejected():
    step = guards.read_tool_call(reply_with("submit", '["SELECT 1"]'), TOOLS)
    assert "not a valid JSON object" in step["error"]
    assert step["arguments"] == "{}"


def test_missing_argument_is_rejected():
    step = guards.read_tool_call(reply_with("submit", '{"sql": "  "}'), TOOLS)
    assert "needs a non-empty value for: sql" in step["error"]


def test_only_first_of_many_calls_is_taken():
    reply = {"text": "", "tool_calls": [
        {"id": "a", "function": {"name": "submit", "arguments": '{"sql": "SELECT 1"}'}},
        {"id": "b", "function": {"name": "submit", "arguments": '{"sql": "SELECT 2"}'}},
    ]}
    assert guards.read_tool_call(reply, TOOLS)["args"] == {"sql": "SELECT 1"}


def test_forecast_written_as_text_is_read():
    arguments = '{"sql": "SELECT 1", "forecast": "{\\"type\\": \\"empty\\", \\"trust\\": true}"}'
    step = guards.read_tool_call(reply_with("execute_sql", arguments), [tools.EXECUTE_SQL_WITH_FORECAST])
    assert step["error"] is None
    assert step["args"]["forecast"] == {"type": "empty", "trust": True}


def test_bad_forecast_names_the_wrong_fields():
    arguments = '{"sql": "SELECT 1", "forecast": {"type": "rows", "rows": "5", "trust": "yes"}}'
    step = guards.read_tool_call(reply_with("execute_sql", arguments), [tools.EXECUTE_SQL_WITH_FORECAST])
    assert step["error"].startswith("Rejected: the forecast is not valid: columns must be")
    assert "rows must be one of: 0, 1, 2-10, 11-100, 100+" in step["error"]
    assert "trust must be true or false" in step["error"]


def past(*steps):
    return SimpleNamespace(steps=list(steps))


def test_repeat_rules():
    old = {"tool": "execute_sql", "args": {"sql": "SELECT 1", "forecast": {}}, "result": "Columns: 1"}
    same_sql = {"tool": "execute_sql", "args": {"sql": " SELECT   1 ", "forecast": {"type": "error"}}}
    assert guards.is_repeat(same_sql, past(old))
    assert guards.repeat_note(same_sql, past(old)).endswith("Its result was:\nColumns: 1")
    other_sql = {"tool": "execute_sql", "args": {"sql": "SELECT 2"}}
    assert not guards.is_repeat(other_sql, past(old))
    search = {"tool": "search_values", "args": {"query": "Boston"}, "result": "..."}
    assert guards.is_repeat(dict(search), past(search))
    submit = {"tool": "submit", "args": {"sql": "SELECT 1"}, "result": "Submitted."}
    assert not guards.is_repeat(dict(submit), past(submit))  # submit hiç tekrar sayılmaz
    rejected = {"tool": "execute_sql", "args": {}, "result": "Rejected: ..."}  # reddedilen çağrının argümanı yok
    assert not guards.is_repeat(other_sql, past(rejected))


def test_long_rows_and_cells_are_trimmed():
    rows = [(i, "x" * 150, None) for i in range(25)]
    trimmed = guards.trim_rows(rows)
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
