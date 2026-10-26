# ForeSQL: Predict – Gate – Settle (PGS)

**Agentic Text-to-SQL with an agent loop, a final check and handoff.**

A small policy agent turns a natural-language question into SQL by calling tools: it searches for values, runs SQL and looks at the real result. The agent submits the SQL query it chooses as the answer; it passes a **final check**, and every answer that is returned has actually been executed. If the agent makes no progress or gets stuck, the task is handed over to a larger teacher model (**handoff**).

The project is being developed as an ICML paper and a course project. The main benchmark is BIRD (SQLite, with evidence).

## Architecture

![PGS flow](docs/PGS_flow_EN.png)

Each column is a component: 🟦 policy agent, 🟩 harness (plain Python, no LLM), 🟥 real database, 🩵 teacher LLM, 🟪 harness decision (final check). The numbers are the steps below.

## How a question is answered

| # | Step | Who | What happens |
|---|---|---|---|
| 1 | Initial context | Harness | Schema, column descriptions, column profiles, evidence |
| 2 | Agent decides | Agent | One tool call per turn: try SQL, search a value or submit; it writes the answer first instead of exploring. At most 10 tool calls |
| 3 | Search for values | Harness | `search_values`: how a value is written and in which column |
| 4 | `execute_sql` | Agent | The agent sends the SQL it wants to try (or writes it in a ` ```sql ` block) |
| 5 | Pre-check | Harness | Is it read-only? Does `EXPLAIN` fail? Has it run before (cache)? |
| 6 | Real execution | Harness | The real result goes back to the agent (at most 20 rows); if it is empty, a note suggests checking the value's spelling with `search_values` |
| 7 | `submit` → final check | Harness | The agent submits the SQL it chooses; queries in between do not matter. Does it run without error, and has the agent seen its result (if not, the result is shown first)? If it fails, a note goes back to the agent; failing twice → 8 |
| 8 | Handoff | Teacher | No progress in the first 4 steps, the same call 3 times, the final check failing twice, or out of budget: the teacher continues from where the agent stopped, with 5 tool calls |

Example: *"Which category had the most returns in 2025?"* → 1 → 2 → 4 (SQL) → 5 → 6 (1 row) → 2 → 7 (passed) → ✔

## Design decisions

| Decision | Why |
|---|---|
| The final answer is always really executed | Whether an unexecuted SQL is correct cannot be known |
| Error notes say how to fix the error | A small model fixes a wrong column only when the note lists the real columns of the tables in its query |
| An agent that makes no progress hands over early | The teacher starts with a short history; no steps or money are wasted |
| No LLM and no agent framework in the harness | Every decision is plain Python: readable and reproducible |

All decisions and the work they are based on: [docs/en/AGENTIC_FLOW.md](docs/en/AGENTIC_FLOW.md).

## Code

Each step of the flow lives in a single file, and each of the agent's tools in its own file under `harness/tools/`; `agent/loop.py` only dispatches.

| File | Step | What it does |
|---|---|---|
| `agent/loop.py` | 2, 8 | The flow itself: each tool is one branch that goes to one file; handoff to the teacher, fallback answer |
| `agent/prompts.py`, `agent/llm.py`, `agent/context.py` | | Everything the model sees (prompts and tool definitions), talking to the model, the state of one question |
| `harness/prepare.py` | 1 | Initial context: schema, column descriptions and profiles, evidence |
| `harness/tools/search_values.py` | 3 | Searching values |
| `harness/tools/execute_sql.py` | 4–6 | Pre-check, real execution and cache, turning the result into text |
| `harness/tools/submit.py` | 7 | Final check; the agent must have seen the result of what it submits |
| `harness/guards.py` | every step | Guardrails: broken output, repeated calls, compressing the context |
| `db/` | 1, 5, 6 | SQLite: read-only execution, `EXPLAIN`, schema, profiles and column descriptions |
| `baseline.py` | | The base for comparison: a tool-free single SQL |
| `evaluate.py`, `report.py`, `run.py` | | Evaluation on BIRD dev, result tables, a single question. Every question, wherever it runs, is written to the experience log (`experience/log.jsonl`) for training the agent later |
| `config.py` | | All constants |
| `tests/` | | 81 tests; no API needed, a small test database |

Every part of the flow is always on. Details: [docs/en/CODE_STRUCTURE.md](docs/en/CODE_STRUCTURE.md).

## Status

The system was built in small, numbered stages; each stage adds one piece and is verified by tests.

- ✅ All 8 steps of the flow, on BIRD.
- ⏳ **Measurements:** not taken yet. Development runs use a local Qwen3.5-0.8B policy and a Qwen3.5-9B teacher on the API; the paper's numbers will use local Qwen3.5-4B / Qwen3.6-27B.
- ⏸ **Later:** training the agent inside the harness with the experience log (SFT → on-policy distillation → RL).

## Running

On Apple Silicon (MLX), Python 3.12:

```bash
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -r requirements.txt

# Data (the data/ folder is not in the repository)
#   BIRD dev: https://bird-bench.github.io → data/bird/dev/ (dev.json, dev_databases/)

# Local model server for the policy (in a separate terminal); the teacher uses OPENROUTER_API_KEY from .env
mlx_lm.server --model Qwen/Qwen3.5-0.8B --port 8080 --chat-template-args '{"enable_thinking":false}'

# A single question: prints every step of the agent
python run.py --db data/bird/dev/dev_databases/california_schools/california_schools.sqlite "How many schools are in Alameda county?"

# Evaluation and the base on the same questions
python evaluate.py --name trial --seed 0 --limit 10
python baseline.py --name trial_base --limit 10
python report.py results/trial*.jsonl

# Tests (no API needed)
pytest tests/ --deselect tests/test_llm.py::test_api_answers
```

The model addresses and names are in `config.py`; running the teacher locally, or the policy on the API, takes a few lines (described in the comment there).

## Documents

English:
- [docs/en/AGENTIC_FLOW.md](docs/en/AGENTIC_FLOW.md): the flow step by step, glossary, design decisions and references
- [docs/en/CODE_STRUCTURE.md](docs/en/CODE_STRUCTURE.md): code rules, file map, tools, constants, record formats, build stages
- [docs/en/RESEARCH.md](docs/en/RESEARCH.md): literature review, datasets, hyperparameters

The originals are in Turkish: [docs/AGENTIC_FLOW.md](docs/AGENTIC_FLOW.md), [docs/KOD_YAPISI.md](docs/KOD_YAPISI.md), [docs/ARASTIRMA.md](docs/ARASTIRMA.md).
