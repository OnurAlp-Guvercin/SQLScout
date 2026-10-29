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
- **Terms:** Project-specific technical terms (small model, harness, final check, handoff...) are in English in the code and the documents; explanations are in Turkish.
- **No flags.** Every part of the flow is always on, as in the figure. When the contribution of a part is to be measured (ablation), a flag is added for that part.

## File map

| File | Place in the flow | What it does |
|---|---|---|
| `agent/loop.py` | Steps 2, 8 | The flow itself. `answer_question`: step 1 → small model → (if stuck or the small model does not respond) large model → fallback → experience log. `run_steps`: the loop over one budget. `take_step`: a single tool call; each tool is one branch, each branch goes to `run` in `harness/tools/<tool>.py`. `early_handoff`: an early handoff if there is no progress in the first 6 steps or 5 calls in a row were wasted. `add_budget_note`: the number of tool calls left. `next_step`: the next tool call from the model (sampled when stuck). Handoff: `start_large_model` (the large model solves the question from scratch: it does not see the small model's conversation and starts with only the small model's system prompt, the step 1 context and a full budget; like the small model, it chooses what to do itself), `fallback_answer` (the last submitted SQL that runs without error, low confidence; otherwise `no_answer` and `error_message`; also when the large model's API does not answer, `large_model_error`). `stop`: why the loop stopped (`handoff_reason` for the small model, `large_model_stop_reason` for the large model). `write_experience`: the experience log, when each question ends; `remember`: writes the answer to the memory (an answer accepted without a check is `unchecked`) |
| `agent/prompts.py` | | Everything the model sees: the prompt texts (small model and large model, the base's single SQL, the large model's check) and the tool definitions (`TOOLS`) |
| `agent/llm.py` | | Sends a request to the model (`chat`), counts tokens (`count_tokens`). The small model goes to a local `mlx_lm.server`, the large model to OpenRouter (`SMALL_MODEL_URL`, `LARGE_MODEL_URL`); both use the OpenAI format, the addresses are in `config.py`. To try it: `python -m agent.llm "question"` |
| `agent/context.py` | | `Context`: the state kept while answering one question (conversation, budget, cache, counters) |
| `harness/prepare.py` | Step 1 | `build_context`: the initial context (schema, descriptions, foreign keys, column profiles, similar questions from the memory if any, evidence, question). `is_near_unique`: a text column where almost every row is different; fewer samples are shown for it. To try it: `python -m harness.prepare <sqlite path> "question" ["evidence"]` |
| `harness/memory.py` | Step 1 | Memory: questions solved before, with their embeddings, in `experience/memory.sqlite`. `similar`: at most 3 candidate rows most similar to the question (above the threshold). `is_candidate`: `correct` in train, `label = ok` in evaluation and in use; in evaluation (when `run` is given) only train and the same run. `add`: embeds and writes rows. `embed`: `Qwen3-Embedding-0.6B`, with MLX (the last token's vector; no new package needed). To add BIRD train: `python -m harness.memory <train.json>` |
| `harness/tools/search_values.py` | Step 3 | Search in the value index (FTS5 trigram + `difflib`; exact match for texts shorter than 3 letters; exact letters first). If a text with several words is not found, each word is searched separately. If no value is found, the columns with a similar name (`similar_columns`; also used by `execute_sql`'s error note) |
| `harness/tools/execute_sql.py` | Steps 4–6 | `run`: the small model's `execute_sql`. `check`: pre-check (read-only, `EXPLAIN`); `error_hint` adds what is needed to fix the error to the note (the columns of the tables in the query, the alias, the tables). `run_sql`: real execution or cache; an exploration query may run 50 seconds, a submitted main query (`answer=True`) 200 seconds, and a timeout during exploration is not cached. `format_result`: turns the result into text (20 rows; `TRIMMED_HINT` if trimmed; a `search_values` reminder if empty or only 0/NULL; the large model's check sees it without notes). `has_rows`: does the result really have rows (a single row that is only 0/NULL does not; the progress limit uses it). `sql_key`: a key that ignores whitespace and a trailing `;` (cache, repeats) |
| `harness/tools/submit.py` | Step 7 | `run`: the small model's and the large model's `submit`; two gates in order: does it run without error, does the large model find it correct. `fail`: the failed gate's note is returned and one try is used; handoff on the second (the last note stays in the handoff message). `runs_without_error`: pre-check, does it run without error as a main query (200 s); a SQL that passes becomes `context.submitted_sql` (the fallback candidate). `large_model_review`: the large model checks every answer (`CHECK_ANSWER`; a separate context: the step 1 context without the memory examples, the SQL and the result without the note meant for the small model, `format_result(hint=False)`); its reply is JSON, `{"reason", "correct"}`, read by `read_review` (a reply that cannot be read is not an approval); if the small model's answer is wrong, handoff (the reason stays in the small model's conversation); if the large model's own answer is wrong, `REVIEWER_NOTE` with the reason is returned and counts as a final check try; every decision on the small model's answers is written to `context.large_model_checks`. If the large model's API does not answer, the answer is accepted (`large_model_error`) |
| `harness/guards.py` | Every step | `read_tool_call`: rejecting broken output. `extract_sql`: the SQL in the model's plain-text reply (the base). `clean_sql`: removes ```sql fences (with any text after the closing fence) and leading `--` or `/* */` comments around the SQL; the base uses it too. `earlier_calls`: the caller's (small model or large model) own repeated calls (handoff on the third repeat). `compress`: a compressed copy of the messages sent to the model (the conversation itself stays complete for the experience log); `is_encodable`: a call whose arguments cannot be encoded as UTF-8 is rejected |
| `db/sqlite_db.py` | Steps 5, 6 | `execute`, `explain` (below) |
| `db/sqlite_schema.py` | Step 1 | `schema`, `profile`, `descriptions` (below). When moving to another database, a twin of these two files with the same functions is written |
| `config.py` | | All constants (table below) |
| `run.py` | | Runs a single question; prints every step as it happens (in colour in a terminal: small model blue, large model turquoise, rejections red, acceptance green; `answer_question(show_step=...)`): `python run.py --db <sqlite path> "question" [--evidence "..."]` |
| `evaluate.py` | | Runs BIRD dev, scores it with BIRD's rule (`run_gold`: the gold SQL once per question, 200 s; `is_correct`), has the split, `question_id` and whether the answer is correct added to the experience log line, also scores every SQL the large model checked (`large_model_checks`), and writes the result: `python evaluate.py --name <experiment> [--limit n] [--no-handoff] [--no-memory] [--large-model-agent]` → `results/<experiment>.jsonl` |
| `baseline.py` | | The base: a tool-free single SQL (temperature 0), to compare the agentic system with; a question with an API error counts as wrong with `error`, and the run goes on: `python baseline.py --name <experiment> [--model <model>] [--limit n]` → `results/<experiment>.jsonl` |
| `report.py` | | The summary of an experiment (`summary`, printed at the end of evaluate.py; including how accurate the large model's check was); a one-line table for several result files: `python report.py results/<experiment>*.jsonl` |
| `requirements.txt` | | Dependencies; every new package is added after asking the user |
| `tests/` | | Tests (no API needed). A small SQLite file is created in the code for testing |
| `data/` | | Datasets and prepared files; not code. `data/bird/dev/` (evaluation), `data/bird/train/train.json` (question–SQL pairs only; added to the memory once), `data/prepared/<db_id>/` (column profiles and value index; built once per database) |
| `models/` | | Local model files; not code, not in git. `models/Qwen3.5-0.8B/` (the small model; `mlx_lm.server` loads it from here), `models/Qwen3-Embedding-0.6B/` (the embedding model; used by the memory) |
| `results/` | | Experiment results (below) |

## Tools

The agent makes a single tool call each turn. Tool calls are written in Qwen's own tool-call format. Every call takes one off the budget, including rejected and malformed calls.

| Tool | Arguments | Returned to the agent | Place in the flow |
|---|---|---|---|
| `search_values` | `query` | The 5 most relevant values that contain the word or are spelled similarly (exact match for words shorter than 3 letters): `table.column = 'value'` | Step 3 |
| `execute_sql` | `sql` | The real result (at most 20 rows; a "you can submit without seeing every row" note if trimmed; a `search_values` reminder if empty or only 0/NULL) or a pre-check note | Steps 4–6 |
| `submit` | `sql` | The answer is returned, or a final check note | Step 7 |

- **`search_values`:** Searches an SQLite FTS5 index built from the distinct values of text columns. The index uses trigrams (a part of a word also matches); the matches are ranked by spelling similarity with `difflib`, so a search for "Los Angles" finds "Los Angeles". Trigrams cannot search a text shorter than 3 letters; a short text (e.g. "UK") is searched by exact match, ignoring upper/lower case. The index is built once per database and stored in `data/prepared/<db_id>/values.sqlite`.

## `db/sqlite_db.py` and `db/sqlite_schema.py` functions

| Function | Returns |
|---|---|
| `execute(db_path, sql, timeout_seconds)` | `{"ok", "error", "timed_out", "columns", "rows", "row_count", "result_key"}`. `rows` is at most 100 rows; `row_count` is the real number of rows. `result_key` is computed from all rows (below). On error, `ok=False` and `error` is filled |
| `explain(db_path, sql)` | `{"ok", "error", "plan"}`: `plan` is the `EXPLAIN QUERY PLAN` rows. On a syntax error, a missing table/column or a second statement, `ok=False` and `error` is filled. A "double-quoted" name that is not found is not treated as text; it gives an error |
| `schema(db_path)` | List of tables: each `{"name", "columns", "foreign_keys"}`. Column: `{"name", "type", "primary_key"}`; foreign key: `{"column", "ref_table", "ref_column"}` |
| `profile(db_path, table)` | `{"table", "row_count", "columns"}`. For each column: type, NULL ratio, number of distinct values, the 10 most frequent values (all of them if there are at most 10 distinct values); min and max of numeric values |
| `descriptions(db_path)` | `{table: {column: description}}`, from BIRD's `database_description/<table>.csv` files |

- **Read-only** has two layers: the database is opened with `mode=ro`, and only queries starting with `SELECT` / `WITH` are accepted.
- **Timeout:** exploration and trial queries (`execute_sql`) 50 seconds; main queries (the submitted SQL, and the gold and the answer in scoring) 200 seconds.
- **Result key:** All rows are taken, duplicates are dropped, the rows are sorted and hashed. Row order does not matter, column order does; this is BIRD's official comparison rule. Scoring uses only this key.

## Agent loop

The core of `agent/loop.py` (simplified). Each branch goes to a single file:

```python
def run_steps(context):                                              # the loop over one budget
    context.calls_left = config.MAX_TOOL_CALLS                      # small model and large model both 10
    while context.calls_left > 0:
        step = next_step(context)                                   # step 2
        context.calls_left -= 1
        outcome = take_step(step, context)                          # steps 3–7
        if outcome == "accepted":
            return context.answer(sql, "ok")
        if outcome == "stopped" or early_handoff(context):         # stuck → step 8
            return None
        add_budget_note(context)
    return None                                                     # out of budget → step 8


def take_step(step, context):                                       # a single tool call
    earlier = guards.earlier_calls(step, context)
    if step["error"]:                                               # tool call could not be read: rejected
        result = step["error"]
    elif len(earlier) >= config.MAX_REPEATS:                        # its own third repeat: stuck
        return "stopped"
    elif earlier:                                                   # same call: the earlier result is returned
        result = guards.repeat_note(earlier)
    elif step["tool"] == "search_values":
        result = search_values.run(query, context)                  # step 3
    elif step["tool"] == "execute_sql":
        result = execute_sql.run(sql, context)                      # steps 4–6
    else:
        outcome = submit.run(sql, context)                          # step 7
        if outcome["done"]:
            return "accepted"
        if outcome["handoff"]:
            return "stopped"                                        # e.g. the final check failed twice
        result = outcome["note"]                                    # the check's note → step 2
    context.add(step, result)
    return None
```

## `config.py` constants

| Constant | Value | Place in the flow |
|---|---|---|
| Tool-call budget | Small model 10, after a handoff the large model 10 too. Rejected requests count too | Steps 2, 8 |
| Budget left | Written under every result; in the last 2 a "submit" reminder is added too (`BUDGET_WARNING`) | Step 2 |
| Repeat limit | If the same call is repeated a third time, handoff (`MAX_REPEATS`); the small model and the large model are compared only with their own calls. `submit` does not count as a repeat | Steps 2, 8 |
| Progress limit | If the small model has not run a SQL query that returned rows in its first 6 tool calls (`PROGRESS_CALLS`; a single row that is only 0/NULL does not count as rows), or 5 of its calls in a row were wasted (`WASTED_CALLS`: unreadable, repeated or rejected by the pre-check; a call that is not wasted resets the count), handoff | Steps 2, 8 |
| Memory | At most 3 similar solved questions (`MEMORY_EXAMPLES`), similarity at least 0.7 (`MEMORY_MIN_SIMILARITY`: among BIRD dev questions, below 0.7 is mostly unrelated, above it they share tables); `MEMORY = True`, `False` with `evaluate.py --no-memory` (nothing is read or written) | Step 1 |
| Number of search results | 5 | Step 3 |
| Value index | Texts longer than 100 characters are not indexed; in one search at most 200 values from the index are ranked by similarity | Step 3 |
| Similar spelling threshold | `difflib` similarity at least 0.8 | Step 3 |
| Initial context | The whole schema and column profiles; at most ~12K tokens in BIRD dev | Step 1 |
| Values in the profile | For text columns, the 10 most frequent values (all of them if there are at most 10 distinct values), at most 40 characters; only 3 for columns whose distinct values are at least 90% of the filled rows (`PROFILE_UNIQUE_RATIO`, `PROFILE_UNIQUE_VALUES`); none for free text whose values are mostly longer than 40 characters (`is_long_text`); a "value description" that repeats the column description is not written; for numeric columns, only min and max | Step 1 |
| Timeout / row limit | Exploration 50 seconds (`EXPLORE_TIMEOUT_SECONDS`), main query 200 seconds (`ANSWER_TIMEOUT_SECONDS`) / 100 rows; a query that returns more than 1 million different rows is an error (`MAX_TOTAL_ROWS`; repeats do not count) | Steps 6, 7 |
| Result shown to the agent | At most 20 rows, at most 100 characters per cell | Step 6 |
| Context limit | 32K tokens; if exceeded, the oldest observations are reduced to one line | Every step |
| Final check retries | If it fails twice, handoff (`FINAL_CHECK_TRIES`) | Steps 7, 8 |
| Handoff (ablation) | `HANDOFF = True`; `False` with `evaluate.py --no-handoff`: the large model only checks, the reason for a rejected small model answer goes back to the small model, no early handoff | Steps 7, 8 |
| Small model and large model generation | Temperature 0 (the most likely reply); if the last call was rejected or was a repeat, the next step is sampled with temperature 0.7 (`RETRY_TEMPERATURE`); top_p 0.8; thinking mode off | Steps 2, 8 |
| Model request | Answer at most 1024 tokens; a request takes at most 300 seconds in total (`LLM_TIMEOUT_SECONDS`; the answer is read in parts and cut and retried when the time is up); at most 4 requests to the API at once (`API_PARALLEL`); on a transient API error (408, 429, 5xx) 8 retries, waiting from 5 s and doubling; on 401/402 (key or credit) the run stops | |
| Parallelism in evaluation | 8 questions at the same time (`EVAL_WORKERS`; the local server batches requests). 4 on the API | |
| Models | The small model is `Qwen/Qwen3.5-0.8B` on a local `mlx_lm.server` (`SMALL_MODEL = "models/Qwen3.5-0.8B"`, the folder given to the server). The large model is `qwen/qwen3.5-9b` on the OpenRouter API, on one of the providers that serve it in bf16 (`LARGE_MODEL_PROVIDERS`: DeepInfra, PrimeIntellect, Parasail); if one is busy, the next one is used; key in `.env`. Running the large model locally too, or moving the small model to the API, is described in the comment in `config.py`. Target local models: small model `Qwen3.5-4B` (`mlx-community/Qwen3.5-4B-bf16`), large model `Qwen3.6-27B` (4-bit) | |
| Sample | `--limit n`: a fixed sample of the questions, chosen with seed 0, in dataset order (`SAMPLE_SEED`). The same n always picks the same questions | |

## Record formats

**`results/<experiment>.jsonl`** (one file per experiment; repeated runs use different names):
- The first line is the experiment itself: experiment name, dataset (`bird`), `--limit`, number of questions, the code's git commit (`code`: the commit and a hash of the uncommitted changes, empty if none), all `config.py` values and the prompt texts. In `baseline.py`'s file: the model, the temperature and the prompt.
- Every following line is a question: `question_id`, `db_id`, `sql` (the answer), `label`, `answered_by` (`small_model` / `large_model`), `error_message` (the reason if there is no answer; `answered_by` is empty for `no_answer`), `correct`, `tool_calls`, `executions` (number of real executions), `handoff_reason` (why the small model's loop stopped; with handoff off, only the stop reason), `large_model_stop_reason` (why the large model's loop stopped), `large_model_checks` (for every SQL the small model submitted, the large model's decision `approved`, its reason `reason` and whether the SQL was really correct `correct`), `large_model_error` (if the large model's API could not be reached), `steps` (every tool call and observation; the `by` field says `small_model` or `large_model`), `memory_examples` (the texts of the similar questions added to the context), `prompt_tokens`, `completion_tokens`, `cost`, `retries` (how many times requests to the model were retried), `seconds`. If the gold SQL gives an error, `gold_error` is written; if the model does not answer, `error`.

**`experience/log.jsonl`** (experience log; the small model's future training data, records accumulate; written by `agent/loop.py` when each question ends): each line is a question: time, split (`use` in use, `dev` in evaluation; `correct` is filled only in `dev`), `run` (in evaluation, the run name and start time), dataset, `question_id`, `db_id`, question, evidence, gold SQL, answer SQL, `label`, `correct`, `answered_by`, `handoff_reason`, `large_model_stop_reason`, `large_model_error`, model names, `handoff` (`config.HANDOFF`), `messages` (the whole conversation the small model saw: system prompt, step 1 context, every tool call and observation) and `large_model_messages` (after a handoff, the large model's conversation that starts from scratch; otherwise empty). Only `split = train` lines are used for training.


## Build order

The system is written in small stages: each stage adds a single part, is tested with `pytest tests/` and one real question (`run.py`), and the next stage starts after the user approves. The user is told in 2–3 sentences what was done and how it was tried.

All 8 steps of the flow are done. Next stages:
1. **Agent training:** with the experience log; the method is open (SFT, distillation or RL, one or a mix); only train records.
2. **Local models:** for the paper's numbers, the small model (Qwen3.5-4B) and the large model run locally.

## Diagram

The flow figure is generated by `docs/diyagram/akis_diyagrami.py` (English: `docs/diyagram/flow_diagram_en.py`); usage is at the top of the file. If the flow changes, the figure and [AGENTIC_FLOW.md](AGENTIC_FLOW.md) are updated together.
