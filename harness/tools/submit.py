"""Adım 7: submit tool'u. Agent'ın cevap olarak seçtiği SQL final check'ten geçerse, agent onun sonucunu daha önce
görmüşse ve teacher cevabı onaylarsa cevap olur. Final check'ten geçmezse nedeni agent'a not olarak döner, ikinci kez
geçmezse iş teacher'a devredilir; teacher onaylamazsa da devredilir (adım 8)."""

import config
from agent import llm, prompts
from harness.tools import execute_sql


def run(sql, context):
    """Agent ya da handoff'tan sonra teacher submit(sql) çağırınca run_steps bunu çağırır (adım 7).
    1. final_check: SQL hatasız çalışmıyorsa nedeni agent'a döner; ikinci kez geçmezse handoff.
    2. Agent bu SQL'in sonucunu daha önce görmediyse cevap henüz kabul edilmez: harness onu çalıştırıp
       sonucunu agent'a gösterir; agent soruyu cevapladığına karar verirse yeniden submit eder. Bu bir hata sayılmaz.
    3. teacher_approves: agent'ın cevabını teacher kontrol eder; onaylamazsa handoff. Teacher'ın kendi submit'i
       kontrol edilmez.
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
    if not context.teacher and not teacher_approves(sql, context):
        return {"done": False, "note": None, "handoff": "teacher cevabı onaylamadı"}
    return {"done": True, "note": None, "handoff": None}


def teacher_approves(sql, context):
    """Teacher'a adım 1'in bağlamını, SQL'i ve sonucunu verip "doğru mu?" diye sorar (temperature 0). Cevabı "yes" ile
    başlamıyorsa onaylanmamış sayılır."""
    result = execute_sql.format_result(execute_sql.run_sql(sql, context))  # final check çalıştırdı: cache'ten gelir
    question = f"{context.messages[1]['content']}\n\nSQL query:\n```sql\n{sql}\n```\nIts result:\n{result}"
    messages = [{"role": "system", "content": prompts.CHECK_ANSWER}, {"role": "user", "content": question}]
    reply = llm.chat(messages, temperature=0, model=config.TEACHER_MODEL)
    context.count_usage(reply)
    return reply["text"].strip().lower().startswith("yes")


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
