# ForeSQL: Predict – Gate – Settle (PGS)

**Agentic Text-to-SQL with a forecast-checked agent loop, candidate selection and handoff.**

A small policy agent (Qwen3.5-4B) turns a natural-language question into SQL by calling tools. Before running any SQL, the agent predicts what its result will look like (**forecast**); the real execution checks this prediction and warns the agent when it misses. The answer is chosen by **consensus**, i.e. independently written SQL queries returning the same result, and every answer that is returned has actually been executed. If the question is ambiguous, the agent asks the user (`ask_user`); if it gets stuck, the task is handed over to a larger teacher model (**handoff**). For expensive queries, a **world model** predicts the result without running the query.

The project is being developed as an ICML paper and a course project. The main benchmark is BIRD (SQLite, with evidence).

## Architecture

![PGS flow](docs/PGS_flow_EN.png)

Each column is a component: 🟦 policy agent, 🟧 world model, 🟩 harness (plain Python, no LLM), 🟥 real database, 🩵 teacher LLM, 🟪 harness decisions (gates, final check). The numbers are the steps below.

## How a question is answered

| # | Step | Who | What happens |
|---|---|---|---|
| 1 | Initial context | Harness | Schema, column descriptions, column profiles, database values matching words in the question ("Los Angles" → `'Los Angeles'`), mistakes made earlier on this database (database memory) |
| 2 | Agent decides | Agent | One tool call per turn: search, ask, try, submit or hand off. At most 10 tool calls |
| 3 | Gather information | Harness | `search_schema`, `search_values`, `ask_user` |
| 4 | `execute_sql` + forecast | Agent | The SQL comes with a prediction: error / empty / rows, how many columns, how many rows |
| 5 | Pre-check | Harness | Is it read-only? Does `EXPLAIN` fail? Has it run before (cache)? Is it expensive, or is the budget low? |
| 6 | World model + prediction gate | Harness | Only for expensive queries: if the prediction is trusted (confidence ≥ 0.9), the query is not run; 5% of trusted predictions are still checked (audit) |
| 7 | Real execution | Harness | The result is compared with the forecast; on a miss, a **surprise note** goes back to the agent ("you expected rows, the result is empty") |
| 8 | `submit` → candidates | Harness | The same model writes 2 more SQL queries; if they disagree, the total is filled up to 8. They are grouped by their real results |
| 9 | Confidence gate | Harness | high (3/3 or ≥6/8) → 10 · medium (4–5/8) → a summary of the two largest groups goes back to the agent · low → 11 |
| 10 | Final check | Harness | Did the answer really run, without error? If it is empty, was that expected? |
| 11 | Handoff | Teacher | The teacher continues from where the agent stopped, with a new budget |

Example: *"Which category had the most returns in 2025?"* → 1 → 2 → 4 (SQL + "rows, 1 row") → 5 → 7 (forecast hit) → 2 → 8 → 9 (3/3 same result: high) → 10 → ✔

## Design decisions

| Decision | Why |
|---|---|
| The agent writes the forecast, the real execution checks it | A separate learning signal for every step (ANTE, ECHO) |
| The harness decides when to call the world model | Agents either never use a world-model tool or use it wrongly |
| The world model is used only for expensive queries | On SQLite, execution is cheap and exact; small models' confidence does not stay calibrated on new schemas |
| The final answer is always really executed | If a prediction becomes the answer or the reward, the policy exploits it |
| The answer is chosen by consensus | The common method of the top systems on the leaderboard; an uncertainty signal the harness can measure without an LLM |
| No LLM and no agent framework in the harness | Every decision is plain Python: readable and reproducible |

All decisions and the work they are based on: [docs/en/AGENTIC_FLOW.md](docs/en/AGENTIC_FLOW.md).

## Code

Each file maps to one or two steps of the flow; files are short (≤ 150 lines).

| File | Step | What it does |
|---|---|---|
| `agent/loop.py` | 2 | The agent loop: the flow itself; each tool is one branch |
| `agent/policy.py`, `agent/llm.py`, `agent/prompts.py`, `agent/tools.py` | 2, 4, 8 | Talking to the model, prompts, tool definitions |
| `harness/prepare.py`, `harness/value_matches.py` | 1 | Initial context and value matches |
| `harness/search.py`, `harness/ask_user.py` | 3 | Search tools; the user or the user simulator |
| `harness/precheck.py`, `harness/cost.py` | 5 | Cheap checks, cache, whether to call the world model, cost simulation |
| `world_model/predict.py`, `harness/gates.py` | 6, 9 | World model, prediction gate, audit, confidence gate |
| `harness/compare.py`, `experience/log.py` | 7 | Forecast comparison, surprise note, experience log |
| `harness/candidates.py`, `harness/final_check.py` | 8, 10 | Candidates and selection, final check |
| `harness/handoff.py`, `experience/memory.py` | 11, 1 | Handoff to the teacher, fallback answer, database memory |
| `harness/guards.py` | every step | Guardrails: broken output, repeated calls, trimming long results, compressing the context |
| `db/` | 5, 7 | SQLite: read-only execution, `EXPLAIN`, cost estimate, schema and profiles |
| `evaluate.py`, `report.py`, `mini_interact.py`, `run.py` | | Evaluation, result tables, Mini-Interact data, a single question |
| `config.py` | | All constants and ablation flags |
| `tests/` | | 103 tests; no API needed, a small test database |

Ablation flags: `USE_AGENT_FORECAST`, `USE_CANDIDATES`, `USE_HANDOFF`, `USE_ASK_USER`, `USE_DB_MEMORY`, `USE_WORLD_MODEL`; for Phase 2, `SIMULATE_COST` (bird-coin budget). Details: [docs/en/CODE_STRUCTURE.md](docs/en/CODE_STRUCTURE.md).

## Status

The system was built in small, numbered stages; each stage adds one piece and is verified by tests.

- ✅ **Phase 1 (stages 1–28):** All 11 steps of the flow; a placeholder world model (an untrained LLM prompted to act as a world model).
- ✅ **Phase 2 code (stages 30–33):** Mini-Interact (300 ambiguous SELECT tasks), its own user simulator, cost simulation with bird-coins, measurement of the prediction gate threshold.
- ⏳ **Measurements:** The full Phase 1 measurement and the ablation table (stage 29), paper numbers with local Qwen3.5-4B / Qwen3.6-27B (stage 35).
- ⏸ **Optional:** World model and policy training (SFT → on-policy distillation → RL), DuckDB.

## Results

A fixed set of 50 questions from BIRD dev (sampled with seed 0). Accuracy follows the official BIRD rule: an answer is correct if its result set equals that of the gold SQL.

**First parts of the flow, Qwen3.5-9B via API:**

| Stage | System | Seed 0 / 1 / 2 |
|---|---|---|
| 5 | Single SQL without tools (baseline) | 64% / 66% / 62% |
| 6 | Agent loop, only the `submit` tool | 60% / 64% / 66% |
| 7 | + `execute_sql` | 58% / – / – |

**Full system (all 11 steps), local Qwen3.5-0.8B** (policy, teacher, simulator and world model are the same small model; only to show that the flow works end to end):

| Seed | Accuracy | Avg. tool calls | Real executions | Answered by teacher | `ask_user` | World model calls |
|---|---|---|---|---|---|---|
| 0 | 4% (2/50) | 17.0 | 1.5 | 18 | 8 | 7 |
| 1 | 0% (0/50) | 17.0 | 1.7 | 16 | 6 | 15 |
| 2 | 6% (3/50) | 16.2 | 1.3 | 15 | 6 | 10 |

The 0.8B model is far too weak for this task: the agent often writes the forecast in the wrong format and the guardrails reject these calls, hence the low accuracy. The table shows that every path of the flow (handoff, user simulator, world model, candidates) runs without errors with a real model; it does not measure how good the system is. Records: `results/asama29_tam_seed*.jsonl`.

On 50 questions, a difference of 1–3 questions is noise; these numbers only track progress and are not paper results. Paper numbers will be taken with local 4B/27B models in stage 35.

## Running

On Apple Silicon (MLX), Python 3.12:

```bash
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -r requirements.txt

# Data (the data/ folder is not in the repository)
#   BIRD dev: https://bird-bench.github.io → data/bird/dev/ (dev.json, dev_databases/)
hf download birdsql/mini-interact --repo-type dataset --local-dir data/mini_interact

# Local model server (in a separate terminal)
mlx_lm.server --model Qwen/Qwen3.5-0.8B --port 8080 --chat-template-args '{"enable_thinking":false}'

# A single question: prints every step of the agent
python run.py --db data/bird/dev/dev_databases/california_schools/california_schools.sqlite "How many schools are in Alameda county?"

# Evaluation and ablation
python evaluate.py --name trial --seed 0 --subset
python evaluate.py --name trial_no_forecast --seed 0 --subset --off USE_AGENT_FORECAST
python evaluate.py --name mini --dataset mini_interact --limit 10 --simulate-cost
python report.py results/trial*.jsonl

# Tests (no API needed)
pytest tests/ --deselect tests/test_llm.py::test_api_answers
```

The model address and names are in `config.py`; switching to the OpenRouter API takes a few lines (described in the comment there).

## Documents

English:
- [docs/en/AGENTIC_FLOW.md](docs/en/AGENTIC_FLOW.md): the flow step by step, glossary, design decisions and references
- [docs/en/CODE_STRUCTURE.md](docs/en/CODE_STRUCTURE.md): code rules, file map, tools, constants, record formats, build stages
- [docs/en/RESEARCH.md](docs/en/RESEARCH.md): literature review, datasets, hyperparameters

The originals are in Turkish: [docs/AGENTIC_FLOW.md](docs/AGENTIC_FLOW.md), [docs/KOD_YAPISI.md](docs/KOD_YAPISI.md), [docs/ARASTIRMA.md](docs/ARASTIRMA.md).
