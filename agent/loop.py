"""Agent loop: akışın kendisi (diyagramda adım 2'nin döngüsü). Agent her turda tek bir tool çağırır, harness onu
çalıştırır ve sonucu agent'a geri verir. submit gelince cevap adım 8–10'dan geçer. Agent takılırsa (budget bitti,
handoff tool'u, confidence low, ikinci medium, final check 2 kez geçmedi) teacher aynı döngüyle devam eder (adım 11)."""

import config
from agent import policy, prompts, tools
from agent.context import Context
from experience import log as experience_log
from experience import memory
from harness import (ask_user, candidates, compare, cost, final_check, gates, guards, handoff, precheck, prepare,
                     search)
from world_model import predict as world_model


def answer_question(question, evidence, db_path, seed=None, question_id=None, split=None, gold_sql=None,
                    ambiguity=None):
    context = Context(question, evidence, db_path, seed=seed, question_id=question_id, split=split,
                      gold_sql=gold_sql, ambiguity=ambiguity)
    if config.SIMULATE_COST:
        context.coins = context.coins_left = cost.start_coins(ambiguity)
    context.messages = [
        {"role": "system", "content": prompts.AGENT},
        {"role": "user", "content": prepare.build_context(question, evidence, db_path)},  # adım 1
    ]
    answer = run_steps(context)
    if answer is None and config.USE_HANDOFF:  # adım 11: teacher kaldığı yerden yeni bir budget'la devam eder
        handoff.start_teacher(context)
        answer = run_steps(context)
    if answer is None:
        answer = handoff.fallback_answer(context)
    memory.write(context, answer)  # cevap ok ise ve yolda bir hata olduysa
    return answer


def run_steps(context):
    """Bir budget boyunca döner. Döner: kabul edilen cevap, ya da takılınca None (nedeni context.handoff_reason)."""
    offered = tools.offered(context.teacher)
    context.budget_end = context.calls + config.MAX_TOOL_CALLS
    while cost.budget_left(context):  # tool call; SIMULATE_COST açıksa bird-coin de
        guards.compress(context)  # bağlam 32K token'ı aştıysa en eski observation'lar kısalır
        step = policy.next_step(context, offered)  # adım 2
        context.calls += 1
        cost.spend(step, context)

        if step["error"]:  # tool call okunamadı: reddedilir, hata agent'a döner
            result = step["error"]
        elif guards.is_repeat(step, context):  # aynı çağrı (submit hariç): çalıştırılmaz, önceki sonuç döner
            result = guards.repeat_note(step, context)
        elif step["tool"] in ("search_schema", "search_values"):
            result = search.run(step, context)  # adım 3
        elif step["tool"] == "ask_user":
            result = ask_user.run(step["args"]["question"], context)  # adım 3
        elif step["tool"] == "execute_sql":
            # Flag kapalıyken model yine de forecast yazarsa denetlenmemiştir; kullanılmaz.
            forecast = step["args"].get("forecast") if config.USE_AGENT_FORECAST else None
            result = run_query(step["args"]["sql"], forecast, context)  # adım 4–7
        elif step["tool"] == "handoff":
            context.handoff_reason = step["args"]["reason"]
            context.add(step, "Handed over.")
            return None
        elif context.teacher:  # teacher'ın submit'i candidate'lere gitmez, doğrudan final check'e gider
            return teacher_submit(step, context)
        else:
            outcome = finish(step["args"]["sql"], context)  # adım 8–10
            if outcome["done"]:
                context.add(step, "Accepted.")
                return context.answer(context.selected_sql, "ok")
            if outcome["handoff"]:
                context.handoff_reason = outcome["handoff"]
                context.add(step, f"Handoff: {outcome['handoff']}")
                return None
            result = outcome["note"]  # medium note ya da final check notu → adım 2

        context.add(step, result)

    if not context.teacher:
        context.handoff_reason = "budget bitti"
    return None


def run_query(sql, forecast, context):
    """Adım 5–7: pre-check; pahalıysa ya da budget azsa önce world model; sonra gerçek çalıştırma (ya da cache) ve
    forecast'le karşılaştırma. Döner: agent'a gidecek metin."""
    run_by = "teacher" if context.teacher else "agent"
    note = precheck.check(context.db_path, sql)  # adım 5: salt okuma ve EXPLAIN
    if note:
        remember_mistake(sql, note, context)
        return note
    prediction = None
    if precheck.needs_world_model(sql, context):  # adım 5'in 4. sorusu → adım 6
        prediction = world_model.predict(sql, context)
        if gates.trusted(prediction) and not gates.audit(sql, context):
            experience_log.write(context, sql, forecast, actual=None, seconds=0, run_by=run_by, prediction=prediction)
            return gates.prediction_note(prediction)  # trusted: sorgu çalıştırılmadı

    note, result = precheck.run(sql, context, run_by, forecast, prediction)  # adım 7
    observation = guards.format_result(result)
    if not result["ok"]:
        remember_mistake(sql, observation, context)
    if forecast:  # USE_AGENT_FORECAST kapalıysa forecast yok, surprise note da yok
        context.last_forecast[precheck.sql_key(sql)] = forecast
        context.forecasts += 1
        surprise = compare.surprise_note(forecast, compare.summary(result))
        if surprise:
            remember_mistake(sql, surprise, context)
            observation += "\n" + surprise
        else:
            context.forecast_hits += 1
    return observation


def remember_mistake(sql, note, context):
    if context.first_mistake is None:
        context.first_mistake = {"sql": sql, "note": note}


def finish(sql, context):
    """Adım 8–10: submit edilen SQL'den cevabı seçer (candidate'ler), confidence gate'ten ve final check'ten geçirir.
    Döner: {"done": cevap kabul edildi mi, "note": agent'a dönecek not, "handoff": handoff nedeni}."""
    if config.USE_CANDIDATES:
        groups, count = candidates.run(sql, context)  # adım 8
        context.selected_sql = groups[0]["sqls"][0] if groups else None
        level = gates.confidence(groups, count)  # adım 9
        if level == "low":
            return {"done": False, "note": None, "handoff": "confidence low"}
        if level == "medium":
            context.medium_notes += 1
            if context.medium_notes > config.MAX_MEDIUM_NOTES:
                return {"done": False, "note": None, "handoff": "ikinci kez medium"}
            return {"done": False, "note": gates.medium_note(groups, count), "handoff": None}
    else:
        context.selected_sql = sql

    note = final_check.check(context.selected_sql, context)  # adım 10
    if note is None:
        return {"done": True, "note": None, "handoff": None}
    context.final_check_fails += 1
    if context.final_check_fails >= config.FINAL_CHECK_TRIES:
        return {"done": False, "note": None, "handoff": "final check 2 kez geçmedi"}
    return {"done": False, "note": note, "handoff": None}


def teacher_submit(step, context):
    """Teacher'ın cevabı final check'ten geçerse ok; geçmezse tekrar denenmez, low_confidence ile döner."""
    sql = step["args"]["sql"]
    context.selected_sql = sql
    note = final_check.check(sql, context)
    context.add(step, note or "Accepted.")
    return context.answer(sql, "low_confidence" if note else "ok", answered_by="teacher")
