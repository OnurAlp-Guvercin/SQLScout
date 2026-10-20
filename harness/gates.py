"""Adım 6: prediction gate ve audit (aşama 27). Adım 9: confidence gate (aşama 20) ve medium note (aşama 21);
confidence gate yalnızca consensus'a bakar: en kalabalık gruptaki candidate sayısı."""

import random

import config
from harness import guards, precheck


def trusted(prediction):
    """World model'in result type ve result shape confidence'ı ikisi de eşiğin üstündeyse trusted."""
    confidence = prediction["confidence"]
    return confidence["type"] >= config.PREDICTION_GATE and confidence["shape"] >= config.PREDICTION_GATE


def audit(sql, context):
    """Trusted prediction'ların AUDIT_SHARE kadarı yine de çalıştırılır. Aynı seed ve SQL hep aynı kararı verir."""
    return random.Random(f"{context.seed} {precheck.sql_key(sql)}").random() < config.AUDIT_SHARE


def prediction_note(prediction):
    """Trusted prediction agent'a "prediction" etiketiyle döner; cevap olarak kullanılamaz."""
    if prediction["type"] == "rows":
        names = ", ".join(str(name) for name in prediction["columns"])
        shape = f"{len(prediction['columns'])} column(s) ({names}), {prediction['rows']} row(s)"
    else:
        shape = prediction["type"]
    note = f"Prediction (the query was NOT run, this is a model's guess): {shape}."
    if prediction["values"]:
        note += f" Values: {prediction['values']}"
    return note + " Use it to plan your next query; to submit an answer, run it for real."


def confidence(groups, candidate_count):
    """high: 3/3 ya da ≥6/8 · medium: 4–5/8 · low: ≤3/8. Hata veren candidate hiçbir gruba sayılmaz."""
    largest = len(groups[0]["sqls"]) if groups else 0
    if largest == candidate_count or largest >= config.HIGH_MIN:
        return "high"
    if largest >= config.MEDIUM_MIN:
        return "medium"
    return "low"


def medium_note(groups, candidate_count):
    """Agent'a dönen not: en kalabalık 2 grubun temsilci SQL'i, candidate sayısı ve sonuç özeti."""
    lines = ["Medium confidence: other SQL queries written for this question give different results. "
             "The largest groups:"]
    for number, group in enumerate(groups[:config.MEDIUM_NOTE_GROUPS], start=1):
        result = group["result"]
        lines.append(f"Group {number} ({len(group['sqls'])} of {candidate_count} candidates): {group['sqls'][0]}")
        lines.append(f"  Columns: {', '.join(result['columns'])}; {result['row_count']} rows")
        for row in guards.trim_rows(result["rows"][:config.MEDIUM_NOTE_ROWS]):
            lines.append("  " + " | ".join(row))
    lines.append("Decide which one answers the question: submit it, or run a new query first.")
    return "\n".join(lines)
