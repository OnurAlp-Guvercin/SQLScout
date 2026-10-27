"""Guardrail'ler: harness'ın agent'ı küçük modellerin tipik hatalarından koruyan kuralları (her adım): bozuk çıktının
reddi, SQL argument'ının temizlenmesi, aynı çağrının tekrarı (3. tekrarda handoff, agent/loop.py), bağlamın
sıkıştırılması. Uzun sonucun kırpılması harness/tools/execute_sql.py'de (trim_rows)."""

import json
import re
import uuid

import config
from agent import llm
from harness.tools import execute_sql

SHORTENED = "[Old result, shortened] "
CODE_FENCE = re.compile(r"^(?:```(?:sqlite|sql)?)?\s*(.*?)\s*(?:```.*)?$", re.DOTALL | re.IGNORECASE)
LEADING_COMMENTS = re.compile(r"^(?:\s*(?:--[^\n]*|/\*.*?\*/))*", re.DOTALL)


def read_tool_call(reply, tools):
    """Modelin cevabını tek bir tool call olarak okur. Okunamazsa step["error"] dolu olur: istek reddedilir, hata agent'a
    gider ve budget yine düşer. Birden çok tool call varsa yalnızca ilki alınır. SQL argument'ı temizlenir (clean_sql).
    Model sunucusu biçimi bozuk tool call'u sessizce atar; o zaman da cevap "tool call yok" görünür."""
    step = {"tool": None, "args": {}, "id": None, "arguments": "", "text": reply["text"], "error": None}
    if not reply["tool_calls"]:
        step["error"] = ("Rejected: no valid tool call was found in your reply. Call exactly one of the tools, in the "
                         "tool-call format.")
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
    if isinstance(args.get("sql"), str):
        args["sql"] = clean_sql(args["sql"])
    missing = [name for name in schema["required"] if is_empty(args.get(name))]
    if missing:
        step["error"] = f"Rejected: '{step['tool']}' needs a non-empty value for: {', '.join(missing)}."
        return step

    step["args"] = args
    return step


def extract_sql(text):
    """Modelin cevabındaki ilk ``` bloğunun içi (kapanmamışsa metnin sonuna kadar); blok yoksa cevabın tamamı. Temizlik
    agent'ınkiyle aynıdır (clean_sql). Base (baseline.py) ve teacher'ın ilk denemesi (agent/loop.py) kullanır."""
    start = text.find("```")
    return clean_sql(text[start:] if start >= 0 else text)


def clean_sql(sql):
    """SQL'in etrafındaki ```sql ... ``` işaretlerini (kapanıştan sonraki açıklama metniyle birlikte) ve baştaki --
    ya da /* */ yorumlarını atar. Küçük modeller bunları sık ekler; atılmazsa okuma sorgusu "SELECT ile başlamıyor" diye
    reddedilir. Ör. "```sql\nSELECT 1\n```" → "SELECT 1". Base de (baseline.py) modelin SQL'ini bununla temizler."""
    text = CODE_FENCE.match(sql.strip()).group(1)
    return LEADING_COMMENTS.sub("", text, count=1).strip()


def is_empty(value):
    """Argument metin değilse ya da boşsa (ör. {"sql": 123}) tool onu kullanamaz."""
    return not isinstance(value, str) or not value.strip()


def earlier_calls(step, context):
    """Bu çağrının, çağıranın (agent ya da teacher) kendi yaptığı aynıları: teacher agent'ın konuşmasını görmediği için
    onun çağrıları teacher'a tekrar sayılmaz. Aynı tool ve aynı argument'lar "aynı çağrı"dır; execute_sql'de SQL'in
    boşlukları önemsenmez. submit ve reddedilen çağrılar hiç tekrar sayılmaz (submit'i final check sınırlar)."""
    if step.get("error") or step["tool"] == "submit":
        return []
    same = []
    by = "teacher" if context.teacher else "agent"
    for old in context.steps:
        if old["by"] != by or old["tool"] != step["tool"] or not old["args"]:
            continue
        if step["tool"] == "execute_sql":
            match = execute_sql.sql_key(old["args"]["sql"]) == execute_sql.sql_key(step["args"]["sql"])
        else:
            match = old["args"] == step["args"]
        if match:
            same.append(old)
    return same


def repeat_note(earlier):
    return ("Not run again: this exact call was already made and its result will not change. Try a different query, "
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
