"""Adım 2 ve 8: akışın kendisi. Agent her turda tek bir tool çağırır, harness onu çalıştırır ve sonucu geri verir;
small model takılırsa large model soruyu sıfırdan, aynı döngüyle çözer. Soru bitince experience log yazılır."""

import json
import threading
import time
from pathlib import Path

import config
from agent import llm, prompts
from agent.context import Context
from harness import guards, memory, prepare
from harness.tools import execute_sql, search_values, submit

log_lock = threading.Lock()  # evaluate.py soruları aynı anda çalıştırır; log satırları birbirine karışmasın


def answer_question(question, evidence, db_path, tags=None, score=None):
    """tags: experience log satırına eklenecek bilgiler (ör. split, question_id). score: cevabı doğru SQL'le puanlayan
    fonksiyon; yalnızca değerlendirmede verilir ve cevap kesinleştikten sonra çağrılır, agent onu hiç görmez.
    Return: sonuç (Context.answer); correct, score verildiyse cevabın doğru olup olmadığı, yoksa None."""
    tags = tags or {}
    context = Context(question, evidence, db_path)
    examples = memory.similar(question, evidence, tags.get("run")) if config.MEMORY else []  # benzer çözülmüş sorular
    context.messages = [
        {"role": "system", "content": prompts.AGENT},
        {"role": "user", "content": prepare.build_context(question, evidence, db_path, examples)},  # adım 1
    ]
    try:
        result = run_steps(context)
    except RuntimeError as error:  # small model cevap vermedi (ör. yerel sunucunun belleği doldu): takıldı sayılır
        stop(context, f"the small model gave an error: {error}")
        result = None
    if result is None and config.HANDOFF:  # adım 8: large model soruyu sıfırdan çözer
        start_large_model(context)
        try:
            result = run_steps(context)
        except RuntimeError as error:  # large model'in API'si cevap vermedi: small model'in submit ettiği SQL fallback olur
            context.large_model_error = str(error)
    if result is None:
        result = fallback_answer(context)
    result["correct"] = None if score is None else result["sql"] is not None and score(result["sql"])
    result["memory_examples"] = [example["question"] for example in examples]  # aynı koşudaki sıra değişebilir: kayıtlı
    write_experience(context, result, tags)
    if config.MEMORY:
        remember(context, result, tags)
    return result


def remember(context, result, tags):
    """Sorunun cevabı belleğe girer; sonraki sorular onu örnek olarak görebilir (memory.is_candidate). Large model'e
    ulaşılamadığı için kontrol edilmeden kabul edilen cevap "unchecked" yazılır, örnek olmaz."""
    if result["sql"] is None:
        return
    label = "unchecked" if result["large_model_error"] else result["label"]
    memory.add([{"question": context.question, "evidence": context.evidence, "sql": result["sql"],
                 "split": tags.get("split", "use"), "run": tags.get("run"), "correct": result["correct"],
                 "label": label}])


def write_experience(context, result, tags):
    """Experience log: her soru bir satır, nereden çalıştırılırsa çalıştırılsın (run.py, evaluate.py, kullanım).
    Small model'in gördüğü konuşmanın tamamı (messages), handoff olduysa large model'inki de (large_model_messages) ve cevap; ileride
    agent'ın eğitim verisi.
    correct yalnızca değerlendirmede dolu; kullanımda doğru SQL olmadığı için boş kalır."""
    record = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "split": "use", **tags, "db_id": Path(context.db_path).stem,
              "question": context.question, "evidence": context.evidence, "sql": result["sql"], "label": result["label"],
              "correct": result["correct"], "answered_by": result["answered_by"],
              "handoff_reason": result["handoff_reason"], "large_model_stop_reason": result["large_model_stop_reason"],
              "large_model_error": result["large_model_error"], "small_model": config.SMALL_MODEL,
              "large_model": config.LARGE_MODEL, "handoff": config.HANDOFF, "messages": context.small_model_messages or context.messages,
              "large_model_messages": context.messages if context.small_model_messages else None}
    with log_lock:
        config.EXPERIENCE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(config.EXPERIENCE_LOG, "a") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_steps(context):
    """Bir budget boyunca döngü. Return: kabul edilen cevap, ya da takılınca None (nedeni stop ile kaydedilir)."""
    context.calls_left = config.MAX_TOOL_CALLS  # small model de large model de 10
    while context.calls_left > 0:
        step = next_step(context)  # adım 2
        context.calls_left -= 1
        context.calls += 1
        outcome = take_step(step, context)  # adım 3–7
        if outcome == "accepted":
            return context.answer(step["args"]["sql"], "ok", "large_model" if context.large_model else "small_model")
        if outcome == "stopped":
            return None
        reason = early_handoff(context)
        if reason:
            stop(context, reason)
            return None
        add_budget_note(context)
    stop(context, "the tool-call budget ran out")
    return None


def take_step(step, context):
    """Tek bir tool call'u çalıştırır ve sonucunu konuşmaya ekler. Her tool kendi dosyasına gider (harness/tools/).
    Return: "accepted" (cevap kabul edildi), "stopped" (takıldı → adım 8) ya da None (döngü sürer)."""
    earlier = guards.earlier_calls(step, context)
    if step["error"]:  # tool call okunamadı: reddedilir, hata agent'a gider
        result = step["error"]
    elif len(earlier) >= config.MAX_REPEATS:  # kendi 3. tekrarı: takıldı
        reason = f"the same call was repeated {config.MAX_REPEATS} times"
        context.add(step, f"{submit.stop_word(context)}: {reason}.")
        stop(context, reason)
        return "stopped"
    elif earlier:  # aynı çağrı: çalıştırılmaz, önceki sonuç döner
        result = guards.repeat_note(earlier)
    elif step["tool"] == "search_values":
        result = search_values.run(step["args"]["query"], context)  # adım 3
    elif step["tool"] == "execute_sql":
        result = execute_sql.run(step["args"]["sql"], context)  # adım 4–6
    else:  # submit: small model'in da large model'in da cevabı aynı yoldan geçer
        outcome = submit.run(step["args"]["sql"], context)  # adım 7
        if outcome["done"]:
            context.add(step, "Accepted.")
            return "accepted"
        if outcome["handoff"]:
            context.add(step, outcome["note"])
            stop(context, outcome["handoff"])
            return "stopped"
        result = outcome["note"]  # final check notu → adım 2

    context.add(step, result)
    # okunamadı, tekrarlandı ya da pre-check'te reddedildi: çağrı boşa gitti ve sıradaki adım örneklenir
    context.stuck = bool(step["error"] or earlier) or result.startswith(("Rejected", "Final check failed: Rejected"))
    context.wasted_in_a_row = context.wasted_in_a_row + 1 if context.stuck else 0
    return None


def early_handoff(context):
    """Small model ilerleyemiyorsa handoff nedeni, yoksa None: arka arkaya WASTED_CALLS çağrısı boşa gitti ya da ilk
    PROGRESS_CALLS çağrısında dolu sonuç yok. Large model'e ve handoff kapalıyken (ablation) uygulanmaz: devralacak kimse
    yoksa agent budget'ının tamamını kullanır."""
    if context.large_model or not config.HANDOFF:
        return None
    if context.wasted_in_a_row >= config.WASTED_CALLS:  # okunamadı, tekrarlandı ya da pre-check'te reddedildi
        return f"{config.WASTED_CALLS} calls in a row were wasted"
    if context.calls == config.PROGRESS_CALLS and context.last_ok_sql is None:  # dolu sonuç veren hiçbir SQL yok
        return f"no query returned rows in the first {config.PROGRESS_CALLS} calls"
    return None


def add_budget_note(context):
    """Kalan tool call sayısı son observation'ın altına yazılır (yalnızca modele giden mesaja, adım kaydına değil);
    son BUDGET_WARNING hakta submit hatırlatması da eklenir."""
    if context.calls_left == 0:
        return
    note = f"\n[{context.calls_left} tool call(s) left."
    if context.calls_left <= config.BUDGET_WARNING:
        note += " If a query you ran answers the question, call submit with it now."
    context.messages[-1]["content"] += note + "]"


def stop(context, reason):
    """Döngünün neden durduğunu kaydeder: small model için handoff nedeni, large model için large_model_stop_reason."""
    if context.large_model:
        context.large_model_stop_reason = reason
    else:
        context.handoff_reason = reason


def next_step(context):
    """Konuşmanın şimdiye kadarki hâlini modele verir, cevabını tek bir tool call olarak okur. Model normalde en olası
    cevabı seçer (temperature 0); son çağrısı reddedildiyse ya da tekrarsa aynı girdiye yine aynı cevabı vereceği için
    bu kez RETRY_TEMPERATURE ile örneklenir."""
    model = config.LARGE_MODEL if context.large_model else config.SMALL_MODEL
    temperature = config.RETRY_TEMPERATURE if context.stuck else None
    messages = guards.compress(context.messages)  # konuşma 32K token'ı aştıysa en eski sonuçlar kısalır
    reply = llm.chat(messages, temperature=temperature, tools=prompts.TOOLS, model=model)
    context.count_usage(reply)
    return guards.read_tool_call(reply, prompts.TOOLS)


def start_large_model(context):
    """Handoff: large model soruyu sıfırdan çözer. Small model'in konuşmasını görmez, yalnızca sistem prompt'u ve adım 1'in
    bağlamıyla başlar; small model'in konuşması experience log için saklanır. Final check hakları large model için baştan
    sayılır."""
    context.large_model = True
    context.stuck = False
    context.final_check_fails = 0
    context.small_model_messages = context.messages
    context.messages = context.messages[:2]


def fallback_answer(context):
    """Hiçbir cevap kabul edilmediyse: small model'in ya da large model'in submit ettiği ve hatasız çalışan son SQL
    (fallback, düşük güven). Kimse böyle bir SQL submit etmediyse cevap yok (no_answer) ve nedeni. Keşif sorguları
    hiçbir zaman cevap olmaz."""
    if context.submitted_sql is None:
        message = ("No answer: no SQL query that runs without error was submitted "
                   f"(handoff reason: {context.handoff_reason}; large model: "
                   f"{context.large_model_error or context.large_model_stop_reason}).")
        return context.answer(None, "no_answer", answered_by=None, error_message=message)
    return context.answer(context.submitted_sql, "fallback", context.submitted_by)
