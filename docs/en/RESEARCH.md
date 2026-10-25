# Literature Review: Agentic Text-to-SQL and World Models

Turkish original: [../ARASTIRMA.md](../ARASTIRMA.md)

**Scope:** 17 April – 17 October 2026. Older arXiv papers published at a conference within this window are marked separately.
**Review date:** 17 October 2026.

## Method and verification

- Five subtopics were reviewed in parallel:
  1. Agentic Text-to-SQL and RL
  2. World models for agents
  3. Verification, selection and confidence
  4. Distillation, handoff and self-improving agents
  5. Benchmarks and state-of-the-art systems
- Most papers were verified from their arXiv abstract page. Where recipe details were needed, the full HTML text was also read. Leaderboards were pulled directly from their pages on 17 October 2026.
- All numbers are values reported by the authors themselves. None were reproduced.
- BIRD numbers cannot be compared directly across papers: some report greedy decoding, others selection or voting among N candidates.
- Label errors have been reported in 52.8% of BIRD Mini-Dev and 62.8% of Spider2-Snow ([2601.08778](https://arxiv.org/abs/2601.08778)). Differences of 1–2 points may fall within this noise.

## 1. Summary: where has the field converged?

1. **SFT on teacher traces first, then RL.** In every work that tests this with an ablation, the two stages together outperform either one alone. RL without SFT drifts into reward hacking (TRUST-SQL).
2. **The model should be trained in the same harness it will be used in.** In HarnessSQL, the model trained outside the harness scores 9.6, while the one trained inside the harness scores 30.4. SFT is done over the full trajectory, with observation tokens masked out of the loss.
3. **The RL algorithm comes from the GRPO family, with DAPO tricks.** Asymmetric clipping, filtering zero-variance groups, removing or reducing KL. The weight of the reward is on execution accuracy; auxiliary terms are kept small and conditioned on correctness.
4. **The 4B scale is sufficient.** DualSQL-4B and FineStep-4B score about 68 on BIRD dev. Closed 4B systems score 76+ on BIRD test (Native mini 76.86, JoyDataAgent-SQL 76.19).
5. **The top of the overall leaderboard is held by the candidate generation & selection architecture.** Candidates are clustered by their results, then a pairwise selector or a tournament is applied. A reward model alone is weaker than cross-cluster consensus; combining the two is better.
6. **Small verifiers collapse on new schemas.** AUROC is 0.77–0.80 on known schemas and 0.58–0.67 on unseen schemas. The only signal that generalizes across schemas is a large, frozen judge model.
7. **A learned world model that predicts the result of an SQL query does not exist in the literature, so `predict_sql` is novel.** Evidence from neighboring fields shows that the largest payoff of a world model lies not in replacing execution but in training the policy. The agent predicts the result before execution (agent forecast), the real execution checks this forecast, and this check provides a separate training signal for each step (ANTE, ECHO).
8. **BIRD-Interact / Mini-Interact is the only benchmark where execution savings can be measured officially.** Every action has a bird-coin cost, and `execute` costs 1 coin. Unnecessary trial executions are negatively correlated with success (r ≈ −0.52).

## 2. Benchmarks and leaderboards (17 October 2026)

### BIRD (test EX)

| Rank | System | Score | Note |
|---|---|---|---|
| 1 | GrainSQL (Purdue) | 82.95 | No report |
| 2 | DataGallery-Text2SQL (Huawei) | 82.39 | Semantic layer + data agent |
| 3 | SiriusAI-SQL (Tencent) | 82.28 | |
| 5 | Agentar-Scale-SQL (Ant) | 81.67 | 17 candidates + tournament with an RL-trained 32B selector ([2509.24403](https://arxiv.org/abs/2509.24403)) |
| Single model 1 | Gemini-SQL2 | 80.04 | Closed |
| Single model 2 | ReToolSQL (Gemma-4 31B) | 78.14 | SFT → multi-turn RL |
| Single model | SiriusAI-SQL-9B | 77.08 | |
| Single model | Native mini (4B) | 76.86 | Single 4B model, RL-trained data agent; closed weights |
| Overall | JoyDataAgent-SQL (4B) | 76.19 | No report |
| Single model | Qwen3.5-2B + StructCoT | 68.47 | Distillation from a Qwen 27B teacher, no RL |
| Single model | xorazm-text2sql (0.8B) | 59.59 | Qwen3.5-0.8B + GRPO |

- Human performance is 92.96.
- A cleaner dev split named `bird_sql_dev_20251106` has been released.

### Other benchmarks

| Benchmark | What it measures | Best | For us |
|---|---|---|---|
| **BIRD-Interact / Mini-Interact** (SQLite, 300 tasks) | Ambiguity, user simulator, bird-coin budget. Costs: `execute`=1, `ask`=2, `submit`=3; budget B = 6 + 2·m_amb + 2·λ | Full set, a-Interact: ~30.9 (Reward*) | **Where the value of the world model can be measured** |
| BIRD-CRITIC-SQLite (500) | SQL debugging | 63.4; open 7B models ~44 | Repair and handoff loop |
| LiveSQLBench Base-Lite-SQLite | Uncontaminated, knowledge-intensive questions | 72.2 | SELECT subset |
| Spider 2.0-Lite (SQLite slice, 135) | Large schemas, out-of-distribution | 76.2 (all) | Generalization test |
| Effi-SQL (new) | SQL efficiency | | Measures query speed, not the number of executions |

## 3. Agentic Text-to-SQL and RL

| Work | Date | Model | Recipe | Result | Lesson for us |
|---|---|---|---|---|---|
| [HarnessSQL 2610.12274](https://arxiv.org/abs/2610.12274) | Oct | Qwen3 8B/14B | SFT on verified teacher traces collected inside the harness → DAPO; binary reward | Spider2-SQLite 15.5→45.2 (8B) | Train inside the harness. Do not delete failed tool calls from the training data. Context 8K→32K: 27→45. Teacher choice is critical |
| [DualSQL 2609.18135](https://arxiv.org/abs/2609.18135) | Sep | Qwen3 4B/8B | RL only, two roles in a single set of weights; tools: FTS5 value search, profiler, execute; REX reward | BIRD dev **68.0 (4B)** / 71.1 | Rollout guardrails: cut on format error, forbid repeating the same call. Without guardrails training collapses |
| [ReToolSQL 2608.27796](https://arxiv.org/abs/2608.27796) | Aug | Gemma-4 31B / E4B | SFT on privileged teacher traces → GRPO + DAPO; with decreasing KL | 74.32 dev; E4B 68.45 | Tool set very similar to ours. Tools and RL amplify each other's effect. Decreasing KL on the small model gives +2 |
| [FineStep 2605.04719](https://arxiv.org/abs/2605.04719) | May | Qwen3 4B–30B | Step-level process reward requiring no extra model (cell recall rate) | **68.51 (4B, voting)** | Cheap step-level credit. Penalize repeated queries |
| [SERL-SQL 2608.00485](https://arxiv.org/abs/2608.00485) | Aug | Qwen2.5-Coder 7–32B | The teacher re-scores the student's actions; GRPO advantages are reweighted only on SQL/tool tokens | 76.56 (selection among 16 candidates) | One way to embed the teacher signal inside RL |
| [TRUST-SQL 2603.16448](https://arxiv.org/abs/2603.16448) | EMNLP'26 | Qwen3 4B/8B | Explore → Propose → Generate → Confirm; schema reward given only if the answer is correct | 64.9 / 67.2 (4B) | The reward for exploration tools (e.g. `search_values`) must be conditioned on correctness. Without SFT the model hacks the reward |
| [SQL-Trail](https://aclanthology.org/2026.acl-long.1677/) | ACL'26 | Qwen2.5-Coder 3–14B | SFT on 1k Claude traces → GRPO; reward 5×accuracy + 2×turn | 64.2 (7B, voting) | The turn reward cuts unnecessary length |
| [BAP-SQL 2608.02876](https://arxiv.org/abs/2608.02876) | Aug | **Qwen3.5-4B** | An analytical cost estimator (EXPLAIN + statistics) + budget reward + runtime shield | +3.4 under a tight budget; BIRD EX unchanged | The closest example to `predict_sql`. Helps only under a tight budget, does not reduce database load |
| [SQLConductor 2606.23537](https://arxiv.org/abs/2606.23537) | Jun | 4B/8B LoRA orchestrator | SFT on traces collected with MCTS → curriculum GRPO; manages large models | 73.2 | Small policy + large models setup. Select SFT data by stability, not by shortest solution |
| [Progress-SQL 2606.06825](https://arxiv.org/abs/2606.06825) | Jun | 7B/14B | Progress reward + early-correction bonus | 67.5 (14B) | A way to reward recovery from errors |
| [MERIT 2606.00547](https://arxiv.org/abs/2606.00547) | May | 4B memory selector | RL-learned memory retrieval + 7B process reward model | BIRD-Interact 23.3→33.0 | Memory retrieval from the experience log. Store only successful trajectories |
| [MARS-SQL 2511.01008](https://arxiv.org/abs/2511.01008) | ICML'26 | 3×7B | Learned verifier | 77.84 (verifier +8.5) | The final check stage has large value |
| [SQL-Zero 2609.04697](https://arxiv.org/abs/2609.04697) | Sep | 3B/7B | Label-free self-play | +6.6 / +7.3 | Only the first iteration transfers out of distribution |
| [ReViSQL 2603.20004](https://arxiv.org/abs/2603.20004) | Aug | | RLVR on verified data; SQL equivalence reward | | The result-match reward has false positives |
| [Sentinel 2610.04156](https://arxiv.org/abs/2610.04156) | Oct | | A classifier that decides reject / stop / keep the answer from trajectory features | | Template for the agent to notice it is stuck and hand off |
| [Small LM DB agent 2609.21341](https://arxiv.org/abs/2609.21341) | Sep | 39 local models | Error analysis | 36% of losses are tool argument errors | Validate the tool schema, log the arguments |

## 4. World models

| Work | Date | What it predicts | How it is used | Result | Lesson for us |
|---|---|---|---|---|---|
| [ANTE 2610.15368](https://arxiv.org/abs/2610.15368) | Oct | Before each tool call the policy writes an agent forecast (test result, exit code) and a "trust / abstain" decision | Trust reward γ = αq*/(1−q*): saying "trust" pays off only when accuracy exceeds the target q* | SWE-bench V 25.0→57.2 (+6.2 over the same RL without beliefs) | **The closest template for the agent forecast (step 4 in the flow) and the forecast reward** |
| [ECHO 2605.24517](https://arxiv.org/abs/2605.24517) | May | Environment tokens | Auxiliary loss added to GRPO: cross-entropy on environment tokens | About 2× GRPO on Terminal-Bench | Dense signal requiring no extra rollouts |
| [DSWorld 2607.15901](https://arxiv.org/abs/2607.15901) | Jul | Data science state transitions (8B) | MLP router: cheap steps go to real execution, expensive ones to the simulator | 3–6× speedup in search; calibration not reported | Rule-based state construction. Cost-aware routing |
| [EnvSimBench 2605.07247](https://arxiv.org/abs/2605.07247) | May | Tool feedback + state changes | 4B simulator | Accuracy falls off a cliff as the number of state changes grows (≤4% at 5+ changes) | Balance training data by result class. Reasoning traces hurt here |
| [Qwen-AgentWorld 2606.24597](https://arxiv.org/abs/2606.24597) | Jun | Language-based world model across 7 domains (35B/397B) | RL in the simulator | Uncontrolled simulation gives no benefit; controllable simulation + rule anchor +3.7 / +12.3 | RL with simulation must always have a real anchor |
| [WMRL 2608.12564](https://arxiv.org/abs/2608.12564) | Aug | Experiment outcome | Reward source in RL | Training 3–4× faster | Online debiasing + inverse-variance weighting |
| [CoMAP 2606.02372](https://arxiv.org/abs/2606.02372) | Jun | Action feedback | Updated via self-distillation on the policy's own trajectories to adapt to the agent's changing behavior | +16.75% (relative) on Qwen3-4B | Continually retrain the world model with the policy's current data |
| [Dual-Frontier 2609.26293](https://arxiv.org/abs/2609.26293) | Sep | | Trust a prediction only if the expected gain exceeds a certified bound on the world model error | Provable guarantee | The "verify first, then trust" principle |
| [Role-Stratified CRC 2607.24343](https://arxiv.org/abs/2607.24343) | Jul | | A separate conformal risk budget for each role | | Separate thresholds for result type, result shape, values and query types |
| [CYGNET 2606.04645](https://arxiv.org/abs/2606.04645) | Jun | Pre-execution gate for Cypher queries | Layered check: parsing → schema → execution on a mirror database | Catches 100% of structural errors; 0% of semantic errors | Cheap structural checks first, then learned prediction |
| [CacheRL 2606.14179](https://arxiv.org/abs/2606.14179) | Jun | | Fuzzy cache of real execution results | | The cache is the first and cheapest world model layer |
| [AOSpec 2608.00881](https://arxiv.org/abs/2608.00881) | Aug | Observation speculation | Speculation is always used with verification | Latency reduced by 12–33% | A prediction, if verified, hides latency losslessly |
| [WorldEvolver 2606.30639](https://arxiv.org/abs/2606.30639) | Jun | | Selective foresight | Gains at noise level on strong models | Raw token probability is overconfident |
| [World-model-as-tool](https://aclanthology.org/2026.acl-long.623/) | ACL'26 | | The world model is given to the agent as a tool | Agents call it in fewer than 1% of steps; when forced, up to 5% loss | The decision to use the simulator should not be left to the policy alone |
| [Imperfect WMs are Exploitable 2605.15960](https://arxiv.org/abs/2605.15960) | May | | Theory | | The policy exploits the world model's errors |
| [False Prophets 2607.23147](https://arxiv.org/abs/2607.23147) | Jul | | Attack | 95% success at triggering a wrong prediction | A prediction must never disable safety protections |

## 5. Verification, selection, confidence and calibration

| Work | Date | Finding | Lesson for us |
|---|---|---|---|
| [Selective prediction 2607.06799](https://arxiv.org/abs/2607.06799) | Jul | Black-box signals 0.61–0.68 AUROC. A fine-tuned verifier 0.77–0.80 on known schemas, 0.66 on new schemas. Combining two large judges with logistic regression gives 0.82 AUROC, ECE 0.03 | Calibrate the gate on databases unseen in training |
| [TraceSQL 2608.17795](https://arxiv.org/abs/2608.17795) | Aug | GradeSQL-7B 0.58 AUROC on unseen databases; structural features help | Do not trust a small reward model on a new schema |
| [Certified Against Which Oracle? 2609.25938](https://arxiv.org/abs/2609.25938) | Sep | Execution match on a single database understates risk by 3–10 points; a nominal 0.10 guarantee carries 17–20 points of risk against expert labels | Do calibration with stricter labels (test suite with multiple database instances) |
| [GradeSQL 2606.30851](https://arxiv.org/abs/2606.30851) | Jun | Outcome reward model, 68.90 among 32 candidates (majority voting 66.95). The 32B reward model is worse | A 1.5–7B reward model is enough, but only on known schemas |
| [SIRIUS-SQL 2606.01246](https://arxiv.org/abs/2606.01246) | May | Reward model alone 74.32 < majority voting 75.03 < consensus + reward model 75.88 | Add the reward model alongside consensus, not in place of it |
| [R³-SQL 2604.25325](https://arxiv.org/abs/2604.25325) | Apr | Candidates are grouped by result; if the correct candidate appears absent from the pool, resampling is done | Gate and resampling can be used together |
| [Knowing When to Stop 2607.03991](https://arxiv.org/abs/2607.03991) | Jul | A learned stopping rule makes 35% fewer calls | Decide adaptively when to stop sampling |
| [LLM-as-Judge audit 2609.30290](https://arxiv.org/abs/2609.30290) | Sep | Qwen3.6-27B judge ≈ Opus level (κ 0.72). Averaging a weak and a strong judge gives worse results | Combine judges with a combiner model (stacking) or unanimity, not by averaging |
| [Small LMs know? 2609.20824](https://arxiv.org/abs/2609.20824) | | In a small model, token entropy carries no information in 91% of cases | Use sampling- or execution-based uncertainty |
| [Predict own failure 2610.18614](https://arxiv.org/abs/2610.18614) | Oct | Verbal confidence rewarded by outcome within GRPO: AUROC 0.68–0.85, ECE <0.12 | Add a calibration reward to RL |
| [PlanPool 2610.02739](https://arxiv.org/abs/2610.02739) | Oct | Agents give up on clarification questions too early | `ask_user` tool; when candidates diverge (medium), the agent is steered toward asking |
| [Crystallization 2608.07213](https://arxiv.org/abs/2608.07213) / [MIRA 2608.06950](https://arxiv.org/abs/2608.06950) | Aug | Storing verified repairs gives +4.34 (MIRA: +16.5) | Database-specific repair memory |

## 6. Distillation, handoff and self-improving agents

### Distillation

| Work | Date | Finding | Lesson for us |
|---|---|---|---|
| [Guided-OPD 2606.15912](https://arxiv.org/abs/2606.15912) | Jun | Teacher intervention decays to zero on a cosine schedule; reverse KL on student turns, forward KL on teacher turns | The closest template for training step 2 (on-policy distillation) (requires the same tokenizer) |
| [TCOD 2604.24005](https://arxiv.org/abs/2604.24005) | Apr | Curriculum over trajectory depth; +18 over OPD | Makes multi-turn OPD stable |
| [SOD 2605.07725](https://arxiv.org/abs/2605.07725) | May | Masking everything after the first wrong tool call drops the score from 42.98 to 31.85 | Do not cut after an error, down-weight it |
| [STRIDE 2609.14636](https://arxiv.org/abs/2609.14636) | Sep | Stops the rollout when the teacher's log-probability drops and restarts from there; 3.7× speedup | The same signal can also be used as a handoff trigger |
| [Top-K tool drift 2607.07050](https://arxiv.org/abs/2607.07050) | Jul | In Qwen3.5, top-K logits miss the token that starts a tool call | **Specific to Qwen3.5:** in top-K OPD, add the tool start tokens back |
| [Sequential Beats Joint 2609.04108](https://arxiv.org/abs/2609.04108) | Sep | OPD first, then RL; OPD is a better starting point for RL than SFT | Confirms our 3-stage design |
| [RL Starts before RL 2609.28145](https://arxiv.org/abs/2609.28145) | Sep | Reverse KL before RL, then forward KL | Choice of KL direction |
| [GATS 2609.37898](https://arxiv.org/abs/2609.37898) / [RSTG 2608.00782](https://arxiv.org/abs/2608.00782) | Sep / Aug | The teacher steps in only in groups where all attempts failed, and withdraws over time | The teacher's role in the RL step |
| [SGCD 2606.12634](https://arxiv.org/abs/2606.12634) | Jun | Direct self-distillation can break tool use | Control should stay in the policy gradient |
| [Solving w/o Stopping 2609.37326](https://arxiv.org/abs/2609.37326) | Sep | OPD teaches the small model to solve, but not to stop | Use thinking disabled or a short thinking mode |
| [Below the Noise Floor 2608.27729](https://arxiv.org/abs/2608.27729) | Aug | Standard deviation across seeds of 2.8–48.7 points | Evaluate with at least 3 seeds |
| [OLIVE 2609.36246](https://arxiv.org/abs/2609.36246) | Sep | The teacher continues from the state where the student left off; no log-probabilities needed | **An OPD alternative for a teacher used via API; our handoff records already have this structure** |
| [BPM 2607.22334](https://arxiv.org/abs/2607.22334) | Jul | OPD across different tokenizers | If the teacher is from a different family |
| [AMD 2608.07169](https://arxiv.org/abs/2608.07169) | Aug | Training-free, hierarchical teacher memory; 4B students gain the most | Knowledge transfer without touching the weights |

### Handoff and routing

| Work | Date | Finding | Lesson for us |
|---|---|---|---|
| [TSDS 2607.26865](https://arxiv.org/abs/2607.26865) | Jul | Handoff threshold calibrated with Learn-Then-Test; cost guarantee | A principled method for threshold calibration |
| [Replay Gap 2608.08239](https://arxiv.org/abs/2608.08239) | Aug | When the model changes, 61–94% of subsequent actions change | Evaluate handoff with live forks, not replay. Give the teacher a new budget |
| [KL-PBD 2610.15128](https://arxiv.org/abs/2610.15128) | Oct | Expert labels exist only for handed-off cases, which creates selection bias | Correct the bias in handoff data |
| [Agentic Routing Flywheel 2607.11399](https://arxiv.org/abs/2607.11399) | Jul | Every decision is kept as a record (query, state, choice, trace, outcome, cost) | Experience log schema |

### Self-improvement and collapse risk

| Work | Date | Finding | Lesson for us |
|---|---|---|---|
| [Continual Experience 2606.04703](https://arxiv.org/abs/2606.04703) | Jun | Over repeated rounds, existing methods progressively collapse | The biggest risk in repeated retraining rounds |
| [ReSAIL 2609.39306](https://arxiv.org/abs/2609.39306) | Sep | Selecting informative steps + regularization toward a frozen teacher | Recipe against collapse |
| [Denser ≠ Better 2607.01763](https://arxiv.org/abs/2607.01763) | Jul | Dense self-distillation causes more forgetting; GRPO preserves | An RL component should remain in every round |
| [BCIT 2608.26730](https://arxiv.org/abs/2608.26730) | Aug | Gating the reuse of past update evidence | Promotion gate for the retrained policy |
| [UpgradeBench 2608.20918](https://arxiv.org/abs/2608.20918) | Aug | The lifetime of a Text-to-SQL specialist model is shorter than one release interval of the base model | Store raw inputs so the teacher can relabel them |
| [OVCSD 2607.27937](https://arxiv.org/abs/2607.27937) / [HINT-SD 2605.17873](https://arxiv.org/abs/2605.17873) | Jul / May | The teacher continues from the student's state; the loss is applied only where the error occurred | Template for turning a handoff case into training data |
| [MFC 2609.13997](https://arxiv.org/abs/2609.13997) | Sep | GRPO with 128 unsolvable problems ≈ with 2,000 problems | Curriculum for hard cases |

## 7. Realistic expectations for a 4B agent

This table is an inference drawn from comparable systems, not a measurement.

| Setup | Expected BIRD EX |
|---|---|
| Qwen3.5-4B zero-shot / plain SFT | ~46 / 54–56 (dev) |
| SFT + RL with tools, single pass | 62–68 (dev) |
| + up to 8 candidates, result clustering | 66–71 (dev); test ~70–74 |
| Ceiling of closed 4B systems | 76+ (test) |
| Handoff to teacher | +2–5, but in this case the system enters the overall leaderboard, not the single-model leaderboard |
| Mini-Interact Reward* | ~10–20 (best models ~30) |

## 8. Datasets

| Dataset | Engine | Size | Use |
|---|---|---|---|
| BIRD train / dev | SQLite | ~9.4k / 1,534 questions, 95 databases, 33.4 GB in total | Policy training and main evaluation. Cleaner dev split: `bird_sql_dev_20251106` |
| SynSQL-2.5M (OmniSQL, [2503.02240](https://arxiv.org/abs/2503.02240)) | SQLite | 2,544,390 examples, 16,583 databases, Apache 2.0 | World model training: SQL queries are executed to produce labels. Extra SFT data for the policy |
| Mini-Interact / BIRD-Interact ([2510.05318](https://arxiv.org/abs/2510.05318)) | SQLite / Postgres | 300 tasks (Mini) | Budgeted evaluation. Some are CRUD tasks; in the read-only setup the SELECT subset is used |
| BIRD-Critic-SQLite | SQLite | 500 tasks | Repair and handoff |
| LiveSQLBench Base-Lite-SQLite | SQLite | | Uncontaminated evaluation (SELECT subset) |
| Spider 2.0-Lite (SQLite slice) / Spider 2.0-DBT | SQLite / DuckDB | 135 / 68 tasks | Out-of-distribution generalization. HarnessSQL ported the DBT databases to SQLite |
| TPC-H / TPC-DS | DuckDB / Postgres | Generated at the desired scale | A genuinely slow database (Phase 3). No natural-language question set |

Label quality warning: ReViSQL reports that 61% of BIRD train examples require correction. Data cleaning should be done before training (DualSQL removed obvious and unsolvable examples and relabeled some of them).

## 9. Implementation recipe summary

The values below are taken from the corresponding papers. They are starting points and should be tuned with ablations.

**Harness and tools**
- Tools compatible with ReToolSQL and DualSQL:
  - Read-only query: SELECT/WITH only, returns at most ~100 rows.
  - Column profiler.
  - Value search with BM25 / FTS5.
  - Clarification question to the user (`ask_user`); in BIRD-Interact `ask` costs 2 bird-coins.
- Turn limit 5–10. In SERL-SQL 10 turns are slightly worse than 5; in TRUST-SQL 12 turns are unstable.
- Context 32K. In HarnessSQL, going from 8K to 32K raises accuracy from 27.4 to 45.2.
- Guardrails (DualSQL):
  - The rollout is cut on a format error.
  - Repeating the same call with the same arguments is forbidden.
  - Observation tokens are masked out of the loss.
- Tool arguments are validated and logged. In small models, 36% of losses are tool argument errors (2609.21341).
- Thinking mode should be disabled or short (Solving w/o Stopping).

**Policy training**
1. **SFT** (HarnessSQL):
   - Data: verified teacher traces collected inside the harness. Failed tool calls within successful traces are not deleted.
   - The loss is computed over the full trajectory, with observations masked.
   - 3 epochs, lr 1e-5 (cosine), effective batch 16.
   - **Chosen teacher: Qwen3.6-27B, 4-bit** (~16–17 GB; fits in 48 GB together with the policy and the world model). Rationale: in HarnessSQL this teacher gives 23.0 versus 7.4 with Qwen3.5-9B; DeepEye-SQL reaches 78.42 on BIRD test with it; as a judge it is at Opus level (κ 0.72). Its success in our harness is measured before use.
2. **On-policy distillation** (Guided-OPD, TCOD):
   - Teacher intervention decays to zero on a cosine schedule.
   - Reverse KL on student turns, forward KL on teacher turns.
   - Everything after the first wrong tool call is not cut but down-weighted (SOD).
   - If top-K logits are used, the tokens that start a tool call are added back (a Qwen3.5-specific issue).
   - First verify whether Qwen3.6 and Qwen3.5 share the same tokenizer. If not, OLIVE is used: the teacher continues from where the student left off, no log-probabilities needed.
   - Switch to RL once the validation score plateaus (Sequential Beats Joint).
3. **RL** (HarnessSQL, ReToolSQL):
   - DAPO, asymmetric clip [0.20, 0.28], lr 1e-6.
   - 8–16 rollouts per group, zero-variance groups are filtered.
   - KL off or decaying to zero (ReToolSQL: 0.005 → 0.001 → 0).
   - **Main reward:** binary execution accuracy with REX (robust result matching), plus a small format term. Auxiliary terms (schema, turn) are given only if the answer is correct (TRUST-SQL).
   - **Forecast reward** (ANTE): a correct forecast marked "trust" gets +α, a wrong forecast marked "trust" gets −γ, "unsure" gets −κ. γ = α·q\*/(1−q\*); so saying "trust" pays off only when accuracy exceeds q\*. Initial values: q\* = 0.8, α = 0.1, γ = 0.4, κ = 0.02.
   - **Optional calibration reward:** verbal confidence is rewarded according to the outcome (2610.18614).
   - The teacher steps in only in groups where all attempts failed, and withdraws over time (GATS, RSTG).

**World model training**
- Input: schema, column profiles, sample values and the SQL.
- Output: a structured target. Result type (error / empty / non-empty); result shape (columns and row-count range); values (only for small results).
- Data is balanced by result type and complexity: error / empty / simple / complex (EnvSimBench).
- Plain SFT is used, without reasoning traces (they hurt in EnvSimBench). RL is optional; its contribution in DSWorld is ~1%.
- The confidence score comes from token probabilities and is corrected with temperature scaling.
- Prediction gate: trusted if confidence ≥ 0.9 for result type and result shape; the values prediction is not used for decisions. The threshold is checked on a held-out set of databases unseen in training: at least 95% of predictions deemed trusted must be correct, otherwise the threshold is raised. The world model is not used until this check is done.
- A random 5% of predictions found trusted are still executed.
- Future work: separate conformal thresholds by level and query type (Role-Stratified CRC).
- As the policy changes, the world model is retrained on the policy's new executions (CoMAP).
- To be measured:
  - The rate of predictions deemed trusted that turn out wrong.
  - The number of executions saved at fixed accuracy.
  - The effect on end-to-end accuracy.

**Candidate selection and gates**
- The agent's SQL also counts as a candidate. The other candidates are written by the same model in a single pass. The harness builds the prompt: question + evidence + clarifications + schema and column profiles + the search notes from step 3. The agent's SQL queries and execution results are not put into the prompt. Temperature ~0.8. Adaptive rule: start with 2 extra candidates; stop if all 3 give the same result, otherwise go up to 8 in total. In the literature the gain from going from 8 to 16 is small (SIRIUS-SQL). For early stopping: Knowing When to Stop (a learned stopping rule makes 35% fewer calls) and ZAS-SQL (stop once a cluster exceeds a threshold).
- Candidates are grouped by their results. In a tie, the group containing the agent's SQL is chosen. In the first version there is no separate verifier model.
- The confidence gate looks only at consensus (the number of candidates in the largest group):
  - High: 3/3, or at least 6 of 8 candidates.
  - Medium: 4–5 of 8 candidates. A summary of the two largest groups (medium note) is returned to the agent, and the agent runs at most one more time; if it comes out medium a second time, handoff.
  - Low: at most 3 of 8 candidates; handoff.
- The ratio is always computed out of 8; a candidate that is eliminated or errors is not counted in any group.
- Other constants: in the "`config.py` constants" table in [CODE_STRUCTURE.md](CODE_STRUCTURE.md). All are starting values; they are tuned by measurement in Phase 2.
- Possible future additions: a verifier with a small reward model (GradeSQL); a confidence score combining execution status and structural flags via logistic regression; leave-DB-out calibration; Learn-Then-Test or conformal thresholds.
- To avoid:
  - Using the small policy model's token entropy as a correctness signal.
  - Untrained verbal self-confidence. The agent's "trust" decision is not in this category, because it is trained with the forecast reward in RL.
  - Averaging a weak and a strong judge.

**Handoff and offline loop**
- The teacher continues from where the agent left off, with a new budget (OLIVE). Only continuations verified by execution enter training, and the loss is applied to the steps where the error occurred (OVCSD, HINT-SD).
- Each round is mixed with previous data. Regularization toward the frozen previous policy (ReSAIL). The RL component is kept (Denser ≠ Better).
- The new policy passes a promotion gate with at least 3 seeds and holdout tests (BCIT, Below the Noise Floor).
- Raw inputs are stored. When the base model is upgraded, the teacher can relabel them (UpgradeBench).
- Experience log schema: query, split, state, action, agent forecast, world model prediction, real result, cost, output, engine/dialect (Agentic Routing Flywheel). Only the train split enters training.
