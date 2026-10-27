"""Modelin gördüğü her şey: prompt metinleri ve tool tanımları. Prompt'u değiştirmek için bakılacak yer burası.
Model İngilizce okuduğu için metinler İngilizce."""

import config

SQL_RULES = """Rules:
- Use only tables and columns shown in the schema. Write names as the schema writes them: names with \
spaces, special characters or SQL keywords are in backticks (e.g. `order`).
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
one tool in each turn. You decide what to do and in which order:
- `execute_sql` runs a read-only query and shows its real result (at most 20 rows). Use it to try a query that \
answers the question, or to explore the data when you are not sure about something (e.g. which values a column \
holds or how two tables are linked).
- `search_values` finds how a value is written in the database and in which column. The value samples show at most \
{config.PROFILE_TOP_VALUES} values per column.
- `submit` gives your final answer: when a query you ran answers the question, submit exactly that query. It must \
return only what the question asks for: leave out helper columns you added only while exploring.

{SQL_RULES}"""

# Teacher kontrolü (adım 7): agent'ın cevabını kabul etmeden önce teacher doğru mu diye bakar.
CHECK_ANSWER = f"""You are an expert SQLite analyst. You are given a database schema with column descriptions and \
value samples, sometimes evidence, a question, a SQL query written for it and its result. Decide whether the query \
answers the question correctly: the right tables, joins, conditions and values, and only what the question asks for.

{SQL_RULES}

Reply with exactly one word: yes or no."""

# Sütun kontrolü (adım 7): birden çok sütunlu cevapta soru her sütunu istiyor mu? Döngüde keşif sorgularının
# yardımcı sütunları (id, ad) cevapta kalıyordu; genel kontrol bunu fark etmiyordu.
COLUMN_CHECK = """You are an expert SQLite analyst. You are given a question, sometimes evidence, and the columns of a \
SQL query's result written to answer it. Decide whether the question asks for every one of these columns. A column \
the question does not ask for, e.g. an id, name or count that was only added to check the answer, is extra. If the \
question asks for one value (e.g. a count, a percentage or a difference), the result should have only that column.

Reply with exactly one word: yes if every column is asked for, no if there is an extra column."""

# Tool'lar (Qwen'in tool-call biçimi). Agent'a ve teacher'a aynı tool'lar sunulur.
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
    "description": "Submit the SQLite query that answers the question as the final answer. It must return only the "
                   "columns the question asks for. Run it with execute_sql first and look at its result. This ends "
                   "the task.",
    "parameters": {"type": "object", "required": ["sql"],
                   "properties": {"sql": {"type": "string", "description": "The final SQLite query."}}},
}}

TOOLS = [SEARCH_VALUES, EXECUTE_SQL, SUBMIT]
