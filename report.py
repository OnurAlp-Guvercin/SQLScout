"""Sonuç dosyalarının özeti. evaluate.py her deneyin sonunda summary'yi yazdırır. Birden çok dosya verilince
(ör. seed'ler) her dosya için tek satırlık bir tablo yazar: python report.py results/asama29_*.jsonl"""

import json
import sys


def summary(rows, wall_seconds):
    """Bir deneyin özeti: doğruluk, süre, maliyet, tool call ve çalıştırma sayıları, handoff, ask_user."""
    scored = [row for row in rows if row["correct"] is not None]
    correct = sum(row["correct"] for row in scored)
    cost = sum(row.get("cost") or 0 for row in rows)
    if scored:
        print(f"Doğruluk: {correct}/{len(scored)} = {100 * correct / len(scored):.2f}%")
    if len(scored) < len(rows):
        print(f"Puanlanmayan soru: {len(rows) - len(scored)} (doğru SQL'i yok)")
    print(f"Süre: {wall_seconds:.0f} sn toplam, soru başına ortalama {sum(r['seconds'] for r in rows) / len(rows):.1f} sn")
    labels = {}
    for row in rows:
        labels[row.get("label")] = labels.get(row.get("label"), 0) + 1
    print(f"Maliyet: ${cost:.4f} | ortalama tool call: {sum(r.get('tool_calls', 0) for r in rows) / len(rows):.1f}"
          f" | ortalama gerçek çalıştırma: {sum(r.get('executions', 0) for r in rows) / len(rows):.1f}"
          f" | label'lar: {labels}")
    searches = 0
    for row in rows:
        for step in row.get("steps", []):
            if step["tool"] == "search_values":
                searches += 1
    print(f"Search çağrısı: {searches}")
    teacher = sum(row.get("answered_by") == "teacher" for row in rows)
    handoffs = sum(bool(row.get("handoff_reason")) for row in rows)
    asks = sum(len(row.get("clarifications", [])) for row in rows)
    print(f"Handoff noktası: {handoffs} (teacher'ın cevabı: {teacher}) | ask_user: {asks}")
    for row in rows:
        if "error" in row:
            print(f"  soru {row['question_id']} hata: {row['error'][:200]}")
        if "gold_error" in row:
            print(f"  soru {row['question_id']} gold hatası: {row['gold_error']}")


def table(paths):
    """Her sonuç dosyası bir satır: deney, seed, doğruluk, ortalama gerçek çalıştırma ve tool call."""
    print("deney | seed | doğruluk | çalıştırma | tool call")
    for path in paths:
        lines = open(path).read().splitlines()
        header, rows = json.loads(lines[0]), [json.loads(line) for line in lines[1:]]
        scored = [row for row in rows if row["correct"] is not None]
        accuracy = f"{100 * sum(row['correct'] for row in scored) / len(scored):.1f}%" if scored else "-"
        executions = sum(row.get("executions", 0) for row in rows) / len(rows)
        calls = sum(row.get("tool_calls", 0) for row in rows) / len(rows)
        print(f"{header['experiment']} | {header['seed']} | {accuracy} ({len(scored)} soru) | "
              f"{executions:.1f} | {calls:.1f}")


if __name__ == "__main__":
    table(sys.argv[1:])
