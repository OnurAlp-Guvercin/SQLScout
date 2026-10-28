"""Adım 7: submit tool'u. Submit edilen SQL iki kapıdan geçer: hatasız çalışıyor mu, teacher doğru buluyor mu.
Geçerse cevap olur; geçmezse gerekçesi not olarak döner ya da iş teacher'a devredilir."""

import json

import config
from agent import llm, prompts
from harness.tools import execute_sql

REVIEWER_NOTE = ("A reviewer judged this query to be wrong for the question: {reason} Check it against the question "
                 "and the evidence, then submit a corrected query.")


def run(sql, context):
    """Agent ya da teacher submit(sql) çağırınca (adım 7). İki kapı sırayla:
    1. runs_without_error: hatasız çalışıyor mu? Geçerse SQL fallback adayı olur (düşük güven).
    2. teacher_review: teacher bağlamı, SQL'i ve sonucu görüp doğru mu diye gerekçesiyle söyler. Agent'ın cevabı yanlış
       bulunursa handoff; teacher'ınki yanlış bulunursa gerekçe teacher'a not olarak döner.
    Geçmeyen kapının notu döner ve bir hak düşer (fail). Return: {"done", "note", "handoff"}."""
    note = runs_without_error(sql, context)
    if note:
        return fail(note, context)
    context.submitted_sql = sql
    context.submitted_by = "teacher" if context.teacher else "agent"

    correct, reason = teacher_review(sql, context)
    if correct:
        return {"done": True, "note": None, "handoff": None}
    if not context.teacher:
        return handoff("a reviewer judged the submitted query to be wrong", f"Reviewer: {reason}")
    return fail(REVIEWER_NOTE.format(reason=reason), context)


def fail(note, context):
    """Bir kapı geçilmedi: not döner ve bir hak düşer. FINAL_CHECK_TRIES'a ulaşınca handoff (teacher için: durur)."""
    context.final_check_fails += 1
    if context.final_check_fails >= config.FINAL_CHECK_TRIES:
        return handoff(f"the final check failed {config.FINAL_CHECK_TRIES} times", note)
    return {"done": False, "note": note, "handoff": None}


def handoff(reason, note=None):
    """Handoff: varsa son not konuşmada (experience log) kalır, altına handoff nedeni yazılır."""
    text = f"Handoff: {reason}."
    if note:
        text = note + "\n" + text
    return {"done": False, "note": text, "handoff": reason}


def teacher_review(sql, context):
    """Teacher'a adım 1'in bağlamını, SQL'i ve sonucunu verip "doğru mu?" diye sorar (CHECK_ANSWER, temperature 0);
    cevap bir JSON object'idir. Return: (correct, reason). Agent'ın cevabına verilen karar context.teacher_check'e
    yazılır (değerlendirme onu da puanlar). Teacher'ın API'si cevap vermezse cevap kaybolmasın diye kabul edilir;
    kontrolün yapılamadığı context.teacher_error'da kalır."""
    result = execute_sql.run_sql(sql, context, answer=True)  # runs_without_error çalıştırdı: cache'ten gelir
    result = execute_sql.format_result(result, hint=False)  # agent'a yönelik search_values notu teacher'a gitmez
    question = f"{context.messages[1]['content']}\n\nSQL query:\n```sql\n{sql}\n```\nIts result:\n{result}"
    messages = [{"role": "system", "content": prompts.CHECK_ANSWER}, {"role": "user", "content": question}]
    try:
        reply = llm.chat(messages, temperature=0, model=config.TEACHER_MODEL)
    except RuntimeError as error:
        context.teacher_error = str(error)
        return True, ""
    context.count_usage(reply)
    correct, reason = read_review(reply["text"])
    if not context.teacher:
        context.teacher_check = {"sql": sql, "approved": correct, "reason": reason}
    return correct, reason


def read_review(text):
    """Teacher'ın JSON cevabı, ör. '{"reason": "It counts every item.", "correct": true}' → (True, "It counts every
    item."). Okunamazsa ya da "correct" true/false değilse onaylanmamış sayılır; reason modelin cevabı olur."""
    try:
        review = json.loads(text[text.find("{"):text.rfind("}") + 1])
    except json.JSONDecodeError:
        review = None
    if not isinstance(review, dict) or not isinstance(review.get("correct"), bool):
        return False, "Unreadable review: " + text.strip()[:200]
    return review["correct"], str(review.get("reason", ""))


def runs_without_error(sql, context):
    """Geçerse None, geçmezse dönecek not. SQL pre-check'ten geçmeli ve gerçekten hatasız çalışmalı: ana sorgu olarak
    en fazla ANSWER_TIMEOUT_SECONDS (daha önce çalıştıysa sonuç cache'ten gelir)."""
    note = execute_sql.check(context.db_path, sql)
    if note:
        return f"Final check failed: {note}"
    result = execute_sql.run_sql(sql, context, answer=True)
    if not result["ok"]:
        return f"Final check failed: the query gives an error: {result['error']}"
    return None
