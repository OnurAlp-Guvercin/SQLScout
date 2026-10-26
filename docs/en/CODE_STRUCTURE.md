# Code structure

Turkish original: [../KOD_YAPISI.md](../KOD_YAPISI.md)

This document describes how the code is organized, how it is written and in what order it was written. The flow itself and the meaning of the terms are in [AGENTIC_FLOW.md](AGENTIC_FLOW.md).

## Rules

- **Each step lives in a single file, each tool in its own file.** You do not jump from file to file to understand something: each of the agent's tools is in `harness/tools/`, in a file named after the tool (entry function `run`). Which step lives where is shown in the map below.
- **Files are short.** A file that grows past roughly 200 lines is split.
- **Each file starts with a 1–2 line description**: what the file does and which step of the flow it is.
- **Plain code.** Ordinary `for` and `if` are used. Short functions, names that say what they do. If a list comprehension makes the code harder to read, a plain loop is written.
- **No over-engineering.** No class hierarchies, plugin systems or abstractions written "because they might be needed later". A class is used only when state really has to be kept (`Context`).
- **No framework.** The harness is a plain Python loop; no agent framework is used.
- **Numbers in one place.** Thresholds, budgets and limits live only in `config.py`.
- **Terms:** Project-specific technical terms (policy, harness, final check, handoff...) are in English in the code and the documents; explanations are in Turkish.
- **No flags.** Every part of the flow is always on, as in the figure. When the contribution of a part is to be measured (ablation), a flag is added for that part.

## File map

| File | Place in the flow | What it does |
|---|---|---|
| `agent/loop.py` | Steps 2, 8 | The flow itself. `answer_question`: step 1 → agent → (if stuck) teacher → fallback → experience log. `run_steps`: the loop over one budget; each tool is one branch, each branch goes to `run` in `harness/tools/<tool>.py`; an early handoff if there is no progress in the first 4 steps. `next_step`: the next tool call from the model (sampled when stuck). Handoff: `start_teacher`, `fallback_answer` (the last SQL that ran without error and returned rows). `write_experience`: the experience log, when each question ends |
| `agent/prompts.py` | | Everything the model sees: the prompt texts (agent, the base's single SQL, the teacher's takeover note) and the tool definitions (`TOOLS`) |
| `agent/llm.py` | | Sends a request to the model (`chat`), counts tokens (`count_tokens`). The policy goes to a local `mlx_lm.server`, the teacher to OpenRouter (`LLM_URL`, `TEACHER_URL`); both use the OpenAI format, the addresses are in `config.py`. To try it: `python -m agent.llm "question"` |
| `agent/context.py` | | `Context`: the state kept while answering one question (conversation, budget, cache, counters) |
| `harness/prepare.py` | Step 1 | `build_context`: the initial context (schema, descriptions, foreign keys, column profiles, evidence, question). To try it: `python -m harness.prepare <sqlite path> "question" ["evidence"]` |
| `harness/tools/search_values.py` | Step 3 | Search in the value index (FTS5 trigram + `difflib`). If no value is found, the columns with a similar name (`similar_columns`) |
| `harness/tools/execute_sql.py` | Steps 4–6 | `run`: the agent's `execute_sql`. `check`: pre-check (read-only, `EXPLAIN`); `error_hint` adds what is needed to fix the error to the note (the columns of the tables in the query, the alias, the tables). `run_sql`: real execution or cache. `format_result`: turns the result into text (20 rows; a `search_values` reminder if empty). |
| `harness/tools/submit.py` | Step 7 | `run`: the agent's and the teacher's `submit`; handoff if it fails twice; if the agent had not seen the result, it shows the result first (`context.seen`). `final_check`: pre-check, does it run without error |
| `harness/guards.py` | Every step | `read_tool_call`: reads the model's reply as one step (a tool call or a ` ```sql ` block); rejecting broken output. `earlier_calls`: repeated calls (handoff on the third repeat). `compress`: compressing the context |
| `db/sqlite_db.py` | Steps 5, 6 | `execute`, `explain` (below) |
| `db/sqlite_schema.py` | Step 1 | `schema`, `profile`, `descriptions` (below). When moving to another database, a twin of these two files with the same functions is written |
| `config.py` | | All constants (table below) |
| `run.py` | | Runs a single question: `python run.py --db <sqlite path> "question" [--evidence "..."]` |
| `evaluate.py` | | Runs BIRD dev with a seed, scores it with BIRD's rule (`score`), has the split, `question_id` and whether the answer is correct added to the experience log line, and writes the result: `python evaluate.py --name <experiment> --seed 0 [--limit n]` → `results/<experiment>_seed<n>.jsonl` |
| `baseline.py` | | The base: a tool-free single SQL (temperature 0), to compare the agentic system with: `python baseline.py --name <experiment> [--model <model>] [--limit n]` → `results/<experiment>_seed0.jsonl` |
| `report.py` | | The summary of an experiment (`summary`, printed at the end of evaluate.py); a one-line table for several result files: `python report.py results/<experiment>_*.jsonl` |
| `requirements.txt` | | Dependencies; every new package is added after asking the user |
| `tests/` | | Tests (no API needed). A small SQLite file is created in the code for testing |
| `data/` | | Datasets and prepared files; not code. `data/bird/dev/`, `data/prepared/<db_id>/` (column profiles and value index; built once per database) |
| `results/` | | Experiment results (below) |

## Tools

The agent makes a single tool call each turn. Tool calls are written in Qwen's own tool-call format; if the agent writes SQL in a ` ```sql ` block in its message, that counts as `execute_sql` too. Every call takes one off the budget, including rejected and malformed calls.

| Tool | Arguments | Returned to the agent | Place in the flow |
|---|---|---|---|
| `search_values` | `query` | The 5 most relevant values that contain the word or are spelled similarly: `table.column = 'value'` | Step 3 |
| `execute_sql` | `sql` | The real result (at most 20 rows; a `search_values` reminder if empty) or a pre-check note | Steps 4–6 |
| `submit` | `sql` | The answer is returned; or a final check note, or the result if the agent had not seen it | Step 7 |

- **`search_values`:** Searches an SQLite FTS5 index built from the distinct values of text columns. The index uses trigrams (a part of a word also matches); the matches are ranked by spelling similarity with `difflib`, so a search for "Los Angles" finds "Los Angeles". The index is built once per database and stored in `data/prepared/<db_id>/values.sqlite`.

## `db/sqlite_db.py` and `db/sqlite_schema.py` functions

| Function | Returns |
|---|---|
| `execute(db_path, sql)` | `{"ok", "error", "columns", "rows", "row_count", "result_key"}`. `rows` is at most 100 rows; `row_count` is the real number of rows. `result_key` is computed from all rows (below). On error, `ok=False` and `error` is filled |
| `explain(db_path, sql)` | `{"ok", "error", "plan"}`: `plan` is the `EXPLAIN QUERY PLAN` rows. On a syntax error, a missing table/column or a second statement, `ok=False` and `error` is filled |
| `schema(db_path)` | List of tables: each `{"name", "columns", "foreign_keys"}`. Column: `{"name", "type", "primary_key"}`; foreign key: `{"column", "ref_table", "ref_column"}` |
| `profile(db_path, table)` | `{"table", "row_count", "columns"}`. For each column: type, NULL ratio, number of distinct values, the 10 most frequent values (all of them if there are at most 10 distinct values); min and max of numeric values |
| `descriptions(db_path)` | `{table: {column: description}}`, from BIRD's `database_description/<table>.csv` files |

- **Read-only** has two layers: the database is opened with `mode=ro`, and only queries starting with `SELECT` / `WITH` are accepted.
- **Timeout:** 30 seconds.
- **Result key:** All rows are taken, duplicates are dropped, the rows are sorted and hashed. Row order does not matter, column order does; this is BIRD's official comparison rule. Scoring uses only this key.

## Agent loop

The core of `agent/loop.py` (simplified). Each branch goes to a single file:

```python
def run_steps(context):
    context.calls_left = context.budget()                           # agent 10, teacher 5
    while context.calls_left > 0:
        guards.compress(context)
        step = next_step(context)                                   # step 2
        context.calls_left -= 1
        earlier = guards.earlier_calls(step, context)

        if step["error"]:                                           # tool call could not be read: rejected
            result = step["error"]
        elif len(own(earlier)) >= config.MAX_REPEATS:               # its own third repeat: stuck → step 8
            return None
        elif earlier:                                               # same call: the earlier result is returned
            result = guards.repeat_note(earlier)
        elif step["tool"] == "search_values":
            result = search_values.run(query, context)              # step 3
        elif step["tool"] == "execute_sql":
            result = execute_sql.run(sql, context)                  # steps 4–6
        else:
            outcome = submit.run(sql, context)                      # step 7
            if outcome["done"]:
                return context.answer(sql, "ok")
            if outcome["handoff"]:
                return None                                         # final check failed twice → step 8
            result = outcome["note"]                                # final check note → step 2

        context.add(step, result)
        if agent and context.calls == 4 and no SQL returned rows:
            return None                                             # no progress → step 8
    return None                                                     # out of budget → step 8
```

## `config.py` constants

| Constant | Value | Place in the flow |
|---|---|---|
| Tool-call budget | Agent 10, teacher half of that (5). Rejected requests count too | Steps 2, 8 |
| Budget left | Written under every result; in the last 2 a "submit" reminder is added too (`BUDGET_WARNING`) | Step 2 |
| Repeat limit | If the same call is repeated a third time, handoff (`MAX_REPEATS`); the agent and the teacher are counted only by their own repeats. `submit` does not count as a repeat | Steps 2, 8 |
| Progress limit | If the agent has not run a SQL query that returned rows in its first 4 tool calls, handoff (`PROGRESS_CALLS`) | Steps 2, 8 |
| Number of search results | 5 | Step 3 |
| Value index | Texts longer than 100 characters are not indexed; in one search at most 200 values from the index are ranked by similarity | Step 3 |
| Similar spelling threshold | `difflib` similarity at least 0.8 | Step 3 |
| Initial context | The whole schema and column profiles; at most ~12K tokens in BIRD dev | Step 1 |
| Values in the profile | For text columns, the 10 most frequent values (all of them if there are at most 10 distinct values), at most 40 characters; for numeric columns, only min and max | Step 1 |
| Timeout / row limit | 30 seconds / 100 rows | Step 6 |
| Result shown to the agent | At most 20 rows, at most 100 characters per cell | Step 6 |
| Context limit | 32K tokens; if exceeded, the oldest observations are reduced to one line | Every step |
| Final check retries | If it fails twice, handoff (`FINAL_CHECK_TRIES`) | Steps 7, 8 |
| Policy and teacher generation | Temperature 0 (the most likely reply); if the last call was rejected or was a repeat, the next step is sampled with temperature 0.7 (`RETRY_TEMPERATURE`); top_p 0.8; thinking mode off | Steps 2, 8 |
| Model request | Answer at most 1024 tokens; 300 seconds timeout per request; on a transient API error 8 retries, waiting from 5 s and doubling | |
| Parallelism in evaluation | 8 questions at the same time (`EVAL_WORKERS`; the local server batches requests). 4 on the API | |
| Models | The policy is `Qwen/Qwen3.5-0.8B` on a local `mlx_lm.server` (no seed is sent, because the server does not batch requests with a seed). The teacher is `qwen/qwen3.5-9b` on the OpenRouter API, on one of the providers that serve it in bf16 (`TEACHER_PROVIDERS`: DeepInfra, PrimeIntellect, Parasail); if one is busy, the next one is used; key in `.env`. Running the teacher locally too, or moving the policy to the API, is described in the comment in `config.py`. Target local models: policy `Qwen3.5-4B` (`mlx-community/Qwen3.5-4B-bf16`), teacher `Qwen3.6-27B` (4-bit) | |
| Seeds | 0, 1, 2 | |
| Sample | `--limit n`: a fixed sample of the questions, chosen with seed 0, in dataset order (`SAMPLE_SEED`). The same n always picks the same questions | |

## Record formats

**`results/<experiment>_seed<n>.jsonl`** (one file per experiment and seed):
- The first line is the experiment itself: experiment name, seed, dataset (`bird`), `--limit`, number of questions, all `config.py` values and the prompt texts. In `baseline.py`'s file: the model, the temperature and the prompt.
- Every following line is a question: `question_id`, `db_id`, `sql` (the answer), `label`, `answered_by` (agent / teacher), `correct`, `tool_calls`, `executions` (number of real executions), `handoff_reason`, `steps` (every tool call and observation; the `by` field says agent or teacher), `prompt_tokens`, `completion_tokens`, `cost`, `seconds`. If the gold SQL gives an error, `gold_error` is written; if the model does not answer, `error`.

**`experience/log.jsonl`** (experience log; the agent's future training data, records accumulate; written by `agent/loop.py` when each question ends): each line is a question: time, split (`use` in use, `dev` in evaluation; `correct` is filled only in `dev`), dataset, `question_id`, `db_id`, question, evidence, gold SQL, answer SQL, `label`, `correct`, `answered_by`, `handoff_reason`, model names, seed and `messages` (the whole conversation the agent, and after a handoff the teacher, saw: system prompt, step 1 context, every tool call and observation). Only `split = train` lines are used for training.


## Build order

The system was written in small stages. Each stage added a single part, was tested with `pytest tests/`, and the next stage started after the user approved. A new part is added the same way: the part is written, tested, and the user is told in 2–3 sentences what was done and how it was tried.

| Section | Stages | What was added |
|---|---|---|
| Foundation (no model) | 1–3 | Database layer; BIRD dev data and scoring; initial context |
| First working agent | 4–8 | Running the model; tool-free single SQL (the base, `baseline.py`); agent loop and `submit`; `execute_sql`; pre-check |
| Trial loop | 9–15 | Repeat guardrail and cache; trimming long results; compressing the context; `search_values` |
| Verifying the answer | 17 | Final check |
| Help | 22 | Handoff (teacher, early when the agent makes no progress) |
| Results | 29 | Measurement with the full system |
| Local models | 35 | Policy and teacher run locally; memory fit and speed |
| Agent training (later) | | SFT → on-policy distillation → RL with the experience log; only train records |

## Diagram

The flow figure is generated by `docs/diyagram/akis_diyagrami.py` (English: `docs/diyagram/flow_diagram_en.py`); usage is at the top of the file. If the flow changes, the figure and [AGENTIC_FLOW.md](AGENTIC_FLOW.md) are updated together.
