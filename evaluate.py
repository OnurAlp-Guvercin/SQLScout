"""BIRD dev'i çalıştırır, BIRD kuralıyla puanlar (result key) ve sonucu results/<deney>.jsonl'a yazar.
Experience log'u agent/loop.py yazar; buradan split, question_id ve cevabın doğru olup olmadığı eklenir.
Kullanım: python evaluate.py --name <deney> [--limit n] [--no-handoff] [--large-model-agent]
(--limit n: soruların sabit bir örneklemi; aynı n hep aynı soruları seçer)."""

import argparse
import hashlib
import json
import random
import subprocess
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


def run_one(question, run=None):
    """Bir soruyu cevaplar ve puanlar; sonuç dosyasının bir satırını return eder. Gold SQL yalnızca puanlamada
    kullanılır: agent'a gitmez, experience log'a not olarak yazılır. run: koşunun adı (--name) ve başlama zamanı;
    memory'de yalnızca bu koşunun soruları örnek olur."""
    start = time.monotonic()
    row = {"question_id": question["question_id"], "db_id": question["db_id"]}
    gold = run_gold(question)
    if not gold["ok"]:
        row["gold_error"] = gold["error"]
    tags = {"split": "dev", "dataset": "bird", "question_id": question["question_id"], "gold_sql": question["SQL"],
            "run": run}

    def check(sql):
        return is_correct(question["db_path"], sql, gold)

    try:
        row.update(loop.answer_question(question["question"], question["evidence"], question["db_path"], tags, check))
        row["correct"] = bool(row["correct"])  # no_answer: None → False
        for large_model_check in row["large_model_checks"]:  # large model'in onayladığı ya da reddettiği SQL doğru muydu?
            same = large_model_check["sql"] == row["sql"]  # cevapla aynıysa yeniden çalışmaz
            large_model_check["correct"] = row["correct"] if same else check(large_model_check["sql"])
    except Exception as error:  # ör. API birkaç denemeye rağmen cevap vermedi; koşu diğer sorularla sürer
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
            "limit": args.limit, "question_count": question_count, "code": code_version(), "config": settings,
            "prompts": prompt_texts}


def code_version():
    """Deneyin çalıştığı kod: git commit'i ve commit edilmemiş değişikliklerin (yeni dosyalar dahil) hash'i; değişiklik
    yoksa None. Harness'ın notları da koddadır; aynı commit ve aynı hash aynı kod demektir."""
    def git(*command):
        return subprocess.run(["git", *command], cwd=config.PROJECT_DIR, capture_output=True, text=True).stdout
    diff = git("diff", "HEAD")
    for name in git("ls-files", "--others", "--exclude-standard").split():  # henüz git'e eklenmemiş dosyalar
        diff += name + (config.PROJECT_DIR / name).read_text(errors="replace")
    return {"commit": git("rev-parse", "HEAD").strip(),
            "uncommitted_diff_sha256": hashlib.sha256(diff.encode()).hexdigest() if diff else None}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--no-handoff", action="store_true", help="ablation: large model yalnızca kontrol eder, devralmaz")
    parser.add_argument("--no-memory", action="store_true", help="ablation: bağlama benzer çözülmüş sorular eklenmez")
    parser.add_argument("--large-model-agent", action="store_true",
                        help="agent de large model (API'de); handoff kapalı: model kendine devretmez")
    args = parser.parse_args()
    if args.no_memory:
        config.MEMORY = False  # başlıktaki config'e de böyle yazılır
    if args.no_handoff or args.large_model_agent:
        config.HANDOFF = False  # başlıktaki config'e de böyle yazılır
    if args.large_model_agent:  # config.py'deki "small model'i API'ye almak" tarifi
        config.SMALL_MODEL_URL = config.LARGE_MODEL_URL
        config.SMALL_MODEL = config.LARGE_MODEL
        config.SMALL_MODEL_PROVIDERS = config.LARGE_MODEL_PROVIDERS
        config.EVAL_WORKERS = 4

    questions = sample(load_questions(), args.limit)
    config.RESULTS_DIR.mkdir(exist_ok=True)
    out_path = config.RESULTS_DIR / f"{args.name}.jsonl"

    start = time.monotonic()
    run = f"{args.name} {time.strftime('%Y-%m-%d %H:%M:%S')}"  # aynı adla tekrar koşu öncekinin cevaplarını görmesin
    rows = []
    with open(out_path, "w") as out, ThreadPoolExecutor(config.EVAL_WORKERS) as pool:
        out.write(json.dumps(experiment_header(args, len(questions))) + "\n")
        for row in pool.map(lambda question: run_one(question, run), questions):
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            rows.append(row)
            if len(rows) % 10 == 0:
                print(f"{len(rows)}/{len(questions)}", flush=True)
    report.summary(rows, time.monotonic() - start)
    print(f"Sonuç: {out_path}")


if __name__ == "__main__":
    main()
