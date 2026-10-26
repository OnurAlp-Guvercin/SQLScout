"""Testlerde modelin yerine verilen sahte cevaplar. Sırayı conftest.py'deki fake_model fixture'ı yönetir."""

import json


def text_reply(text):
    return {"text": text, "tool_calls": [], "prompt_tokens": 100, "completion_tokens": 5, "cost": 0.001}


def call_reply(tool, args):
    call = {"id": "call_1", "function": {"name": tool, "arguments": json.dumps(args)}}
    return {"text": "", "tool_calls": [call], "prompt_tokens": 100, "completion_tokens": 5, "cost": 0.001}


def execute_reply(sql):
    return call_reply("execute_sql", {"sql": sql})


def submit_reply(sql):
    return call_reply("submit", {"sql": sql})


def observation(message):
    """Modele giden mesajın içeriği, harness'ın sona eklediği kalan budget notu olmadan."""
    text = message["content"]
    return text.rsplit("\n[", 1)[0] if "tool call(s) left." in text[-120:] else text
