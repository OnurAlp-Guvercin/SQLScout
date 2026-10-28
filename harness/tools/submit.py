"""Adım 7: submit tool'u. Submit edilen SQL iki kapıdan geçer: hatasız çalışıyor mu, large model doğru buluyor mu.
Geçerse cevap olur; geçmezse gerekçesi not olarak döner ya da iş large model'e devredilir."""

import json

import config
from agent import llm, prompts
from harness import prepare
from harness.tools import execute_sql

REVIEWER_NOTE = ("A reviewer judged this query to be wrong for the question: {reason} Check it against the question "
                 "and the evidence, run a corrected query and submit it.")


def run(sql, context):
    """Small model ya da large model submit(sql) çağırınca (adım 7). İki kapı sırayla:
    1. runs_without_error: hatasız çalışıyor mu? Geçerse SQL fallback adayı olur (düşük güven).
    2. large_model_review: large model bağlamı, SQL'i ve sonucu görüp doğru mu diye gerekçesiyle söyler. Small model'in cevabı yanlış
       bulunursa handoff; large model'inki yanlış bulunursa (ya da handoff kapalıysa small model'inki) gerekçe not olarak döner.
    Geçmeyen kapının notu döner ve bir hak düşer (fail). Return: {"done", "note", "handoff"}."""
    note = runs_without_error(sql, context)
    if note:
        return fail(note, context)
    context.submitted_sql = sql
    context.submitted_by = "large_model" if context.large_model else "small_model"

    correct, reason = large_model_review(sql, context)
    if correct:
        return {"done": True, "note": None, "handoff": None}
    if not context.large_model and config.HANDOFF:
        return handoff("a reviewer judged the submitted query to be wrong", context, f"Reviewer: {reason}")
    return fail(REVIEWER_NOTE.format(reason=reason), context)


def fail(note, context):
    """Bir kapı geçilmedi: not döner ve bir hak düşer. FINAL_CHECK_TRIES'a ulaşınca handoff (large model için: durur)."""
    context.final_check_fails += 1
    if context.final_check_fails >= config.FINAL_CHECK_TRIES:
        return handoff(f"the final check failed {config.FINAL_CHECK_TRIES} times", context, note)
    return {"done": False, "note": note, "handoff": None}


def handoff(reason, context, note=None):
    """Döngü durur: varsa son not konuşmada (experience log) kalır, altına neden yazılır. "Handoff:" yalnızca large model
    gerçekten devralacaksa; large model'in kendi döngüsünde ya da handoff kapalıyken (ablation) "Stopped:"."""
    text = f"{stop_word(context)}: {reason}."
    if note:
        text = note + "\n" + text
    return {"done": False, "note": text, "handoff": reason}


def stop_word(context):
    return "Handoff" if config.HANDOFF and not context.large_model else "Stopped"


def large_model_review(sql, context):
    """Large model'e adım 1'in bağlamını, SQL'i ve sonucunu verip "doğru mu?" diye sorar (CHECK_ANSWER, temperature 0);
    cevap bir JSON object'idir. Return: (correct, reason). Small model'in cevabına verilen her karar context.large_model_checks'e
    yazılır (değerlendirme onu da puanlar). Large model'in API'si cevap vermezse cevap kaybolmasın diye kabul edilir;
    kontrolün yapılamadığı context.large_model_error'da kalır."""
    result = execute_sql.run_sql(sql, context, answer=True)  # runs_without_error çalıştırdı: cache'ten gelir
    result = execute_sql.format_result(result, hint=False)  # small model'e yönelik search_values notu large model'e gitmez
    question = prepare.build_context(context.question, context.evidence, context.db_path)  # memory örnekleri olmadan
    question = f"{question}\n\nSQL query:\n```sql\n{sql}\n```\nIts result:\n{result}"
    messages = [{"role": "system", "content": prompts.CHECK_ANSWER}, {"role": "user", "content": question}]
    try:
        reply = llm.chat(messages, temperature=0, model=config.LARGE_MODEL)
    except RuntimeError as error:
        context.large_model_error = str(error)
        return True, ""
    context.count_usage(reply)
    correct, reason = read_review(reply["text"])
    if not context.large_model:
        context.large_model_checks.append({"sql": sql, "approved": correct, "reason": reason})
    return correct, reason


def read_review(text):
    """Large model'in JSON cevabı, ör. '{"reason": "It counts every item.", "correct": true}' → (True, "It counts every
    item."). Okunamazsa ya da "correct" true/false değilse onaylanmamış sayılır; reason modelin cevabı olur."""
    try:
        review, _ = json.JSONDecoder().raw_decode(text[text.find("{"):])  # ilk JSON object'i; sonrası önemsenmez
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
