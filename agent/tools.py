"""Agent'a sunulan tool'ların tanımları (Qwen'in tool-call biçimi) ve hangi tool'un ne zaman sunulduğu.
Tool'lar KOD_YAPISI.md "Tool'lar" tablosunda."""

import config

SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_schema",
        "description": "Find the tables and columns whose names or descriptions contain the given words.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "A few words, e.g. 'phone number'."}},
            "required": ["query"],
        },
    },
}

SEARCH_VALUES = {
    "type": "function",
    "function": {
        "name": "search_values",
        "description": "Find database values that contain the given text or are spelled like it, with their "
                       "table and column, e.g. 'Los Angles' finds city = 'Los Angeles'.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "The text to look for."}},
            "required": ["query"],
        },
    },
}

EXECUTE_SQL_DESCRIPTION = ("Run a read-only SQLite query on the database and see its result: the columns, "
                           "the number of rows and the first rows, or the error message.")
SQL_PARAMETER = {"type": "string", "description": "The SQLite query to run."}

# USE_AGENT_FORECAST kapalıyken
EXECUTE_SQL = {
    "type": "function",
    "function": {
        "name": "execute_sql",
        "description": EXECUTE_SQL_DESCRIPTION,
        "parameters": {"type": "object", "properties": {"sql": SQL_PARAMETER}, "required": ["sql"]},
    },
}

# USE_AGENT_FORECAST açıkken (adım 4): agent sonucu çalıştırmadan önce tahmin eder.
FORECAST_PARAMETER = {
    "type": "object",
    "description": "Before the query runs, your forecast of its result. type: 'error', 'empty' or 'rows'. "
                   "If type is 'rows', also give columns (the column names you expect) and rows (the expected "
                   "number of rows). trust: true if you are confident, false if you are unsure.",
    "properties": {
        "type": {"type": "string", "enum": ["error", "empty", "rows"]},
        "columns": {"type": "array", "items": {"type": "string"}},
        "rows": {"type": "string", "enum": config.ROW_RANGES},
        "trust": {"type": "boolean"},
    },
    "required": ["type", "trust"],
}

EXECUTE_SQL_WITH_FORECAST = {
    "type": "function",
    "function": {
        "name": "execute_sql",
        "description": EXECUTE_SQL_DESCRIPTION,
        "parameters": {
            "type": "object",
            "properties": {"sql": SQL_PARAMETER, "forecast": FORECAST_PARAMETER},
            "required": ["sql", "forecast"],
        },
    },
}

SUBMIT = {
    "type": "function",
    "function": {
        "name": "submit",
        "description": "Submit the final SQLite query that answers the question. This ends the task.",
        "parameters": {
            "type": "object",
            "properties": {"sql": {"type": "string", "description": "The final SQLite query."}},
            "required": ["sql"],
        },
    },
}

ASK_USER = {
    "type": "function",
    "function": {
        "name": "ask_user",
        "description": "Ask the user one short clarification question. Use it only when the question is ambiguous "
                       "and the schema, values and evidence cannot resolve it.",
        "parameters": {
            "type": "object",
            "properties": {"question": {"type": "string", "description": "The clarification question."}},
            "required": ["question"],
        },
    },
}

HANDOFF = {
    "type": "function",
    "function": {
        "name": "handoff",
        "description": "Hand the question over to a stronger model when you are stuck. This ends your turn.",
        "parameters": {
            "type": "object",
            "properties": {"reason": {"type": "string", "description": "Why you are stuck, in a few words."}},
            "required": ["reason"],
        },
    },
}


def offered(teacher):
    """Agent'a ve teacher'a sunulan tool'lar. Teacher'a handoff sunulmaz; flag'i kapalı parçanın tool'u sunulmaz."""
    execute_sql = EXECUTE_SQL_WITH_FORECAST if config.USE_AGENT_FORECAST else EXECUTE_SQL
    tools = [SEARCH_SCHEMA, SEARCH_VALUES, execute_sql, SUBMIT]
    if config.USE_ASK_USER:
        tools.append(ASK_USER)
    if config.USE_HANDOFF and not teacher:
        tools.append(HANDOFF)
    return tools
