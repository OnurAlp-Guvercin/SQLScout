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

# Tool'suz tek SQL: adım 7'de candidate'ler bununla yazılır.
WRITE_SQL = f"""You are an expert SQLite analyst. You are given a database schema with column descriptions \
and value samples, sometimes evidence, and a question. Write one SQLite query that answers the question.

{SQL_RULES}

Return only the SQL query inside a ```sql code block, with no explanation."""

# Agent loop (adım 2). Agent her turda tek bir tool çağırır.
AGENT = f"""You are an expert SQLite analyst working as an agent. You are given a database schema with column \
descriptions and value samples, sometimes evidence, and a question. You act only by calling tools: call exactly \
one tool in each turn. The value samples show at most {config.PROFILE_TOP_VALUES} values per column: if a value from the question is not \
among them or in the evidence, call `search_values` before you use it, to find its exact spelling and its column. \
Use `execute_sql` to run a query and see its real result. Check that the result answers the question; if it shows \
an error, no rows or something unexpected, fix the query and try again. When you know the SQL query that answers the question, call `submit` with it.

{SQL_RULES}"""

# Schema linking (adım 1): bağlam sınırı aşınca model soruya gereken tabloları seçer (harness/prepare.py select_tables).
SELECT_TABLES = """You are an expert SQLite analyst. You are given part of a database schema and a question. List \
the tables needed to write the SQL query that answers the question, including tables needed only to join others. \
Return only a JSON list of table names, like ["orders", "customers"], or [] if no table here is needed."""

# Handoff (adım 10): teacher, agent'ın konuşmasını bu notla devralır.
TEACHER_TAKEOVER = """A smaller agent worked on this question and handed it over to you. Reason: {reason}.
Everything it tried is above. Continue from here: you have a new budget of {budget} tool calls. \
When you know the SQL query that answers the question, call `submit` with it."""

# Tool'lar (Qwen'in tool-call biçimi). Agent'a ve teacher'a aynı tool'lar sunulur.
SEARCH_VALUES = {"type": "function", "function": {
    "name": "search_values",
    "description": "Find database values that contain the given text or are spelled like it, with their table and "
                   "column, e.g. 'Los Angles' finds city = 'Los Angeles'.",
    "parameters": {"type": "object", "required": ["query"],
                   "properties": {"query": {"type": "string", "description": "The text to look for."}}},
}}

ASK_USER = {"type": "function", "function": {
    "name": "ask_user",
    "description": "Ask the user one short clarification question. Use it only when the question is ambiguous and "
                   "the schema, values and evidence cannot resolve it.",
    "parameters": {"type": "object", "required": ["question"],
                   "properties": {"question": {"type": "string", "description": "The clarification question."}}},
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
    "description": "Submit the final SQLite query that answers the question. This ends the task.",
    "parameters": {"type": "object", "required": ["sql"],
                   "properties": {"sql": {"type": "string", "description": "The final SQLite query."}}},
}}

TOOLS = [SEARCH_VALUES, EXECUTE_SQL, SUBMIT, ASK_USER]
