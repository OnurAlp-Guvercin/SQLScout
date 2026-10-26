# Predict – Gate – Settle (PGS)

Turkish original: [../AGENTIC_FLOW.md](../AGENTIC_FLOW.md)

**Agentic Text-to-SQL with an agent loop, a final check and handoff.**

A small policy agent solves the question with tools: it searches for values, tries SQL, looks at the result and fixes it. The agent submits the SQL query it chooses as the answer; the answer passes a final check, and every answer that is returned has actually been executed. If the agent makes no progress or gets stuck, the task is handed over to a large teacher LLM (handoff). The literature behind the design is in [RESEARCH.md](RESEARCH.md); the structure of the code is in [CODE_STRUCTURE.md](CODE_STRUCTURE.md).

## Flow

**In short:** question → initial context (1) → agent loop: search for values (3), try SQL (4–6) → `submit` → final check (7) → answer. If the agent gets stuck, the teacher takes over (8).

![PGS flow](../PGS_flow_EN.png)

| Color | Component |
|---|---|
| 🟦 Blue | Policy agent |
| 🟩 Green | Harness (no LLM) |
| 🟥 Red | Real database |
| 🩵 Turquoise | Teacher LLM |
| 🟪 Purple | Harness decision (final check) |
| ⬜ Dashed | After the question: experience log, agent training (later) |
| ⚪ White, rounded | Outside the system: the user's question and the returned answer |

Arrow colors: **black** tool call, **blue** observation returned to the agent, **purple** decision result, **turquoise** handoff, **dashed** after the question.

## Terms

| Term | Meaning |
|---|---|
| Policy agent | The small model that solves the question step by step |
| Tool call | The single request the agent makes in one turn (e.g. `execute_sql`) |
| Observation | The result returned to the agent after a tool call |
| Tool-call budget | The maximum number of tool calls for one question (10) |
| Trial loop | The loop in which the agent searches, tries, looks at the result and fixes (steps 2–6) |
| Column profile | A summary of a column: type, NULL ratio, most frequent values (all of them for columns with few values), min and max if numeric |
| Harness | The plain code around the agent: runs the tools, manages the checks and the handoff. No LLM inside |
| Pre-check | The cheap checks the harness makes before a SQL query runs: is it read-only, does `EXPLAIN` fail, is it in the cache (step 5) |
| Cache | The stored results of SQL queries that already ran for the same question; the same SQL is not run again |
| Final check | The last check before the answer is returned: does the submitted SQL run without error, has the agent seen its result (step 7) |
| Handoff | Handing the task over to the large teacher model |
| Evidence | The short hint text BIRD gives with each question (e.g. "returned = `status = 'returned'`") |
| Result key | The key used to compare query results. All rows of the result are taken as a set: row order and duplicate rows do not matter, column order does (BIRD's official rule). An answer is correct if its result key equals the correct SQL's |
| Fallback answer | The answer returned when no answer passes the final check: the last SQL that ran without error and returned rows; it carries the `fallback` label |
| Label | The label of the returned answer: `ok` (passed the final check), `fallback` (did not pass but a SQL that runs exists), `no_answer` (no SQL that returned rows) |
| Base | The tool-free single SQL used for comparison: the model sees the step 1 context and writes one SQL query in one go (`baseline.py`) |
| Experience log | The record of each question's whole conversation (every step of the agent and the teacher), the answer and whether it is correct; the agent's training data comes from here |
| Split | A part of the data: train or dev (evaluation). Only train is used for training |
| SFT | Training a model to imitate correct examples |
| On-policy distillation | Training the student model on its own attempts, corrected by the teacher |
| RL | Training a model with rewards and penalties based on the outcome of its attempts |
| Guardrail | The harness rules that protect the agent: no repeated calls, long results are trimmed, the context is compressed when full |
| Temperature | The randomness in the model's reply: at 0 always the most likely reply, more varied as it grows |
| EXPLAIN | The database showing its plan for a query without running it. In SQLite it also catches syntax errors and missing tables/columns without running |
| Seed | A number that fixes randomness; repeating with different seeds shows that a result is not luck |
| Stage | A small numbered piece of work that adds a single part (CODE_STRUCTURE.md "Build order") |

## Components

- **Policy agent:** Decides which tool to call at each step. Currently the local `Qwen3.5-0.8B`; the target is `Qwen3.5-4B`. Used untrained for now; later it is trained inside the harness with the experience log.
- **Harness (plain Python, no LLM):** Runs the tools, makes the checks and the final check, decides on the handoff. It also applies the guardrails.
- **Database (SQLite, read-only):** `execute_sql`. The correct SQL never enters the agent's context; it is used only for scoring.
- **Teacher LLM:** Used only after a handoff; continues where the agent left off. Currently `Qwen3.5-9B` on the OpenRouter API; the target is a local `Qwen3.6-27B` (4-bit).

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
- Column profiles. For text columns the 10 most frequent values (all values for columns with at most 10 distinct values, e.g. `status`); the agent finds the remaining values with `search_values` if needed. For numeric columns only the minimum and maximum.

In BIRD dev this context is at most ~12K tokens, well below the model's context limit.

→ 2

### 2. The agent decides what to do

The agent makes a single tool call each turn. The prompt gives it an order of work: first write and run the SQL query that answers the question (do not start with an exploratory query), look at the result, fix it if needed, and submit when the result answers the question.
- If it wants to try the query that answers the question → `execute_sql` → 4
- If it does not know how a value is written in the database → `search_values` → 3
- If a query it ran answers the question → `submit` with that query → 7. The queries it ran in between (checks, fixes) do not affect the answer

After every observation the agent returns here. At each step the agent takes its most likely reply (temperature 0). If its last call was rejected or was a repeat, it would give the same reply to the same input again, so the next step is sampled (temperature 0.7). Every tool call takes one off the budget (at most 10). Rejected requests and outputs that cannot be read as a tool call also count; the error is returned to the agent. The number of tool calls left is written under every result; in the last 2, a reminder is added too: "if a query you ran answers the question, submit it now". If the agent has not run any SQL that returned rows in its first 4 tool calls, it is considered not to be making progress and the harness hands over to the teacher right away → 8; the teacher starts with a short history, and no steps or money are wasted. If the budget runs out, the harness also forces a handoff → 8.

**Guardrails.** Small models often make certain typical mistakes; so that these do not break the system, the harness applies three simple rules at every step (DualSQL).
1. **No repeats:** If the same call (same tool, same arguments) comes a second time, it is not run; a "you already tried this" note and the earlier result are returned, and the budget still goes down. If the same call is repeated a third time, the agent is considered stuck and the harness hands over → 8. Only its own repeats count: the teacher repeating a call the agent made does not make the teacher stuck. `submit` does not count as a repeat; the final check limits it (step 7).
2. **Long results are trimmed:** The agent sees at most 20 rows, with the total number of rows next to them.
3. **The context is compressed:** If the conversation exceeds 32K tokens, the oldest results shrink to a one-line summary (e.g. "Columns: name | 358 rows").

### 3. Searching for values: `search_values`

Since step 1 is rich, it is rarely needed. `search_values` finds in which column, and as which value, a word appears in the database, including similarly spelled values. Example: "Los Angles" → `city = 'Los Angeles'`. If it finds no value and the word looks like a column name, it names those columns; small models also look for column names with this tool. Example: "Consumption" → the column `yearmonth.Consumption`.

Search cannot find everything: if the question says "iade" (Turkish for "returned") and the database says `'returned'`, they do not match. In this case the evidence usually provides the match; if it does not, the agent gets an empty result with the wrong value; the note under the empty result steers it to check the value's spelling with `search_values`.
→ 2

### 4. The `execute_sql` request

The agent sends the SQL it wants to try with `execute_sql(sql="SELECT ...")`. If it writes the SQL in a ` ```sql ` block in its message instead of a tool call, that is run the same way.
→ 5

### 5. Pre-check

**Why:** To catch a broken query the cheap way, without running it.

The agent's SQL queries and the final check go through here. The harness asks three questions in order:
1. **Does it write?** If it does not start with `SELECT` or `WITH`, it is rejected. Example: `DELETE FROM orders`.
2. **Is it broken?** `EXPLAIN` catches syntax errors, missing tables and columns without running the query. The note also says what is needed to fix the error: which tables have the missing column, the alias of a table that was written by its own name after being given an alias, and the real columns of the tables in the query; for a missing table, the tables of the database. Example: `no such column: cc.client_id` → "client_id exists in: client, disp. Tables in your query and their columns: card (cc): card_id, disp_id, type, issued; ...".
3. **Did it already run (cache)?** If so, it is not run again; the stored result is used. Example: the final check runs again a SQL query the agent already ran.

The note of a query stopped at 1–2 is returned to the agent (→ 2).
→ 6

### 6. Real execution

The query runs read-only on the database (at most 30 seconds). The real result is returned to the agent: the columns, the number of rows, at most 20 rows, or the error message. If the result is empty, a note is added under it: "if the query filters on a text value, check how it is written with `search_values`"; a misspelled value is the most common cause of an empty result.
→ 2

> Steps 2 → 6 are the agent's **trial loop**: search, try, look at the result, fix.

### 7. `submit` → final check

The agent sends the SQL it chooses as the answer with `submit(sql="SELECT ...")`; the queries it ran in between do not affect the answer. The last check before the answer is returned:
- **Is it read-only, do the tables and columns exist, does it run without error?** (steps 5–6; if the agent ran this SQL before, the result comes from the cache). An answer that gives an error does not pass. An empty result passes.
- **Had the agent seen this SQL's result?** The agent cannot submit an answer whose result it has not looked at. If it had not seen it, the harness runs the query, shows the result to the agent and says "if it answers the question, submit it again" → 2. This does not count as a failure. Example: if the agent wrote `WHERE County = 'Alemeda'` without trying it, it sees the empty result here and fixes the value. Since the agent is shown at most 20 rows, large results are not a problem.

Passed → **the answer is returned ✔** (label `ok`). Failed the final check → the reason is returned to the agent as a note → 2. If it fails a second time → 8.

### 8. Handoff

The harness does the handoff: no progress in the first 4 steps, the same call repeated 3 times, the final check failing twice, or the budget running out.
- The teacher does not start from scratch; it continues where the agent left off: it sees the whole conversation and the reason for the handoff.
- It works with a new budget half the size of the agent's (5 tool calls) and the same tools (steps 2–7).
- The teacher's `submit` goes through the final check like the agent's (step 7). If the final check fails twice again, or the teacher does not submit within its budget, the fallback answer is returned.

**Fallback answer:** the last SQL of the agent or the teacher that ran without error and returned rows (`fallback`); otherwise no answer (`no_answer`). A SQL query that does not run is never an answer.
→ Answer ✔

**The returned answer:** the SQL, the label (`ok`, `fallback`, `no_answer`) and who found the answer (agent or teacher).

### Two examples

**Example 1 ("Which category had the most returns in 2025?"):**
1 (evidence: returned = `status = 'returned'`) → 2 → 4 (SQL) → 5 → 6 (real result: 1 row) → 2 → 7 (final check passed) → ✔

**Example 2 (the same question, the agent writes a wrong column and a wrong value):**
1 → 2 → 4 → 5 (`no such column: o.state`; the note shows the real columns of the tables in the query) → 2 → 4 (fixed SQL) → 5 → 6 (empty result) → 2 → 3 (`search_values`: "returnd" → `status = 'returned'`) → 2 → 4 → 5 → 6 (1 row) → 2 → 7 → ✔

### After the question

**Experience log:** When a question ends, wherever it was run from (`run.py`, `evaluate.py` or an application in use), one line is written: the whole conversation the agent (and, after a handoff, the teacher) saw, the answer and the label. In evaluation, whether the answer is correct is also written (`split = dev`); in use there is no correct SQL, so this field stays empty (`split = use`), and the training signal there is the teacher's solutions and the label. Records accumulate and are never deleted.

**Agent training (later):** The agent is trained inside the harness it will be used in, with the records in the experience log: first SFT on the teacher's correct solutions, then on-policy distillation (the agent's own attempts, corrected by the teacher), then RL (reward: whether the answer is correct). Only records from the train split are used for training.

## Design decisions

| Decision | Why | Basis |
|---|---|---|
| The final answer is always really executed | Whether an unexecuted SQL is correct cannot be known | — |
| The agent writes the answer first, it does not start with exploratory queries | A small model that starts with exploratory queries often stays exploring and never writes the answer | — |
| The error note says what is needed to fix it | Small models fix an error only when what is wrong is written out clearly (e.g. the real columns of the tables in the query) | DualSQL |
| Temperature 0; sampling when stuck | The most likely reply gives a more accurate single SQL; but the same input always gets the same reply, so after a rejected or repeated call the next step is sampled | — |
| Results are compared with BIRD's official rule (result key) | "The same result" is defined in one place | BIRD |
| Step 1 gives as much information as possible (column descriptions, column profiles) | Every search costs a tool call. If the information comes up front, the budget is left for trying | DualSQL, HarnessSQL |
| An agent that makes no progress hands over early | An agent that gets no rows in its first steps usually cannot solve the question; the teacher starts with a short history and the cost goes down | — |
| The teacher continues where the agent left off | What the agent found is not wasted; handoff records become training data directly | OLIVE, OVCSD |
| The agent is trained inside the harness | A model trained outside the harness drops from 30.4 to 9.6 when used in the harness | HarnessSQL |

## Build order

The system was built in small, numbered stages; each stage added a single part and was tested. The list is in the "Build order" section of [CODE_STRUCTURE.md](CODE_STRUCTURE.md).

1. **SQLite + BIRD:** foundation (database, scoring, initial context), first working agent, trial loop (guardrails, `search_values`), verifying the answer (final check), handoff.
2. **Local models:** The policy and the teacher run locally.
3. **Agent training (later):** SFT → on-policy distillation → RL with the experience log.

## Evaluation

- **BIRD dev:** 1,534 questions, with evidence. Accuracy is measured with BIRD's official rule: an answer is correct if its result key is the same as the gold SQL's.
- **Base:** the tool-free single SQL on the same questions (`baseline.py`); the agentic system is compared with it.
- **For a test,** 10 questions are enough (`--limit 10`). Comparisons use at least 3 seeds (0, 1, 2).
- **Ablations:** When the contribution of a part is to be measured, a flag that turns that part off is added; currently every part is always on.

All thresholds are starting values; they are tuned by measurement.

## References

Only the works that directly shaped this design. The full survey is in [RESEARCH.md](RESEARCH.md).

**Pre-check**
- CYGNET ([2606.04645](https://arxiv.org/abs/2606.04645)): cheap structural checks first (step 5).
- CacheRL ([2606.14179](https://arxiv.org/abs/2606.14179)): a cache of real executions (step 5).

**Harness**
- HarnessSQL ([2610.12274](https://arxiv.org/abs/2610.12274)): training the agent inside the harness it will be used in; the tool set; the choice of teacher (Qwen3.6-27B).
- DualSQL ([2609.18135](https://arxiv.org/abs/2609.18135)): guardrails (repeated calls, format errors).

**Handoff**
- OLIVE ([2609.36246](https://arxiv.org/abs/2609.36246)) and OVCSD ([2607.27937](https://arxiv.org/abs/2607.27937)): the teacher continuing where the agent left off (step 8); on-policy distillation.

**Evaluation**
- BIRD ([2305.03111](https://arxiv.org/abs/2305.03111)): the main benchmark, evidence and the official result comparison rule.
