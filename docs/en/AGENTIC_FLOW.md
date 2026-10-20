# Predict – Gate – Settle (PGS)

Turkish original: [../AGENTIC_FLOW.md](../AGENTIC_FLOW.md)

**Agentic Text-to-SQL with a forecast-supervised agent loop, candidate selection and handoff.**

A small policy agent solves the question with tools; if the question is ambiguous, it asks the user. Before running each SQL query, it predicts the result (agent forecast), and the real execution checks this prediction. The world model is used only when execution is expensive. If the agent gets stuck, the work is handed over to a large teacher LLM (handoff). The literature behind the design is in [RESEARCH.md](RESEARCH.md); the code structure and build order are in [CODE_STRUCTURE.md](CODE_STRUCTURE.md).

## Flow

**In short:** question → initial context (1) → agent loop: search or ask (3), try SQL (4–7) → `submit` → candidates (8) → confidence gate (9) → final check (10) → answer. If the agent gets stuck, the teacher takes over (11).

![PGS flow](../PGS_flow_EN.png)

| Color | Component |
|---|---|
| 🟦 Blue | Policy agent |
| 🟧 Orange | World model |
| 🟩 Green | Harness (no LLM) |
| 🟥 Red | Real database |
| 🩵 Turquoise | Teacher LLM |
| 🟪 Purple | Harness decision (gates, final check) |
| ⬜ Dashed | Offline learning |
| ⚪ White, rounded | Outside the system: the user's question, the user who answers `ask_user`, and the returned answer |

Arrow colors: **black** tool call, **blue** observation returned to the agent, **purple** decision outcome, **turquoise** handoff, **dashed** offline learning.

## Terms

| Term | Meaning |
|---|---|
| Policy agent | The small model that solves the question step by step |
| Tool call | The single request the agent makes in one turn (e.g. `execute_sql`) |
| Observation | The result returned to the agent after a tool call |
| Tool-call budget | The maximum number of tool calls allowed for one question (10) |
| Trial loop | The loop in which the agent searches, asks, tries, looks at the result and corrects (steps 2–7) |
| Column profile | A summary of a column: its type, NULL ratio, most frequent values (all values for low-cardinality columns), and min and max if numeric |
| Harness | The ordinary code around the agent: it runs the tools and manages the checks and gates. It contains no LLM |
| World model | A small model that predicts the result of a SQL query without running it |
| Placeholder world model | An untrained LLM used in place of the world model until the world model is trained. It is prompted to behave like a world model: it produces predictions and confidences in the same format, and the rest of the system does not see the difference |
| Agent forecast | The result prediction the agent writes before running a SQL query |
| Prediction | The world model's prediction of a SQL query's result. It is separate from the agent forecast, which is written by the agent |
| Pre-check | Cheap checks the harness performs before a SQL query is run: is it read-only, does `EXPLAIN` raise an error, is it in the cache, should it go to the world model (step 5) |
| Cache | Stored results of SQL queries already run within the same question; the same SQL is not run again |
| Gate | A decision point where the harness decides "continue, stop, or take another path?". The prediction gate decides whether the world model's prediction can be trusted (step 6); the confidence gate decides whether the candidates agree enough (step 9) |
| Final check | The last check before the answer is returned: did it actually run, is there no error, and if it is empty, was that expected (step 10) |
| Candidate | An alternative SQL query written for the same question |
| Consensus | Different candidates producing the same result |
| Adaptive rule | The rule that chooses the number of candidates depending on the situation: first 2 extra candidates, and 8 in total if there is no agreement (step 8) |
| Handoff | Handing the work over to the large teacher model |
| Evidence | The short hint text BIRD provides with each question (e.g. "returned = `status = 'returned'`"). Standard evaluation on BIRD uses it |
| `ask_user` | The tool with which the agent asks the user a short clarification question about an ambiguous question (e.g. "count or amount?") |
| Clarification | The user's answer to an `ask_user` question. It is treated as part of the question |
| User simulator | The model that answers `ask_user` questions in place of a real user during evaluation. It sees the correct SQL but does not reveal the SQL or the answer; it only clarifies the question |
| Search notes | A copy of the search results, stored separately for the candidate prompt |
| Surprise note | A short note returned to the agent together with the real result when the forecast misses (e.g. "you expected rows, it came back empty") |
| Medium note | The note returned to the agent when the confidence gate comes out medium: a summary of the two largest candidate groups |
| Database memory | A record of verified corrections made earlier on a database. It is added to the context in step 1; an example is given in step 1 |
| Result key | The key used to compare query results. All rows of the result are taken as a set: row order and duplicate rows do not matter, column order does (BIRD's official rule). Two results with the same key count as "the same result" |
| Fallback answer | The best answer returned when no answer passes the checks; it carries the `low_confidence` label |
| Label | The label of the returned answer: `ok` (passed the checks), `low_confidence` (did not pass, but there is an answer), `no_answer` (no SQL that runs) |
| Experience log | The record in which every execution, prediction and result is written; training data comes from it |
| Guardrail | The harness rules that protect the agent: no repeating the same call, long results are trimmed, the context is compressed when it fills up |
| Split | A partition of the data: train (training) or dev/test (evaluation). Only train is used for training |
| LoRA | A method that trains a small added layer instead of the whole large model |
| SFT | Training a model by having it imitate correct examples |
| On-policy distillation | Training the student model on its own attempts, corrected by the teacher |
| RL | Training a model by giving reward and penalty according to the outcomes of its attempts |
| EXPLAIN | The database showing its plan for a query ("how would I run this, how much would I scan") without running it. In SQLite it also catches syntax errors and missing tables/columns without running the query |
| Calibration | A confidence score matching reality: when it says "90% sure", it is right 90% of the time |
| Audit | Running and checking a small share of trusted predictions anyway |
| Cost simulation | Treating some queries as expensive, since queries are cheap in SQLite; it makes it possible to exercise the expensive-query path (step 6) on SQLite |
| Bird-coin | Mini-Interact's cost unit: every execution, question and answer submission costs bird-coins, and every task has a bird-coin budget |
| Baseline | The simplest system measured for comparison (e.g. the tool-free single SQL of stage 5) |
| Ablation | Turning off a single part of the system (with a flag) and comparing the result with the full system; it shows that part's contribution |
| Promotion gate | A retrained policy is not put into use until it has been tested to be no worse than the old one |
| Phase / stage | Phase: one of three large periods (defined by the database environment). Stage: a small numbered piece of work that adds a single part (CODE_STRUCTURE.md "Build order"). Training is a separate, optional section that comes after the phases |
| Imagination loop (Dyna) | The model trying some steps with the world model's prediction instead of the real database |
| Seed | A number that fixes randomness; repeating with different seeds shows the result is not luck |
| Live fork | When evaluating handoff, actually re-running the system from that point instead of replaying the old record |

## Components

- **Policy agent (Qwen3.5-4B):** Decides which tool to call at each step. Predicts the result before running SQL. Used in its untrained form. Its training (inside the harness: SFT → on-policy distillation → RL) is optional and is done after the system works end to end.
- **World model (placeholder LLM in the first version; Qwen3.5-0.8B + LoRA if training is done):** Predicts the result of a SQL query at three levels without running it, and gives a confidence score for each:
  - **Result type:** will the query raise an error, return empty, or return rows?
  - **Result shape:** which columns will come back, and roughly how many rows?
  - **Values:** the actual values that will be returned (only for small results).

  In the first version it is a placeholder: an untrained LLM that is prompted to behave like a world model. If training is done, it is replaced by a small model trained on real execution records; the rest of the system does not change.
- **Harness (plain Python, no LLM):** Runs the tools, performs the checks, manages the gates and keeps the experience log. It also enforces the guardrails.
- **Database (SQLite, read-only):** `execute_sql`.
- **User:** Answers `ask_user` questions. In `run.py` it is the person at the terminal. In evaluation it is the user simulator: the teacher model answers like a user while seeing the correct SQL (as in BIRD-Interact). Only the simulator sees the correct SQL; it never enters the agent's context. In Mini-Interact the benchmark's own simulator is used; its LLM is also the teacher model, run locally.
- **Teacher LLM (Qwen3.6-27B, 4-bit):** Comes in only after a handoff. Continues from where the agent left off. In its 4-bit form it takes ~16–17 GB; together with the policy and the world model it is expected to fit in 48 GB (measured in stage 35).

## The flow step by step

The numbers in the figure are these steps. The division of labor is simple:
- The **agent** decides what to do: which tool, which SQL, the forecast, what to ask the user, and when to `submit` or `handoff`.
- The **harness** decides everything else: the checks, whether to go to the world model, the candidates, the gates, the final check.

Tool arguments and numeric limits are in [CODE_STRUCTURE.md](CODE_STRUCTURE.md).

### 1. Initial context

**Why:** Every search costs a tool call. If information is given up front, the budget is left for trying.

The harness gives the agent:
- The question and, if any, the evidence.
- The schema: tables, columns, BIRD's column descriptions, foreign keys.
- Column profiles. For columns with at most 30 distinct values (e.g. `status`), all values.
- Value matches for the words in the question: the harness runs `search_values` itself. Example: "Los Angles" → `city = 'Los Angeles'`.
- Database memory: errors made earlier on this database and their corrections (at most 3 records).

The context is at most 16K tokens (half of the context window); if it overflows, the details of tables that do not match the question are shortened.

Database memory example: in an earlier question the agent wrote `status = 'iade'` (Turkish for "returned"), the result came back empty, and it then corrected this to `'returned'`. This error and its correction are recorded; in a new question about returns, the agent sees it from the start. The record is written only if the answer passed the checks; gold SQL is not used.
→ 2

### 2. The agent decides what to do

The agent makes a single tool call each turn:
- If information is missing → `search_schema` / `search_values` → 3
- If the question is ambiguous and the schema, values or evidence do not resolve it → `ask_user` → 3
- If it wants to try a SQL query → `execute_sql` → 4
- If it is confident in the answer → `submit` → 8
- If it is stuck → `handoff` → 11

After every observation the agent returns here. Every tool call takes one off the budget (at most 10). Rejected requests and outputs that cannot be read as a tool call also count; the error is returned to the agent. If the budget runs out, the harness forces a handoff → 11.

**Guardrails.** Small models often make certain typical mistakes; so that these do not break the system, the harness applies three simple rules at every step. Without them, even the agent's training collapses (DualSQL).
1. **No repeats:** The model sometimes sends the same SQL over and over and gets stuck in a loop. If the same call (same tool, same arguments) comes a second time, it is not run; a "you already tried this" note and the earlier result are returned, and the budget still goes down. For `execute_sql` only the SQL is considered: it counts as a repeat even if the forecast differs. `submit` is the exception: resending the same SQL after a medium note is a valid choice.
2. **Long results are trimmed:** Giving all 50,000 rows would fill the context. The agent sees at most 20 rows, with "50,000 rows in total" next to them.
3. **The context is compressed:** If the conversation exceeds 32K tokens, the oldest results are reduced to a one-line summary (e.g. "3 columns, 120 rows").

### 3. Gathering information: search and `ask_user`

The agent can use these whenever it wants. Since step 1 is rich, they are rarely needed for most questions.
- **`search_schema`:** Finds the tables and columns related to the question; searches in names and column descriptions. Example: "category" → the `categories` table.
- **`search_values`:** Finds in which column, and as which value, a word appears in the database, including similarly spelled values. Example: "Los Angles" → `city = 'Los Angeles'`.
- **`ask_user`:** A short question is asked only if only the user can clarify the question. Example: "count or amount?" → "count". It is not asked if the schema, values or evidence give the answer. At most 5 times per question (agent and teacher combined).

Search cannot find everything: if the question says "iade" (Turkish for "returned") and the database says `'returned'`, they do not match. In this case the evidence usually provides the match; if it does not, the agent asks the user, or gets an empty result with the wrong value and the surprise note steers it to try another value.

The result returns to the agent as an observation. The harness also keeps a copy: search results as **search notes**, and the user's answers as **clarifications**. Both are given to the candidates in step 8 and to the teacher in step 11. Why a copy? Candidates do not see the agent's history; if they did, they would copy the agent's SQL. Thanks to the copy, they get the information found (e.g. `'returned'`) but not the SQL.
→ 2

### 4. The `execute_sql` request and the forecast

Along with the SQL, the agent also predicts what the result will be (forecast):
- Result type: `error`, `empty` or `rows` (non-empty).
- Result shape (only if `rows`): the columns and the row range (`0`, `1`, `2-10`, `11-100`, `100+`).
- `trust` or `unsure`.

Example: `{"type": "rows", "columns": ["category", "n"], "rows": "1", "trust": true}`

If there is no forecast, the request is rejected (→ 2). If `USE_AGENT_FORECAST` is off, no forecast is requested. From here on, the harness decides where the query goes.
→ 5

### 5. Pre-check

**Why:** To catch a broken or expensive query cheaply, without running it.

Both the agent's SQL queries and the candidates pass through here. The harness asks four questions in order:
1. **Does it write?** If it does not start with `SELECT` or `WITH`, it is rejected. Example: `DELETE FROM orders`.
2. **Is it broken?** `EXPLAIN` catches syntax errors and missing tables and columns without running the query. Example: a `price` column that does not exist in the `customers` table.
3. **Has it run before (cache)?** If it has, it is not run again; the stored result is compared with the forecast as in step 7 and returned. The agent's own repeats are already caught by the guardrail; the cache is for when the same SQL arrives by another path. Example: a candidate rewrites the agent's SQL verbatim.
4. **Is it expensive, or is the budget low?** If the estimated number of scanned rows exceeds 1 million, or the remaining budget is below 25% of the initial budget → 6 (world model). Otherwise → 7 (real execution). Since expensive queries are rare in SQLite, most queries go directly to 7. If `USE_WORLD_MODEL` is off, this question is not asked.

The note for a query that fails at 1–3 is returned to the agent (→ 2). If the query is a candidate, the note goes back to step 8 instead of the agent.

### 6. World model and prediction gate

**Why:** To predict the result of an expensive query without running it.

The harness calls the world model, not the agent. The world model gives a prediction for the result type, result shape and values, and a confidence score for each. The prediction gate looks only at the confidence for type and shape; values are shown to the agent for information only.
- Both ≥ 0.9 → trusted: the prediction is returned to the agent with the label "prediction" → 2. The agent may use it when writing its next SQL, but may not use it as the answer.
- Otherwise → untrusted → 7.
- **Audit:** A random 5% of trusted predictions are still run at 7. This way the gate's calibration keeps being checked against real results.

### 7. Real execution, compare & log

The query is run read-only on the database (at most 30 seconds). The real result is compared with the agent's forecast (and with the world model's prediction, if any) and written to the experience log.
- For the forecast to count as a "hit", the result type must match; if `rows`, the number of columns and the row range must match too. Column names are not considered, because the same column can come back under a different alias.
- The real result (its trimmed form) is returned to the agent. If the forecast missed, a surprise note comes with it. Example: "you expected rows, it came back empty".
→ 2

> Steps 2 → 7 form the agent's **trial loop**: search, ask, try, look at the result, correct.

### 8. `submit` → candidates

**Why:** A SQL query running without errors does not show that it is correct. The strongest signal is independently written SQL queries producing the same result (consensus).

- **Who writes them:** The agent's SQL is also a candidate. The others are written by the same policy model, without tools, in a single pass. The prompt contains the question, the evidence, the clarifications, the step 1 context and the search notes. The agent's SQL is not put into the prompt; if it were, the model would copy it. There is no search or trial loop.
- **How many (adaptive rule):** First 2 extra candidates. If they all give the same result as the agent's SQL, generation stops. If they diverge, 5 more are generated, for a total of 8.
- **How they run:** Each candidate goes through the same path as the agent's SQL queries: 5 → (6) → 7. SQL that has already run comes from the cache; if the agent's SQL has never run, it is run now. If the world model is on and a candidate is expensive, a candidate confidently predicted to "raise an error" or "return empty" is dropped without being run. Candidates do not count against the budget, and their results are not returned to the agent (the only exception is the medium note in step 9).
- **Grouping:** Candidates with the same result key, that is, with the same real result, form a group. The result key is computed from all rows, not from the 20 rows shown to the agent. A candidate that raises an error or is dropped joins no group.
- **Selection:** The largest group is chosen. In a tie, the group containing the agent's SQL; if the agent's group is not among the tied ones, the group containing the earliest generated candidate. The group's answer is a single SQL: the agent's SQL if it is in the group, otherwise the group's earliest generated candidate.
- **Second `submit`:** If the agent submits again after a medium note or a final check note, the candidates are regenerated from scratch, because the search notes and clarifications may have changed. Identical SQL queries come from the cache.

The extra executions are a deliberate trade-off: a few executions are cheaper than returning a wrong answer or handing off to the teacher. The trade-off is measured: if `USE_CANDIDATES` is off, 8 and 9 are skipped and the agent's SQL goes directly to 10.
→ 9

### 9. Confidence gate

The decision looks only at consensus: how many candidates are in the largest group? Candidates that raise an error or are dropped are not counted.
- **High:** 3/3 or at least 6 of 8 → 10.
- **Medium:** 4–5 of 8 → a medium note is returned to the agent → 2. The note shows the two largest groups: a representative SQL, how many candidates it appears in, the columns, the row count, the first 3 rows. The agent can pick one and submit again, make a new attempt, or, if the difference comes from the question's ambiguity, ask with `ask_user`. This happens at most once; a second medium → 11.
- **Low:** at most 3 of 8 → 11.

### 10. Final check

The last check before the answer is returned:
- **Was it actually run?** If it was not (e.g. the teacher's answer), the harness runs it now; this way every returned answer has actually been run. An answer that raises an error does not pass.
- **Is it read-only, and do the tables and columns exist?**
- **If the result is empty, was that expected?** It does not pass if the last forecast written for this SQL is not "empty", or if there is no forecast. For example, there is no forecast if the selected SQL is a candidate or if `USE_AGENT_FORECAST` is off.

Passed → **the answer is returned ✔** (label `ok`). Did not pass → the reason is returned to the agent as a note → 2. If it fails a second time → 11.

### 11. Handoff

The agent can request a handoff itself (step 2), or the harness forces it: the budget ran out, confidence is low, medium for the second time, the final check failed twice.
- The teacher does not start from scratch; it continues from where the agent left off: the question, the evidence, the clarifications, all observations, the medium note if any, and the reason for the handoff.
- It works with a new budget (10 tool calls) and the same tools (steps 2–7). The `handoff` tool is not offered to the teacher; for `ask_user` it uses only the question's remaining allowance.
- The teacher's `submit` does not go to the candidates; it goes directly to the final check. If it passes, `ok`; if not, it is not retried and the SQL is returned with `low_confidence`. If the teacher does not submit within its budget, the fallback answer is returned.

**Fallback answer** order: the most recently selected answer (the SQL chosen by step 8; if step 8 is off, the SQL the agent submitted; the SQL the teacher submitted) → otherwise the most recent SQL that ran without errors (the agent's or the teacher's) → otherwise no answer. The first two are returned with the `low_confidence` label, the last with `no_answer`. If `USE_HANDOFF` is off, the fallback answer is always returned instead of the teacher, and the `handoff` tool is not offered to the agent.
→ Answer ✔

**Returned answer:** the SQL, its result, the label (`ok`, `low_confidence`, `no_answer`) and who found the answer (agent or teacher).

### Two examples

**Example 1 ("Which category had the most returns in 2025?", SQLite):**
1 (evidence: returned = `status = 'returned'`; the schema has a `categories` table, so step 3 is not needed) → 2 → 4 (SQL + forecast: "rows, 1 row") → 5 (cheap) → 7 (real result, forecast hit) → 2 → 8 → 9 (high: 3/3) → 10 → ✔

**Example 2 (same question, if the candidates diverge):**
1 → 2 → 4 → 5 → 7 → 2 → 8 → 9 (medium: 5 of the 8 candidates count items, 3 sum the amount; the medium note shows both groups) → 2 → 3 (`ask_user`: "count or amount?" → "count") → 2 → 8 (the clarification is now in the prompt) → 9 (high: 7/8) → 10 → ✔

### After the question (offline learning)

The experience log flows into three places:
- **Database memory:** If the question ended with `ok` and there was an error or a surprise note along the way, a record is written immediately: the question, the first faulty SQL, the note it received, the answer SQL. Since it does not use gold, it is also written during evaluation. For reproducibility it starts empty on every run and questions are run in dataset order. If `USE_DB_MEMORY` is off, memory is neither read nor written.
- **World model:** Retrained on real executions, and the gates are recalibrated.
- **Policy:** Re-distilled on handoff cases (re-distillation). A new policy is not put into use until it has been tested to be no worse than the old one (promotion gate).

The last two are training: they are optional and are done after the system works end to end; until then the experience log only accumulates. Only records from the train split are used for training and calibration; dev and test runs are written to the log but not used in training.

## Design decisions

| Decision | Why | Basis |
|---|---|---|
| The agent makes the forecast, real execution checks it | Gives a separate training signal for every step | ANTE, ECHO |
| The harness decides whether to go to the world model | Agents either never use a world model tool or use it wrongly | World-model-as-tool (ACL'26) |
| The world model is used only for expensive queries | Execution on SQLite is cheap and exact; small models' confidence does not stay calibrated on new schemas | DSWorld, BAP-SQL |
| The final answer is always actually executed | If the prediction becomes the answer or the reward, the policy exploits it | Imperfect WMs are Exploitable |
| Candidate generation & selection | The common method of the systems at the top of the leaderboard | Agentar-Scale-SQL, SIRIUS-SQL |
| Results are compared with BIRD's official rule (result key) | Candidate grouping and scoring use the same measure; "the same result" is defined in a single place | BIRD |
| The `ask_user` tool is always on | Asking instead of guessing on an ambiguous question; agents give up on clarification questions too early. Since the user simulator sees the correct SQL, results with `ask_user` off are also reported for comparison with the literature | BIRD-Interact, PlanPool |
| Step 1 gives as much information as possible (value matches, column descriptions) | Every search costs a tool call. If information comes up front, the budget is left for trying, and the candidates get the same information | DualSQL, HarnessSQL |
| The uncertainty signal is candidate divergence (medium note) | The harness has no LLM and cannot detect uncertainty by itself. Diverging candidate groups are a measurable sign; the decision is the agent's | SIRIUS-SQL, PlanPool |
| The agent is trained inside the harness | A model trained outside the harness drops from 30.4 to 9.6 when used in the harness | HarnessSQL |
| The teacher continues from where the agent left off | Handoff records become training data directly | OLIVE, OVCSD |
| Database memory does not use gold; training uses only train data | Evaluation answers do not leak into the system | — |
| The first version uses fixed thresholds and only the consensus rule | Simple and explainable. No learned aggregator, certified threshold or separate verifier model is needed; they can be added later | What Predicts Correctness, SIRIUS-SQL |
| In Phase 1 the policy is not trained in the world model's imagination (no imagination loop) | Real execution on SQLite is cheap and exact. Errors accumulate in imagined rollouts and the policy exploits the world model. A limited Dyna-style imagination loop is added if training is done: single-step imagination, with the reward always from real execution | Qwen-AgentWorld, Imperfect WMs are Exploitable |
| The world model is a placeholder in the first version (a prompted untrained LLM); training is optional and comes last | All steps of the flow are built and measured end to end without waiting for training. The world model's interface (prediction + confidence) is fixed from the start; if a trained model arrives, only this component changes | — |
| The system is built in small stages | Each stage adds a single part and is measured; each part's contribution is visible on its own, and an error is caught where it appears | — |

## Implementation order

There are three phases, followed by the switch to local models and optional training. Each is divided into small, numbered stages (43 in total). Each stage adds a single part, leaves a working system and is tried with a small test. The full list of stages, their files and how to try them are in the "Build order" section of [CODE_STRUCTURE.md](CODE_STRUCTURE.md).

Throughout development the models come from an API: the policy, the teacher and the user simulator are real LLMs; the world model is a placeholder (an untrained LLM prompted to behave like a world model). Once the system works end to end, we switch to local models and the paper's numbers are obtained with them. Training is left to the end and is optional; if it is not done, the world model stays a placeholder and is described as such in the paper.

1. **Phase 1, SQLite + BIRD:** The agent, harness, gates and placeholder world model are built. Cost simulation is off; step 6 runs only for genuinely expensive queries or when the budget is low.
   - **A. Foundation, no model (stages 1–3):** database layer, BIRD data and scoring, initial context.
   - **B. The agent piece by piece.** Each tool and each guardrail is added in a separate stage; each part builds on the previous one and is measured on its own:
     - B1, first working agent (4–8): model, tool-free single SQL, loop skeleton with only `submit`, `execute_sql`, pre-check.
     - B2, strengthening the trial loop (9–16): the three guardrails separately (repeats and cache, trimming, compression), `search_values`, `search_schema`, value matching in step 1, forecast, experience log.
     - B3, verifying the answer (17–21): final check, candidates, adaptive rule, confidence gate, medium note.
     - B4, help and memory (22–25): handoff, `ask_user` (terminal), user simulator, database memory.
     - B5, world model (26–28): placeholder world model and its measurement, prediction gate and audit, candidate pruning with the world model.
     - B6, Phase 1 results (29): full BIRD dev and ablations (with API models; shows progress and the direction of the ablations).
2. **Phase 2, cost simulation in the same environment (stages 30–33):** In order: Mini-Interact and its user simulator, cost simulation, and tuning the thresholds by measurement.
3. **Phase 3, a genuinely slow database (stage 34):** First a DuckDB adapter (TPC-DS) or scaled-up BIRD databases, then real latency measurement.
4. **Switch to local models (stage 35):** The policy, teacher and world model run locally; it is measured that the models fit in memory together. The paper's numbers are obtained here.
5. **Training, optional (stages 36–43):** World model training (data collection, training and calibration; replaces the placeholder), policy training (teacher traces → SFT → on-policy distillation → RL), a Dyna-style imagination loop and the promotion gate. Done if time allows; if done, the numbers are obtained again.

Each phase has a single database. "Cheap / expensive" is not two separate databases but a decision the harness makes for each query (step 5).

Rules to follow from the start to keep transitions cheap:
- Database work sits behind a single adapter interface: `execute`, `explain`, `estimate_cost`, `schema`, `profile`. Moving to a new engine only requires writing a new adapter.
- The cost model is pluggable: simulated or real.
- Engine and dialect information is also written to the experience log.
- When moving to a new dialect, the training data is translated with SQLGlot.

Implementation details (hyperparameters, rewards, datasets) are in sections 8 and 9 of [RESEARCH.md](RESEARCH.md).

## Evaluation

- **BIRD dev (main result):** The original 1,534 questions, with evidence, full system (`ask_user` on, answered by the user simulator). Since other systems do not ask questions, results with `ask_user` off are also reported. A Pareto curve of accuracy versus number of executions. Accuracy is measured with BIRD's official rule: an answer is correct if its result key is the same as the gold SQL's. The cleaner dev split (`bird_sql_dev_20251106`) is reported as an additional result.
- **Stage checks:** After the last stage of each section (B1–B5), a quick measurement is made on a fixed 50-question subset of BIRD dev. These numbers are only for tracking progress; they do not go into the paper.
- **Mini-Interact:** The real test of the world model and `ask_user`, because here every execution and every question has a cost. `ask_user` is answered by the benchmark's own user simulator; its LLM is the teacher model, run locally. Therefore the numbers are not directly comparable with the official leaderboard; this is stated in the paper.
- **BIRD-Critic-SQLite and Spider 2.0-Lite (SQLite):** repair ability and generalization.
- **Ablations:** Each flag is turned off one at a time and compared with the full system (the flags are in CODE_STRUCTURE.md).
- Every comparison uses at least 3 seeds (0, 1, 2). Handoff is evaluated with a live fork, not with replay.
- **Target:** BIRD dev 66–71 (inferred from similar systems, not measured).

All thresholds are initial values; they are tuned by measurement in Phase 2.

## Bibliography

Only the works that directly shaped this design. The full survey is in [RESEARCH.md](RESEARCH.md).

**Agent forecast and the role of the world model**
- ANTE: Anticipate, Then Execute ([2610.15368](https://arxiv.org/abs/2610.15368)): the agent writing a forecast before execution, and the forecast reward (step 4).
- ECHO: Terminal Agents Learn World Models for Free ([2605.24517](https://arxiv.org/abs/2605.24517)): real execution checking the forecast and producing a training signal (step 7).
- DSWorld ([2607.15901](https://arxiv.org/abs/2607.15901)): going to the simulator only at expensive steps (steps 5–6).
- BAP-SQL ([2608.02876](https://arxiv.org/abs/2608.02876)): pre-execution cost estimation and budget (step 5).
- Current Agents Fail to Leverage World Model as Tool for Foresight ([ACL 2026](https://aclanthology.org/2026.acl-long.623/)): not leaving the decision to go to the world model to the agent (step 5).
- Imperfect World Models are Exploitable ([2605.15960](https://arxiv.org/abs/2605.15960)): the prediction never being the final answer or the reward (steps 6, 10).

**Pre-check and gates**
- CYGNET ([2606.04645](https://arxiv.org/abs/2606.04645)): cheap structural checks first, then learned prediction (step 5).
- CacheRL ([2606.14179](https://arxiv.org/abs/2606.14179)): a real execution cache (step 5).
- What Predicts Correctness in Text-to-SQL? ([2607.06799](https://arxiv.org/abs/2607.06799)): confidence signals; choosing thresholds on unseen databases (steps 6, 9).

**Candidate selection**
- Agentar-Scale-SQL ([2509.24403](https://arxiv.org/abs/2509.24403)): candidate generation & selection (step 8).
- SIRIUS-SQL ([2606.01246](https://arxiv.org/abs/2606.01246)): grouping candidates by result; consensus alone being a strong signal (steps 8, 9).
- Knowing When to Stop ([2607.03991](https://arxiv.org/abs/2607.03991)): stopping sampling early when candidates agree (step 8).

**Asking the user**
- BIRD-Interact ([2510.05318](https://arxiv.org/abs/2510.05318)): the cost of the `ask` action and the user simulator (step 3).
- PlanPool ([2610.02739](https://arxiv.org/abs/2610.02739)): agents giving up on clarification questions too early (steps 3, 9).

**Harness and training**
- HarnessSQL ([2610.12274](https://arxiv.org/abs/2610.12274)): training the agent inside the harness it will be used in; the tool set; the choice of teacher (Qwen3.6-27B).
- DualSQL ([2609.18135](https://arxiv.org/abs/2609.18135)): rollout guardrails (repeating the same call, format errors).

**Handoff and offline learning**
- OLIVE ([2609.36246](https://arxiv.org/abs/2609.36246)) and OVCSD ([2607.27937](https://arxiv.org/abs/2607.27937)): the teacher continuing from where the agent left off (step 11).
- Measuring Crystallization in Text-to-SQL ([2608.07213](https://arxiv.org/abs/2608.07213)): writing verified corrections to database memory (step 1).
- BCIT ([2608.26730](https://arxiv.org/abs/2608.26730)): a promotion gate for the retrained policy.
- Qwen-AgentWorld ([2606.24597](https://arxiv.org/abs/2606.24597)): RL with simulation working only with a real anchor (the imagination loop decision).

**Evaluation**
- BIRD ([2305.03111](https://arxiv.org/abs/2305.03111)): the main benchmark, evidence and the official result comparison rule.
- BIRD-Interact ([2510.05318](https://arxiv.org/abs/2510.05318)): a benchmark with execution costs (Mini-Interact).
- OmniSQL / SynSQL-2.5M ([2503.02240](https://arxiv.org/abs/2503.02240)): synthetic SQL data for world model training.
