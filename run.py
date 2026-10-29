"""Tek bir soruyu baştan sona çalıştırır: agent'ın her adımını olduğu anda (terminalde renkli), cevabı ve cevabın
gerçek sonucunu yazar. Kullanım: python run.py --db <sqlite yolu> "soru" [--evidence "..."]"""

import argparse
import json
import sys

import config
from agent import loop
from db import sqlite_db

# Terminal renkleri (ANSI). Çıktı bir dosyaya yönlendirilince renk kodu yazılmaz, düz metin kalır.
BLUE, CYAN, GREEN, YELLOW, RED, GRAY, BOLD = "34", "36", "32", "33", "31", "90", "1"
STOP_WORDS = ("Rejected", "Final check failed", "Not run again", "Reviewer:", "Handoff:", "Stopped:")


def paint(text, code):
    return f"\033[{code}m{text}\033[0m" if sys.stdout.isatty() else text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("question")
    parser.add_argument("--evidence", default="")
    args = parser.parse_args()

    print(paint("Çalışıyor; her adım olduğu anda yazılır.\n", GRAY), flush=True)
    answer = loop.answer_question(args.question, args.evidence, args.db, show_step=show_step)
    if answer["memory_examples"]:
        print(paint("\nBağlama eklenen benzer sorular (memory):", BOLD))
        for question in answer["memory_examples"]:
            print(paint(f"  - {question}", GRAY))
    label_color = {"ok": GREEN, "fallback": YELLOW}.get(answer["label"], RED)
    print("\n" + paint(f"Label: {answer['label']}", label_color + ";" + BOLD) + f" | cevabı bulan: {answer['answered_by']} | tool call: {answer['tool_calls']}"
          f" | gerçek çalıştırma: {answer['executions']}"
          f" | {answer['prompt_tokens']} + {answer['completion_tokens']} token, ${answer['cost']:.4f}")
    if answer["handoff_reason"]:
        print(paint(f"Handoff nedeni: {answer['handoff_reason']}", CYAN))
    if answer["large_model_error"]:
        print(paint(f"Large model'e ulaşılamadı: {answer['large_model_error']}", RED))
    if answer["sql"] is None:
        print(paint(answer["error_message"], RED))
        return
    print(paint("SQL: ", BOLD) + answer["sql"])
    result = sqlite_db.execute(args.db, answer["sql"], config.ANSWER_TIMEOUT_SECONDS)
    if not result["ok"]:
        print(paint(f"Hata: {result['error']}", RED))
        return
    print(paint(f"Sonuç ({result['row_count']} satır): ", BOLD) + str(result["columns"]))
    for row in result["rows"][:10]:
        print(f"  {row}")


def show_step(number, step):
    """Bir adımı (tool call ve sonucu) okunur biçimde, olduğu anda yazar. Small model mavi, large model turkuaz; sonuç
    gri, ret ve hata kırmızı, kabul yeşil."""
    who = paint("small model", BLUE) if step["by"] == "small_model" else paint("large model", CYAN)
    if step["tool"]:
        call = paint(step["tool"], BOLD) + "(" + json.dumps(step["args"], ensure_ascii=False) + ")"
    else:
        call = paint("(tool call yok) ", RED) + repr(step["text"][:200])
    result = step["result"]
    result_color = RED if result.startswith(STOP_WORDS) else GREEN if result == "Accepted." else GRAY
    print(f"[{number}] {who} → {call}")
    print(paint("    " + result.replace("\n", "\n    "), result_color) + "\n", flush=True)


if __name__ == "__main__":
    main()
