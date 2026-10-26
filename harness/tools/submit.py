"""Adım 7: submit tool'u. Agent'ın cevap olarak seçtiği SQL final check'ten geçerse ve agent onun sonucunu daha önce
görmüşse cevap olur. Final check'ten geçmezse nedeni agent'a not olarak döner, ikinci kez geçmezse iş teacher'a
devredilir (adım 8)."""

import config
from harness.tools import execute_sql


def run(sql, context):
    """Agent ya da handoff'tan sonra teacher submit(sql) çağırınca run_steps bunu çağırır (adım 7).
    1. final_check: SQL hatasız çalışmıyorsa nedeni agent'a döner; ikinci kez geçmezse handoff.
    2. Agent bu SQL'in sonucunu daha önce görmediyse cevap henüz kabul edilmez: harness onu çalıştırıp
       sonucunu agent'a gösterir; agent soruyu cevapladığına karar verirse yeniden submit eder. Bu bir hata sayılmaz.
    Return: {"done": cevap kabul edildi mi, "note": agent'a gidecek not ya da None, "handoff": handoff nedeni ya da None}."""
    note = final_check(sql, context)
    if note:
        context.final_check_fails += 1
        if context.final_check_fails >= config.FINAL_CHECK_TRIES:
            return {"done": False, "note": None, "handoff": "final check 2 kez geçmedi"}
        return {"done": False, "note": note, "handoff": None}
    if execute_sql.sql_key(sql) not in context.seen:
        result = execute_sql.run(sql, context)
        note = (f"You had not seen the result of this query yet. Its result:\n{result}\n"
                "If it answers the question, call submit with it again.")
        return {"done": False, "note": note, "handoff": None}
    return {"done": True, "note": None, "handoff": None}


def final_check(sql, context):
    """Geçerse None, geçmezse agent'a dönecek not. SQL pre-check'ten geçmeli ve gerçekten hatasız çalışmalı (agent onu
    daha önce çalıştırdıysa sonuç cache'ten gelir)."""
    note = execute_sql.check(context.db_path, sql)
    if note:
        return f"Final check failed: {note}"
    result = execute_sql.run_sql(sql, context)
    if not result["ok"]:
        return f"Final check failed: the query gives an error: {result['error']}"
    return None
