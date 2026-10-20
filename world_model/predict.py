"""World model (adım 6 ve 8, aşama 26): SQL'in sonucunu çalıştırmadan tahmin eder. Prediction, forecast'le aynı
biçimdedir (type, columns, rows) ve ek olarak values ile her biri için confidence taşır. İlk sürümde placeholder:
eğitilmemiş bir LLM'e prompt'la sorar (agent/prompts.py WORLD_MODEL). Eğitilmiş model gelirse yalnızca bu dosya değişir.
Ölçmek için: python -m world_model.predict [satır sayısı]  (experience log'daki gerçek çalıştırmalarla)"""

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import config
from agent import llm, prompts
from harness import compare, prepare

UNKNOWN = {"type": None, "columns": [], "rows": None, "values": [], "confidence": {"type": 0, "shape": 0, "values": 0}}


def predict(sql, context):
    """context.messages[1] adım 1'in şema bağlamıdır."""
    reply = ask(sql, context.messages[1]["content"])
    context.count_usage(reply)
    context.world_model_calls += 1
    return read_prediction(reply["text"])


def ask(sql, schema_context):
    messages = [{"role": "system", "content": prompts.WORLD_MODEL},
                {"role": "user", "content": f"{schema_context}\n\nSQL query:\n{sql}"}]
    return llm.chat(messages, model=config.WORLD_MODEL, temperature=0)


def read_prediction(text):
    """Modelin JSON cevabını okur. Biçimi bozuksa "bilmiyorum" (UNKNOWN) sayılır. Confidence eksik ya da bozuksa
    tahmin okunur ama confidence'lar 0 olur: gate ona hiç güvenmez, ölçüm yine type ve shape'e bakabilir."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    try:
        prediction = json.loads(match.group(0))
    except (AttributeError, ValueError):
        return dict(UNKNOWN)
    if not isinstance(prediction, dict) or compare.forecast_error(dict(prediction, trust=True)):
        return dict(UNKNOWN)
    confidence = {"type": 0, "shape": 0, "values": 0}
    try:
        scores = {name: float(prediction["confidence"][name]) for name in confidence}
        if all(0 <= score <= 1 for score in scores.values()):
            confidence = scores
    except (TypeError, KeyError, ValueError):
        pass
    return {"type": prediction["type"], "columns": prediction.get("columns") or [], "rows": prediction.get("rows"),
            "values": prediction.get("values") or [], "confidence": confidence}


def measure(count):
    """Aşama 26 ve 33'ün ölçümü: experience log'un son gerçek çalıştırmaları için tahmin; type ve shape ne sıklıkla
    tuttu ve GATE_CHOICES'taki her eşikte kaç prediction trusted olur, kaçı doğru (eşik buna bakılarak seçilir).
    Eşik train split'inin kayıtlarıyla seçilmelidir; dev kayıtlarıyla yapılan ölçüm yalnızca bakmak içindir."""
    rows = [json.loads(line) for line in config.EXPERIENCE_LOG.read_text().splitlines()]
    rows = [row for row in rows if row["result"] and row.get("db_path") and row["question_id"] is not None][-count:]

    def one(row):
        schema = prepare.build_context("", "", row["db_path"])
        return read_prediction(ask(row["sql"], schema)["text"])

    with ThreadPoolExecutor(config.EVAL_WORKERS) as pool:
        predictions = list(pool.map(one, rows))
    hits = []
    for row, prediction in zip(rows, predictions):
        hits.append(prediction["type"] is not None and compare.forecast_hit(prediction, row["result"]))
    unknown = sum(prediction["type"] is None for prediction in predictions)
    type_hits = sum(prediction["type"] == row["result"]["type"] for row, prediction in zip(rows, predictions))
    print(f"{len(rows)} çalıştırma | okunamadı: {unknown} | type tuttu: {type_hits} | type ve shape tuttu: {sum(hits)}")
    for threshold in config.GATE_CHOICES:
        trusted = [hit for prediction, hit in zip(predictions, hits)
                   if min(prediction["confidence"]["type"], prediction["confidence"]["shape"]) >= threshold]
        print(f"  eşik {threshold}: trusted {len(trusted)}, doğru {sum(trusted)}")


if __name__ == "__main__":
    measure(int(sys.argv[1]) if len(sys.argv) > 1 else 50)
