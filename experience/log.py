"""Experience log (adım 7): her gerçek çalıştırma ve her world model prediction'ı experience/log.jsonl'a bir satırdır.
Eğitim verisi buradan çıkar; eğitime yalnızca split = train satırları girer."""

import json
import threading
from pathlib import Path

import config
from harness import compare

log_lock = threading.Lock()  # evaluate.py soruları aynı anda çalıştırır; satırlar birbirine karışmasın


def write(context, sql, forecast, actual, seconds, run_by="agent", prediction=None):
    """actual: compare.summary'nin gerçek sonuç özeti; trusted bir prediction'da sorgu çalışmadığı için None.
    prediction: world model'e gidildiyse onun tahmini. Karşılaştırılacak bir şey yoksa *_hit alanları boştur."""
    forecast_hit = compare.forecast_hit(forecast, actual) if forecast and actual else None
    prediction_hit = None
    if prediction and actual:
        prediction_hit = prediction["type"] is not None and compare.forecast_hit(prediction, actual)
    model = config.TEACHER_MODEL if run_by == "teacher" else config.POLICY_MODEL
    record = {
        "question_id": context.question_id, "split": context.split, "db_id": Path(context.db_path).stem,
        "db_path": context.db_path,
        "engine": "sqlite", "dialect": "sqlite", "run_by": run_by, "sql": sql,
        "forecast": forecast, "prediction": prediction, "result": actual, "forecast_hit": forecast_hit,
        "prediction_hit": prediction_hit, "seconds": round(seconds, 3), "model": model, "seed": context.seed,
    }
    with log_lock:
        config.EXPERIENCE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(config.EXPERIENCE_LOG, "a") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
