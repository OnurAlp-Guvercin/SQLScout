"""Agent loop: akışın kendisi. Agent her turda tek bir tool çağırır; harness onu çalıştırır ve sonucu agent'a geri
verir. Her tool bir dal, her dal kendi adını taşıyan dosyaya gider (harness/tools/): search_values ve ask_user
(adım 3), execute_sql (adım 4–6), submit (adım 7–9).
Agent takılırsa (budget bitti, aynı çağrı 3 kez tekrarlandı, confidence low, ikinci medium, final check 2 kez geçmedi)
harness işi teacher'a verir (adım 10): teacher aynı döngüyle, yarım budget'la devam eder.
Soru bitince database memory ve experience log yazılır."""

import json
import threading
import time
from pathlib import Path

import config
from agent import llm, prompts
from agent.context import Context
from harness import guards, memory, prepare
from harness.tools import ask_user, execute_sql, search_values, submit

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
    if result is None:  # adım 10: teacher kaldığı yerden devam eder
        start_teacher(context)
        result = run_steps(context)
    if result is None:
        result = fallback_answer(context)
    memory.write(context, result)
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

        if step["error"]:  # tool call okunamadı: reddedilir, hata agent'a gider
            result = step["error"]
        elif len(earlier) >= config.MAX_REPEATS:  # aynı çağrının 3. tekrarı: agent takıldı
            context.add(step, "Handoff: the same call was repeated too many times.")
            if not context.teacher:
                context.handoff_reason = "aynı çağrı 3 kez tekrarlandı"
            return None
        elif earlier:  # aynı çağrı (submit hariç): çalıştırılmaz, önceki sonuç agent'a gider
            result = guards.repeat_note(earlier)
        elif step["tool"] == "search_values":
            result = search_values.run(step["args"]["query"], context)  # adım 3
        elif step["tool"] == "ask_user":
            result = ask_user.run(step["args"]["question"], context)  # adım 3
        elif step["tool"] == "execute_sql":
            result = execute_sql.run(step["args"]["sql"], context)  # adım 4–6
        elif context.teacher:  # teacher'ın submit'i candidate'lere gitmez, doğrudan final check'e gider
            return teacher_submit(step, context)
        else:
            outcome = submit.run(step["args"]["sql"], context)  # adım 7–9
            if outcome["done"]:
                context.add(step, "Accepted.")
                return context.answer(context.selected_sql, "ok")
            if outcome["handoff"]:
                context.handoff_reason = outcome["handoff"]
                context.add(step, f"Handoff: {outcome['handoff']}")
                return None
            result = outcome["note"]  # medium note ya da final check notu → adım 2

        context.add(step, result)
        if context.calls_left > 0:  # kalan budget yalnızca modele giden mesaja eklenir, adım kaydına değil
            note = f"\n[{context.calls_left} tool call(s) left."
            if context.calls_left <= config.BUDGET_WARNING:
                note += " If a query you ran answers the question, call submit with it now."
            context.messages[-1]["content"] += note + "]"

    if not context.teacher:
        context.handoff_reason = "budget bitti"
    return None


def next_step(context):
    """Konuşmanın şimdiye kadarki hâlini modele verir, cevabını tek bir tool call olarak okur."""
    model = config.TEACHER_MODEL if context.teacher else config.POLICY_MODEL
    reply = llm.chat(context.messages, tools=prompts.TOOLS, seed=context.seed, model=model)
    context.count_usage(reply)
    return guards.read_tool_call(reply, prompts.TOOLS)


def start_teacher(context):
    """Handoff: teacher agent'ın bütün konuşmasını, nedeni ve yeni budget'ı söyleyen bir notla devralır."""
    context.teacher = True
    note = prompts.TEACHER_TAKEOVER.format(reason=context.handoff_reason, budget=context.budget())
    context.messages.append({"role": "user", "content": note})


def teacher_submit(step, context):
    """Teacher'ın cevabı final check'ten geçerse ok. Geçmezse tekrar denenmez: SQL çalışıyorsa low_confidence ile
    return edilir (ör. beklenmeyen boş sonuç), hiç çalışmıyorsa fallback answer."""
    sql = step["args"]["sql"]
    note = submit.final_check(sql, context)
    context.add(step, note or "Accepted.")
    if note is None:
        return context.answer(sql, "ok", answered_by="teacher")
    if submit.result_of(sql, context):
        return context.answer(sql, "low_confidence", answered_by="teacher")
    return fallback_answer(context)


def fallback_answer(context):
    """Hiçbir cevap kabul edilmediyse: en son seçilen SQL, yoksa candidate'lerin consensus'u, o da yoksa en son
    hatasız çalışan SQL (low_confidence); hiçbiri yoksa cevap yok (no_answer)."""
    sql = context.selected_sql or submit.consensus_answer(context) or context.last_ok_sql
    if sql is None:
        return context.answer(None, "no_answer")
    return context.answer(sql, "low_confidence")
