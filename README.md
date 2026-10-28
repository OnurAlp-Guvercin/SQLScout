# ForeSQL: Predict – Gate – Settle (PGS)

**Agentic Text-to-SQL with an agent loop, a final check and handoff.**

A small model turns a natural-language question into SQL by calling tools: it searches for values, runs SQL and looks at the real result. The small model submits the SQL query it chooses as the answer; it passes a **final check**, and every answer that is returned has actually been executed. If the small model makes no progress or gets stuck, the task is handed over to a larger large model (**handoff**).

The project is being developed as an ICML paper and a course project. The main benchmark is BIRD (SQLite, with evidence).

## Architecture

![PGS flow](docs/PGS_flow_EN.png)

Each column is a component: 🟦 small model, 🟩 harness (plain Python, no LLM), 🟥 real database, 🩵 large model, 🟪 harness decision (final check). The numbers are the steps below.

## How a question is answered

| # | Step | Who | What happens |
|---|---|---|---|
| 1 | Initial context | Harness | Schema, column descriptions, column profiles, up to 3 similar questions solved before (memory), evidence |
| 2 | Agent decides | Agent | One tool call per turn, in the order it chooses: try or explore with SQL, search a value, or submit. At most 10 tool calls |
| 3 | Search for values | Harness | `search_values`: how a value is written and in which column |
| 4 | `execute_sql` | Agent | The agent sends the SQL it wants to try, or a small query to check something it is not sure about |
| 5 | Pre-check | Harness | Is it read-only? Does `EXPLAIN` fail? Has it run before (cache)? |
| 6 | Real execution | Harness | The real result goes back to the agent (at most 20 rows); if it is empty or only 0/NULL, a note suggests checking the value's spelling with `search_values` |
| 7 | `submit` → final check | Harness | The small model submits the SQL it chooses; queries in between do not matter. Two gates: does it run without error, and does the large model find it correct (a JSON reply with a reason)? If it does not run, a note goes back to the small model; failing twice or the large model saying no → 8 |
| 8 | Handoff | Large model | No progress in the first 6 steps or 5 wasted calls in a row, the same call 3 times, the final check failing twice, the large model not approving the answer, or out of budget: the large model solves the question from scratch in the same agent loop as the small model, with the same prompt and 10 tool calls; its answer is checked too |

Example: *"Which category had the most returns in 2025?"* → 1 → 2 → 4 (SQL) → 5 → 6 (1 row) → 2 → 7 (passed) → ✔

## Design decisions

| Decision | Why |
|---|---|
| The final answer is always really executed | Whether an unexecuted SQL is correct cannot be known |
| Error notes say how to fix the error | A small model fixes a wrong column only when the note lists the real columns of the tables in its query |
| A small model that makes no progress hands over early | The large model starts with a short history; no steps or money are wasted |
| No LLM and no agent framework in the harness | Every decision is plain Python: readable and reproducible |

All decisions and the work they are based on: [docs/en/AGENTIC_FLOW.md](docs/en/AGENTIC_FLOW.md).

## Code

Each step of the flow lives in a single file, and each of the agent's tools in its own file under `harness/tools/`; `agent/loop.py` only dispatches.

| File | Step | What it does |
|---|---|---|
| `agent/loop.py` | 2, 8 | The flow itself: each tool is one branch that goes to one file; handoff to the large model, fallback answer |
| `agent/prompts.py`, `agent/llm.py`, `agent/context.py` | | Everything the model sees (prompts and tool definitions), talking to the model, the state of one question |
| `harness/prepare.py` | 1 | Initial context: schema, column descriptions and profiles, evidence |
| `harness/tools/search_values.py` | 3 | Searching values |
| `harness/tools/execute_sql.py` | 4–6 | Pre-check, real execution and cache, turning the result into text |
| `harness/tools/submit.py` | 7 | Final check: runs without error; the large model checks every answer and gives a reason |
| `harness/guards.py` | every step | Guardrails: broken output, repeated calls, compressing the context |
| `db/` | 1, 5, 6 | SQLite: read-only execution, `EXPLAIN`, schema, profiles and column descriptions |
| `baseline.py` | | The base for comparison: a tool-free single SQL |
| `evaluate.py`, `report.py`, `run.py` | | Evaluation on BIRD dev, result tables, a single question. Every question, wherever it runs, is written to the experience log (`experience/log.jsonl`) for training the agent later |
| `config.py` | | All constants |
| `tests/` | | 81 tests; no API needed, a small test database |

Every part of the flow is always on; the ablation flags are `evaluate.py --no-handoff` (the large model only checks answers and never takes over) and `--no-memory` (no similar solved questions in the context). Details: [docs/en/CODE_STRUCTURE.md](docs/en/CODE_STRUCTURE.md).

## Status

- ✅ All 8 steps of the flow, on BIRD.
- ⏭ **Next:** training the agent inside the harness with the experience log (method open: SFT, distillation, RL or a mix).
- ⏸ **Later:** the paper's numbers with local models (Qwen3.5-4B small model). Development runs use a local Qwen3.5-0.8B small model and a Qwen3.5-9B large model on the API.

## Running

On Apple Silicon (MLX), Python 3.12:

```bash
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -r requirements.txt

# Data (the data/ folder is not in the repository)
#   BIRD dev: https://bird-bench.github.io → data/bird/dev/ (dev.json, dev_databases/)

# Local models (the models/ folder is not in the repository)
hf download Qwen/Qwen3.5-0.8B --local-dir models/Qwen3.5-0.8B
hf download Qwen/Qwen3-Embedding-0.6B --local-dir models/Qwen3-Embedding-0.6B

# Memory: add BIRD train's gold question–SQL pairs once (only train/train.json from BIRD's train.zip is needed)
python -m harness.memory data/bird/train/train.json

# Local model server for the small model (in a separate terminal); the large model uses OPENROUTER_API_KEY from .env
mlx_lm.server --model models/Qwen3.5-0.8B --port 8080 --chat-template-args '{"enable_thinking":false}'

# A single question: prints every step of the agent
python run.py --db data/bird/dev/dev_databases/california_schools/california_schools.sqlite "How many schools are in Alameda county?"

# Evaluation and the base on the same questions
python evaluate.py --name trial --limit 10
python baseline.py --name trial_base --limit 10
python report.py results/trial*.jsonl

# Tests (no API needed)
pytest tests/ --deselect tests/test_llm.py::test_api_answers
```

The model addresses and names are in `config.py`; running the large model locally, or the small model on the API, takes a few lines (described in the comment there).

## Documents

English:
- [docs/en/AGENTIC_FLOW.md](docs/en/AGENTIC_FLOW.md): the flow step by step, glossary, design decisions and references
- [docs/en/CODE_STRUCTURE.md](docs/en/CODE_STRUCTURE.md): code rules, file map, tools, constants, record formats, next stages
- [docs/en/RESEARCH.md](docs/en/RESEARCH.md): literature review, datasets, hyperparameters

The originals are in Turkish: [docs/AGENTIC_FLOW.md](docs/AGENTIC_FLOW.md), [docs/KOD_YAPISI.md](docs/KOD_YAPISI.md), [docs/ARASTIRMA.md](docs/ARASTIRMA.md).
