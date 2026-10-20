"""Bir veri setini (BIRD dev ya da Mini-Interact) bir seed'le çalıştırır, BIRD kuralıyla puanlar (result key) ve sonucu
results/<deney>_seed<n>.jsonl'a yazar. ask_user'ı user simulator cevaplar.
Kullanım: python evaluate.py --name <deney> --seed 0 [--dataset bird|mini_interact] [--subset] [--limit n]
                           [--off USE_CANDIDATES ...] [--simulate-cost]
(--subset: BIRD'den sabit 50 soru; --limit n: ilk n soru; --off: ablation için flag'leri kapatır;
--simulate-cost: bird-coin budget'ı ve simüle edilmiş sorgu maliyeti, Phase 2)."""

import argparse
import json
import random
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import config
import mini_interact
import report
from agent import loop, prompts, tools
from db import sqlite_db


def load_questions(subset):
    """BIRD dev soruları; her soru kendi veritabanının yolunu (db_path) da taşır."""
    with open(config.BIRD_DEV_DIR / "dev.json") as file:
        questions = json.load(file)
    if subset:
        questions = random.Random(config.SUBSET_SEED).sample(questions, config.SUBSET_SIZE)
        questions.sort(key=lambda question: question["question_id"])
    for question in questions:
        question["db_path"] = str(database_path(question["db_id"]))
    return questions


def database_path(db_id):
    return config.BIRD_DEV_DIR / "dev_databases" / db_id / f"{db_id}.sqlite"


def score(db_path, sql, gold_sql):
    """BIRD kuralı: cevabın result key'i gold SQL'inkiyle aynıysa doğru. Döner: (doğru mu, gold'un hatası)."""
    gold = sqlite_db.execute(db_path, gold_sql)
    if not gold["ok"]:
        return False, gold["error"]
    answer = sqlite_db.execute(db_path, sql)
    return answer["ok"] and answer["result_key"] == gold["result_key"], None


def answer_question(question, seed):
    # Gold SQL ve belirsizlik notları yalnızca user simulator'e gider (ask_user); agent'ın mesajlarına hiç girmez.
    return loop.answer_question(question["question"], question["evidence"], question["db_path"], seed,
                                question_id=question["question_id"], split="dev", gold_sql=question["SQL"],
                                ambiguity=question.get("ambiguity"))


def run_one(question, seed):
    """Bir soruyu cevaplar ve puanlar; sonuç dosyasının bir satırını döndürür."""
    start = time.monotonic()
    row = {"question_id": question["question_id"], "db_id": question["db_id"]}
    try:
        row.update(answer_question(question, seed))
        if question["SQL"] is None:  # Mini-Interact'in doğru SQL'leri yoksa puanlanmaz
            correct, gold_error = None, None
        elif row["sql"] is None:  # no_answer
            correct, gold_error = False, None
        else:
            correct, gold_error = score(question["db_path"], row["sql"], question["SQL"])
        row["correct"] = correct
        if gold_error:
            row["gold_error"] = gold_error
    except RuntimeError as error:  # ör. API birkaç denemeye rağmen cevap vermedi
        row["correct"] = None if question["SQL"] is None else False
        row["error"] = str(error)
    row["seconds"] = round(time.monotonic() - start, 2)
    return row


def experiment_header(args, question_count):
    settings = {}
    for name, value in vars(config).items():
        if name.isupper():
            settings[name] = str(value) if isinstance(value, Path) else value
    prompt_texts = {name: value for name, value in vars(prompts).items() if name.isupper()}
    prompt_texts.update({name: value for name, value in vars(tools).items() if name.isupper()})
    return {"experiment": args.name, "seed": args.seed, "dataset": args.dataset, "split": "dev",
            "subset": args.subset, "limit": args.limit, "question_count": question_count, "config": settings,
            "prompts": prompt_texts}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--dataset", choices=["bird", "mini_interact"], default="bird")
    parser.add_argument("--subset", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--off", nargs="*", default=[], choices=[name for name in vars(config) if name.startswith("USE_")])
    parser.add_argument("--simulate-cost", action="store_true")
    args = parser.parse_args()
    for flag in args.off:
        setattr(config, flag, False)
    config.SIMULATE_COST = args.simulate_cost

    random.seed(args.seed)
    if args.dataset == "bird":
        questions = load_questions(args.subset)[:args.limit]
    else:
        questions = mini_interact.load_questions()[:args.limit]
    # Her deney ve seed boş bir database memory ile başlar.
    config.MEMORY_DIR = config.MEMORY_DIR / f"{args.name}_seed{args.seed}"
    shutil.rmtree(config.MEMORY_DIR, ignore_errors=True)
    config.RESULTS_DIR.mkdir(exist_ok=True)
    out_path = config.RESULTS_DIR / f"{args.name}_seed{args.seed}.jsonl"

    start = time.monotonic()
    rows = []
    with open(out_path, "w") as out, ThreadPoolExecutor(config.EVAL_WORKERS) as pool:
        out.write(json.dumps(experiment_header(args, len(questions))) + "\n")
        for row in pool.map(lambda question: run_one(question, args.seed), questions):
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            rows.append(row)
            if len(rows) % 10 == 0:
                print(f"{len(rows)}/{len(questions)}", flush=True)
    report.summary(rows, time.monotonic() - start)
    print(f"Sonuç: {out_path}")


if __name__ == "__main__":
    main()
