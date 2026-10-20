"""Policy agent'ın modelle konuşan kısmı (diyagramda mavi sütun, adım 2).
write_sql: tool kullanmadan tek bir SQL yazar (aşama 5; adım 8'de candidate'leri de bu yazar).
next_step: agent loop'ta sıradaki tool call'u alır (aşama 6); handoff'tan sonra teacher modeliyle (aşama 22)."""

import re

import config
from agent import llm, prompts
from harness import guards


def next_step(context, tools):
    """Konuşmanın şimdiye kadarki hâlini modele verir, cevabını tek bir tool call olarak okur."""
    model = config.TEACHER_MODEL if context.teacher else config.POLICY_MODEL
    reply = llm.chat(context.messages, tools=tools, seed=context.seed, model=model)
    context.count_usage(reply)
    return guards.read_tool_call(reply, tools)


def write_sql(prompt, temperature=None, seed=None):
    """prompt: adım 1'in metni (şema, değerler, evidence, soru); candidate'lerde search notes ve clarification'lar da.
    Döner: sql ve modelin istek bilgileri."""
    messages = [
        {"role": "system", "content": prompts.WRITE_SQL},
        {"role": "user", "content": prompt},
    ]
    reply = llm.chat(messages, temperature=temperature, seed=seed)
    reply["sql"] = extract_sql(reply["text"])
    return reply


def extract_sql(text):
    """Modelin cevabından SQL'i çıkarır: önce ```sql bloğu, yoksa herhangi bir ``` bloğu, yoksa metnin tamamı."""
    match = re.search(r"```sql\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if not match:
        match = re.search(r"```\s*(.*?)```", text, re.DOTALL)
    sql = match.group(1) if match else text
    return sql.strip()
