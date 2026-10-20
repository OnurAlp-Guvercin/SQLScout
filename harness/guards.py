"""Guardrail'ler: harness'ın agent'ı küçük modellerin tipik hatalarından koruyan kuralları (her adım).
Bozuk çıktının reddi (aşama 6), aynı çağrının tekrarı (aşama 9), uzun sonucun kırpılması (aşama 10),
bağlamın sıkıştırılması (aşama 11)."""

import json
import uuid

import config
from agent import llm
from harness import compare, precheck

SHORTENED = "[Old result, shortened] "


def read_tool_call(reply, tools):
    """Modelin cevabını tek bir tool call olarak okur. Okunamazsa step["error"] dolu olur: istek reddedilir,
    hata agent'a döner ve budget yine düşer. Birden çok tool call varsa yalnızca ilki alınır."""
    step = {"tool": None, "args": {}, "id": None, "arguments": "", "text": reply["text"], "error": None}
    if not reply["tool_calls"]:
        step["error"] = "Rejected: your reply was not a tool call. Call exactly one of the tools."
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
        step["error"] = f"Rejected: there is no tool named '{step['tool']}'. Available tools: {names}."
        return step

    try:
        args = json.loads(step["arguments"])
    except json.JSONDecodeError:
        args = None
    if not isinstance(args, dict):
        # Model sunucusu geçmişteki argümanları JSON nesnesi olarak okur; bozuk hâli konuşmaya konursa sonraki istek hata verir.
        step["arguments"] = "{}"
        step["error"] = f"Rejected: the arguments of '{step['tool']}' are not a valid JSON object."
        return step
    if isinstance(args.get("forecast"), str):  # küçük modeller iç içe nesneyi bazen metin olarak yazar
        try:
            args["forecast"] = json.loads(args["forecast"])
        except json.JSONDecodeError:
            pass
    missing = [name for name in schema["required"] if is_empty(args.get(name))]
    if missing:
        step["error"] = f"Rejected: '{step['tool']}' needs a non-empty value for: {', '.join(missing)}."
        return step
    if "forecast" in schema["required"]:
        problem = compare.forecast_error(args["forecast"])
        if problem:
            step["error"] = f"Rejected: the forecast is not valid: {problem}."
            return step

    step["args"] = args
    return step


def is_empty(value):
    return value is None or (isinstance(value, str) and not value.strip())


def is_repeat(step, context):
    return previous_result(step, context) is not None


def repeat_note(step, context):
    return "Not run again: you already made this exact call. Its result was:\n" + previous_result(step, context)


def previous_result(step, context):
    """Aynı çağrı daha önce yapıldıysa onun sonucu, yoksa None. Aynı tool ve aynı argümanlar "aynı çağrı"dır;
    execute_sql'de yalnızca SQL'e bakılır (forecast farklı olsa da tekrar). submit hiç tekrar sayılmaz."""
    if step["tool"] == "submit":
        return None
    for old in context.steps:
        if old["tool"] != step["tool"] or not old["args"]:
            continue
        if step["tool"] == "execute_sql":
            same = precheck.sql_key(old["args"]["sql"]) == precheck.sql_key(step["args"]["sql"])
        else:
            same = old["args"] == step["args"]
        if same:
            return old["result"]
    return None


def format_result(result):
    """Gerçek sonucu agent'ın okuyacağı metne çevirir: sütunlar, satır sayısı ve kırpılmış satırlar ya da hata."""
    if not result["ok"]:
        return f"Error: {result['error']}"
    lines = [f"Columns: {', '.join(result['columns'])}"]
    if result["row_count"] == 0:
        lines.append("No rows: the result is empty.")
        return "\n".join(lines)
    rows = trim_rows(result["rows"])
    if len(rows) < result["row_count"]:
        lines.append(f"{result['row_count']} rows (first {len(rows)} shown):")
    else:
        lines.append(f"{result['row_count']} rows:")
    for row in rows:
        lines.append(" | ".join(row))
    return "\n".join(lines)


def trim_rows(rows):
    """Agent en fazla SHOWN_ROWS satır görür; uzun hücreler SHOWN_CELL_CHARS karakterde kesilir."""
    trimmed = []
    for row in rows[:config.SHOWN_ROWS]:
        cells = []
        for value in row:
            text = "NULL" if value is None else str(value)
            if len(text) > config.SHOWN_CELL_CHARS:
                text = text[:config.SHOWN_CELL_CHARS] + "..."
            cells.append(text)
        trimmed.append(cells)
    return trimmed


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
