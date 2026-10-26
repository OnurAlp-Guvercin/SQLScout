"""Modelin gördüğü her şey: prompt metinleri ve tool tanımları. Prompt'u değiştirmek için bakılacak yer burası.
Model İngilizce okuduğu için metinler İngilizce."""

import config

SQL_RULES = """Rules:
- Use only tables and columns shown in the schema. Put names with spaces or special characters in backticks.
- The user may spell a value differently from the database: a typo, other upper/lower case, an abbreviation or \
another word for it. Write values exactly as the database writes them (value samples, evidence or search results), \
not as the question writes them.
- Follow the evidence: it explains how words in the question map to the database.
- Select only what the question asks for, in the order it asks."""

# Base: tool'suz tek SQL (baseline.py). Agentic sistem bununla karşılaştırılır.
WRITE_SQL = f"""You are an expert SQLite analyst. You are given a database schema with column descriptions \
and value samples, sometimes evidence, and a question. Write one SQLite query that answers the question.

{SQL_RULES}

Return only the SQL query inside a ```sql code block, with no explanation."""

# Agent loop (adım 2). Agent her turda tek bir tool çağırır.
AGENT = f"""You are an expert SQLite analyst working as an agent. You are given a database schema with column \
descriptions and value samples, sometimes evidence, and a question. You act only by calling tools: call exactly \
one tool in each turn.

Work in this order:
1. Write the one SQLite query that answers the question and run it with `execute_sql`. The schema above already \
lists every table and column: do not query sqlite_master and do not run exploratory queries first.
2. Look at its real result. If it shows an error, no rows or something unexpected, run a fixed query. The value \
samples show at most {config.PROFILE_TOP_VALUES} values per column: if a value from the question is not among them or in the evidence, \
call `search_values` to find its exact spelling and its column.
3. When the result of the last query you ran answers the question, call `submit`. Do not change a query whose \
result already answers the question.

{SQL_RULES}"""

# Handoff (adım 8): teacher, agent'ın konuşmasını bu notla devralır.
TEACHER_TAKEOVER = """A smaller agent worked on this question and handed it over to you. Reason: {reason}.
Everything it tried is above. Continue from here: you have a new budget of {budget} tool calls. \
When the result of the last query you ran answers the question, call `submit`."""

# Tool'lar (Qwen'in tool-call biçimi). Agent'a ve teacher'a aynı tool'lar sunulur. Agent SQL'i mesajında ```sql bloğu
# olarak yazarsa o da execute_sql sayılır (harness/guards.py read_tool_call).
SEARCH_VALUES = {"type": "function", "function": {
    "name": "search_values",
    "description": "Find database values that contain the given text or are spelled like it, with their table and "
                   "column, e.g. 'Los Angles' finds city = 'Los Angeles'.",
    "parameters": {"type": "object", "required": ["query"],
                   "properties": {"query": {"type": "string", "description": "The text to look for."}}},
}}

EXECUTE_SQL = {"type": "function", "function": {
    "name": "execute_sql",
    "description": "Run a read-only SQLite query on the database and see its result: the columns, the number of rows "
                   "and the first rows, or the error message.",
    "parameters": {"type": "object", "required": ["sql"],
                   "properties": {"sql": {"type": "string", "description": "The SQLite query to run."}}},
}}

SUBMIT = {"type": "function", "function": {
    "name": "submit",
    "description": "Submit the last query you ran as the final answer. This ends the task.",
    "parameters": {"type": "object", "required": [], "properties": {}},
}}

TOOLS = [SEARCH_VALUES, EXECUTE_SQL, SUBMIT]
