"""Agent loop: akışın kendisi. Agent her turda tek bir tool çağırır; harness onu çalıştırır ve sonucu agent'a geri
verir. Her tool bir dal, her dal kendi adını taşıyan dosyaya gider (harness/tools/): search_values (adım 3),
execute_sql (adım 4–6), submit (adım 7; agent cevap olarak seçtiği SQL'i yazar).
Agent takılırsa (ilk 4 adımda ilerleme yok, aynı çağrı 3 kez tekrarlandı, final check 2 kez geçmedi, budget bitti)
harness işi teacher'a verir (adım 8): teacher aynı döngüyle, yarım budget'la devam eder.
Soru bitince experience log yazılır."""

import json
import threading
import time
from pathlib import Path

import config
from agent import llm, prompts
from agent.context import Context
from harness import guards, prepare
from harness.tools import execute_sql, search_values, submit

log_lock = threading.Lock()  # evaluate.py soruları aynı anda çalıştırır; log satırları birbirine karışmasın


def answer_question(question, evidence, db_path, tags=None, score=None):
    """tags: experience log satırına eklenecek bilgiler (ör. split, question_id). score: cevabı doğru SQL'le puanlayan
    fonksiyon; yalnızca değerlendirmede verilir ve cevap kesinleştikten sonra çağrılır, agent onu hiç görmez.
    Return: sonuç (Context.answer); correct, score verildiyse cevabın doğru olup olmadığı, yoksa None."""
    context = Context(question, evidence, db_path)
    context.messages = [
        {"role": "system", "content": prompts.AGENT},
        {"role": "user", "content": prepare.build_context(question, evidence, db_path)},  # adım 1
    ]
    result = run_steps(context)
    if result is None:  # adım 8: teacher kaldığı yerden devam eder
        start_teacher(context)
        try:
            result = run_steps(context)
        except RuntimeError as error:  # teacher'ın API'si cevap vermedi: agent'ın submit ettiği SQL fallback olur
            context.teacher_error = str(error)
    if result is None:
        result = fallback_answer(context)
    result["correct"] = None if score is None else result["sql"] is not None and score(result["sql"])
    write_experience(context, result, tags or {})
    return result


def write_experience(context, result, tags):
    """Experience log: her soru bir satır, nereden çalıştırılırsa çalıştırılsın (run.py, evaluate.py, kullanım).
    Agent'ın (handoff olduysa teacher'ın da) gördüğü konuşmanın tamamı ve cevap; ileride agent'ın eğitim verisi.
    correct yalnızca değerlendirmede dolu; kullanımda doğru SQL olmadığı için boş kalır."""
    record = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "split": "use", **tags, "db_id": Path(context.db_path).stem,
              "question": context.question, "evidence": context.evidence, "sql": result["sql"], "label": result["label"],
              "correct": result["correct"], "answered_by": result["answered_by"],
              "handoff_reason": result["handoff_reason"], "teacher_stop_reason": result["teacher_stop_reason"],
              "teacher_error": result["teacher_error"], "policy_model": config.POLICY_MODEL,
              "teacher_model": config.TEACHER_MODEL, "messages": context.messages}
    with log_lock:
        config.EXPERIENCE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(config.EXPERIENCE_LOG, "a") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_steps(context):
    """Bir budget boyunca döngü. Return: kabul edilen cevap, ya da takılınca None (nedeni stop ile kaydedilir)."""
    context.calls_left = context.budget()  # agent 10, teacher 5
    while context.calls_left > 0:
        guards.compress(context)  # konuşma 32K token'ı aştıysa en eski sonuçlar kısalır
        step = next_step(context)  # adım 2
        context.calls_left -= 1
        context.calls += 1
        earlier = guards.earlier_calls(step, context)
        by = "teacher" if context.teacher else "agent"  # teacher, agent'ın denediğini bir kez görmek isterse takılmış sayılmaz

        if step["error"]:  # tool call okunamadı: reddedilir, hata agent'a gider
            result = step["error"]
        elif len([old for old in earlier if old["by"] == by]) >= config.MAX_REPEATS:  # kendi 3. tekrarı: takıldı
            context.add(step, "Handoff: the same call was repeated too many times.")
            stop(context, f"the same call was repeated {config.MAX_REPEATS} times")
            return None
        elif earlier:  # aynı çağrı: çalıştırılmaz, önceki sonuç agent'a gider
            result = guards.repeat_note(earlier)
        elif step["tool"] == "search_values":
            result = search_values.run(step["args"]["query"], context)  # adım 3
        elif step["tool"] == "execute_sql":
            result = execute_sql.run(step["args"]["sql"], context)  # adım 4–6
        else:  # agent'ın da teacher'ın da submit'i aynı yoldan geçer
            outcome = submit.run(step["args"]["sql"], context)  # adım 7
            if outcome["done"]:
                context.add(step, "Accepted.")
                return context.answer(step["args"]["sql"], "ok", by)
            if outcome["handoff"]:
                stop(context, outcome["handoff"])
                note = f"Handoff: {outcome['handoff']}."
                if outcome["note"]:  # final check'in son notu: teacher son SQL'in neden geçmediğini görsün
                    note = outcome["note"] + "\n" + note
                context.add(step, note)
                return None
            result = outcome["note"]  # final check notu → adım 2

        context.add(step, result)
        context.stuck = bool(step["error"] or earlier)  # reddedildi ya da tekrarladı: sıradaki adım örneklenir
        if not context.teacher and context.calls == config.PROGRESS_CALLS and context.last_ok_sql is None:
            # Dolu sonuç veren hiçbir SQL yok: teacher erken devralır.
            stop(context, f"no query returned rows in the first {config.PROGRESS_CALLS} calls")
            return None
        if context.calls_left > 0:  # kalan budget yalnızca modele giden mesaja eklenir, adım kaydına değil
            note = f"\n[{context.calls_left} tool call(s) left."
            if context.calls_left <= config.BUDGET_WARNING:
                note += " If a query you ran answers the question, call submit with it now."
            context.messages[-1]["content"] += note + "]"

    stop(context, "the tool-call budget ran out")
    return None


def stop(context, reason):
    """Döngünün neden durduğunu kaydeder: agent için handoff nedeni, teacher için teacher_stop_reason."""
    if context.teacher:
        context.teacher_stop_reason = reason
    else:
        context.handoff_reason = reason


def next_step(context):
    """Konuşmanın şimdiye kadarki hâlini modele verir, cevabını tek bir tool call olarak okur. Model normalde en olası
    cevabı seçer (temperature 0); son çağrısı reddedildiyse ya da tekrarsa aynı girdiye yine aynı cevabı vereceği için
    bu kez RETRY_TEMPERATURE ile örneklenir."""
    model = config.TEACHER_MODEL if context.teacher else config.POLICY_MODEL
    temperature = config.RETRY_TEMPERATURE if context.stuck else None
    reply = llm.chat(context.messages, temperature=temperature, tools=prompts.TOOLS, model=model)
    context.count_usage(reply)
    return guards.read_tool_call(reply, prompts.TOOLS)


def start_teacher(context):
    """Handoff: teacher agent'ın bütün konuşmasını, nedeni ve yeni budget'ı söyleyen bir notla devralır. Agent'ın son
    çağrısı reddedilmiş ya da tekrar olsa da teacher ilk adımını temperature 0 ile atar; final check'te de agent'ın
    hatalarından bağımsız olarak kendi 2 hakkı vardır."""
    context.teacher = True
    context.stuck = False
    context.final_check_fails = 0
    note = prompts.TEACHER_TAKEOVER.format(reason=context.handoff_reason, budget=context.budget())
    context.messages.append({"role": "user", "content": note})


def fallback_answer(context):
    """Hiçbir cevap kabul edilmediyse: agent'ın ya da teacher'ın submit ettiği ve final check'ten geçen son SQL
    (fallback, düşük güven). Kimse böyle bir SQL submit etmediyse cevap yok (no_answer) ve nedeni. Keşif sorguları
    hiçbir zaman cevap olmaz."""
    if context.submitted_sql is None:
        message = ("No answer: no SQL query that runs without error was submitted "
                   f"(handoff reason: {context.handoff_reason}; teacher: "
                   f"{context.teacher_error or context.teacher_stop_reason}).")
        return context.answer(None, "no_answer", answered_by=None, error_message=message)
    return context.answer(context.submitted_sql, "fallback", context.submitted_by)
