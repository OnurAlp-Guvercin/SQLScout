"""Base: tool'suz tek SQL. Model adım 1'in bağlamını görür ve tek seferde bir SQL yazar (temperature 0); agent loop,
tool, final check ve handoff yoktur. Agentic sistem bununla karşılaştırılır; sonuç dosyası evaluate.py'ninkiyle aynı
biçimdedir, report.py ikisini de okur.
Kullanım: python baseline.py --name <deney> [--model <model>] [--limit n] → results/<deney>_seed0.jsonl"""

import argparse
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor

import config
import evaluate
import report
from agent import llm, prompts
from harness import prepare


def answer(question, model):
    """Bir soruyu tek SQL'le cevaplar ve puanlar. Return: sonuç dosyasının bir satırı."""
    start = time.monotonic()
    context = prepare.build_context(question["question"], question["evidence"], question["db_path"])
    messages = [{"role": "system", "content": prompts.WRITE_SQL}, {"role": "user", "content": context}]
    reply = llm.chat(messages, temperature=0, model=model)
    sql = extract_sql(reply["text"])
    correct, gold_error = evaluate.score(question["db_path"], sql, question["SQL"])
    row = {"question_id": question["question_id"], "db_id": question["db_id"], "sql": sql, "correct": correct,
           "prompt_tokens": reply["prompt_tokens"], "completion_tokens": reply["completion_tokens"],
           "cost": reply["cost"] or 0, "seconds": round(time.monotonic() - start, 2)}
    if gold_error:
        row["gold_error"] = gold_error
    return row


def extract_sql(text):
    """Modelin cevabındaki ilk ``` bloğunun içi (```sql ya da düz ```; kapanmamışsa metnin sonuna kadar); blok yoksa
    cevabın tamamı."""
    match = re.search(r"```(?:sql)?\s*(.*?)(?:```|$)", text, re.DOTALL | re.IGNORECASE)
    if match and match.group(1).strip():
        return match.group(1).strip()
    return text.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--model", default=config.POLICY_MODEL)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    questions = evaluate.sample(evaluate.load_questions(), args.limit)
    start = time.monotonic()
    with ThreadPoolExecutor(config.EVAL_WORKERS) as pool:
        rows = list(pool.map(lambda question: answer(question, args.model), questions))
    header = {"experiment": args.name, "seed": 0, "dataset": "bird", "split": "dev", "limit": args.limit,
              "question_count": len(rows), "system": "baseline", "model": args.model, "temperature": 0,
              "prompt": prompts.WRITE_SQL}
    config.RESULTS_DIR.mkdir(exist_ok=True)
    out_path = config.RESULTS_DIR / f"{args.name}_seed0.jsonl"
    with open(out_path, "w") as out:
        out.write(json.dumps(header) + "\n")
        for row in rows:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
    report.summary(rows, time.monotonic() - start)
    print(f"Sonuç: {out_path}")


if __name__ == "__main__":
    main()
