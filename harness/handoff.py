"""Adım 11: handoff. Agent takılınca ya da harness zorlayınca (budget bitti, confidence low, ikinci medium, final check
2 kez geçmedi) iş teacher'a geçer (aşama 22): teacher agent'ın bütün konuşmasını alır ve aynı döngüyle, yeni bir
budget'la devam eder (agent/loop.py). USE_HANDOFF kapalıysa ya da teacher submit etmezse fallback answer döner."""

import config
from agent import prompts


def start_teacher(context):
    context.teacher = True
    context.coins_left = context.coins  # SIMULATE_COST açıksa teacher da yeni bir bird-coin budget'ı alır
    note = prompts.TEACHER_TAKEOVER.format(reason=context.handoff_reason, budget=config.MAX_TOOL_CALLS)
    context.messages.append({"role": "user", "content": note})


def fallback_answer(context):
    """Hiçbir cevap kontrollerden geçmediğinde dönen en iyi cevap. Sıra: en son seçilen cevap (adım 8'in seçtiği SQL;
    USE_CANDIDATES kapalıysa submit edilen SQL) → en son hatasız çalışan SQL → cevap yok.
    İlk ikisi low_confidence, sonuncusu no_answer etiketi taşır."""
    if context.selected_sql:
        return context.answer(context.selected_sql, "low_confidence")
    if context.last_ok_sql:
        return context.answer(context.last_ok_sql, "low_confidence")
    return context.answer(None, "no_answer")
