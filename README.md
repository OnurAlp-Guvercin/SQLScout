# ForeSQL: Predict – Gate – Settle (PGS)

**Agentic Text-to-SQL with an agent loop, candidate selection and handoff.**

A small policy agent (Qwen3.5-4B) turns a natural-language question into SQL by calling tools: it searches for values, runs SQL and looks at the real result. The answer is chosen by **consensus**, i.e. independently written SQL queries returning the same result, and every answer that is returned has actually been executed. If the question is ambiguous, the agent asks the user (`ask_user`); if it gets stuck (out of budget, or its answer does not pass the checks), the task is handed over to a larger teacher model (**handoff**).

The project is being developed as an ICML paper and a course project. The main benchmark is BIRD (SQLite, with evidence).

## Architecture

![PGS flow](docs/PGS_flow_EN.png)

Each column is a component: 🟦 policy agent, 🟩 harness (plain Python, no LLM), 🟥 real database, 🩵 teacher LLM, 🟪 harness decisions (confidence gate, final check). The numbers are the steps below.

## How a question is answered

| # | Step | Who | What happens |
|---|---|---|---|
| 1 | Initial context | Harness | Schema, column descriptions, column profiles, mistakes made earlier on this database (database memory) |
| 2 | Agent decides | Agent | One tool call per turn: search, ask, try or submit. At most 10 tool calls |
| 3 | Gather information | Harness | `search_values`, `ask_user` |
| 4 | `execute_sql` | Agent | The agent sends the SQL it wants to try |
| 5 | Pre-check | Harness | Is it read-only? Does `EXPLAIN` fail? Has it run before (cache)? |
| 6 | Real execution | Harness | The real result goes back to the agent (at most 20 rows); if it is empty, a note suggests checking the value's spelling with `search_values` |
| 7 | `submit` → candidates | Harness | The same model writes 2 more SQL queries; if they disagree, the total is filled up to 8. They are grouped by their real results |
| 8 | Confidence gate | Harness | high (3/3 or ≥6/8) → 9 · medium (4–5/8) → a summary of the two largest groups goes back to the agent · low → 10 |
| 9 | Final check | Harness | Did the answer really run, without error? If it is empty, was that expected? |
| 10 | Handoff | Teacher | The teacher continues from where the agent stopped, with a new budget of half the agent's (5 tool calls) |

Example: *"Which category had the most returns in 2025?"* → 1 → 2 → 4 (SQL) → 5 → 6 (1 row) → 2 → 7 → 8 (3/3 same result: high) → 9 → ✔

## Design decisions

| Decision | Why |
|---|---|
| The final answer is always really executed | Whether an unexecuted SQL is correct cannot be known |
| The answer is chosen by consensus | The common method of the top systems on the leaderboard; an uncertainty signal the harness can measure without an LLM |
| No LLM and no agent framework in the harness | Every decision is plain Python: readable and reproducible |

All decisions and the work they are based on: [docs/en/AGENTIC_FLOW.md](docs/en/AGENTIC_FLOW.md).

## Code

Each step of the flow lives in a single file, and each of the agent's tools in its own file under `harness/tools/`; `agent/loop.py` only dispatches.

| File | Step | What it does |
|---|---|---|
| `agent/loop.py` | 2, 10 | The flow itself: each tool is one branch that goes to one file; handoff to the teacher, fallback answer |
| `agent/prompts.py`, `agent/llm.py`, `agent/context.py` | | Everything the model sees (prompts and tool definitions), talking to the model, the state of one question |
| `harness/prepare.py` | 1 | Initial context; table selection when the schema is too long |
| `harness/tools/search_values.py`, `harness/tools/ask_user.py` | 3 | Searching values; asking the user |
| `harness/tools/execute_sql.py` | 4–6 | Pre-check, real execution and cache, turning the result into text |
| `harness/tools/submit.py` | 7–9 | Candidates and selection, confidence gate, medium note, final check |
| `harness/guards.py` | every step | Guardrails: broken output, repeated calls, compressing the context |
| `harness/memory.py` | 1 | Database memory |
| `db/` | 1, 5, 6 | SQLite: read-only execution, `EXPLAIN`, schema, profiles and column descriptions |
| `evaluate.py`, `report.py`, `mini_interact.py`, `run.py` | | Evaluation, result tables, Mini-Interact data, a single question. Every question, wherever it runs, is written to the experience log (`experience/log.jsonl`) for training the agent later |
| `config.py` | | All constants |
| `tests/` | | 99 tests; no API needed, a small test database |

Every part of the flow is always on. Details: [docs/en/CODE_STRUCTURE.md](docs/en/CODE_STRUCTURE.md).

## Status

The system was built in small, numbered stages; each stage adds one piece and is verified by tests.

- ✅ **Phase 1:** All 10 steps of the flow.
- ✅ **Phase 2 code:** Mini-Interact (300 ambiguous SELECT tasks).
- ⏳ **Measurements:** with local Qwen3.5-4B / Qwen3.6-27B.
- ⏸ **Later:** training the agent inside the harness with the experience log (SFT → on-policy distillation → RL).

## Results

A fixed set of 50 questions from BIRD dev (sampled with seed 0). Accuracy follows the official BIRD rule: an answer is correct if its result set equals that of the gold SQL.

**First parts of the flow, Qwen3.5-9B via API:**

| Stage | System | Seed 0 / 1 / 2 |
|---|---|---|
| 5 | Single SQL without tools (baseline) | 64% / 66% / 62% |
| 6 | Agent loop, only the `submit` tool | 60% / 64% / 66% |
| 7 | + `execute_sql` | 58% / – / – |

**Full system, local Qwen3.5-0.8B, current code:** 0/10 on a fixed sample of 10 BIRD dev questions (`python evaluate.py --name sade_08b --limit 10`, `results/sade_08b_seed0.jsonl`); across repeated runs of this kind the result moved between 0 and 2 out of 10, and a tool-free single SQL from the same model gets 2/10. The 0.8B model is far too weak for this task (it often writes SQL that does not run); the run shows that every path of the flow runs end to end without errors.

On 50 questions, a difference of 1–3 questions is noise; these numbers only track progress.

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

# Evaluation (if the agent calls ask_user, the question appears in the terminal and waits for an answer)
python evaluate.py --name trial --seed 0 --limit 10
python evaluate.py --name mini --dataset mini_interact --limit 10
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
