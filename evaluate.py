"""BIRD dev'i bir seed'le çalıştırır, BIRD kuralıyla puanlar (result key) ve sonucu
results/<deney>_seed<n>.jsonl'a yazar. Experience log'u agent/loop.py yazar; buradan split, question_id ve cevabın
doğru olup olmadığı eklenir.
Kullanım: python evaluate.py --name <deney> --seed 0 [--limit n]
(--limit n: soruların sabit bir örneklemi; aynı n hep aynı soruları seçer)."""

import argparse
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import config
import report
from agent import loop, prompts
from db import sqlite_db


def load_questions():
    """BIRD dev soruları; her soru kendi veritabanının yolunu (db_path) da taşır."""
    with open(config.BIRD_DEV_DIR / "dev.json") as file:
        questions = json.load(file)
    for question in questions:
        question["db_path"] = str(database_path(question["db_id"]))
    return questions


def sample(questions, limit):
    """limit soruluk sabit bir örneklem (SAMPLE_SEED ile), veri setindeki sırayla. Soruların hepsi aynı veritabanından
    gelmesin diye ilk n soru değil, örneklem alınır."""
    if limit is None or limit >= len(questions):
        return questions
    chosen = random.Random(config.SAMPLE_SEED).sample(range(len(questions)), limit)
    return [questions[number] for number in sorted(chosen)]


def database_path(db_id):
    return config.BIRD_DEV_DIR / "dev_databases" / db_id / f"{db_id}.sqlite"


def score(db_path, sql, gold_sql):
    """BIRD kuralı: cevabın result key'i gold SQL'inkiyle aynıysa doğru. Return: (doğru mu, gold'un hatası)."""
    gold = sqlite_db.execute(db_path, gold_sql)
    if not gold["ok"]:
        return False, gold["error"]
    answer = sqlite_db.execute(db_path, sql)
    return answer["ok"] and answer["result_key"] == gold["result_key"], None


def answer_question(question, seed):
    """Gold SQL yalnızca puanlamada kullanılır: agent'a gitmez, experience log'a not olarak yazılır."""
    tags = {"split": "dev", "dataset": "bird", "question_id": question["question_id"], "gold_sql": question["SQL"]}

    def check(sql):
        return score(question["db_path"], sql, question["SQL"])[0]
    return loop.answer_question(question["question"], question["evidence"], question["db_path"], seed, tags, check)


def run_one(question, seed):
    """Bir soruyu cevaplar ve puanlar; sonuç dosyasının bir satırını return eder."""
    start = time.monotonic()
    row = {"question_id": question["question_id"], "db_id": question["db_id"]}
    try:
        row.update(answer_question(question, seed))
        if row["sql"] is None:  # no_answer
            correct, gold_error = False, None
        else:
            correct, gold_error = score(question["db_path"], row["sql"], question["SQL"])
        row["correct"] = correct
        if gold_error:
            row["gold_error"] = gold_error
    except RuntimeError as error:  # ör. API birkaç denemeye rağmen cevap vermedi
        row["correct"] = False
        row["error"] = str(error)
    row["seconds"] = round(time.monotonic() - start, 2)
    return row


def experiment_header(args, question_count):
    settings = {}
    for name, value in vars(config).items():
        if name.isupper():
            settings[name] = str(value) if isinstance(value, Path) else value
    prompt_texts = {name: value for name, value in vars(prompts).items() if name.isupper()}
    return {"experiment": args.name, "seed": args.seed, "dataset": "bird", "split": "dev",
            "limit": args.limit, "question_count": question_count, "config": settings,
            "prompts": prompt_texts}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    questions = sample(load_questions(), args.limit)
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
