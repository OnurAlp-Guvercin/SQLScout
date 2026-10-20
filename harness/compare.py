"""Adım 7: compare. Agent'ın forecast'ini gerçek sonuçla karşılaştırır; tutmadıysa surprise note yazar (aşama 15).
Forecast'in biçimi de burada denetlenir (adım 4). World model'in prediction'ı forecast'le aynı biçimde olduğu için
o da forecast_hit ile karşılaştırılır (experience/log.py, world_model/predict.py)."""

import config

TYPES = ["error", "empty", "rows"]


def forecast_error(forecast):
    """Forecast doğruysa None; değilse agent'a dönecek, hatalı alanları adıyla söyleyen kısa metin."""
    if not isinstance(forecast, dict):
        return 'it must be an object like {"type": "rows", "columns": ["name"], "rows": "1", "trust": true}'
    problems = []
    if forecast.get("type") not in TYPES:
        problems.append(f"type must be one of: {', '.join(TYPES)}")
    if forecast.get("type") == "rows":
        columns = forecast.get("columns")
        if not isinstance(columns, list) or not columns:
            problems.append("columns must be a non-empty list of the expected column names")
        if forecast.get("rows") not in config.ROW_RANGES:
            problems.append(f"rows must be one of: {', '.join(config.ROW_RANGES)}")
    if not isinstance(forecast.get("trust"), bool):
        problems.append("trust must be true or false")
    return "; ".join(problems) or None


def summary(result):
    """Gerçek sonucun özeti: type, sütun sayısı, satır aralığı ve result key. Experience log'a da bu yazılır."""
    if not result["ok"]:
        return {"type": "error", "columns": None, "rows": None, "result_key": None}
    if result["row_count"] == 0:
        return {"type": "empty", "columns": len(result["columns"]), "rows": "0", "result_key": result["result_key"]}
    return {"type": "rows", "columns": len(result["columns"]), "rows": row_range(result["row_count"]),
            "result_key": result["result_key"]}


def row_range(count):
    """Satır sayısının aralığı: config.ROW_RANGES'teki "0", "2-10", "100+" gibi etiketlerden biri."""
    for label in config.ROW_RANGES:
        if "-" in label:
            low, high = label.split("-")
            if int(low) <= count <= int(high):
                return label
        elif label.endswith("+"):
            if count > int(label[:-1]):
                return label
        elif count == int(label):
            return label
    return None


def forecast_hit(forecast, actual):
    """Tuttu mu: type aynı; rows ise sütun sayısı ve satır aralığı da aynı. Sütun adlarına bakılmaz."""
    if forecast["type"] != actual["type"]:
        return False
    if actual["type"] != "rows":
        return True
    return len(forecast["columns"]) == actual["columns"] and forecast["rows"] == actual["rows"]


def surprise_note(forecast, actual):
    """Forecast tuttuysa None, tutmadıysa gerçek sonucun yanında agent'a dönecek kısa not."""
    if forecast_hit(forecast, actual):
        return None
    expected = describe(forecast["type"], len(forecast.get("columns") or []), forecast.get("rows"))
    real = describe(actual["type"], actual["columns"], actual["rows"])
    return f"Surprise: you forecast {expected}, but the real result is {real}. Check the query before you submit it."


def describe(result_type, columns, rows):
    if result_type == "error":
        return "an error"
    if result_type == "empty":
        return "an empty result"
    return f"{columns} column(s) and {rows} row(s)"
