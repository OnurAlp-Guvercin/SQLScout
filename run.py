"""Tek bir soruyu baştan sona çalıştırır: agent'ın her adımını, cevabı ve cevabın gerçek sonucunu yazar.
Kullanım: python run.py --db <sqlite yolu> "soru" [--evidence "..."]"""

import argparse
import json

from agent import loop
from db import sqlite_db


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("question")
    parser.add_argument("--evidence", default="")
    args = parser.parse_args()

    answer = loop.answer_question(args.question, args.evidence, args.db)
    show_steps(answer)
    print(f"\nLabel: {answer['label']} | cevabı bulan: {answer['answered_by']} | tool call: {answer['tool_calls']}"
          f" | gerçek çalıştırma: {answer['executions']}"
          f" | {answer['prompt_tokens']} + {answer['completion_tokens']} token, ${answer['cost']:.4f}")
    if answer["handoff_reason"]:
        print(f"Handoff nedeni: {answer['handoff_reason']}")
    if answer["sql"] is None:
        print("Cevap yok.")
        return
    print(f"SQL: {answer['sql']}")
    result = sqlite_db.execute(args.db, answer["sql"])
    if not result["ok"]:
        print(f"Hata: {result['error']}")
        return
    print(f"Sonuç ({result['row_count']} satır): {result['columns']}")
    for row in result["rows"][:10]:
        print(f"  {row}")


def show_steps(answer):
    """Adımları okunur biçimde yazar."""
    for number, step in enumerate(answer["steps"], start=1):
        if step["by"] == "teacher":
            print("    (teacher)")
        if step["tool"]:
            print(f"[{number}] {step['tool']}({json.dumps(step['args'], ensure_ascii=False)})")
        else:
            print(f"[{number}] (tool call yok) {step['text'][:200]!r}")
        print(f"    → {step['result']}")


if __name__ == "__main__":
    main()
