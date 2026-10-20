"""Testlerde modelin yerine verilen sahte cevaplar. Sırayı conftest.py'deki fake_model fixture'ı yönetir."""

import json


def text_reply(text):
    return {"text": text, "tool_calls": [], "prompt_tokens": 100, "completion_tokens": 5, "cost": 0.001}


ONE_ROW = {"type": "rows", "columns": ["n"], "rows": "1", "trust": True}
EMPTY = {"type": "empty", "trust": False}


def call_reply(tool, args):
    call = {"id": "call_1", "function": {"name": tool, "arguments": json.dumps(args)}}
    return {"text": "", "tool_calls": [call], "prompt_tokens": 100, "completion_tokens": 5, "cost": 0.001}


def execute_reply(sql, forecast=ONE_ROW):
    return call_reply("execute_sql", {"sql": sql, "forecast": forecast})


def submit_reply(sql):
    return call_reply("submit", {"sql": sql})


def sql_reply(sql):
    """Candidate'in cevabı: tool'suz, ```sql bloğunda tek SQL."""
    return text_reply(f"```sql\n{sql}\n```")


def json_reply(data):
    """World model'in cevabı: tool'suz bir JSON metni."""
    return text_reply(json.dumps(data))
