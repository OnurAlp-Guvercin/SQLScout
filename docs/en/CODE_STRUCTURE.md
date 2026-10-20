# Code structure

Turkish original: [../KOD_YAPISI.md](../KOD_YAPISI.md)

This document describes how the code is organized, how it is written and in what order it is written. The flow itself and the meaning of the terms are in [AGENTIC_FLOW.md](AGENTIC_FLOW.md).

## Rules

- **Each file corresponds to one or two steps of the flow.** Which step lives where is shown in the map below.
- **Files are short.** A file that grows past roughly 150 lines is split.
- **Each file starts with a 1–2 line description**: what the file does and which step of the flow it is.
- **Plain code.** Ordinary `for` and `if` are used. Short functions, names that say what they do. Lambdas and list comprehensions are allowed but not required; if they make the code harder to read, a plain loop is written.
- **No over-engineering.** No class hierarchies, plugin systems or abstractions written because "we might need it later". A class is used only when state really has to be kept.
- **No framework.** The harness is a plain Python loop; no agent framework is used.
- **Numbers in one place.** Thresholds, budgets and candidate counts live only in `config.py`; no numbers are hard-coded in the code. `config.py` is created in the first stage and grows as needed.
- **Terms:** Project-specific technical terms (policy, world model, harness, gate, candidate, handoff...) are in English in the code and the docs; explanations are in Turkish.
- **Piece by piece.** The code is written in the stages listed under "Build order" below. Each stage adds a single piece and leaves a working system. When a stage is done, the user is told what was done and how it was tested; the next stage does not start until the user approves.
- **Flags come with their piece.** An ablation flag is added to `config.py` in the stage where its piece is written. A piece that has not been written yet behaves as if its flag were off.

## File map

The files of stages 1–33 are written (Phase 1 and Phase 2). `world_model/collect.py` and `training/` belong to the optional training section and do not exist yet.

| File | Place in the flow | Stage | What it does |
|---|---|---|---|
| `config.py` | | 1 | All constants and ablation flags (tables below) |
| `requirements.txt` | | 4 | Dependencies; each new package is added only after asking the user |
| `db/sqlite_db.py` | Step 5, 7 | 1 | `execute`, `explain`, `estimate_cost` (below) |
| `db/sqlite_schema.py` | Step 1 | 1, 3 | `schema`, `profile` (below). When moving to another database, a counterpart of these two files with the same functions is written |
| `evaluate.py` | | 2, 29, 30 | Runs a dataset with one seed, scores it with the BIRD rule (`score`) and writes the result: `python evaluate.py --name <experiment> --seed 0 [--dataset bird\|mini_interact] [--subset] [--limit n] [--off USE_... ] [--simulate-cost]` → `results/<experiment>_seed<n>.jsonl`. Each question carries the path of its own database (`db_path`) |
| `report.py` | | 29, 33 | Summary of one experiment (`summary`, written at the end of evaluate.py); for several result files, a table with one line each (seeds, ablations): `python report.py results/<experiment>_*.jsonl` |
| `mini_interact.py` | | 30 | Converts Mini-Interact tasks into evaluate.py's question format: the ambiguous question, the knowledge base as evidence (except the items the task hides), ambiguity notes (for the simulator only), and the correct SQL if available (`data/mini_interact/mini_interact_gold.jsonl`) |
| `harness/prepare.py` | Step 1 | 3, 14, 25 | `build_context`: the initial context. Question, evidence, schema (descriptions, foreign keys), column profiles (stage 3); value matches for the words in the question (stage 14, from `harness/value_matches.py`); database memory (stage 25). To try it: `python -m harness.prepare <sqlite path> "question" ["evidence"]` |
| `harness/value_matches.py` | Step 1 | 14 | `find`: values spelled similarly to word groups in the question; the search itself is done by `search.find_values` |
| `harness/descriptions.py` | Step 1, 3 | 3, 30 | `load`: column descriptions; in BIRD `database_description/<table>.csv`, in Mini-Interact `<db>_column_meaning_base.json` (with the fields of JSON columns) |
| `agent/llm.py` | | 4 | Sends a request to the model and returns the answer; counts tokens with `count_tokens`. During development it goes to the OpenRouter API (cheap Qwen models), at the end to a local `mlx_lm.server` (both use the OpenAI format; the address is in `config.py`). The policy, candidates, teacher, user simulator and placeholder world model all use it |
| `agent/prompts.py` | | 5, 22, 24, 26 | Prompt texts: tool-free SQL, agent, the teacher's takeover note, user simulator, placeholder world model |
| `agent/tools.py` | Step 2 | 6 and later | Tool definitions and `offered`: which tools are offered to the agent and to the teacher (depending on the flags) |
| `agent/policy.py` | Step 2, 4, 8 | 5, 6 | `write_sql`: writes a single SQL without tools (stage 5; in step 8 it also writes the candidates). `next_step`: reads the next tool call (stage 6) |
| `agent/loop.py` | Step 2 | 6 and later | Agent loop: `answer_question`, `run_steps` (the loop over one budget; the teacher uses it too), `run_query` (steps 4–7), `finish` (steps 8–10). The flow itself lives here; each tool is a branch |
| `agent/context.py` | | 6 and later | `Context`: the state kept during one question (conversation, budget, cache, counters) |
| `run.py` | | 6 | Runs a single question: `python run.py --db <sqlite path> "question" [--evidence "..."]` |
| `harness/precheck.py` | Step 5, 7 | 8, 9, 27 | `check`: `None` if there is no problem, otherwise the note returned to the agent; read-only and `EXPLAIN` check (stage 8). `run`: serves an SQL that passed the pre-check from the cache, or really executes it and writes it to the experience log (stage 9); the agent's SQLs, the candidates and the final check all go through here. Whether to go to the world model (stage 27) |
| `harness/handoff.py` | Step 11 | 6, 22 | `start_teacher`: the teacher takes over the agent's conversation with a takeover note and continues in the same loop with a new budget (stage 22). `fallback_answer` (stage 6) |
| `harness/guards.py` | Every step | 6, 9–11 | Rejection of malformed output (`read_tool_call`, stage 6; also the forecast format, stage 15); repetition of the same call (`is_repeat`, stage 9), trimming of long results (`format_result`, `trim_rows`, stage 10), compression of the context (`compress`, stage 11) |
| `harness/search.py` | Step 3 | 12, 13, 18 | `search_values` (stage 12), `search_schema` (stage 13); writes the results to the search notes (stage 18) |
| `harness/compare.py` | Step 7 | 15, 26 | Compares the forecast with the real result and writes a surprise note (stage 15); also compares the world model's prediction (stage 26) |
| `experience/log.py` | Step 7 | 16 | Writes the experience log to the `experience/log.jsonl` file |
| `harness/final_check.py` | Step 10 | 17 | Final check |
| `harness/candidates.py` | Step 8 | 18, 19, 28 | Generates candidates, executes them, groups them by result key and selects the answer; filters out expensive candidates with the world model (stage 28) |
| `harness/gates.py` | Step 6, 9 | 20, 21, 27 | Confidence gate (stage 20), medium note (stage 21); prediction gate and audit (stage 27) |
| `harness/ask_user.py` | Step 3 | 23, 24, 31 | `run`: asks the question to the person at the terminal (stage 23; `run.py`), to the user simulator that sees the gold SQL in BIRD (stage 24), or to Mini-Interact's own two-step simulator (stage 31: the encoder classifies the question, the decoder answers; prompts taken verbatim from BIRD-Interact), and stores the clarification. An answer containing SQL is rejected. Only the simulator sees the gold SQL and the ambiguity notes; they never enter the agent's context |
| `harness/cost.py` | Step 2, 5 | 32 | Cost simulation (`SIMULATE_COST`): starting bird-coins (`start_coins`), spending (`spend`), whether budget is left / low (`budget_left`, `budget_low`), simulated query cost (`query_cost`) |
| `experience/memory.py` | Step 1, offline | 25 | Reads and writes the database memory: `experience/memory/<db_id>.jsonl`. `evaluate.py` starts each experiment and seed with an empty memory |
| `world_model/predict.py` | Step 6, 8 | 26, 33 | `predict`: SQL and the step 1 context → prediction (type, columns, rows in the forecast format; plus values and a confidence for each). Malformed output counts as "don't know"; a missing confidence counts as confidence 0. In the first version it is a placeholder: it asks an LLM through a prompt. Measurement (stages 26, 33): `python -m world_model.predict [n]` with the last n real executions in the experience log; for each threshold in `GATE_CHOICES`, how many predictions are trusted and how many of them are correct. If a trained model arrives (stage 37), only the inside of this file changes |
| `world_model/collect.py` | | 36 | Collects the world model's training data (executes SQLs and labels them); part of the optional training section |
| `training/` | | 37–43 | World model training (stage 37) and policy training (38–43); optional, after the system works end to end |
| `tests/` | | every stage | Tests. For testing, a small SQLite file with a few rows is created in code |
| `data/` | | | Datasets and prepared files; not code. `data/bird/dev/` (`dev.json`, `dev_databases/`), `data/prepared/<db_id>/` (column profiles and the search index prepared for step 1; built once per database) |
| `results/` | | | Experiment results (below) |

The experience log (`experience/`) is training data. `results/`, on the other hand, holds the experiment results that the paper's numbers come from.

## Tools

The agent makes a single tool call per turn. Tool calls are written in Qwen's own tool-call format (the `tools` field of the chat template). Each call costs one unit of the budget; rejected and malformed calls do too.

| Tool | Arguments | Returned to the agent | Place in the flow |
|---|---|---|---|
| `search_schema` | `query` | The 5 most relevant tables/columns and their descriptions | Step 3 |
| `search_values` | `query` | The 5 most relevant values that contain the word or are spelled similarly: `table.column = 'value'` | Step 3 |
| `ask_user` | `question` | The user's answer (clarification). At most 5 times per question; the agent decides whether it is needed | Step 3; `USE_ASK_USER` |
| `execute_sql` | `sql`, `forecast` | The real result (at most 20 rows) and a surprise note if any; or a check error | Steps 4–7 |
| `submit` | `sql` | The answer is returned; or a medium note or a final check note | Steps 8–10 |
| `handoff` | `reason` | Nothing is returned; the work passes to the teacher | Step 11; `USE_HANDOFF` |

- **Forecast format:** `{"type": "rows", "columns": ["category", "n"], "rows": "2-10", "trust": true}`
  - `type`: `error`, `empty` or `rows`.
  - `columns` and `rows` are written only if `type` is `rows`. `rows` is one of the row ranges.
  - `trust`: `true` means "I trust it" (trust), `false` means "I'm not sure" (unsure). It does not affect the harness's decisions; it is used in the forecast reward in RL.
  - For a forecast to count as a "hit", `type` must match; if it is `rows`, the number of columns and the row range must match too. Column names are not compared.
- **`search_schema`:** Looks for word matches in table and column names and in BIRD's column descriptions (the `database_description` CSVs).
- **`search_values`:** Searches an SQLite FTS5 index built from the distinct values of text columns. The index uses trigrams (a part of a word also matches); candidates are ranked by spelling similarity with Python's `difflib` module, so a search for "Los Angles" finds "Los Angeles". The index is built once per database and stored under `data/prepared/<db_id>/`. FTS5 and `difflib` are built into Python; no extra package is needed.

## `db/sqlite_db.py` and `db/sqlite_schema.py` functions

| Function | Returns |
|---|---|
| `execute(db_path, sql)` | `{"ok", "error", "columns", "rows", "row_count", "result_key"}`. `rows` is at most 100 rows; `row_count` is the real number of rows. `result_key` is computed from all rows (below). On error, `ok=False` and `error` is filled |
| `explain(db_path, sql)` | `{"ok", "error", "plan"}`: `plan` is the `EXPLAIN QUERY PLAN` rows. On a syntax error, a missing table/column or a second statement, `ok=False` and `error` is filled |
| `schema(db_path)` | List of tables: each is `{"name", "columns", "foreign_keys"}`. Column: `{"name", "type", "primary_key"}`; foreign key: `{"column", "ref_table", "ref_column"}`. A foreign key without a target column is linked to the primary key of the target table |
| `profile(db_path, table)` | `{"table", "row_count", "columns"}`. For each column: type, NULL ratio, number of distinct values, the 5 most frequent values and their counts (all of them if there are at most 30 distinct values); min and max of numeric values |
| `estimate_cost(db_path, sql)` | Estimated number of rows to be scanned; `None` if the SQL is invalid. SQLite's plan has no row estimate; so the row counts of all tables scanned from start to end are summed, and indexed lookups are not counted because they are small. Because `EXPLAIN QUERY PLAN` writes the alias (`T1`) instead of the table, scans are read from the `EXPLAIN` bytecode |

- **Read-only** has two layers: the database is opened with `mode=ro`, and only queries starting with `SELECT` / `WITH` are accepted.
- **Timeout:** 30 seconds.
- **Result key:** All rows are fetched, duplicates are dropped, the rows are sorted and the result is hashed. Row order does not matter, column order does; this is BIRD's official comparison rule (`set(rows) == set(gold_rows)`). Candidate grouping and scoring both use only this key.

## Agent loop sketch

`agent/loop.py` looks roughly like this (simplified); it matches step 2 in AGENTIC_FLOW.md. The teacher uses the same `run_steps`: the `handoff` tool is not offered to it and its `submit` goes directly to the final check. `step` is the tool call read by `harness/guards.py` (`tool`, `args`, `error`...).

```python
def answer_question(question, evidence, db_path, seed=None, ..., gold_sql=None):
    context = Context(...)                                          # gold_sql only for the user simulator
    context.messages = [system prompt, prepare.build_context(question, evidence, db_path)]  # step 1
    answer = run_steps(context)                                     # agent
    if answer is None and config.USE_HANDOFF:                       # step 11
        handoff.start_teacher(context)
        answer = run_steps(context)                                 # teacher, new budget
    if answer is None:
        answer = handoff.fallback_answer(context)
    memory.write(context, answer)                                   # if ok and there was an error along the way
    return answer


def run_steps(context):
    while context.calls < context.budget_end:
        step = policy.next_step(context, tools.offered(context.teacher))  # step 2
        context.calls += 1

        if step["error"]:                                           # tool call could not be read: rejected
            result = step["error"]
        elif guards.is_repeat(step, context):                       # same call (except submit): previous result is returned
            result = guards.repeat_note(step, context)
        elif step["tool"] in ("search_schema", "search_values"):
            result = search.run(step, context)                      # step 3 (also writes to the search notes)
        elif step["tool"] == "ask_user":
            result = ask_user.run(question, context)                # step 3 (also stores the clarification)
        elif step["tool"] == "execute_sql":
            result = run_query(sql, forecast, context)              # steps 4–7
        elif step["tool"] == "handoff":
            return None                                             # reason in context.handoff_reason
        elif context.teacher:
            return teacher_submit(step, context)                    # directly to the final check
        else:
            outcome = finish(sql, context)                          # steps 8–10
            if outcome["done"]:
                return context.answer(..., "ok")
            if outcome["handoff"]:
                return None                                         # low, second medium, or final check failed twice
            result = outcome["note"]                                # medium note or final check note → step 2

        context.add(step, result)
    return None                                                     # budget ran out
```

`run_query` calls, in order, `precheck.check`, if needed `precheck.needs_world_model` → `world_model.predict` → `gates.trusted` / `gates.audit`, then `precheck.run` and `compare`; `finish` calls `candidates`, `gates.confidence` and `final_check`.


## `config.py` constants

| Constant | Value | Place in the flow |
|---|---|---|
| Tool-call budget | 10 (also for the teacher). Rejected requests count, candidate executions do not | Step 2, 11 |
| `ask_user` limit | 5 per question (agent and teacher combined); deducted from the budget | Step 3 |
| Number of search results | 5 | Step 3 |
| Value index | Texts longer than 100 characters do not enter the index; in one search, at most 200 candidates from the index are ranked by similarity | Step 3 |
| `search_schema` description | Trimmed at 200 characters | Step 3 |
| Initial context | At most 16K tokens; if it overflows, the details of the tables that match the question least are shortened. Tokens are counted with the policy's tokenizer | Step 1 |
| All values in the profile | For columns with at most 30 distinct values | Step 1 |
| Value length in the profile | At most 40 characters; longer values are trimmed | Step 1 |
| Upfront value matching | The best 2 values for each word, or group of up to 3 words, in the question; groups that start or end with a stopword are not searched. Only values with similar spelling (difflib ≥ 0.8); the difference from `search_values` is that values merely containing the word are not counted. Against noise: single words shorter than 4 letters and table/column names are not searched, and the threshold for single words is 0.9 | Step 1 |
| Similar spelling threshold | `difflib` similarity at least 0.8 | Step 3 |
| Database memory | The 3 records most similar to the question (by word overlap) | Step 1 |
| Row ranges (forecast) | `0`, `1`, `2-10`, `11-100`, `100+` | Step 4, 7 |
| Expensive query | `estimate_cost` more than 1 million rows | Step 5 |
| Budget low | Remaining tool-call budget below 25% of the starting budget (in Mini-Interact, remaining bird-coins) | Step 5 |
| Prediction gate threshold | Confidence ≥ 0.9 for result type and result shape. The placeholder world model writes its confidence itself (0–1) | Step 6 |
| Audit share | 5% of trusted predictions are executed anyway | Step 6 |
| Timeout / row limit | 30 seconds / 100 rows | Step 7 |
| Result shown to the agent | At most 20 rows, at most 100 characters per cell | Step 7 |
| Context limit | 32K tokens; if exceeded, the oldest observations are reduced to a single line | Every step |
| First extra candidates | 2 | Step 8 |
| Total candidates | Filled up to 8 if there is no consensus (including the agent's SQL) | Step 8 |
| Candidate temperature | 0.8; each candidate is a separate sample from the same prompt | Step 8 |
| Confidence gate | High: 3/3 or ≥6/8 · Medium: 4–5/8 · Low: ≤3/8. The ratio is always out of 8; a filtered-out or failing candidate counts toward no group | Step 9 |
| Medium note | The 2 largest groups; for each, the representative SQL, number of candidates, columns, number of rows, first 3 rows | Step 9 |
| Medium repetition | At most 1 | Step 9 |
| Final check repetition | Handoff if it fails twice | Step 10 |
| Cache | Within the same question; the key is the SQL text with whitespace normalized. The repetition guardrail uses the same key (for `execute_sql` it ignores the forecast) | Step 5 |
| Policy and teacher generation | Temperature 0.7, top_p 0.8; thinking mode off | Step 2, 11 |
| Model request | Answer at most 1024 tokens; 300-second timeout per request; on a transient API error (429, 5xx, connection) 8 attempts, with the wait starting at 5 s and doubling each time | |
| Parallelism in evaluation | 8 questions at once (`EVAL_WORKERS`; the local server batches requests). 4 on the API: at 8 the provider returned 429 errors | Evaluation |
| Models | Currently all model calls go to `Qwen/Qwen3.5-0.8B` on a local `mlx_lm.server` (only to see that the flow works; no seed is sent, because the server does not batch requests with a seed). For development measurements (stages 4–34), cheap Qwen models on OpenRouter: `qwen/qwen3.5-9b` in place of the policy (provider DeepInfra, bf16), teacher and user simulator `qwen/qwen3.6-27b`, placeholder world model `qwen/qwen3.5-9b` (via prompt). For the paper's numbers (stage 35), local models: policy `Qwen3.5-4B` (`mlx-community/Qwen3.5-4B-bf16`), a local Qwen as the placeholder world model (which one is chosen by measurement in stage 35; if training is done, `Qwen3.5-0.8B` + LoRA), teacher and user simulator `Qwen3.6-27B` (4-bit). MLX versions; if no ready MLX version exists, it is converted with `mlx_lm.convert` | |
| Bird-coin (cost simulation) | Only when `SIMULATE_COST` is on. Costs as in BIRD-Interact: `execute_sql` 1, `ask_user` 2, `submit` 3, malformed call 0.2; `search_schema` / `search_values` 0.5, `handoff` 0. Start: 6 + 2 × number of ambiguities + the user's patience (6). The tool-call budget also stays in effect; whichever runs out first. The teacher gets a new bird-coin budget | Step 2, 5 |
| Simulated query cost | When `SIMULATE_COST` is on, `estimate_cost` × 1000: the expensive-query path (step 6) is exercised on SQLite too | Step 5 |
| Threshold measurement | `GATE_CHOICES` = 0.5, 0.7, 0.8, 0.9, 0.95; the world model measurement gives the number of trusted and correct predictions at each threshold | Step 6 |
| Seeds | 0, 1, 2. No seed is sent on the local server; there, seeds only change the audit decision, and repetitions are independent samples | Evaluation |
| Stage check subset | A fixed set of 50 questions selected from BIRD dev with seed 0 | Evaluation |

**Ablation flags:**

| Flag | Default | What happens when off |
|---|---|---|
| `USE_AGENT_FORECAST` (step 4) | On | `execute_sql` does not ask for a forecast, no surprise note. In the final check an empty result never passes |
| `USE_CANDIDATES` (step 8) | On | Steps 8 and 9 are skipped; the agent's SQL goes directly to the final check |
| `USE_HANDOFF` (step 11) | On | The `handoff` tool is not offered; at every point where a handoff is needed, the fallback answer is returned |
| `USE_DB_MEMORY` (step 1) | On | Database memory is neither read nor written |
| `USE_ASK_USER` (step 3) | On | The `ask_user` tool is not offered. Turned off only for the comparison measurement against the literature |
| `USE_WORLD_MODEL` (step 6, 8) | On (from stage 27 on) | Question 4 of step 5 is not asked, step 6 never runs, and no world model filtering is done in step 8 |
| `SIMULATE_COST` | Off | The budget is only the number of tool calls, and the query cost is `estimate_cost` itself. In Phase 2 (stage 32) it is turned on with `evaluate.py --simulate-cost` |

The rule "the final answer is always really executed" has no flag; it is never turned off.

These are starting values; they are tuned by measurement in Phase 2.

## Record formats

**`results/<experiment>_seed<n>.jsonl`** (one file per experiment and seed, e.g. `results/asama18_candidates_seed0.jsonl`):
- The first line is the experiment itself: experiment name, seed, dataset (`bird` / `mini_interact`) and split, whether it is a subset, `--limit`, number of questions, all `config.py` values (including model names and flags) and the prompt texts.
- Each following line is one question: `question_id`, `db_id`, `sql` (the answer), `label`, `answered_by` (agent / teacher), `correct` (empty if there is no correct SQL), `tool_calls`, `executions` (number of real executions), `handoff_reason` (empty if there was no handoff), `steps` (each tool call and observation), `prompt_tokens`, `completion_tokens`, `cost` (dollars), `seconds`. If the gold SQL fails, `gold_error` is also written; if the model API does not answer, `error` is written. The number of forecasts and hits (`forecasts`, `forecast_hits`), the number of candidates generated (`candidates`), the number of calls to the world model (`world_model_calls`), the `ask_user` questions and their answers (`clarifications`) and, when `SIMULATE_COST` is on, the remaining bird-coins (`coins_left`) are also written; the `by` field of each step in `steps` says whether it was the agent or the teacher.

**`experience/log.jsonl`** (one line per real execution and per world model prediction): question id, split, database (`db_id` and `db_path`), engine and dialect, who executed it (agent / candidate / teacher), SQL, the agent's forecast, the world model's prediction, a summary of the real result (type, number of columns, row range, result key; empty for a trusted prediction since the query was not executed), whether the forecast was a hit, whether the prediction was a hit, duration, model name, seed. Only `split = train` lines go into training.

**`experience/memory/<db_id>.jsonl`** (database memory): question, first faulty SQL, the note it received (error or surprise note), answer SQL.

## Build order

Each stage adds a single piece. At the end of each stage:
1. `pytest tests/` passes.
2. In stages that use a model, 1–2 real questions are tried with `run.py`. `evaluate.py` is run on the 50-question subset (seed 0) only at the last stage of each section (B1: 8, B2: 16, B3: 21, B4: 25, B5: 28; stages 5–7 were also measured one by one), and the result is written under `results/`; this keeps the cost low and shows the contribution of each section. What the section's other stages would measure (e.g. the forecast hit rate) is looked at in this final measurement. On 50 questions, a difference of 1–3 questions is chance. These numbers are only for tracking progress and do not go into the paper.
3. The user is told in 2–3 sentences what was done and how it was tested; once the user approves, the next stage starts.

### Phase 1-A: Foundation (no model)

| # | What is added | Files | How it is tested |
|---|---|---|---|
| 1 | Database layer | `config.py`, `db/sqlite_db.py` | On a small test database: a write query is rejected, the 100-row limit works, `row_count` is correct, and `result_key` stays the same when the same rows come in a different order. It is checked that the Python to be installed has FTS5 |
| 2 | BIRD dev data and scoring | `evaluate.py` (data loading + scoring) | BIRD dev is downloaded together with the user. Each gold SQL comes out correct when compared with itself; gold SQLs that time out are listed |
| 3 | Initial context | `harness/prepare.py` | The context of a BIRD database is printed: schema, descriptions, foreign keys, column profiles, evidence. On the largest database, if the context exceeds 16K tokens, it is checked that shortening works |

### Phase 1-B1: First working agent

Goal: the model runs and the agent answers a single question end to end.

| # | What is added | Files | How it is tested |
|---|---|---|---|
| 4 | Running the model | `requirements.txt` (after asking the user), `agent/llm.py` | Qwen3.5-4B is loaded locally and produces a short answer; memory and speed are measured. During development the same requests go to the OpenRouter API |
| 5 | Single SQL without tools (first baseline) | `agent/prompts.py`, `agent/policy.py` (`write_sql`) | The model writes a single SQL from the context, the harness executes it. First accuracy number on 50 questions |
| 6 | Agent loop skeleton and `submit` | `agent/policy.py` (`next_step`), `agent/loop.py`, `harness/guards.py` (rejection of malformed output), `harness/handoff.py` (fallback answer only), `run.py` | The agent's only tool is `submit`. The tool call is read, malformed output is rejected, and when the budget runs out the fallback answer is returned. A single question runs end to end with `run.py`; on 50 questions it should not be worse than stage 5 |
| 7 | `execute_sql` tool | `agent/loop.py` (`run_query`) | The agent tries the SQL and sees the result, then calls `submit`. Compared with stage 6 on 50 questions |
| 8 | Pre-check: read-only and `EXPLAIN` | `harness/precheck.py` | A write query and a nonexistent column are rejected without execution; the error returns to the agent with a clear note. B1's 50-question measurement |

### Phase 1-B2: Strengthening the trial loop

Goal: the agent does not spin in place, finds the information it needs and sees its mistake through its forecast. Each guardrail and each tool is a separate stage.

| # | What is added | Files | How it is tested |
|---|---|---|---|
| 9 | Guardrail: no repetition, and cache | `harness/guards.py`, `harness/precheck.py` (cache) | The same SQL is sent twice (even with a different forecast): the second is not executed, a note is returned, the budget goes down (except `submit`) |
| 10 | Guardrail: trimming long results | `harness/guards.py` | A 100-row result goes to the agent as 20 rows plus the total row count |
| 11 | Guardrail: compressing the context | `harness/guards.py` | When the context exceeds 32K tokens, the oldest observations are reduced to a single line |
| 12 | `search_values` tool | `harness/search.py` (value search) | A search for "Los Angles" finds `city = 'Los Angeles'` |
| 13 | `search_schema` tool | `harness/search.py` (schema search) | A search for "telefon" finds the `schools.Phone` column. Its contribution on BIRD may be small |
| 14 | Value matching in step 1 | `harness/prepare.py` | When "Los Angles" appears in the question, the match shows up in the step 1 context |
| 15 | Agent forecast and surprise note | `harness/compare.py`; `USE_AGENT_FORECAST` | A request without a forecast is rejected; a forecast that misses produces a surprise note |
| 16 | Experience log | `experience/log.py` | Each real execution is written as one line with the fields in "Record formats". B2's 50-question measurement: accuracy, number of search calls, forecast hit rate |

### Phase 1-B3: Verifying the answer

Goal: catch a wrong answer before it is sent.

| # | What is added | Files | How it is tested |
|---|---|---|---|
| 17 | Final check | `harness/final_check.py` | No candidates yet: `submit` goes directly to the final check. An empty result whose forecast was not "empty" does not pass; if it fails twice, the fallback answer is returned |
| 18 | Candidates: 2 extra candidates, grouping, selection | `harness/candidates.py`, `harness/search.py` (search notes); `USE_CANDIDATES` | The candidate prompt contains the search notes but not the agent's SQL. Grouping by result key, tie-breaking and representative SQL rules are tested. No gate yet: the answer of the largest group goes to the final check |
| 19 | Adaptive rule: filling up to 8 | `harness/candidates.py` | Stops if 3 agree, fills up to 8 if they diverge |
| 20 | Confidence gate: high and low | `harness/gates.py` | High → final check; low → fallback answer (no handoff yet) |
| 21 | Medium note | `harness/gates.py` | On medium, a summary of the two groups returns to the agent and the agent works once more; on a second medium, the fallback answer is returned. B3's 50-question measurement: accuracy and number of real executions |

### Phase 1-B4: Help and memory

Goal: when stuck, the agent turns to the teacher or the user, and learns from its mistakes.

| # | What is added | Files | How it is tested |
|---|---|---|---|
| 22 | Handoff | `harness/handoff.py` (teacher); `USE_HANDOFF` | The teacher comes from the API (the memory-fit measurement is in stage 35). The mandatory handoff points and the agent's `handoff` tool work; the teacher's `submit` goes to the final check |
| 23 | `ask_user`: terminal | `harness/ask_user.py`; `USE_ASK_USER` | With `run.py`, the agent asks on an ambiguous question; the answer enters the candidate prompt as a clarification. The limit of 5 per question is tested; it is checked that the agent does not ask on a question whose answer is in the schema |
| 24 | User simulator | `harness/ask_user.py` (simulator) | In `evaluate.py` the simulator answers. Tests check that it does not reveal the SQL or the answer, and that the gold SQL does not enter the agent's context |
| 25 | Database memory | `experience/memory.py`, `harness/prepare.py` (memory reading); `USE_DB_MEMORY` | In a test, a question that goes error → fix → `ok` writes a record. The next similar question on the same database sees this record in its context. B4's 50-question measurement: accuracy, handoff rate, number of `ask_user` calls |

### Phase 1-B5: World model (placeholder)

Goal: the world model path of the flow (step 6 and the filtering in step 8) works without waiting for training. The world model is an untrained LLM that behaves like a world model through a prompt (placeholder).

| # | What is added | Files | How it is tested |
|---|---|---|---|
| 26 | Placeholder world model and its measurement | `world_model/predict.py`, `agent/prompts.py` (world model prompt), `harness/compare.py` (comparing the prediction) | In a test (with a fake model) the prediction and the confidences are read, and malformed output counts as "don't know" (confidence 0). The world model predicts the real executions in the experience log of the 50 questions: how often result type and shape were a hit, and what percentage of those it gave confidence ≥ 0.9 are correct. Measurement only; it makes no decisions yet |
| 27 | Prediction gate and audit | `harness/precheck.py` (question 4), `harness/gates.py` (prediction gate); `USE_WORLD_MODEL` | Three paths are tested: trusted → the prediction returns to the agent labeled "prediction"; untrusted → real execution; audit → executed even though trusted. It is checked that the final answer is always really executed |
| 28 | Candidate filtering with the world model | `harness/candidates.py` | If an expensive candidate is confidently predicted to "error" or "return empty", it is dropped without execution; tested. B5's 50-question measurement: accuracy, number of real executions, how many times the world model was called |

### Phase 1-B6: Phase 1 results

Goal: the first large measurement of the full system and the contribution of each piece. Taken with the API models; it shows progress and the direction of the ablations. The paper's numbers are taken with local models in stage 35.

| # | What is added | Files | How it is tested |
|---|---|---|---|
| 29 | Phase 1 results | `evaluate.py` | Full BIRD dev, 3 seeds. Then an ablation table by turning off each flag one at a time |

### Phase 2: Cost simulation

Goal: test the world model and `ask_user` in a setting where executing and asking the user are costly.

| # | What is added | Files | How it is tested |
|---|---|---|---|
| 30 | Mini-Interact data (300 SELECT tasks; `data/mini_interact/`, `hf download birdsql/mini-interact --repo-type dataset`) | `mini_interact.py`, `evaluate.py` (`--dataset mini_interact`), `harness/descriptions.py` (column meanings) | In a test, a task turns into a question, the knowledge base item hidden by the task does not enter the evidence, and the correct SQL file is read if present. The correct SQLs are not in the public files (they are requested from bird.bench25@gmail.com); without them the questions run but are not scored |
| 31 | Mini-Interact's own user simulator | `harness/ask_user.py`, `agent/prompts.py` | In a test, the two steps (encoder, decoder) run; the ambiguity notes are in the simulator's prompt and not in the agent's messages |
| 32 | Cost simulation: bird-coin budget, the "budget low" rule with bird-coins, simulated query cost | `harness/cost.py`; `SIMULATE_COST` (`--simulate-cost`) | In a test, the loop stops if the bird-coins run out first; the "budget low" and "expensive" decisions look at the simulated values |
| 33 | Threshold measurement and Phase 2 results | `world_model/predict.py` (threshold table), `report.py` | Mini-Interact with `--simulate-cost`, 3 seeds. The threshold is chosen with the records of the train split; the measurement on dev records is for viewing only |

### Phase 3

| # | What is added |
|---|---|
| 34 | DuckDB adapter (`db/duckdb_db.py`) or scaled-up BIRD databases; real latency measurement |

### Moving to local models

| # | What is added | How it is tested |
|---|---|---|
| 35 | Local models and the paper's numbers | The address and model names in `config.py` are switched to the local server (commands in CLAUDE.md). It is measured that the policy (4B), the teacher (27B, 4-bit) and the placeholder world model fit in memory together, and how fast they are. Full BIRD dev and Mini-Interact, 3 seeds, ablation table |

### Training (optional)

Done after the system works end to end and after stage 35, if time allows. Before each stage, it is measured which training stages fit on this machine; for a stage that does not fit, the user is asked.

| # | What is added | How it is tested |
|---|---|---|
| 36 | Collecting the world model's training data (`world_model/collect.py`) | BIRD train SQLs and a subset of SynSQL-2.5M are executed, and result type / shape / values labels are extracted; the train lines of the experience log are added. The data is balanced by result type and complexity. Dev SQL never goes in |
| 37 | World model training and calibration (`world_model/predict.py`, `training/`) | Plain SFT with LoRA; the trained model replaces the placeholder. On train databases not seen in training, are at least 95% of the predictions called trusted correct? If not, the threshold is raised |
| 38 | Collecting teacher traces | The teacher solves BIRD train inside the harness; only traces verified against the gold are kept |
| 39 | SFT (LoRA) | Over the whole trajectory, with observations masked out of the loss. Compared with the untrained policy on 50 questions |
| 40 | On-policy distillation | First it is verified that the Qwen3.5 and Qwen3.6 tokenizers are the same; if not, OLIVE is used |
| 41 | RL | DAPO; the main reward is execution accuracy, alongside the forecast reward ([RESEARCH.md](RESEARCH.md) section 9) |
| 42 | Dyna-style imagination loop | Added to RL: one-step imagination, the reward always from real execution |
| 43 | Promotion gate and new results | The new policy is put into use if it is not worse than the old one. Full BIRD dev, 3 seeds |

## Diagram

The flow diagram is generated with `docs/diyagram/akis_diyagrami.py`; how to use it is written at the top of that file. If the flow changes, the diagram and [AGENTIC_FLOW.md](AGENTIC_FLOW.md) are updated together.
