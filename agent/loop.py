"""Agent loop: akışın kendisi. Agent her turda tek bir tool çağırır; harness onu çalıştırır ve sonucu agent'a geri
verir. Her tool bir dal, her dal kendi adını taşıyan dosyaya gider (harness/tools/): search_values (adım 3),
execute_sql (adım 4–6), submit (adım 7; agent'ın en son çalıştırdığı SQL cevaptır).
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


def answer_question(question, evidence, db_path, seed=None, tags=None, score=None):
    """tags: experience log satırına eklenecek bilgiler (ör. split, question_id). score: cevabı doğru SQL'le puanlayan
    fonksiyon; yalnızca değerlendirmede verilir ve cevap kesinleştikten sonra çağrılır, agent onu hiç görmez."""
    context = Context(question, evidence, db_path, seed=seed)
    context.messages = [
        {"role": "system", "content": prompts.AGENT},
        {"role": "user", "content": prepare.build_context(question, evidence, db_path)},  # adım 1
    ]
    result = run_steps(context)
    if result is None:  # adım 8: teacher kaldığı yerden devam eder
        start_teacher(context)
        result = run_steps(context)
    if result is None:
        result = fallback_answer(context)
    correct = None if score is None else result["sql"] is not None and score(result["sql"])
    write_experience(context, result, correct, tags or {})
    return result


def write_experience(context, result, correct, tags):
    """Experience log: her soru bir satır, nereden çalıştırılırsa çalıştırılsın (run.py, evaluate.py, kullanım).
    Agent'ın (handoff olduysa teacher'ın da) gördüğü konuşmanın tamamı ve cevap; ileride agent'ın eğitim verisi.
    correct yalnızca değerlendirmede dolu; kullanımda doğru SQL olmadığı için boş kalır."""
    record = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "split": "use", **tags, "db_id": Path(context.db_path).stem,
              "question": context.question, "evidence": context.evidence, "sql": result["sql"], "label": result["label"],
              "correct": correct, "answered_by": result["answered_by"], "handoff_reason": result["handoff_reason"],
              "policy_model": config.POLICY_MODEL, "teacher_model": config.TEACHER_MODEL, "seed": context.seed,
              "messages": context.messages}
    with log_lock:
        config.EXPERIENCE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(config.EXPERIENCE_LOG, "a") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_steps(context):
    """Bir budget boyunca döngü. Return: kabul edilen cevap, ya da takılınca None (nedeni context.handoff_reason)."""
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
            if not context.teacher:
                context.handoff_reason = "aynı çağrı 3 kez tekrarlandı"
            return None
        elif earlier:  # aynı çağrı: çalıştırılmaz, önceki sonuç agent'a gider
            result = guards.repeat_note(earlier)
        elif step["tool"] == "search_values":
            result = search_values.run(step["args"]["query"], context)  # adım 3
        elif step["tool"] == "execute_sql":
            result = execute_sql.run(step["args"]["sql"], context)  # adım 4–6
        else:  # agent'ın da teacher'ın da submit'i aynı yoldan geçer: en son çalıştırdığı SQL cevaptır
            outcome = submit.run(context.last_run_sql, context)  # adım 7
            if outcome["done"]:
                context.add(step, "Accepted.")
                return context.answer(context.last_run_sql, "ok", by)
            if outcome["handoff"]:
                if not context.teacher:
                    context.handoff_reason = outcome["handoff"]
                context.add(step, f"Handoff: {outcome['handoff']}")
                return None
            result = outcome["note"]  # final check notu → adım 2

        if step["tool"] == "execute_sql" and not step["error"]:
            context.last_run_sql = step["args"]["sql"]  # tekrar olsa da: submit bunu gönderir
        context.add(step, result)
        context.stuck = bool(step["error"] or earlier)  # reddedildi ya da tekrarladı: sıradaki adım örneklenir
        if not context.teacher and context.calls == config.PROGRESS_CALLS and context.last_ok_sql is None:
            context.handoff_reason = "ilerleme yok"  # dolu sonuç veren hiçbir SQL yok: teacher erken devralır
            return None
        if context.calls_left > 0:  # kalan budget yalnızca modele giden mesaja eklenir, adım kaydına değil
            note = f"\n[{context.calls_left} tool call(s) left."
            if context.calls_left <= config.BUDGET_WARNING:
                note += " If the last query you ran answers the question, call submit now."
            context.messages[-1]["content"] += note + "]"

    if not context.teacher:
        context.handoff_reason = "budget bitti"
    return None


def next_step(context):
    """Konuşmanın şimdiye kadarki hâlini modele verir, cevabını tek bir tool call olarak okur. Model normalde en olası
    cevabı seçer (temperature 0); son çağrısı reddedildiyse ya da tekrarsa aynı girdiye yine aynı cevabı vereceği için
    bu kez RETRY_TEMPERATURE ile örneklenir."""
    model = config.TEACHER_MODEL if context.teacher else config.POLICY_MODEL
    temperature = config.RETRY_TEMPERATURE if context.stuck else None
    reply = llm.chat(context.messages, temperature=temperature, tools=prompts.TOOLS, seed=context.seed, model=model)
    context.count_usage(reply)
    return guards.read_tool_call(reply, prompts.TOOLS)


def start_teacher(context):
    """Handoff: teacher agent'ın bütün konuşmasını, nedeni ve yeni budget'ı söyleyen bir notla devralır."""
    context.teacher = True
    note = prompts.TEACHER_TAKEOVER.format(reason=context.handoff_reason, budget=context.budget())
    context.messages.append({"role": "user", "content": note})


def fallback_answer(context):
    """Hiçbir cevap kabul edilmediyse: agent'ın ya da teacher'ın en son hatasız ve dolu çalışan SQL'i (fallback);
    yoksa cevap yok (no_answer)."""
    if context.last_ok_sql is None:
        return context.answer(None, "no_answer")
    return context.answer(context.last_ok_sql, "fallback")
