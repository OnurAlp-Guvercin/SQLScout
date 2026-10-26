"""Guardrail'ler: harness'ın agent'ı küçük modellerin tipik hatalarından koruyan kuralları (her adım): bozuk çıktının
reddi, aynı çağrının tekrarı (3. tekrarda handoff, agent/loop.py), bağlamın sıkıştırılması. Uzun sonucun kırpılması harness/tools/execute_sql.py'de (trim_rows)."""

import json
import uuid

import config
from agent import llm
from harness.tools import execute_sql, submit

SHORTENED = "[Old result, shortened] "


def read_tool_call(reply, tools):
    """Modelin cevabını tek bir tool call olarak okur. Okunamazsa step["error"] dolu olur: istek reddedilir,
    hata agent'a gider ve budget yine düşer. Birden çok tool call varsa yalnızca ilki alınır."""
    step = {"tool": None, "args": {}, "id": None, "arguments": "", "text": reply["text"], "error": None}
    if not reply["tool_calls"]:
        step["error"] = ("Rejected: your reply was not a tool call. Do not work out the answer in text: call exactly "
                         "one of the tools, e.g. execute_sql to compute it or submit when you have the query.")
        return step

    call = reply["tool_calls"][0]
    step["tool"] = call["function"]["name"]
    step["id"] = call.get("id") or "call_" + uuid.uuid4().hex[:8]
    arguments = call["function"].get("arguments") or "{}"
    step["arguments"] = arguments if isinstance(arguments, str) else json.dumps(arguments)

    schema = None
    for tool in tools:
        if tool["function"]["name"] == step["tool"]:
            schema = tool["function"]["parameters"]
    if schema is None:
        names = ", ".join(tool["function"]["name"] for tool in tools)
        step["arguments"] = "{}"  # bozuk olabilir: konuşmaya konmaz (aşağıdaki nota bakın)
        step["error"] = f"Rejected: there is no tool named '{step['tool']}'. Available tools: {names}."
        return step

    try:
        args = json.loads(step["arguments"])
    except json.JSONDecodeError:
        args = None
    if not isinstance(args, dict):
        # Model sunucusu geçmişteki argument'ları JSON object olarak okur; bozuk hâli konuşmaya konursa sonraki istek hata verir.
        step["arguments"] = "{}"
        step["error"] = f"Rejected: the arguments of '{step['tool']}' are not a valid JSON object."
        return step
    missing = [name for name in schema["required"] if is_empty(args.get(name))]
    if missing:
        step["error"] = f"Rejected: '{step['tool']}' needs a non-empty value for: {', '.join(missing)}."
        return step

    step["args"] = args
    return step


def is_empty(value):
    """Argument metin değilse ya da boşsa (ör. {"sql": 123}) tool onu kullanamaz."""
    return not isinstance(value, str) or not value.strip()


def earlier_calls(step, context):
    """Bu çağrının daha önce yapılmış aynıları. Aynı tool ve aynı argument'lar "aynı çağrı"dır; execute_sql'de ve
    submit'te SQL'in boşlukları önemsenmez. Reddedilen çağrılar hiç tekrar sayılmaz. submit yalnızca önceki submit
    çalışmadığı için geri döndüyse tekrar sayılır: medium note'tan sonra aynı SQL'i yeniden göndermek geçerlidir."""
    if step.get("error"):
        return []
    same = []
    for old in context.steps:
        if old["tool"] != step["tool"] or not old["args"]:
            continue
        if step["tool"] == "submit" and not old["result"].startswith(submit.REJECTED):
            continue
        if step["tool"] in ("execute_sql", "submit"):
            match = execute_sql.sql_key(old["args"]["sql"]) == execute_sql.sql_key(step["args"]["sql"])
        else:
            match = old["args"] == step["args"]
        if match:
            same.append(old)
    return same


def repeat_note(earlier):
    return ("Not run again: you already made this exact call and its result will not change. Try a different query, "
            "or submit your answer. Its result was:\n" + earlier[0]["result"])


def compress(context):
    """Konuşma CONVERSATION_MAX_TOKENS'ı aşarsa en eski observation'lar, sınırın altına inene kadar tek satıra iner.
    Sistem prompt'u ve adım 1'in bağlamı (ilk iki mesaj) kısaltılmaz."""
    for message in context.messages[2:]:
        if conversation_tokens(context.messages) <= config.CONVERSATION_MAX_TOKENS:
            return
        if message["role"] in ("tool", "user") and not message["content"].startswith(SHORTENED):
            message["content"] = shorten(message["content"])


def shorten(observation):
    """Observation'ın ilk iki satırı tek satırda kalır, ör. "Columns: city, n | 120 rows (first 20 shown)"."""
    first_lines = [line.rstrip(":") for line in observation.splitlines()[:2]]
    return SHORTENED + " | ".join(first_lines)[:config.SHOWN_CELL_CHARS]


def conversation_tokens(messages):
    total = 0
    for message in messages:
        total += llm.count_tokens(message["content"] or "")
        for call in message.get("tool_calls", []):
            total += llm.count_tokens(call["function"]["arguments"])
    return total
