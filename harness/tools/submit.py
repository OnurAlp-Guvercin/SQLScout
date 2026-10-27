"""Adım 7: submit tool'u. Agent'ın cevap olarak seçtiği SQL final check'ten geçerse, agent onun sonucunu daha önce
görmüşse ve teacher cevabı onaylarsa cevap olur. Final check'ten geçmezse nedeni agent'a not olarak döner, ikinci kez
geçmezse iş teacher'a devredilir; teacher onaylamazsa da devredilir (adım 8)."""

import re

import config
from agent import llm, prompts
from harness.tools import execute_sql


def run(sql, context):
    """Agent ya da handoff'tan sonra teacher submit(sql) çağırınca run_steps bunu çağırır (adım 7).
    1. final_check: SQL hatasız çalışmıyorsa nedeni agent'a döner; ikinci kez geçmezse handoff. Geçerse SQL
       context.submitted_sql olur: aşağıda kabul edilmese de fallback answer bu olur (düşük güven).
    2. Agent bu SQL'in sonucunu daha önce görmediyse cevap henüz kabul edilmez: harness onu çalıştırıp
       sonucunu agent'a gösterir; agent soruyu cevapladığına karar verirse yeniden submit eder. Bu bir hata sayılmaz.
    3. teacher_approves: agent'ın cevabını teacher kontrol eder; onaylamazsa handoff. Teacher'ın kendi submit'i
       kontrol edilmez. Teacher'ın API'si cevap vermezse cevap kabul edilir (context.teacher_error).
    Return: {"done": cevap kabul edildi mi, "note": agent'a gidecek not ya da None,
             "handoff": handoff nedeni ya da None}.
    Final check ikinci kez geçmeyince note da dolu: teacher son SQL'in neden geçmediğini görsün."""
    note = final_check(sql, context)
    if note:
        context.final_check_fails += 1
        if context.final_check_fails >= config.FINAL_CHECK_TRIES:
            return {"done": False, "note": note, "handoff": f"the final check failed {config.FINAL_CHECK_TRIES} times"}
        return {"done": False, "note": note, "handoff": None}
    context.submitted_sql = sql  # hatasız çalışıyor: kabul edilmese de fallback answer olabilir (düşük güven)
    context.submitted_by = "teacher" if context.teacher else "agent"
    if execute_sql.sql_key(sql) not in context.seen:
        result = execute_sql.run(sql, context)
        note = (f"You had not seen the result of this query yet. Its result:\n{result}\n"
                "If it answers the question, call submit with it again.")
        return {"done": False, "note": note, "handoff": None}
    if not context.teacher and not teacher_approves(sql, context):
        return {"done": False, "note": None, "handoff": "a reviewer judged the submitted query to be wrong"}
    return {"done": True, "note": None, "handoff": None}


def teacher_approves(sql, context):
    """Teacher'a adım 1'in bağlamını, SQL'i ve sonucunu verip "doğru mu?" diye sorar (temperature 0). Cevabı (harf
    olmayan karakterler atılınca, ör. "**Yes**") "yes" ile başlamıyorsa onaylanmamış sayılır; karar
    context.teacher_check'e yazılır (değerlendirme onu da puanlar).
    Teacher'ın API'si birkaç denemeye rağmen cevap vermezse agent'ın cevabı kaybolmasın diye kabul edilir; kontrolün
    yapılamadığı context.teacher_error'da kalır."""
    result = execute_sql.run_sql(sql, context, answer=True)  # final check çalıştırdı: cache'ten gelir
    result = execute_sql.format_result(result, hint=False)  # agent'a yönelik search_values notu teacher'a gitmez
    question = f"{context.messages[1]['content']}\n\nSQL query:\n```sql\n{sql}\n```\nIts result:\n{result}"
    messages = [{"role": "system", "content": prompts.CHECK_ANSWER}, {"role": "user", "content": question}]
    try:
        reply = llm.chat(messages, temperature=0, model=config.TEACHER_MODEL)
    except RuntimeError as error:
        context.teacher_error = str(error)
        return True
    context.count_usage(reply)
    approved = re.sub(r"[^a-z]", "", reply["text"].lower()).startswith("yes")
    context.teacher_check = {"sql": sql, "approved": approved}
    return approved


def final_check(sql, context):
    """Geçerse None, geçmezse agent'a dönecek not. SQL pre-check'ten geçmeli ve gerçekten hatasız çalışmalı: ana sorgu
    olarak en fazla ANSWER_TIMEOUT_SECONDS (agent onu daha önce çalıştırdıysa sonuç cache'ten gelir)."""
    note = execute_sql.check(context.db_path, sql)
    if note:
        return f"Final check failed: {note}"
    result = execute_sql.run_sql(sql, context, answer=True)
    if not result["ok"]:
        return f"Final check failed: the query gives an error: {result['error']}"
    return None
