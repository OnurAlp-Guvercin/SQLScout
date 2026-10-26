"""Adım 7: submit tool'u. Agent'ın en son çalıştırdığı SQL final check'ten geçerse cevap olur; geçmezse nedeni agent'a
not olarak döner, ikinci kez geçmezse iş teacher'a devredilir (adım 8)."""

import config
from harness.tools import execute_sql


def run(sql, context):
    """Agent ya da handoff'tan sonra teacher submit çağırınca run_steps bunu, en son çalıştırılan SQL'le çağırır (adım 7).
    Return: {"done": cevap kabul edildi mi, "note": agent'a gidecek not ya da None, "handoff": handoff nedeni ya da None}."""
    note = final_check(sql, context)
    if note is None:
        return {"done": True, "note": None, "handoff": None}
    context.final_check_fails += 1
    if context.final_check_fails >= config.FINAL_CHECK_TRIES:
        return {"done": False, "note": None, "handoff": "final check 2 kez geçmedi"}
    return {"done": False, "note": note, "handoff": None}


def final_check(sql, context):
    """Geçerse None, geçmezse agent'a dönecek not. Çalıştırılmış bir SQL olmalı; pre-check'ten geçmeli ve gerçekten hatasız
    çalışmalı. Boş sonuç kabul edilir: agent onu çalıştırıp görmüştür."""
    if sql is None:
        return "Final check failed: you have not run a query yet. Run it with execute_sql first."
    note = execute_sql.check(context.db_path, sql)
    if note:
        return f"Final check failed: {note}"
    result = execute_sql.run_sql(sql, context)
    if not result["ok"]:
        return f"Final check failed: the query gives an error: {result['error']}"
    return None
