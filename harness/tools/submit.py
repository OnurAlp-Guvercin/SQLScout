"""Adım 7: submit tool'u. Agent'ın cevap olarak seçtiği SQL final check'ten geçerse, agent onun sonucunu daha önce
görmüşse, sonuçta sorunun istemediği bir sütun yoksa ve teacher cevabı onaylarsa cevap olur. Final check'ten ya da
sütun kontrolünden geçmezse nedeni agent'a not olarak döner, ikinci kez geçmezse iş teacher'a devredilir; teacher
onaylamazsa da devredilir (adım 8). Handoff'tan sonra teacher'ın kendi cevabı da kontrol edilir; onaylanmazsa
teacher'a düzeltmesi için not döner."""

import re

import config
from agent import llm, prompts
from harness.tools import execute_sql

COLUMNS_NOTE = ("A reviewer found a column in the result that the question does not ask for (columns: {columns}). "
                "Submit a query that returns only what the question asks for.")
REVIEWER_NOTE = ("A reviewer judged this query to be wrong for the question. Check it against the question and the "
                 "evidence, then submit a corrected query.")


def run(sql, context):
    """Agent ya da handoff'tan sonra teacher submit(sql) çağırınca run_steps bunu çağırır (adım 7).
    1. final_check: SQL hatasız çalışmıyorsa nedeni agent'a döner; ikinci kez geçmezse handoff. Geçerse SQL
       context.submitted_sql olur: aşağıda kabul edilmese de fallback answer bu olur (düşük güven).
    2. Agent bu SQL'in sonucunu daha önce görmediyse cevap henüz kabul edilmez: harness onu çalıştırıp
       sonucunu agent'a gösterir; agent soruyu cevapladığına karar verirse yeniden submit eder. Bu bir hata sayılmaz.
    3. extra_column_note: sonuç birden çok sütunluysa teacher soru her sütunu istiyor mu diye bakar; istemiyorsa
       COLUMNS_NOTE döner (agent'a da teacher'a da) ve final check hakkından düşer. Döngüde keşif sorgularının yardımcı
       sütunları (id, ad) cevapta kalıyordu; bunu genel kontrol fark etmiyordu, çağıran da kolayca düzeltebilir.
       Çağıran aynı SQL'i yeniden submit ederse sütunların istendiğinde ısrar ediyordur: sütun kontrolü atlanır, karar
       teacher_approves'a kalır (sütun kontrolünün yanlış bir "hayır"ı doğru cevabı handoff'a götürmesin).
    4. teacher_approves: cevabı teacher kontrol eder. Agent'ın cevabını onaylamazsa handoff; teacher'ın kendi cevabını
       onaylamazsa REVIEWER_NOTE döner ve final check hakkından düşer (ikinci kez olursa teacher durur). Teacher'ın
       API'si cevap vermezse cevap kabul edilir (context.teacher_error).
    Return: {"done": cevap kabul edildi mi, "note": agent'a gidecek not ya da None,
             "handoff": handoff nedeni ya da None}.
    Final check ikinci kez geçmeyince note da dolu: agent'ın konuşmasında (experience log) kalsın."""
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
    note = None
    if execute_sql.sql_key(sql) not in context.column_noted:
        note = extra_column_note(sql, context)
    if note:
        context.column_noted.add(execute_sql.sql_key(sql))
    else:
        if teacher_approves(sql, context):
            return {"done": True, "note": None, "handoff": None}
        if not context.teacher:
            return {"done": False, "note": None, "handoff": "a reviewer judged the submitted query to be wrong"}
        note = REVIEWER_NOTE  # teacher'ın cevabı reddedilirse handoff yok: not döner, final check hakkından düşer
    context.final_check_fails += 1
    if context.final_check_fails >= config.FINAL_CHECK_TRIES:
        return {"done": False, "note": note, "handoff": f"the final check failed {config.FINAL_CHECK_TRIES} times"}
    return {"done": False, "note": note, "handoff": None}


def teacher_approves(sql, context):
    """Teacher'a adım 1'in bağlamını, SQL'i ve sonucunu verip "doğru mu?" diye sorar (temperature 0). Cevabı (harf
    olmayan karakterler atılınca, ör. "**Yes**") "yes" ile başlamıyorsa onaylanmamış sayılır; karar
    agent'ın cevabına verilen karar context.teacher_check'e yazılır (değerlendirme onu da puanlar).
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
    approved = says_yes(reply["text"])
    if not context.teacher:
        context.teacher_check = {"sql": sql, "approved": approved}
    return approved


def extra_column_note(sql, context):
    """Sonuç birden çok sütunluysa teacher'a yalnızca soruyu, evidence'ı ve sütun adlarını verip "soru her sütunu
    istiyor mu?" diye sorar (COLUMN_CHECK, temperature 0). Tek sütun fazladan olamaz; sorulmaz. Sütun adları backtick
    içinde ve sayısıyla verilir: SQLite bir ifadenin sütununu ifadenin metniyle adlandırır, ör. ROUND(x, 2) virgül
    içerir. Return: istenmeyen bir sütun varsa COLUMNS_NOTE, yoksa None. Teacher'ın API'si cevap vermezse None: bu
    kontrol atlanır, cevabı teacher_approves yine kontrol eder."""
    columns = execute_sql.run_sql(sql, context, answer=True)["columns"]  # final check çalıştırdı: cache'ten gelir
    if len(columns) < 2:
        return None
    shown = ", ".join(f"`{column}`" for column in columns)
    text = f"Question: {context.question}\n\nColumns of the result ({len(columns)}): {shown}"
    if context.evidence:
        text = f"Evidence: {context.evidence}\n" + text
    messages = [{"role": "system", "content": prompts.COLUMN_CHECK}, {"role": "user", "content": text}]
    try:
        reply = llm.chat(messages, temperature=0, model=config.TEACHER_MODEL)
    except RuntimeError:
        return None
    context.count_usage(reply)
    if says_yes(reply["text"]):
        return None
    return COLUMNS_NOTE.format(columns=shown)


def says_yes(text):
    """Teacher'ın tek kelimelik cevabı "yes" mi? Harf olmayan karakterler atılır (ör. "**Yes**")."""
    return re.sub(r"[^a-z]", "", text.lower()).startswith("yes")


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
