# Predict – Gate – Settle (PGS)

Turkish original: [../AGENTIC_FLOW.md](../AGENTIC_FLOW.md)

**Agentic Text-to-SQL with an agent loop, a final check and handoff.**

A small model solves the question with tools: it searches for values, tries SQL, looks at the result and fixes it. The small model submits the SQL query it chooses as the answer; the answer passes a final check, and every answer that is returned has actually been executed. If the small model makes no progress or gets stuck, the task is handed over to a large model (handoff). The literature behind the design is in [RESEARCH.md](RESEARCH.md); the structure of the code is in [CODE_STRUCTURE.md](CODE_STRUCTURE.md).

## Flow

**In short:** question → initial context (1) → agent loop: search for values (3), try SQL (4–6) → `submit` → final check (7) → answer. If the small model gets stuck, the large model takes over (8).

![PGS flow](../PGS_flow_EN.png)

| Color | Component |
|---|---|
| 🟦 Blue | Small model |
| 🟩 Green | Harness (no LLM) |
| 🟥 Red | Real database |
| 🩵 Turquoise | Large model |
| 🟪 Purple | Harness decision (final check) |
| ⬜ Dashed | After the question: experience log, agent training (later) |
| ⚪ White, rounded | Outside the system: the user's question and the returned answer |

Arrow colors: **black** tool call, **blue** observation returned to the agent, **purple** decision result, **turquoise** handoff, **dashed** after the question.

## Terms

| Term | Meaning |
|---|---|
| Small model | The small model that solves the question step by step (currently `Qwen3.5-0.8B`); the model to be trained on the experience log |
| Large model | The large model that checks the small model's answer and solves the question from scratch when the small model gets stuck (currently `Qwen3.5-9B`) |
| Agent | The model in the loop that solves the question by calling tools: first the small model, after a handoff the large model |
| Tool call | The single request the agent makes in one turn (e.g. `execute_sql`) |
| Observation | The result returned to the agent after a tool call |
| Tool-call budget | The maximum number of tool calls for one question (10) |
| Trial loop | The loop in which the agent searches, tries, looks at the result and fixes (steps 2–6) |
| Column profile | A summary of a column: type, NULL ratio, most frequent values (all of them for columns with few values), min and max if numeric |
| Harness | The plain code around the agent: runs the tools, manages the checks and the handoff. No LLM inside |
| Pre-check | The cheap checks the harness makes before a SQL query runs: is it read-only, does `EXPLAIN` fail, is it in the cache (step 5) |
| Cache | The stored results of SQL queries that already ran for the same question; the same SQL is not run again |
| Final check | The last check before the answer is returned, two gates: does the submitted SQL run without error, does the large model find it correct (step 7) |
| Handoff | Handing the task over to the large model |
| Evidence | The short hint text BIRD gives with each question (e.g. "returned = `status = 'returned'`") |
| Result key | The key used to compare query results. All rows of the result are taken as a set: row order and duplicate rows do not matter, column order does (BIRD's official rule). An answer is correct if its result key equals the correct SQL's |
| Fallback answer | The answer returned when no answer is accepted: the last SQL the small model or the large model submitted that runs without error; it carries the `fallback` label and has low confidence |
| Label | The label of the returned answer: `ok` (accepted), `fallback` (not accepted, but a submitted SQL that runs exists; low confidence), `no_answer` (no such SQL; an error message is returned instead of SQL) |
| Base | The tool-free single SQL used for comparison: the model sees the step 1 context and writes one SQL query in one go (`baseline.py`) |
| Memory | A small database (`experience/memory.sqlite`) of questions solved correctly before (question, evidence, SQL) with their embeddings; the 3 most similar to a new question are added to the step 1 context |
| Experience log | The record of each question's whole conversations (every step of the small model and, after a handoff, of the large model), the answer and whether it is correct; the small model's training data comes from here |
| Split | A part of the data: train or dev (evaluation). Only train is used for training |
| SFT | Training a model to imitate correct examples |
| On-policy distillation | Training the small model on its own attempts, corrected by the large model |
| RL | Training a model with rewards and penalties based on the outcome of its attempts |
| Guardrail | The harness rules that protect the agent: no repeated calls, long results are trimmed, the context is compressed when full |
| Temperature | The randomness in the model's reply: at 0 always the most likely reply, more varied as it grows |
| EXPLAIN | The database showing its plan for a query without running it. In SQLite it also catches syntax errors and missing tables/columns without running |
| Stage | A small numbered piece of work that adds a single part (CODE_STRUCTURE.md "Build order") |

## Components

- **Small model:** Decides which tool to call at each step. Currently the local `Qwen3.5-0.8B`; the target is `Qwen3.5-4B`. Used untrained for now; later it is trained inside the harness with the experience log.
- **Harness (plain Python, no LLM):** Runs the tools, makes the checks and the final check, decides on the handoff. It also applies the guardrails.
- **Database (SQLite, read-only):** `execute_sql`. The correct SQL never enters the agent's context; it is used only for scoring.
- **Large model:** Checks the small model's answer (step 7); after a handoff, solves the question from scratch with its own agent loop (step 8). Currently `Qwen3.5-9B` on the OpenRouter API; the target is a local `Qwen3.6-27B` (4-bit).

## The flow step by step

The numbers in the figure are these steps. The division of work is simple:
- **The agent** decides what to do: which tool, which SQL, when to `submit`.
- **The harness** decides everything else: the checks, the final check, the handoff.

Tool arguments and numeric limits are in [CODE_STRUCTURE.md](CODE_STRUCTURE.md).

### 1. Initial context

**Why:** Every search costs a tool call. If the information is given up front, the budget is left for trying.

The harness gives the agent:
- The question and, if any, the evidence.
- The schema: tables, columns, BIRD's column descriptions, foreign keys.
- Column profiles. For text columns the 10 most frequent values (all values for columns with at most 10 distinct values, e.g. `status`); the agent finds the remaining values with `search_values` if needed. For text columns where almost every row is different (e.g. names, codes) only 3 samples: ten names do not teach a spelling, they only make the context longer. For columns whose values are mostly long free text (e.g. comments) no samples; trimmed sentences do not teach a spelling. A value description that repeats the column description is not written. For numeric columns only the minimum and maximum. Names with spaces, special characters or SQL keywords (e.g. the `` `order` `` table) are shown in backticks, and the agent writes them that way.

- **Similar solved questions (memory):** At most 3 questions solved correctly before that are most similar to the question, with their SQL; after the schema, before the evidence and the question. Their heading says "they may come from another database, use them if they help"; the model decides whether to use them. Similarity is measured with the embedding (`Qwen3-Embedding-0.6B`) of the question + evidence text; those below the threshold are not added. What counts as correct: in BIRD train, those correct according to the gold (`correct`); in evaluation and in use, those the large model approved (`label = ok`), because the gold is not known there. In evaluation only train and questions solved earlier in the same run are examples; a run is identified by its name (`--name`) and start time: when the same questions are measured again, even under the same name, the earlier run's answers are not visible. Since questions run in parallel, which same-run examples a question sees depends on the order they finish; the examples shown are written to the result row (`memory_examples`). The large model that checks the answer (step 7) does not see these examples.

In BIRD dev this context is at most ~12K tokens, well below the model's context limit.

→ 2

### 2. The agent decides what to do

The agent makes a single tool call each turn. It decides itself what to do and in which order; the prompt only describes the tools and what they are for. The agent can start with a sample query, explore the data first (e.g. which values a column holds or how two tables are linked), or search for a value first.
- If it wants to try a query or explore the data → `execute_sql` → 4
- If it does not know how a value is written in the database → `search_values` → 3
- If a query it ran answers the question → `submit` with that query → 7. The queries it ran in between (checks, fixes) do not affect the answer

After every observation the small model returns here. At each step the small model takes its most likely reply (temperature 0). If its last call was rejected or was a repeat, it would give the same reply to the same input again, so the next step is sampled (temperature 0.7). Every tool call takes one off the budget (at most 10). Rejected requests and outputs that cannot be read as a tool call also count; the error is returned to the small model. ```sql fences around the SQL argument and leading `--` comment lines are removed; small models often add them. The number of tool calls left is written under every result; in the last 2, a reminder is added too: "if a query you ran answers the question, submit it now". If the small model has not run any SQL that returned rows in its first 6 tool calls, or 5 of its calls in a row were wasted (unreadable, repeated or rejected by the pre-check; a call that is not wasted resets the count), it is considered not to be making progress and the harness hands over to the large model right away → 8; no steps or money are wasted. If the budget runs out, the harness also forces a handoff → 8.

**Guardrails.** Small models often make certain typical mistakes; so that these do not break the system, the harness applies three simple rules at every step (DualSQL).
1. **No repeats:** If the same call (same tool, same arguments; whitespace and a trailing `;` in SQL do not matter) comes a second time, it is not run; a "you already tried this" note and the earlier result are returned, and the budget still goes down. If the same call is repeated a third time, the small model is considered stuck and the harness hands over → 8. Only its own calls count: the large model does not see the small model's conversation, so a call the small model made is not a repeat for the large model; it is run. `submit` does not count as a repeat; the final check limits it (step 7).
2. **Long results are trimmed:** The small model sees at most 20 rows, with the total number of rows next to them. A note is added below: "you do not need to see every row; if this query answers the question, submit it as it is, the answer keeps all rows". Otherwise the model may try to page through the rows (`LIMIT … OFFSET`) and run out of budget. The large model's check does not see this note.
3. **The context is compressed:** If the conversation exceeds 32K tokens, the oldest results shrink to a one-line summary in the request sent to the model (e.g. "Columns: name | 358 rows"). The experience log gets the conversation unshortened.

### 3. Searching for values: `search_values`

Since step 1 is rich, it is rarely needed. `search_values` finds in which column, and as which value, a word appears in the database, including similarly spelled values. Example: "Los Angles" → `city = 'Los Angeles'`. Words shorter than 3 letters (e.g. "UK") are searched by exact match, ignoring upper/lower case. If a text with several words is not found, each word is searched separately: in "Lewis Hamilton" the first and last names are in different columns. At equal similarity, a value with the exact same letters comes first ('Hamilton', not 'hamilton'). If it finds no value and the word looks like a column name, it names those columns; small models also look for column names with this tool. Example: "Consumption" → the column `yearmonth.Consumption`.

Search cannot find everything: if the question says "iade" (Turkish for "returned") and the database says `'returned'`, they do not match. In this case the evidence usually provides the match; if it does not, the agent gets an empty result with the wrong value; the note under the empty result steers it to check the value's spelling with `search_values`.
→ 2

### 4. The `execute_sql` request

The agent sends the SQL it wants to try with `execute_sql(sql="SELECT ...")`.
→ 5

### 5. Pre-check

**Why:** To catch a broken query the cheap way, without running it.

The agent's SQL queries and the final check go through here. The harness asks three questions in order:
1. **Does it write?** If it does not start with `SELECT` or `WITH`, it is rejected. Example: `DELETE FROM orders`.
2. **Is it broken?** `EXPLAIN` catches syntax errors, missing tables and columns without running the query. SQLite normally treats a "double-quoted" name it cannot find as text (`"Free Meal Count" > 10` runs without error but wrongly); in the pre-check this is off, and SQLite asks "should this be a string literal in single-quotes?". The note also says what is needed to fix the error: which tables have the missing column (if no column has that name, columns with a similar name, e.g. `Free Meal Count` → `` `Free Meal Count (K-12)` ``), the alias of a table that was written by its own name after being given an alias, and the real columns of the tables in the query; for a missing table, the tables of the database. Example: `no such column: cc.client_id` → "client_id exists in: client, disp. Tables in your query and their columns: card (cc): card_id, disp_id, type, issued; ...".
3. **Did it already run (cache)?** If so, it is not run again; the stored result is used. Example: the final check runs again a SQL query the agent already ran.

The note of a query stopped at 1–2 is returned to the agent (→ 2).
→ 6

### 6. Real execution

The query runs read-only on the database: exploration and trial queries for at most 50 seconds, the main query submitted as the answer for at most 200 seconds. If an exploration query times out, the agent is told it can submit it if it answers the question; once submitted, it runs again with the long limit. A query that returns more than 1 million different rows (e.g. a missing join condition; repeated rows do not count, scoring looks at the set of rows) is stopped with an "add a join condition or a filter" error; the largest correct result in BIRD dev is ~278 thousand rows. The real result is returned to the agent: the columns, the number of rows, at most 20 rows, or the error message. If the result is empty, or its single row is only 0 or NULL (e.g. `COUNT(*)` = 0 with a misspelled value), a note is added under it: "if the query filters on a text value, check how it is written with `search_values`"; a misspelled value is the most common cause. Such a result does not count as returning rows for the progress limit (step 2).
→ 2

> Steps 2 → 6 are the agent's **trial loop**: search, try, look at the result, fix.

### 7. `submit` → final check

The agent sends the SQL it chooses as the answer with `submit(sql="SELECT ...")`; the queries it ran in between do not affect the answer. Before the answer is returned, it passes two gates:
- **Is it read-only, do the tables and columns exist, does it run without error?** (steps 5–6; if the agent ran this SQL before, the result comes from the cache). An answer that gives an error does not pass. An empty result passes.
- **Does the large model find the answer correct?** A SQL query that runs can still be wrong. The large model checks every answer, whether or not there was a handoff. In a separate, clean context it sees its own system prompt, the step 1 context (schema, evidence, question), the SQL and its result (without the `search_values` note meant for the small model); it checks two things: first the columns (what the question asks for, and whether every column of the result is asked for; an id, a name or a count added only to identify or check the answer makes it wrong), then the rows (tables, joins, conditions, values). It reads the question and the evidence literally: a query that adds something they do not state (another column for the same idea, `COUNT(DISTINCT ...)` instead of `COUNT(...)`, a different denominator, extra grouping or rounding) is wrong even if it looks more sensible; BIRD's correct answers read the question literally. Its reply is a JSON object, first the reason and then the decision: `{"reason": "columns: the question asks only for the id, the result also has name; rows: ...", "correct": false}`. The reason comes before the decision, so the model thinks before it decides. A reply that cannot be read does not count as approval. If the small model's answer is judged wrong, the task goes to the large model → 8; the reason stays in the small model's conversation (experience log). After a handoff, the large model's own `submit` goes through the same check; if it is judged wrong, the task goes to no one: the reason goes back to the large model as a note ("the answer was judged wrong: <reason>; fix it"), and it counts as a final check try. If the large model's API cannot be reached after several tries, the small model's answer is accepted so that it is not lost; the result record says the check could not be done (`large_model_error`).

Passed → **the answer is returned ✔** (label `ok`). Did not run without error → the reason is returned as a note → 2. If it fails a second time → 8.

### 8. Handoff

The harness does the handoff: no progress in the first 6 steps or 5 wasted calls in a row, the same call repeated 3 times, the final check failing twice, the large model not approving the small model's answer, the budget running out, or the small model not responding (e.g. the local server ran out of memory; the reason is written to `handoff_reason`).
- The large model solves the question from scratch: it does not see the small model's conversation and starts with only the system prompt and the step 1 context. The small model's repeats and wrong attempts lead the large model astray too. The small model's conversation is kept for the experience log.
- It runs the same agent loop with the same prompt, the same budget (10 tool calls) and the same tools as the agent (steps 2–7). Like the agent, it decides what to do itself: it may first try a query, explore the data or search for a value. It takes its first step with temperature 0. In the final check it has its own 2 tries.
- The large model's `submit` goes through the final check like the small model's (step 7). If the final check fails twice again, the large model does not submit within its budget, or the large model's API cannot be reached (`large_model_error`), the fallback answer is returned.

**Fallback answer:** the last SQL the small model or the large model submitted that runs without error (`fallback`, low confidence). Example: the large model said "no" to the small model's answer but could not solve the question either; the small model's rejected SQL is returned. If nobody submitted such a SQL, there is no answer (`no_answer`): an error message that gives the reason is returned instead of SQL. Exploration queries and SQL that does not run are never an answer.
→ Answer ✔

**The returned answer:** the SQL (an error message if there is no answer), the label (`ok`, `fallback`, `no_answer`) and who found the answer (small model or large model).

### Two examples

**Example 1 ("Which category had the most returns in 2025?"):**
1 (evidence: returned = `status = 'returned'`) → 2 → 4 (SQL) → 5 → 6 (real result: 1 row) → 2 → 7 (final check passed) → ✔

**Example 2 (the same question, the agent writes a wrong column and a wrong value):**
1 → 2 → 4 → 5 (`no such column: o.state`; the note shows the real columns of the tables in the query) → 2 → 4 (fixed SQL) → 5 → 6 (empty result) → 2 → 3 (`search_values`: "returnd" → `status = 'returned'`) → 2 → 4 → 5 → 6 (1 row) → 2 → 7 → ✔

### After the question

**Experience log:** When a question ends, wherever it was run from (`run.py`, `evaluate.py` or an application in use), one line is written: the whole conversation the small model saw, after a handoff the large model's too (separately), the answer and the label. In evaluation, whether the answer is correct is also written (`split = dev`); in use there is no correct SQL, so this field stays empty (`split = use`), and the training signal there is the large model's solutions and the label. Records accumulate and are never deleted. Every question with an answer is also written to the memory; later questions can see it as an example (step 1).

**Small model training (later):** The small model is trained inside the harness it will be used in, with the records in the experience log. The method is not chosen yet: SFT (the large model's correct solutions), distillation (on-policy, off-policy or self-distillation) or RL (reward: whether the answer is correct); one of them or a mix. Only records from the train split are used for training.

## Design decisions

| Decision | Why | Basis |
|---|---|---|
| The final answer is always really executed | Whether an unexecuted SQL is correct cannot be known | — |
| The error note says what is needed to fix it | Small models fix an error only when what is wrong is written out clearly (e.g. the real columns of the tables in the query) | DualSQL |
| Temperature 0; sampling when stuck | The most likely reply gives a more accurate single SQL; but the same input always gets the same reply, so after a rejected or repeated call the next step is sampled | — |
| Results are compared with BIRD's official rule (result key) | "The same result" is defined in one place | BIRD |
| Step 1 gives as much information as possible (column descriptions, column profiles) | Every search costs a tool call. If the information comes up front, the budget is left for trying | DualSQL, HarnessSQL |
| The large model checks every answer, with a reason | A SQL query that runs can still be wrong, and a small model does not notice its own mistake. A single check looks at everything (including columns the question does not ask for); the JSON reply gives an easy-to-read decision and a reason, and the reason helps the large model fix its own answer | — |
| The fallback is only a submitted SQL | Since the agent can explore the data, the last query that ran may be an exploration query; a submitted SQL is the one somebody called "my answer". As it was not accepted, it is returned with low confidence under the `fallback` label | — |
| An agent that makes no progress hands over early | An agent that gets no rows in its first steps, or wastes its calls, usually cannot solve the question; an early handoff spends fewer tool calls for the same accuracy | — |
| The large model works freely, with the small model's prompt and in the same loop; its answer is checked too | The large model's conversations are the small model's training data: when the large model works with the prompt and tools the small model will see, the small model learns what to do in exactly its own situation. A rejection by the check lets the large model fix a mistake it missed (e.g. a missing `HAVING`) in the loop | HarnessSQL |
| Similar solved questions are added to the context (memory) | The SQL of a solved question shows the pattern of a similar question (a ratio, the largest, a join); when a similar question comes, the harness benefits from earlier solutions. In evaluation the large model's approval is used instead of the gold and other runs' answers are not visible, so the measurement involves no copying | DAIL-SQL, ReasoningBank |
| The large model starts from scratch with a full budget | A large model that took over the small model's conversation kept following the small model's repeats and wrong paths; with a clean context it runs its own loop and solves more questions | — |
| The agent is trained inside the harness | A model trained outside the harness drops from 30.4 to 9.6 when used in the harness | HarnessSQL |

## Build order

All 8 steps of the flow are done on BIRD. The next stages are in the "Build order" section of [CODE_STRUCTURE.md](CODE_STRUCTURE.md): agent training (method open: SFT, distillation, RL or a mix), then local models for the paper's numbers.

## Evaluation

- **BIRD dev:** 1,534 questions, with evidence. Accuracy is measured with BIRD's official rule: an answer is correct if its result key is the same as the gold SQL's.
- **Base:** the tool-free single SQL on the same questions (`baseline.py`); the agentic system is compared with it.
- **The large model's check is measured too:** the SQL it approves or rejects is scored as well; the summary says how many approvals were right and how many rejections were in fact of a correct answer.
- **For a test,** 10 questions are enough (`--limit 10`). Comparisons use at least 3 repeated runs (each with its own `--name`). The gold SQL runs once per question, with the main-query time limit (200 seconds).
- **Ablations:** When the contribution of a part is to be measured, a flag that turns that part off is added. `--no-memory`: no similar solved questions are added to the context, and nothing is written to the memory. `--no-handoff`: the large model never takes over and only checks the answer (step 7); if the small model's answer is judged wrong, the reason goes back to the small model as a note, the early handoff rules are off; the small model stops when the final check fails twice, on its third repeat of the same call or when the budget runs out, and if no answer is accepted the fallback answer is returned. The conversation and the result say "Stopped", not "Handoff"; `handoff_reason` is only the stop reason.

All thresholds are starting values; they are tuned by measurement.

## References

Only the works that directly shaped this design. The full survey is in [RESEARCH.md](RESEARCH.md).

**Pre-check**
- CYGNET ([2606.04645](https://arxiv.org/abs/2606.04645)): cheap structural checks first (step 5).
- CacheRL ([2606.14179](https://arxiv.org/abs/2606.14179)): a cache of real executions (step 5).

**Harness**
- HarnessSQL ([2610.12274](https://arxiv.org/abs/2610.12274)): training the small model inside the harness it will be used in; the tool set; the choice of large model (Qwen3.6-27B).
- DualSQL ([2609.18135](https://arxiv.org/abs/2609.18135)): guardrails (repeated calls, format errors).

**Handoff**
- OLIVE ([2609.36246](https://arxiv.org/abs/2609.36246)) and OVCSD ([2607.27937](https://arxiv.org/abs/2607.27937)): on-policy distillation (training the agent, later).

**Evaluation**
- BIRD ([2305.03111](https://arxiv.org/abs/2305.03111)): the main benchmark, evidence and the official result comparison rule.
