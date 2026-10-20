"""Adım 10: final check. Cevap dönmeden önceki son kontrol (aşama 17).
Cevap gerçekten çalıştırılmış olmalı, hata vermemeli; boşsa agent bu SQL için "empty" forecast'i yazmış olmalı."""

from harness import precheck


def check(sql, context):
    """Geçerse None; geçmezse agent'a dönecek not. Çalıştırılmamış SQL burada çalıştırılır; salt okuma ve
    tablo/sütun kontrolleri de pre-check'ten gelir."""
    note, result = precheck.run(sql, context)
    if note:
        return f"Final check failed: {note}"
    if not result["ok"]:
        return f"Final check failed: the query gives an error: {result['error']}"
    if result["row_count"] == 0:
        forecast = context.last_forecast.get(precheck.sql_key(sql))  # USE_AGENT_FORECAST kapalıysa hiç yok
        if not forecast or forecast["type"] != "empty":
            return ("Final check failed: the query returns no rows, but you did not forecast an empty result for it. "
                    "Check the values and conditions in the query.")
    return None
