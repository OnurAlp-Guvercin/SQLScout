"""Sonuç dosyalarının özeti. evaluate.py her deneyin sonunda summary'yi yazdırır. Birden çok dosya verilince
(ör. aynı deneyin tekrar koşuları) her dosya için tek satırlık bir tablo yazar: python report.py results/<deney>*.jsonl"""

import json
import sys


def summary(rows, wall_seconds):
    """Bir deneyin özeti: doğruluk, süre, maliyet, adım ve çalıştırma sayıları, handoff."""
    correct = sum(bool(row["correct"]) for row in rows)
    cost = sum(row.get("cost") or 0 for row in rows)
    print(f"Doğruluk: {correct}/{len(rows)} = {100 * correct / len(rows):.2f}%")
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
    print(f"Handoff noktası: {handoffs} (teacher'ın cevabı: {teacher})")
    approved, rejected = [], []
    for row in rows:
        check = row.get("teacher_check")
        if check:
            (approved if check["approved"] else rejected).append(check)
    print(f"Teacher kontrolü: {len(approved)} onay ({sum(check['correct'] for check in approved)} doğru), "
          f"{len(rejected)} ret ({sum(check['correct'] for check in rejected)} aslında doğru)")
    for row in rows:
        if "error" in row:
            print(f"  soru {row['question_id']} hata: {row['error'][:200]}")
        if row.get("teacher_error"):
            print(f"  soru {row['question_id']} teacher'a ulaşılamadı: {row['teacher_error'][:200]}")
        if "gold_error" in row:
            print(f"  soru {row['question_id']} gold hatası: {row['gold_error']}")


def table(paths):
    """Her sonuç dosyası bir satır: deney, doğruluk, ortalama gerçek çalıştırma ve tool call."""
    print("deney | doğruluk | çalıştırma | tool call")
    for path in paths:
        lines = open(path).read().splitlines()
        header, rows = json.loads(lines[0]), [json.loads(line) for line in lines[1:]]
        accuracy = f"{100 * sum(bool(row['correct']) for row in rows) / len(rows):.1f}%"
        executions = sum(row.get("executions", 0) for row in rows) / len(rows)
        calls = sum(row.get("tool_calls", 0) for row in rows) / len(rows)
        print(f"{header['experiment']} | {accuracy} ({len(rows)} soru) | "
              f"{executions:.1f} | {calls:.1f}")


if __name__ == "__main__":
    table(sys.argv[1:])
