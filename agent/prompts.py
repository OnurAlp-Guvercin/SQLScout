"""Modelin gördüğü her şey: prompt metinleri ve tool tanımları. Prompt'u değiştirmek için bakılacak yer burası.
Model İngilizce okuduğu için metinler İngilizce."""

import config

SQL_RULES = """Rules:
- Use only tables and columns shown in the schema. Write names as the schema writes them: names with \
spaces, special characters or SQL keywords are in backticks (e.g. `order`).
- The user may spell a value differently from the database: a typo, other upper/lower case, an abbreviation or \
another word for it. Write values exactly as the database writes them (value samples, evidence or search results), \
not as the question writes them.
- Follow the evidence exactly: its mappings and formulas define the answer (e.g. "difference = SUBTRACT(A, B)" \
means A - B, even if the result is negative).
- Select only what the question asks for, in the order it asks."""

# Memory (adım 1): bağlama eklenen benzer, daha önce çözülmüş soruların başlığı.
MEMORY_NOTE = ("Similar questions answered before. They may come from another database, so their tables can differ "
               "from this schema. Use them only if they help.")

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

Answer the question as it is written. Explore only to find how values are written and how tables are linked; do not \
change what the question asks for because of what you see in the data.

{SQL_RULES}"""

# Large model kontrolü (adım 7): her cevap kabul edilmeden önce large model bağlamı, SQL'i ve sonucu görüp doğru mu diye bakar.
CHECK_ANSWER = f"""You are an expert SQLite analyst. You are given a database schema with column descriptions and \
value samples, sometimes evidence, a question, a SQL query written for it and its result. Decide whether the query \
answers the question correctly. Check two things:
1. Columns: say what the question asks to return, then look at each column of the result. Every column must be asked \
for. A column added only to identify, explain or check the answer (an id or a name the question does not ask for, the \
value used for ordering, a count) makes the answer wrong, even if the asked value is also in the result. If the \
question names the field to return (e.g. "indicate the id"), only that field is asked for.
2. Rows: the right tables, joins, conditions and values, so that the result holds exactly what the question asks \
for, and the query follows the evidence's mappings and formulas exactly. Read the question and the evidence \
literally: a query that adds something they do not state (e.g. another column for the same idea, COUNT(DISTINCT ...) \
instead of COUNT(...), a different denominator, extra grouping or rounding) is wrong, even if it looks more sensible.

{SQL_RULES}

Reply with only a JSON object: first the reason (the columns check, then the rows check), then your decision.
{{"reason": "<columns: ...; rows: ...>", "correct": <true or false>}}"""

# Tool'lar (Qwen'in tool-call biçimi). Small model'e ve large model'e aynı tool'lar sunulur.
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
