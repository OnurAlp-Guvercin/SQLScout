"""BIRD dev'i çalıştırır, BIRD kuralıyla puanlar (result key) ve sonucu results/<deney>.jsonl'a yazar.
Experience log'u agent/loop.py yazar; buradan split, question_id ve cevabın doğru olup olmadığı eklenir.
Kullanım: python evaluate.py --name <deney> [--limit n]
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


def run_gold(question):
    """Gold SQL'in sonucu; soru başına bir kez, ana sorgu süre sınırıyla (ANSWER_TIMEOUT_SECONDS). BIRD dev'in en yavaş
    gold'u ~153 sn sürüyor."""
    return sqlite_db.execute(question["db_path"], question["SQL"], config.ANSWER_TIMEOUT_SECONDS)


def is_correct(db_path, sql, gold):
    """BIRD kuralı: cevabın result key'i gold SQL'inkiyle aynıysa doğru. Gold hata verdiyse hiçbir cevap doğru değil."""
    if not gold["ok"]:
        return False
    answer = sqlite_db.execute(db_path, sql, config.ANSWER_TIMEOUT_SECONDS)
    return answer["ok"] and answer["result_key"] == gold["result_key"]


def run_one(question):
    """Bir soruyu cevaplar ve puanlar; sonuç dosyasının bir satırını return eder. Gold SQL yalnızca puanlamada
    kullanılır: agent'a gitmez, experience log'a not olarak yazılır."""
    start = time.monotonic()
    row = {"question_id": question["question_id"], "db_id": question["db_id"]}
    gold = run_gold(question)
    if not gold["ok"]:
        row["gold_error"] = gold["error"]
    tags = {"split": "dev", "dataset": "bird", "question_id": question["question_id"], "gold_sql": question["SQL"]}

    def check(sql):
        return is_correct(question["db_path"], sql, gold)

    try:
        row.update(loop.answer_question(question["question"], question["evidence"], question["db_path"], tags, check))
        row["correct"] = bool(row["correct"])  # no_answer: None → False
        teacher_check = row["teacher_check"]
        if teacher_check:  # teacher'ın onayladığı ya da reddettiği SQL doğru muydu? Cevapla aynıysa yeniden çalışmaz
            same = teacher_check["sql"] == row["sql"]
            teacher_check["correct"] = row["correct"] if same else check(teacher_check["sql"])
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
    return {"experiment": args.name, "dataset": "bird", "split": "dev",
            "limit": args.limit, "question_count": question_count, "config": settings,
            "prompts": prompt_texts}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    questions = sample(load_questions(), args.limit)
    config.RESULTS_DIR.mkdir(exist_ok=True)
    out_path = config.RESULTS_DIR / f"{args.name}.jsonl"

    start = time.monotonic()
    rows = []
    with open(out_path, "w") as out, ThreadPoolExecutor(config.EVAL_WORKERS) as pool:
        out.write(json.dumps(experiment_header(args, len(questions))) + "\n")
        for row in pool.map(run_one, questions):
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            rows.append(row)
            if len(rows) % 10 == 0:
                print(f"{len(rows)}/{len(questions)}", flush=True)
    report.summary(rows, time.monotonic() - start)
    print(f"Sonuç: {out_path}")


if __name__ == "__main__":
    main()
